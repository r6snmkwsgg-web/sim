"""
Tests for the challenge engine.

The suite is organised around the one thing that is easy to get wrong and
expensive to get wrong: the drawdown limit is a property of the *path*, not of
the closes.  ``test_dip_below_drawdown_then_recovers_is_a_fail`` is the
headline case and it asserts both halves of the claim -- that the engine fails
the attempt, and that a close-only engine would have passed it.

Written as plain functions with bare asserts, so they run under pytest and
under ``python run_tests.py`` unchanged.
"""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from propsim.costs import ZERO_COSTS, CostModel
from propsim.data import NS_PER_MINUTE, BarSeries, Instrument, make_bars
from propsim.engine import (
    CLOSE,
    ChallengeConfig,
    DrawdownMode,
    ExitReason,
    ExposureBasis,
    IntrabarOrder,
    Order,
    Outcome,
    SizingMode,
    Strategy,
    run_challenge,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

#: $1 of P&L per 1.00 of price per unit.  Keeps every expected number in the
#: tests arithmetic a reader can do in their head.
TEST_INSTRUMENT = Instrument(
    symbol="TEST", point_value=1.0, unit_name="unit",
    min_size=1.0, size_step=1.0, leverage=1.0,
    tick_size=0.01, price_decimals=2,
)

BASE_CONFIG = ChallengeConfig(drawdown_mode=DrawdownMode.STATIC)


def assert_close(actual, expected, tol=1e-6, what="value"):
    assert abs(actual - expected) <= tol, \
        f"{what}: expected {expected!r}, got {actual!r} (tol {tol})"


class Scripted(Strategy):
    """Emits pre-programmed actions keyed by bar number within the attempt."""

    name = "scripted"

    def __init__(self, actions):
        self.actions = dict(actions)
        self.seen_indices = []

    def on_start(self, ctx):
        self.seen_indices = []

    def on_bar(self, ctx):
        self.seen_indices.append(ctx.i)
        return self.actions.get(ctx.bar_number)


class NeverTrades(Strategy):
    name = "never"

    def on_bar(self, ctx):
        return None


def long_units(n, **kw):
    return Order(direction=1, sizing_mode=SizingMode.UNITS, size=n, **kw)


def short_units(n, **kw):
    return Order(direction=-1, sizing_mode=SizingMode.UNITS, size=n, **kw)


def flat_bars(n, price=100.0, start="2024-01-02T00:00:00Z"):
    return make_bars("TEST", [(price, price, price, price)] * n, start=start)


def run(bars, strategy, costs=ZERO_COSTS, config=BASE_CONFIG, **kw):
    return run_challenge(bars, strategy, TEST_INSTRUMENT, cost_model=costs,
                         config=config, rng=random.Random(7), **kw)


# ---------------------------------------------------------------------------
# THE test: path dependence
# ---------------------------------------------------------------------------

def test_dip_below_drawdown_then_recovers_is_a_fail():
    """A trade that goes $400 underwater intrabar and closes green is a FAIL.

    Long 100 units at 100.00 ($100 per 1.00 of price):

        bar 1  low 96.00  -> equity 19,600, which is $400 below the start
        bar 1  close 101  -> equity 20,100  (green at the close)
        bar 2  close 120  -> equity 22,000  (past the +1,500 target)

    Reading only the closes, this attempt passes.  Reading the path, the
    account was liquidated on bar 1.
    """
    bars = make_bars("TEST", [
        (100.0, 100.0, 100.0, 100.0),    # entry bar
        (100.0, 101.0, 96.0, 101.0),     # dips $400 under, closes $100 up
        (101.0, 121.0, 101.0, 120.0),    # would have blown past the target
    ])
    res = run(bars, Scripted({0: long_units(100)}))

    assert res.outcome is Outcome.FAIL_DRAWDOWN
    assert res.breach_ts == bars.ts[1]
    # Liquidated the instant equity touched 19,700 -- at 100 units of $1 per
    # point that is a mid of 97.00, three full points above the bar low.
    assert_close(res.final_balance, 19_700.0, what="final_balance")
    assert_close(res.breach_equity, 19_600.0, what="raw mark at the bar low")
    assert len(res.trades) == 1
    assert res.trades[0].exit_reason is ExitReason.DRAWDOWN_BREACH
    assert_close(res.trades[0].exit_mid, 97.0, what="liquidation price")

    # And the counterfactual, so the test documents *why* it matters: an
    # engine that only looked at bar closes would have called this a PASS.
    entry = 100.0
    size = 100.0
    close_only_equity = [20_000.0 + (c - entry) * size for c in bars.close[1:]]
    assert min(close_only_equity) > BASE_CONFIG.starting_balance - 300.0, \
        "no bar close ever breaches -- the breach is intrabar only"
    assert max(close_only_equity) >= BASE_CONFIG.target_equity, \
        "a close-only engine would have recorded a PASS here"


def test_short_side_breach_uses_the_bar_high():
    """The mirror image: for a short the adverse extreme is the high."""
    bars = make_bars("TEST", [
        (100.0, 100.0, 100.0, 100.0),
        (100.0, 104.0, 100.0, 99.0),     # +$400 against a short, closes green
        (99.0, 99.0, 80.0, 80.0),
    ])
    res = run(bars, Scripted({0: short_units(100)}))
    assert res.outcome is Outcome.FAIL_DRAWDOWN
    assert_close(res.final_balance, 19_700.0, what="final_balance")
    assert_close(res.trades[0].exit_mid, 103.0, what="liquidation price")


def test_breach_exactly_at_the_limit_is_a_breach():
    """Touching the limit counts; the comparison is inclusive."""
    bars = make_bars("TEST", [
        (100.0, 100.0, 100.0, 100.0),
        (100.0, 100.0, 97.0, 100.0),     # exactly -$300
        (100.0, 100.0, 100.0, 100.0),
    ])
    res = run(bars, Scripted({0: long_units(100)}))
    assert res.outcome is Outcome.FAIL_DRAWDOWN
    assert_close(res.final_balance, 19_700.0, what="final_balance")


def test_one_dollar_inside_the_limit_survives():
    """The boundary is tested from both sides."""
    bars = make_bars("TEST", [
        (100.0, 100.0, 100.0, 100.0),
        (100.0, 100.0, 97.01, 100.0),    # -$299
        (100.0, 100.0, 100.0, 100.0),
    ])
    res = run(bars, Scripted({0: long_units(100)}))
    assert res.outcome is not Outcome.FAIL_DRAWDOWN
    assert_close(res.max_drawdown_reached, 299.0, tol=1e-6,
                 what="max drawdown reached")


def test_resting_stop_truncates_the_adverse_excursion():
    """A stop inside the bar caps the drawdown at the stop, not at the low.

    Without this the engine invents breaches that could not physically happen:
    the position is already gone by the time price reaches the low.
    """
    bars = make_bars("TEST", [
        (100.0, 100.0, 100.0, 100.0),
        (100.0, 100.0, 90.0, 95.0),      # low is -$1,000; the stop is -$50
        (95.0, 95.0, 95.0, 95.0),
    ])
    res = run(bars, Scripted({0: long_units(100, stop_loss_price=99.5)}))
    assert res.outcome is not Outcome.FAIL_DRAWDOWN
    assert res.trades[0].exit_reason is ExitReason.STOP_LOSS
    assert_close(res.final_balance, 19_950.0, what="final_balance")


# ---------------------------------------------------------------------------
# Outcomes
# ---------------------------------------------------------------------------

def test_pass_when_equity_touches_the_target_intrabar():
    bars = make_bars("TEST", [
        (100.0, 100.0, 100.0, 100.0),
        (100.0, 116.0, 100.0, 115.0),    # +$1,600 at the high
        (115.0, 115.0, 115.0, 115.0),
    ])
    res = run(bars, Scripted({0: long_units(100)}))
    assert res.outcome is Outcome.PASS
    assert res.trades[0].exit_reason is ExitReason.PROFIT_TARGET
    # Closed exactly on the target rather than at the bar high.
    assert_close(res.final_balance, 21_500.0, what="final_balance")
    assert_close(res.trades[0].exit_mid, 115.0, what="exit price")


def test_timeout_when_neither_limit_is_hit():
    bars = flat_bars(2000)               # 2,000 minutes > 24 hours
    res = run(bars, NeverTrades())
    assert res.outcome is Outcome.FAIL_TIMEOUT
    assert res.bars_in_window == 1440, "24h of 1-minute bars"
    assert res.truncated is False
    assert_close(res.final_balance, 20_000.0, what="final_balance")
    assert res.trades == []


def test_open_position_is_closed_at_the_24h_boundary():
    bars = flat_bars(2000)
    res = run(bars, Scripted({0: long_units(10)}))
    assert res.outcome is Outcome.FAIL_TIMEOUT
    assert len(res.trades) == 1
    assert res.trades[0].exit_reason is ExitReason.TIMEOUT
    assert res.trades[0].exit_index == 1439
    assert res.bars_in_market == 1439


def test_truncated_when_the_data_runs_out_first():
    bars = flat_bars(120)                # only 2 hours available
    res = run(bars, NeverTrades())
    assert res.truncated is True
    assert res.bars_in_window == 120


def test_target_measured_on_closed_balance_when_configured():
    """With ``target_on_equity=False`` an unrealised spike does not pass."""
    cfg = ChallengeConfig(drawdown_mode=DrawdownMode.STATIC,
                          target_on_equity=False)
    bars = make_bars("TEST", [
        (100.0, 100.0, 100.0, 100.0),
        (100.0, 116.0, 100.0, 100.5),    # +$1,600 unrealised, gives it back
        (100.5, 120.0, 100.5, 120.0),
    ])
    res = run(bars, Scripted({0: long_units(100), 2: CLOSE}), config=cfg)
    assert res.outcome is Outcome.PASS
    assert res.trades[0].exit_reason is ExitReason.STRATEGY_CLOSE
    assert_close(res.final_balance, 22_000.0, what="final_balance")


# ---------------------------------------------------------------------------
# Drawdown modes
# ---------------------------------------------------------------------------

def test_trailing_drawdown_is_stricter_than_static():
    """Same path, two rulebooks, two verdicts.

    Equity peaks at +$500 then gives back $350.  A static floor at 19,700 is
    never threatened; a trailing floor that followed the peak to 20,200 is.
    """
    bars = make_bars("TEST", [
        (100.0, 100.0, 100.0, 100.0),
        (100.0, 105.0, 100.0, 105.0),    # peak equity 20,500
        (105.0, 105.0, 101.5, 105.0),    # -$350 from the peak
        (105.0, 105.0, 105.0, 105.0),
    ])
    strat = lambda: Scripted({0: long_units(100)})

    static = run(bars, strat(),
                 config=ChallengeConfig(drawdown_mode=DrawdownMode.STATIC))
    assert static.outcome is not Outcome.FAIL_DRAWDOWN

    trailing = run(bars, strat(), config=ChallengeConfig(
        drawdown_mode=DrawdownMode.TRAILING_EQUITY))
    assert trailing.outcome is Outcome.FAIL_DRAWDOWN
    assert_close(trailing.final_balance, 20_200.0, what="final_balance")
    assert_close(trailing.peak_equity, 20_500.0, what="peak equity")


def test_trailing_balance_ignores_unrealised_peaks():
    """TRAILING_BALANCE only ratchets when a trade is actually closed."""
    bars = make_bars("TEST", [
        (100.0, 100.0, 100.0, 100.0),
        (100.0, 105.0, 100.0, 105.0),    # unrealised peak, nothing closed
        (105.0, 105.0, 101.5, 105.0),
        (105.0, 105.0, 105.0, 105.0),
    ])
    res = run(bars, Scripted({0: long_units(100)}), config=ChallengeConfig(
        drawdown_mode=DrawdownMode.TRAILING_BALANCE))
    assert res.outcome is not Outcome.FAIL_DRAWDOWN


# ---------------------------------------------------------------------------
# Intrabar ordering
# ---------------------------------------------------------------------------

def test_stop_and_target_in_one_bar_resolve_by_intrabar_order():
    """When both levels sit inside a bar, OHLC cannot say which came first.

    The default resolves it against the trader, which is the only defensible
    choice for a risk study.
    """
    bars = make_bars("TEST", [
        (100.0, 100.0, 100.0, 100.0),
        (100.0, 103.0, 97.0, 101.0),     # touches both 102 and 98
        (101.0, 101.0, 101.0, 101.0),
    ])
    order = lambda: long_units(100, take_profit_price=102.0,
                               stop_loss_price=98.0)

    adverse = run(bars, Scripted({0: order()}), config=ChallengeConfig(
        drawdown_mode=DrawdownMode.STATIC,
        intrabar_order=IntrabarOrder.ADVERSE_FIRST))
    assert adverse.trades[0].exit_reason is ExitReason.STOP_LOSS
    assert_close(adverse.final_balance, 19_800.0, what="stopped out")

    favorable = run(bars, Scripted({0: order()}), config=ChallengeConfig(
        drawdown_mode=DrawdownMode.STATIC,
        intrabar_order=IntrabarOrder.FAVORABLE_FIRST))
    assert favorable.trades[0].exit_reason is ExitReason.TAKE_PROFIT
    assert_close(favorable.final_balance, 20_200.0, what="target hit")


def test_intrabar_order_changes_the_verdict_on_a_marginal_bar():
    """Favourable-first can lift the trailing floor above a later dip."""
    bars = make_bars("TEST", [
        (100.0, 100.0, 100.0, 100.0),
        (100.0, 101.0, 97.2, 100.0),     # high +$100, low -$280
        (100.0, 100.0, 100.0, 100.0),
    ])
    cfg = lambda o: ChallengeConfig(drawdown_mode=DrawdownMode.TRAILING_EQUITY,
                                    intrabar_order=o)
    adverse = run(bars, Scripted({0: long_units(100)}),
                  config=cfg(IntrabarOrder.ADVERSE_FIRST))
    favorable = run(bars, Scripted({0: long_units(100)}),
                    config=cfg(IntrabarOrder.FAVORABLE_FIRST))
    # -$280 from the start survives; -$280 measured from a +$100 peak does not.
    assert adverse.outcome is not Outcome.FAIL_DRAWDOWN
    assert favorable.outcome is Outcome.FAIL_DRAWDOWN


# ---------------------------------------------------------------------------
# Costs
# ---------------------------------------------------------------------------

def test_costs_are_charged_on_entry_and_exit():
    """Round trip at an unchanged price must lose exactly spread + commission."""
    costs = CostModel(spread=0.10, commission_per_side=2.50)
    bars = flat_bars(3)
    res = run(bars, Scripted({0: long_units(10), 1: CLOSE}), costs=costs)

    assert_close(res.spread_paid, 1.00, what="spread")        # 0.10 * 1 * 10
    assert_close(res.commission_paid, 50.00, what="commission")  # $5 RT * 10
    assert_close(res.total_costs, 51.00, what="total costs")
    assert_close(res.final_balance, 19_949.00, what="final_balance")
    assert_close(res.trades[0].net_pnl, -51.00, what="net pnl")
    assert_close(res.trades[0].gross_pnl, 0.0, what="gross pnl")

    frictionless = run(bars, Scripted({0: long_units(10), 1: CLOSE}))
    assert_close(frictionless.final_balance, 20_000.0,
                 what="frictionless control")


def test_costs_alone_can_breach_the_floor():
    """Enough size and the round-turn friction is itself a blown account."""
    costs = CostModel(spread=1.0, commission_per_side=2.50)
    bars = flat_bars(3)
    res = run(bars, Scripted({0: long_units(100)}), costs=costs)
    # 100 units: $100 of spread + $500 of commission on a $300 limit.
    assert res.outcome is Outcome.FAIL_DRAWDOWN
    assert res.trades[0].exit_index == 0, "dies on the entry bar"


def test_session_widening_applies_to_the_right_hours():
    costs = CostModel(spread=0.10, commission_per_side=0.0,
                      session_widening=((21, 1, 3.0),))
    quiet = make_bars("TEST", [(100.0,) * 4] * 3,
                      start="2024-01-02T10:00:00Z")
    rollover = make_bars("TEST", [(100.0,) * 4] * 3,
                         start="2024-01-02T22:00:00Z")
    a = run(quiet, Scripted({0: long_units(10), 1: CLOSE}), costs=costs)
    b = run(rollover, Scripted({0: long_units(10), 1: CLOSE}), costs=costs)
    assert_close(a.spread_paid, 1.00, what="quiet-hours spread")
    assert_close(b.spread_paid, 3.00, what="rollover spread")


# ---------------------------------------------------------------------------
# Sizing and the exposure cap
# ---------------------------------------------------------------------------

def test_exposure_cap_scales_the_position_down():
    """1,000 units at 100 is $100k notional against a $15k cap -> 150 units."""
    bars = flat_bars(3)
    res = run(bars, Scripted({0: long_units(1000), 1: CLOSE}))
    assert_close(res.trades[0].size, 150.0, what="capped size")


def test_account_pct_sizing_matches_the_cap():
    bars = flat_bars(3)
    res = run(bars, Scripted({
        0: Order(direction=1, sizing_mode=SizingMode.ACCOUNT_PCT, size=0.75),
        1: CLOSE}))
    assert_close(res.trades[0].size, 150.0, what="75% of equity as notional")


def test_notional_sizing():
    bars = flat_bars(3)
    res = run(bars, Scripted({
        0: Order(direction=1, sizing_mode=SizingMode.NOTIONAL, size=5_000.0),
        1: CLOSE}))
    assert_close(res.trades[0].size, 50.0, what="$5,000 / (100 * 1)")


def test_margin_basis_allows_far_more_size():
    """The cap's meaning is a real modelling fork, so both readings are testable."""
    lever = Instrument(symbol="TEST", point_value=1.0, min_size=1.0,
                       size_step=1.0, leverage=30.0)
    bars = flat_bars(3)
    res = run_challenge(
        bars, Scripted({0: long_units(1000), 1: CLOSE}), lever,
        cost_model=ZERO_COSTS,
        config=ChallengeConfig(drawdown_mode=DrawdownMode.STATIC,
                               exposure_basis=ExposureBasis.MARGIN),
        rng=random.Random(1))
    # $100k notional / 30 = $3.3k of margin, comfortably under the $15k cap.
    assert_close(res.trades[0].size, 1000.0, what="uncapped under margin basis")


def test_order_below_minimum_size_is_rejected():
    bars = flat_bars(3)
    res = run(bars, Scripted({
        0: Order(direction=1, sizing_mode=SizingMode.NOTIONAL, size=50.0)}))
    assert res.trades == []
    assert res.orders_rejected == 1


def test_orders_while_in_a_position_are_rejected():
    bars = flat_bars(5)
    res = run(bars, Scripted({0: long_units(10), 1: short_units(10), 4: CLOSE}))
    assert len(res.trades) == 1
    assert res.orders_rejected == 1
    assert res.trades[0].direction == 1


# ---------------------------------------------------------------------------
# Bookkeeping invariants
# ---------------------------------------------------------------------------

def test_balance_reconciles_with_the_trade_log():
    costs = CostModel(spread=0.05, commission_per_side=2.50)
    bars = flat_bars(20, price=100.0)
    res = run(bars, Scripted({0: long_units(10), 3: CLOSE,
                              5: short_units(10), 9: CLOSE}), costs=costs)
    assert len(res.trades) == 2
    total = sum(t.net_pnl for t in res.trades)
    assert_close(res.final_balance, 20_000.0 + total, what="balance vs log")
    assert_close(res.total_costs,
                 sum(t.spread_cost + t.commission for t in res.trades),
                 what="cost totals vs log")


def test_equity_curve_tracks_the_run():
    bars = flat_bars(100)
    res = run(bars, Scripted({0: long_units(10), 50: CLOSE}))
    assert len(res.equity_curve) == res.bars_in_window
    assert len(res.equity_ts) == res.bars_in_window
    assert_close(res.equity_curve[-1], res.final_equity, what="curve tail")
    assert res.equity_ts[0] == bars.ts[0]


def test_final_equity_equals_final_balance_when_flat():
    bars = flat_bars(50)
    res = run(bars, Scripted({0: long_units(10), 10: CLOSE}))
    assert_close(res.final_equity, res.final_balance, what="flat at the end")


def test_max_drawdown_and_min_equity_are_reported():
    bars = make_bars("TEST", [
        (100.0, 100.0, 100.0, 100.0),
        (100.0, 100.0, 98.0, 100.0),     # -$200 intrabar
        (100.0, 100.0, 100.0, 100.0),
    ])
    res = run(bars, Scripted({0: long_units(100), 2: CLOSE}))
    assert_close(res.max_drawdown_reached, 200.0, what="max drawdown")
    assert_close(res.min_equity, 19_800.0, what="min equity")
    assert_close(res.max_drawdown_from_start, 200.0, what="drawdown from start")


# ---------------------------------------------------------------------------
# Windowing and lookahead
# ---------------------------------------------------------------------------

def test_start_index_defines_the_window():
    bars = flat_bars(5000)
    res = run(bars, NeverTrades(), start_index=1000)
    assert res.start_ts == bars.ts[1000]
    assert res.bars_in_window == 1440
    assert res.end_ts == bars.ts[1000 + 1439]


def test_duration_is_configurable():
    bars = flat_bars(2000)
    cfg = ChallengeConfig(drawdown_mode=DrawdownMode.STATIC, duration_hours=6.0)
    res = run(bars, NeverTrades(), config=cfg)
    assert res.bars_in_window == 360


def test_orders_fill_at_the_signal_bars_close():
    bars = make_bars("TEST", [
        (100.0, 101.0, 99.0, 100.5),
        (100.5, 102.0, 100.0, 101.0),
        (101.0, 101.0, 101.0, 101.0),
    ])
    res = run(bars, Scripted({0: long_units(10), 2: CLOSE}))
    assert_close(res.trades[0].entry_mid, 100.5, what="fills at close[0]")
    assert res.trades[0].entry_index == 0


def test_strategy_cannot_see_the_future():
    """Rewriting bars *after* the decision bar must not change the decision.

    The engine cannot forbid a strategy from indexing past ``ctx.i``; this
    pins down that the engine itself does not hand it future information.
    """
    class RecordsWhatItSaw(Strategy):
        name = "recorder"

        def on_start(self, ctx):
            self.snapshot = None

        def on_bar(self, ctx):
            if ctx.bar_number == 1:
                self.snapshot = (ctx.i, ctx.price, ctx.equity, ctx.balance)
                return long_units(10)
            return None

    base = [(100.0, 101.0, 99.0, 100.0), (100.0, 101.0, 99.0, 100.5)]
    a_strat, b_strat = RecordsWhatItSaw(), RecordsWhatItSaw()
    a = run(make_bars("TEST", base + [(100.5, 101.0, 100.0, 100.7)] * 5),
            a_strat)
    b = run(make_bars("TEST", base + [(100.5, 140.0, 60.0, 130.0)] * 5),
            b_strat)

    assert a_strat.snapshot == b_strat.snapshot
    assert_close(a.trades[0].entry_mid, b.trades[0].entry_mid,
                 what="entry unaffected by future bars")
    # ... while the outcomes differ, proving the futures really were different.
    assert a.outcome is not b.outcome


def test_bar_indices_are_visited_in_order_exactly_once():
    bars = flat_bars(100)
    strat = Scripted({})
    run(bars, strat, start_index=10)
    assert strat.seen_indices == list(range(10, 100))


# ---------------------------------------------------------------------------
# Series integrity
# ---------------------------------------------------------------------------

def test_bar_series_validation_rejects_impossible_bars():
    bad = BarSeries(symbol="X", ts=[0, int(NS_PER_MINUTE)],
                    open=[100.0, 100.0], high=[100.0, 99.0],
                    low=[99.0, 98.0], close=[99.5, 100.0])
    try:
        bad.validate()
    except ValueError:
        pass
    else:
        raise AssertionError("high < close should have been rejected")


def test_bar_series_validation_rejects_unsorted_timestamps():
    bad = BarSeries(symbol="X", ts=[int(NS_PER_MINUTE), 0],
                    open=[100.0, 100.0], high=[101.0, 101.0],
                    low=[99.0, 99.0], close=[100.0, 100.0])
    try:
        bad.validate()
    except ValueError:
        pass
    else:
        raise AssertionError("descending timestamps should have been rejected")
