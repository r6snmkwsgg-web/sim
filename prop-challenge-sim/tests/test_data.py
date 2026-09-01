"""Tests for the data layer: wire formats, resampling, and the generator."""

from __future__ import annotations

import lzma
import os
import struct
import sys
import tempfile
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from propsim.costs import CostModel
from propsim.data import (
    DUKASCOPY_SYMBOLS,
    NS_PER_MINUTE,
    TICK_STRUCT,
    BarSeries,
    TickSeries,
    _dukascopy_url,
    decode_bi5,
    generate_synthetic,
    get_instrument,
    make_bars,
    ticks_to_bars,
)


def assert_close(actual, expected, tol=1e-9, what="value"):
    assert abs(actual - expected) <= tol, \
        f"{what}: expected {expected!r}, got {actual!r}"


def _bi5(records):
    """Build a Dukascopy payload from ``(ms, ask_pts, bid_pts)`` triples."""
    raw = b"".join(struct.pack(TICK_STRUCT, ms, a, b, 1.0, 2.0)
                   for ms, a, b in records)
    return lzma.compress(raw, format=lzma.FORMAT_ALONE)


# ---------------------------------------------------------------------------
# Dukascopy wire format
# ---------------------------------------------------------------------------

def test_bi5_round_trips():
    payload = _bi5([(0, 108_505, 108_495), (30_000, 108_520, 108_510)])
    ticks = decode_bi5(payload, 1e5, 0, "EURUSD")
    assert len(ticks) == 2
    assert_close(ticks.ask[0], 1.08505, 1e-9, "ask")
    assert_close(ticks.bid[0], 1.08495, 1e-9, "bid")
    assert ticks.ts[1] == 30_000 * 1_000_000, "ms offset -> ns"


def test_bi5_empty_hour_is_not_an_error():
    """Weekends and holidays legitimately have no ticks."""
    ticks = decode_bi5(b"", 1e5, 0, "EURUSD")
    assert len(ticks) == 0


def test_bi5_rejects_a_truncated_payload():
    raw = b"\x00" * 30                     # not a multiple of 20
    try:
        decode_bi5(lzma.compress(raw, format=lzma.FORMAT_ALONE), 1e5, 0, "X")
    except ValueError:
        pass
    else:
        raise AssertionError("a partial record should have been rejected")


def test_dukascopy_months_are_zero_indexed():
    """The single most common way to fetch the wrong month."""
    url = _dukascopy_url("EURUSD", datetime(2024, 1, 2, 5, tzinfo=timezone.utc))
    assert "/2024/00/02/05h_ticks.bi5" in url, url
    url = _dukascopy_url("EURUSD", datetime(2024, 12, 31, 23,
                                            tzinfo=timezone.utc))
    assert "/2024/11/31/23h_ticks.bi5" in url, url


def test_nq_is_flagged_as_a_proxy():
    """Dukascopy has no CME futures; the CFD must not masquerade as one."""
    assert DUKASCOPY_SYMBOLS["MNQ"][2] is True
    assert DUKASCOPY_SYMBOLS["EURUSD"][2] is False


# ---------------------------------------------------------------------------
# Resampling
# ---------------------------------------------------------------------------

def test_ticks_to_bars_builds_mid_ohlc_and_measures_the_spread():
    ticks = decode_bi5(_bi5([
        (0,      108_510, 108_490),        # mid 1.08500, spread 0.0002
        (10_000, 108_610, 108_590),        # mid 1.08600  <- high
        (20_000, 108_410, 108_390),        # mid 1.08400  <- low
        (50_000, 108_520, 108_500),        # mid 1.08510  <- close
        (61_000, 108_700, 108_680),        # next bar
    ]), 1e5, 0, "EURUSD")
    bars = ticks_to_bars(ticks, 60)
    assert len(bars) == 2
    assert_close(bars.open[0], 1.085, 1e-9, "open")
    assert_close(bars.high[0], 1.086, 1e-9, "high")
    assert_close(bars.low[0], 1.084, 1e-9, "low")
    assert_close(bars.close[0], 1.0851, 1e-9, "close")
    assert_close(bars.spread[0], 0.0002, 1e-9, "mean measured spread")
    assert bars.volume[0] == 4.0, "tick count as volume"
    bars.validate()


def test_measured_spread_beats_the_configured_one():
    bars = make_bars("EURUSD", [(1.0,) * 4] * 3)
    bars.spread = [0.0002, 0.0002, 0.0002]
    cm = CostModel(spread=0.00008, commission_per_side=0.0)
    hs = cm.half_spread_series(bars)
    assert_close(hs[0], 0.0001, 1e-12, "half of the measured spread")
    ignored = CostModel(spread=0.00008, commission_per_side=0.0,
                        use_measured_spread=False)
    assert_close(ignored.half_spread_series(bars)[0], 0.00004, 1e-12,
                 "falls back to the configured spread")


def test_spread_multiplier_is_a_stress_knob():
    bars = make_bars("EURUSD", [(1.0,) * 4] * 2)
    bars.spread = [0.0002, 0.0002]
    cm = CostModel(spread=0.0, spread_multiplier=2.0)
    assert_close(cm.half_spread_series(bars)[0], 0.0002, 1e-12, "2x spread")


