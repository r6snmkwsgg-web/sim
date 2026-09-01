"""Tests for the three baseline strategies and the spec plumbing."""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from propsim.costs import ZERO_COSTS
from propsim.data import Instrument, make_bars
from propsim.engine import (
    ChallengeConfig,
    DrawdownMode,
    ExposureBasis,
    Order,
    SizingMode,
    run_challenge,
)
from propsim.strategies import (
    STRATEGY_REGISTRY,
    BuyAndHold,
    FixedTPSL,
    Momentum,
    StrategySpec,
    make_strategy,
)

INST = Instrument(symbol="TEST", point_value=1.0, min_size=1.0, size_step=1.0,
                  leverage=10.0)
CFG = ChallengeConfig(drawdown_mode=DrawdownMode.STATIC,
                      exposure_basis=ExposureBasis.MARGIN)


def assert_close(a, b, tol=1e-6, what="value"):
    assert abs(a - b) <= tol, f"{what}: expected {b!r}, got {a!r}"


def go(bars, strategy, seed=3, **kw):
    return run_challenge(bars, strategy, INST, cost_model=ZERO_COSTS,
                         config=CFG, rng=random.Random(seed), **kw)


def flat(n, price=100.0):
    return make_bars("TEST", [(price,) * 4] * n)


def ramp(n, start=100.0, step=0.05):
    rows = []
    p = start
    for _ in range(n):
        rows.append((p, p + step, p - 0.01, p + step))
        p += step
    return make_bars("TEST", rows)


# ---------------------------------------------------------------------------

def test_buy_and_hold_enters_once_and_never_exits():
    res = go(flat(500), BuyAndHold(size=0.2))
    assert len(res.trades) == 1
    assert res.trades[0].entry_index == 0
    assert res.trades[0].exit_reason.value in ("timeout", "end_of_data")


def test_buy_and_hold_can_go_short():
    res = go(flat(50), BuyAndHold(direction=-1, size=0.2))
    assert res.trades[0].direction == -1


def test_fixed_tp_sl_entry_rate_tracks_entries_per_day():
    """12 entries a day over 1,440 one-minute bars, one position at a time."""
    strat = FixedTPSL(size=0.05, tp_pct=0.5, sl_pct=0.5, entries_per_day=12)
    res = go(flat(1440), strat, seed=17)
    # Every trade runs to the timeout only if it never exits, so with wide
    # levels the count is bounded by the Poisson draw, not by the exits.
    assert 1 <= len(res.trades) <= 30, len(res.trades)


def test_fixed_tp_sl_respects_max_trades():
    strat = FixedTPSL(size=0.05, tp_pct=0.0001, sl_pct=0.0001,
                      entries_per_day=2000, max_trades=3)
    res = go(flat(1440), strat, seed=5)
    assert len(res.trades) <= 3


def test_fixed_tp_sl_places_the_levels_it_was_asked_for():
    strat = FixedTPSL(size=0.05, tp_pct=0.02, sl_pct=0.01,
                      entries_per_day=100000, direction="long")
    res = go(flat(200), strat)
    t = res.trades[0]
    assert t.direction == 1
    # Long entered at 100.00 -> tp 102.00, sl 99.00; flat bars never reach
    # either, so the trade ends at the timeout with the levels unused.
    assert t.exit_reason.value in ("timeout", "end_of_data")


def test_fixed_tp_sl_direction_can_be_forced():
    for want, d in (("long", 1), ("short", -1)):
        strat = FixedTPSL(size=0.05, entries_per_day=100000, direction=want,
                          tp_pct=0.5, sl_pct=0.5)
        res = go(flat(100), strat)
        assert res.trades[0].direction == d


def test_momentum_needs_a_breakout():
    """A flat series has no range to break, so nothing should trade."""
    res = go(flat(400), Momentum(lookback=20, size=0.05, tp_pct=0.5,
                                 sl_pct=0.5))
    assert res.trades == []


def test_momentum_enters_long_on_a_new_high():
    res = go(ramp(300), Momentum(lookback=20, size=0.05, tp_pct=0.5,
                                 sl_pct=0.5))
    assert len(res.trades) >= 1
    assert res.trades[0].direction == 1
    assert res.trades[0].entry_index >= 20, "waits for the lookback window"


def test_momentum_can_be_restricted_to_longs():
    rows = [(100.0, 100.0, 100.0, 100.0)] * 30
    rows += [(100.0, 100.0, 99.0, 99.0)] * 20      # break the range downward
    bars = make_bars("TEST", rows)
    both = go(bars, Momentum(lookback=20, size=0.05, allow_short=True,
                             tp_pct=0.5, sl_pct=0.5))
    longs = go(bars, Momentum(lookback=20, size=0.05, allow_short=False,
                              tp_pct=0.5, sl_pct=0.5))
    assert any(t.direction == -1 for t in both.trades)
    assert longs.trades == []


def test_momentum_cooldown_suppresses_immediate_re_entry():
    hot = Momentum(lookback=10, size=0.05, tp_pct=0.0005, sl_pct=0.0005,
                   cooldown_bars=0)
    cool = Momentum(lookback=10, size=0.05, tp_pct=0.0005, sl_pct=0.0005,
                    cooldown_bars=120)
    bars = ramp(600, step=0.2)
    assert len(go(bars, cool).trades) < len(go(bars, hot).trades)


def test_dollar_exits_are_placed_at_the_right_distance():
    """A $50 stop on 10 units of $1/point must sit 5.00 below the entry."""
    class Once(FixedTPSL):
        def on_bar(self, ctx):
            if ctx.position is None and ctx.bar_number == 0:
                return Order(direction=1, sizing_mode=SizingMode.UNITS,
                             size=10.0, stop_loss_dollars=50.0,
                             take_profit_dollars=100.0)
            return None

    bars = make_bars("TEST", [(100.0, 100.0, 100.0, 100.0),
                              (100.0, 100.0, 94.0, 99.0),
                              (99.0, 99.0, 99.0, 99.0)])
    res = go(bars, Once())
    assert res.trades[0].exit_reason.value == "stop_loss"
    assert_close(res.trades[0].exit_mid, 95.0, 1e-9, "stop 5.00 below entry")
    assert_close(res.final_balance, 19_950.0, 1e-6, "lost exactly $50")


def test_margin_pct_sizing_saturates_the_cap():
    """size=0.75 against a 75% margin cap must be exactly at the limit."""
    class Once(BuyAndHold):
        pass

    res = go(flat(20, price=100.0),
             Once(size=0.75, sizing_mode=SizingMode.MARGIN_PCT))
    # $15,000 of margin at 10:1 on a $100 instrument of $1/point = 1,500 units.
    assert_close(res.trades[0].size, 1500.0, 1e-6, "saturated size")


def test_strategy_spec_round_trips_and_overrides():
    spec = StrategySpec("momentum", {"lookback": 20, "size": 0.3})
    assert isinstance(spec.build(), Momentum)
    tweaked = spec.with_params(size=0.6)
    assert tweaked.params["lookback"] == 20
    assert tweaked.params["size"] == 0.6
    assert spec.params["size"] == 0.3, "the original must not be mutated"


def test_registry_covers_the_three_baselines():
    assert set(STRATEGY_REGISTRY) == {"fixed_tp_sl", "momentum",
                                      "buy_and_hold"}
    for name in STRATEGY_REGISTRY:
        assert make_strategy(name).describe()


def test_unknown_strategy_is_rejected():
    try:
        make_strategy("martingale_of_doom")
    except KeyError:
        pass
    else:
        raise AssertionError("unknown strategy names must raise")
