"""Tests for sampling, aggregation and the two confidence intervals."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from propsim.costs import ZERO_COSTS, get_costs
from propsim.data import INSTRUMENTS, generate_synthetic, make_bars
from propsim.engine import ChallengeConfig, DrawdownMode, Outcome
from propsim.montecarlo import (
    Attempt,
    MonteCarloConfig,
    MonteCarloResult,
    independent_window_count,
    run_monte_carlo,
    sample_starts,
    valid_start_range,
    _z_for,
)
from propsim.strategies import StrategySpec

CFG = ChallengeConfig()
INST = INSTRUMENTS["EURUSD"]
COSTS = get_costs("EURUSD")
SPEC = StrategySpec("fixed_tp_sl", {"size": 0.4, "tp_dollars": 800.0,
                                    "sl_dollars": 150.0, "tp_pct": None,
                                    "sl_pct": None})


def assert_close(a, b, tol=1e-6, what="value"):
    assert abs(a - b) <= tol, f"{what}: expected {b!r}, got {a!r}"


def _synthetic(days=20, seed=1):
    return generate_synthetic("EURUSD", days=days, seed=seed)


def _fake(outcomes, start_ts_of):
    """Build a MonteCarloResult from raw outcomes, for interval maths."""
    res = MonteCarloResult(config=CFG, mc_config=MonteCarloConfig(),
                           strategy="test", symbol="EURUSD",
                           data_source="fixture")
    for k, o in enumerate(outcomes):
        res.attempts.append(Attempt(outcome=o, start_ts=start_ts_of(k),
                                    net_profit=0.0, max_drawdown=0.0,
                                    total_costs=0.0, n_trades=1,
                                    bars_in_window=1440, bars_in_market=10))
    return res


# ---------------------------------------------------------------------------
# Windowing
# ---------------------------------------------------------------------------

def test_valid_start_range_leaves_a_full_window():
    bars = make_bars("X", [(1.0,) * 4] * 3000)          # 3,000 minutes
    top = valid_start_range(bars, CFG)
    assert bars.ts[top] + 24 * 3_600_000_000_000 <= bars.ts[-1]
    assert bars.ts[top + 1] + 24 * 3_600_000_000_000 > bars.ts[-1]


def test_independent_window_count_is_the_real_sample_size():
    bars = make_bars("X", [(1.0,) * 4] * (1440 * 30))   # 30 days
    assert independent_window_count(bars, CFG) == 29


def test_sample_starts_is_reproducible():
    bars = _synthetic()
    mc = MonteCarloConfig(n_attempts=200, seed=7)
    a, _ = sample_starts(bars, CFG, mc)
    b, _ = sample_starts(bars, CFG, mc)
    assert a == b


def test_sample_starts_rejects_windows_that_are_mostly_closed():
    """A Friday-evening start is calendar, not strategy -- it must be
    rejected and counted, not silently recorded as a timeout failure."""
    bars = _synthetic(days=30, seed=2)
    strict = MonteCarloConfig(n_attempts=300, seed=3, min_bars_in_window=1200)
    loose = MonteCarloConfig(n_attempts=300, seed=3, min_bars_in_window=1)
    _, rejected_strict = sample_starts(bars, CFG, strict)
    _, rejected_loose = sample_starts(bars, CFG, loose)
    assert rejected_strict > 0
    assert rejected_loose == 0


def test_too_short_a_dataset_is_an_error_not_a_silent_zero():
    bars = make_bars("X", [(1.0,) * 4] * 100)
    try:
        sample_starts(bars, CFG, MonteCarloConfig(n_attempts=10))
    except ValueError:
        pass
    else:
        raise AssertionError("a dataset shorter than the window must raise")


# ---------------------------------------------------------------------------
# Intervals
# ---------------------------------------------------------------------------

def test_z_for_matches_the_known_95_percent_value():
    assert_close(_z_for(0.95), 1.959964, 1e-5, "z(95%)")
    assert_close(_z_for(0.99), 2.575829, 1e-5, "z(99%)")


def test_wilson_interval_stays_inside_zero_and_one_at_zero_passes():
    """The normal approximation gives a negative lower bound here; Wilson
    does not, which is why it is used."""
    res = _fake([Outcome.FAIL_TIMEOUT] * 1000, lambda k: k * 10 ** 15)
    lo, hi = res.wilson_interval()
    assert lo < 1e-9, f"lower bound should sit at zero, got {lo}"
    assert 0.0 < hi < 0.01


def test_wilson_interval_brackets_the_point_estimate():
    outcomes = [Outcome.PASS] * 50 + [Outcome.FAIL_DRAWDOWN] * 950
    res = _fake(outcomes, lambda k: k * 10 ** 15)
    lo, hi = res.wilson_interval()
    assert lo < res.pass_rate < hi
    assert_close(res.pass_rate, 0.05, 1e-12, "pass rate")


def test_cluster_interval_is_wider_when_windows_overlap():
    """The whole point of the day-cluster bootstrap.

    500 attempts spread over 5 days, with every attempt on a given day
    agreeing, carry far less information than 500 independent coin flips.
    The binomial interval cannot see that; the cluster bootstrap can.
    """
    day = 86_400 * 10 ** 9
    outcomes = []
    for d in range(5):
        hit = d < 1                      # one day of passes, four of failures
        outcomes += [Outcome.PASS if hit else Outcome.FAIL_DRAWDOWN] * 100
    res = _fake(outcomes, lambda k: (k // 100) * day)
    res.mc_config = MonteCarloConfig(bootstrap_samples=1500)
    wl, wh = res.wilson_interval()
    cl, ch = res.cluster_interval()
    assert (ch - cl) > 3 * (wh - wl), \
        f"cluster {ch - cl:.3f} should dwarf Wilson {wh - wl:.3f}"


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------

def test_monte_carlo_is_reproducible():
    bars = _synthetic()
    mc = MonteCarloConfig(n_attempts=150, seed=42, bootstrap_samples=50)
    a = run_monte_carlo(bars, SPEC, INST, COSTS, CFG, mc)
    b = run_monte_carlo(bars, SPEC, INST, COSTS, CFG, mc)
    assert [x.outcome for x in a.attempts] == [x.outcome for x in b.attempts]
    assert a.pass_rate == b.pass_rate


def test_parallel_workers_give_identical_results():
    bars = _synthetic()
    base = MonteCarloConfig(n_attempts=150, seed=11, bootstrap_samples=50)
    one = run_monte_carlo(bars, SPEC, INST, COSTS, CFG, base)
    try:
        many = run_monte_carlo(bars, SPEC, INST, COSTS, CFG,
                               MonteCarloConfig(n_attempts=150, seed=11,
                                                bootstrap_samples=50,
                                                n_jobs=3))
    except (OSError, NotImplementedError, ImportError):
        return                    # no process pool in this sandbox
    assert [x.outcome for x in one.attempts] == \
           [x.outcome for x in many.attempts]


def test_outcomes_partition_the_attempts():
    bars = _synthetic()
    res = run_monte_carlo(bars, SPEC, INST, COSTS, CFG,
                          MonteCarloConfig(n_attempts=200, seed=9,
                                           bootstrap_samples=50))
    assert res.n_pass + res.n_fail_drawdown + res.n_fail_timeout == res.n
    assert res.n == 200


def test_expected_value_and_breakeven_arithmetic():
    res = _fake([Outcome.PASS] * 100 + [Outcome.FAIL_DRAWDOWN] * 900,
                lambda k: k * 10 ** 15)
    assert_close(res.breakeven_pass_rate, 0.10, 1e-12, "500/5000")
    assert_close(res.pass_rate, 0.10, 1e-12, "pass rate")
    assert_close(res.ev_per_attempt, 0.0, 1e-9,
                 "EV is zero exactly at breakeven")
    better = _fake([Outcome.PASS] * 200 + [Outcome.FAIL_DRAWDOWN] * 800,
                   lambda k: k * 10 ** 15)
    assert_close(better.ev_per_attempt, 500.0, 1e-9, "20% -> +$500")


def test_report_names_the_verdict_against_breakeven():
    res = _fake([Outcome.FAIL_DRAWDOWN] * 500, lambda k: k * 10 ** 15)
    res.mc_config = MonteCarloConfig(bootstrap_samples=100)
    text = res.report()
    assert "breakeven" in text
    assert "below breakeven" in text
    assert "FAIL_DRAWDOWN" in text


def test_zero_cost_control_beats_the_costed_run():
    """Costs must move the answer -- if they do not, they are not applied."""
    bars = _synthetic(days=30, seed=6)
    mc = MonteCarloConfig(n_attempts=400, seed=21, bootstrap_samples=50)
    costed = run_monte_carlo(bars, SPEC, INST, COSTS, CFG, mc)
    free = run_monte_carlo(bars, SPEC, INST, ZERO_COSTS, CFG, mc)
    assert free.pass_rate >= costed.pass_rate
    assert free.summary()["mean_costs"] == 0.0
    assert costed.summary()["mean_costs"] > 0.0


def test_static_drawdown_passes_more_often_than_trailing():
    """A sanity check on the rulebook axis: the looser rule cannot be
    harder to survive."""
    bars = _synthetic(days=30, seed=8)
    mc = MonteCarloConfig(n_attempts=400, seed=31, bootstrap_samples=50)
    static = run_monte_carlo(
        bars, SPEC, INST, COSTS,
        ChallengeConfig(drawdown_mode=DrawdownMode.STATIC), mc)
    trailing = run_monte_carlo(
        bars, SPEC, INST, COSTS,
        ChallengeConfig(drawdown_mode=DrawdownMode.TRAILING_EQUITY), mc)
    assert static.pass_rate >= trailing.pass_rate
    assert static.n_fail_drawdown <= trailing.n_fail_drawdown


def test_engine_reproduces_gamblers_ruin():
    """End-to-end validation against a closed-form answer.

    For a driftless price and a *static* floor, holding a position until one
    barrier is touched is the gambler's ruin problem: the probability of
    reaching +T before -D is D/(T+D), independent of position size and
    volatility.  Drive the barriers close enough that the 24-hour clock never
    binds, remove costs, randomise the intrabar order so neither barrier gets
    a systematic head start, and the simulator should land on that number.

    Nothing else in this suite tests the engine, the sampler and the
    aggregation together against an outside truth.
    """
    from propsim.engine import IntrabarOrder

    bars = generate_synthetic("EURUSD", days=90, seed=13)
    for target, drawdown in ((450.0, 150.0), (300.0, 300.0), (150.0, 450.0)):
        cfg = ChallengeConfig(profit_target=target, max_drawdown=drawdown,
                              drawdown_mode=DrawdownMode.STATIC,
                              intrabar_order=IntrabarOrder.RANDOM)
        res = run_monte_carlo(
            bars, StrategySpec("buy_and_hold", {"size": 0.6}), INST,
            ZERO_COSTS, cfg,
            MonteCarloConfig(n_attempts=1200, seed=77, bootstrap_samples=50))
        expected = drawdown / (target + drawdown)
        assert res.n_fail_timeout / res.n < 0.05, \
            "the clock should not bind at these barrier distances"
        assert abs(res.pass_rate - expected) < 0.04, (
            f"target ${target:.0f} / drawdown ${drawdown:.0f}: got "
            f"{res.pass_rate:.2%}, gambler's ruin says {expected:.2%}")