def test_session_widening_wraps_past_midnight():
    cm = CostModel(spread=0.0001, session_widening=((22, 2, 4.0),))
    day = 24 * 3_600 * 1_000_000_000
    assert_close(cm.widening_at(23 * 3_600_000_000_000), 4.0, 1e-12, "23:00")
    assert_close(cm.widening_at(1 * 3_600_000_000_000), 4.0, 1e-12, "01:00")
    assert_close(cm.widening_at(12 * 3_600_000_000_000), 1.0, 1e-12, "12:00")


# ---------------------------------------------------------------------------
# BarSeries
# ---------------------------------------------------------------------------

def test_csv_round_trip_preserves_the_spread():
    bars = make_bars("EURUSD", [(1.0, 1.1, 0.9, 1.05), (1.05, 1.2, 1.0, 1.15)])
    bars.spread = [0.0001, 0.0002]
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "bars.csv")
        bars.to_csv(path)
        back = BarSeries.from_csv(path, "EURUSD")
    assert back.ts == bars.ts
    assert back.spread == bars.spread
    assert_close(back.high[1], 1.2, 1e-12, "high")


def test_slice_keeps_the_spread_aligned():
    bars = make_bars("X", [(1.0,) * 4] * 5)
    bars.spread = [0.1, 0.2, 0.3, 0.4, 0.5]
    cut = bars.slice(2, 4)
    assert len(cut) == 2
    assert cut.spread == [0.3, 0.4]


def test_step_ns_survives_session_gaps():
    """A weekend gap must not be mistaken for the bar length."""
    bars = make_bars("X", [(1.0,) * 4] * 10)
    bars.ts = bars.ts[:5] + [t + 3 * 86_400 * 10 ** 9 for t in bars.ts[5:]]
    assert bars.step_ns == NS_PER_MINUTE


def test_index_at_or_after():
    bars = make_bars("X", [(1.0,) * 4] * 10)
    assert bars.index_at_or_after(bars.ts[4]) == 4
    assert bars.index_at_or_after(bars.ts[4] - 1) == 4
    assert bars.index_at_or_after(bars.ts[4] + 1) == 5


# ---------------------------------------------------------------------------
# Synthetic generator
# ---------------------------------------------------------------------------

def test_synthetic_is_deterministic_and_valid():
    a = generate_synthetic("EURUSD", days=3, seed=11)
    b = generate_synthetic("EURUSD", days=3, seed=11)
    c = generate_synthetic("EURUSD", days=3, seed=12)
    a.validate()
    assert a.close == b.close, "same seed, same path"
    assert a.close != c.close, "different seed, different path"


def test_synthetic_respects_the_weekend():
    bars = generate_synthetic("EURUSD", days=14, seed=2)
    for t in bars.ts:
        when = datetime.fromtimestamp(t / 1e9, timezone.utc)
        assert not (when.weekday() == 5), "no Saturday bars"


def test_synthetic_ranges_are_built_from_a_path():
    """Highs and lows must come from simulated sub-bar steps, not decoration.

    If the range were fabricated the low would frequently sit above the open
    or below both open and close by a constant, and the drawdown study would
    be measuring an artefact.
    """
    bars = generate_synthetic("XAUUSD", days=3, seed=4)
    bars.validate()
    strictly_inside = sum(1 for i in range(len(bars))
                          if bars.low[i] < min(bars.open[i], bars.close[i])
                          and bars.high[i] > max(bars.open[i], bars.close[i]))
    assert strictly_inside > 0.3 * len(bars), \
        "most bars should overshoot both ends of the open/close range"


def test_synthetic_volatility_clusters():
    """Absolute returns should be autocorrelated -- that is what makes
    drawdown tails fat, and a constant-vol GBM would not show it."""
    bars = generate_synthetic("EURUSD", days=20, seed=7)
    r = [abs(bars.close[i] / bars.close[i - 1] - 1.0)
         for i in range(1, len(bars))]
    n = len(r)
    mean = sum(r) / n
    num = sum((r[i] - mean) * (r[i - 1] - mean) for i in range(1, n))
    den = sum((x - mean) ** 2 for x in r)
    assert num / den > 0.05, "expected positive autocorrelation in |returns|"


def test_instrument_lookup_and_contract_maths():
    eur = get_instrument("EURUSD")
    assert_close(eur.notional(1.0, 1.10), 110_000.0, 1e-6, "1 lot notional")
    assert_close(eur.margin_required(1.0, 1.10), 110_000.0 / 30.0, 1e-6,
                 "30:1 margin")
    mnq = get_instrument("MNQ")
    assert_close(mnq.margin_required(3.0, 18_000.0), 7_200.0, 1e-6,
                 "flat margin per contract")
    assert_close(mnq.round_size(2.9), 2.0, 1e-12, "rounds down to whole lots")


def test_zero_costs_really_is_zero_even_with_measured_spreads():
    """A control named ZERO_COSTS must not quietly charge the measured
    spread when the series happens to carry one."""
    from propsim.costs import ZERO_COSTS
    bars = make_bars("EURUSD", [(1.0,) * 4] * 3)
    bars.spread = [0.0002] * 3
    assert ZERO_COSTS.half_spread_series(bars) == [0.0, 0.0, 0.0]
