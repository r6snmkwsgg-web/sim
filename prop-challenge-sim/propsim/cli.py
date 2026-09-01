"""
cli.py -- command line entry points.

    python -m propsim demo                     end-to-end on synthetic data
    python -m propsim fetch  --symbol EURUSD   pull and cache tick history
    python -m propsim run    --symbol EURUSD   one attempt, with a trade log
    python -m propsim mc     --symbol EURUSD   Monte Carlo pass rate
    python -m propsim sweep  --symbol EURUSD   grid + heatmap
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from typing import Optional

from .costs import DEFAULT_COSTS, CostModel, get_costs
from .data import DEFAULT_CACHE, get_instrument, load_bars
from .engine import (
    ChallengeConfig,
    DrawdownMode,
    ExposureBasis,
    IntrabarOrder,
    Outcome,
    run_challenge,
)
from .montecarlo import MonteCarloConfig, run_monte_carlo
from .strategies import STRATEGY_REGISTRY, StrategySpec
from .sweep import auto_grid, run_sweep

SYNTHETIC_WARNING = """
  +------------------------------------------------------------------+
  |  SYNTHETIC DATA.  These numbers describe a simulated driftless    |
  |  market, not any real one.  Use them to verify the machinery and  |
  |  as a zero-edge null; do not quote them as a fact about EURUSD.   |
  +------------------------------------------------------------------+
"""


def _progress(label: str):
    """Live progress on a terminal; sparse lines when redirected to a file.

    A carriage-return spinner written into a pipe produces one enormous line,
    which is worse than no progress at all."""
    start = time.time()
    tty = sys.stderr.isatty()
    state = {"last": 0.0}

    def report(done: int, total: int) -> None:
        frac = done / total if total else 1.0
        el = time.time() - start
        eta = el / frac - el if frac > 0 else 0.0
        if tty:
            sys.stderr.write(f"\r  {label}: {done:,}/{total:,} ({frac:6.1%}) "
                             f"eta {eta:5.0f}s")
            sys.stderr.flush()
            if done >= total:
                sys.stderr.write("\n")
        elif el - state["last"] > 15.0 or done >= total:
            state["last"] = el
            sys.stderr.write(f"  {label}: {done:,}/{total:,} ({frac:.0%}) "
                             f"eta {eta:.0f}s\n")
            sys.stderr.flush()
    return report


def _config_from_args(a) -> ChallengeConfig:
    return ChallengeConfig(
        starting_balance=a.balance, profit_target=a.target,
        max_drawdown=a.max_dd, duration_hours=a.hours,
        max_symbol_exposure_pct=a.max_exposure,
        entry_fee=a.fee, payout=a.payout,
        drawdown_mode=DrawdownMode(a.dd_mode),
        intrabar_order=IntrabarOrder(a.intrabar),
        exposure_basis=ExposureBasis(a.exposure_basis),
    )


def _costs_from_args(a, symbol: str) -> CostModel:
    base = (get_costs(symbol) if symbol.upper() in DEFAULT_COSTS
            else CostModel(spread=0.0001))
    return CostModel(
        spread=base.spread if a.spread is None else a.spread,
        commission_per_side=(base.commission_per_side if a.commission is None
                             else a.commission / 2.0),
        slippage=a.slippage,
        session_widening=base.session_widening,
        use_measured_spread=not a.ignore_measured_spread,
        spread_multiplier=a.spread_multiplier,
    )


def _load(a):
    bars = load_bars(a.symbol, source=a.source, start=a.start, end=a.end,
                     timeframe_seconds=a.timeframe, cache_dir=a.cache,
                     seed=a.data_seed, jobs=a.jobs,
                     progress=_progress("downloading"))
    if a.source == "synthetic":
        print(SYNTHETIC_WARNING)
    print(f"  {bars.describe()}")
    return bars


def _spec_from_args(a) -> StrategySpec:
    params = {}
    for kv in a.param or []:
        k, _, v = kv.partition("=")
        if v.lower() in ("none", "null"):
            params[k] = None
        elif v.lower() in ("true", "false"):
            params[k] = v.lower() == "true"
        else:
            try:
                params[k] = int(v) if v.isdigit() or (
                    v.startswith("-") and v[1:].isdigit()) else float(v)
            except ValueError:
                params[k] = v
    return StrategySpec(a.strategy, params)


# ---------------------------------------------------------------------------

def cmd_fetch(a) -> int:
    bars = _load(a)
    print(f"  cached under {os.path.join(a.cache, 'bars')}")
    if bars.spread:
        import statistics
        print(f"  measured mean spread: {statistics.fmean(bars.spread):.6f} "
              f"price units")
    return 0


def cmd_run(a) -> int:
    bars = _load(a)
    inst = get_instrument(a.symbol)
    res = run_challenge(bars, _spec_from_args(a).build(), inst,
                        cost_model=_costs_from_args(a, a.symbol),
                        config=_config_from_args(a),
                        start_index=a.start_index)
    print(f"\n  outcome            {res.outcome.value}")
    print(f"  final balance      ${res.final_balance:,.2f}")
    print(f"  peak / min equity  ${res.peak_equity:,.2f} / "
          f"${res.min_equity:,.2f}")
    print(f"  max drawdown       ${res.max_drawdown_reached:,.2f}")
    print(f"  costs paid         ${res.total_costs:,.2f} "
          f"(spread ${res.spread_paid:,.2f} + "
          f"commission ${res.commission_paid:,.2f})")
    print(f"  bars in window     {res.bars_in_window:,}"
          f"   in market {res.bars_in_market:,}")
    if res.trades:
        print(f"\n  {'#':>3} {'side':>5} {'size':>8} {'entry':>11} "
              f"{'exit':>11} {'net':>10}  reason")
        for k, t in enumerate(res.trades[:a.max_trades_shown], 1):
            print(f"  {k:>3} {'long' if t.direction > 0 else 'short':>5} "
                  f"{t.size:>8.3f} {t.entry_mid:>11.5f} {t.exit_mid:>11.5f} "
                  f"{t.net_pnl:>10,.2f}  {t.exit_reason.value}")
        if len(res.trades) > a.max_trades_shown:
            print(f"      ... {len(res.trades) - a.max_trades_shown} more")
    return 0


def cmd_mc(a) -> int:
    bars = _load(a)
    res = run_monte_carlo(
        bars, _spec_from_args(a), get_instrument(a.symbol),
        _costs_from_args(a, a.symbol), _config_from_args(a),
        MonteCarloConfig(n_attempts=a.attempts, seed=a.seed, n_jobs=a.workers,
                         min_bars_in_window=a.min_bars),
        progress=_progress("simulating"))
    print()
    print(res.report())
    if a.csv:
        import csv
        with open(a.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["start_ts", "outcome", "net_profit", "max_drawdown",
                        "total_costs", "n_trades"])
            for at in res.attempts:
                w.writerow([at.start_ts, at.outcome.value, at.net_profit,
                            at.max_drawdown, at.total_costs, at.n_trades])
        print(f"  attempts written to {a.csv}")
    return 0


def cmd_sweep(a) -> int:
    bars = _load(a)
    inst = get_instrument(a.symbol)
    cfg = _config_from_args(a)
    grid = auto_grid(bars, inst, cfg, axis=a.axis)
    print(f"  grid: {len(grid.tp_values)} tp x {len(grid.sl_values)} sl x "
          f"{len(grid.size_values)} size = {len(grid):,} cells "
          f"x {a.attempts:,} attempts")
    res = run_sweep(bars, _spec_from_args(a), inst,
                    _costs_from_args(a, a.symbol), cfg, grid,
                    attempts_per_cell=a.attempts, holdout_frac=a.holdout,
                    validate_top=a.validate_top,
                    validation_attempts=a.validation_attempts,
                    seed=a.seed, progress=_progress("cells"))
    print()
    print(res.report())
    out = a.out or os.path.join("out", f"{a.symbol}_{a.strategy}_heatmap.svg")
    written = res.heatmap(out)
    res.to_csv(os.path.splitext(written)[0] + ".csv")
    print(f"\n  heatmap -> {written}")
    print(f"  cells   -> {os.path.splitext(written)[0]}.csv")
    return 0


def cmd_demo(a) -> int:
    a.source = "synthetic"
    bars = _load(a)
    inst = get_instrument(a.symbol)
    costs = _costs_from_args(a, a.symbol)
    cfg = _config_from_args(a)
    print(f"  costs: {costs.describe(inst.point_value)}")
    for name, params in (
            ("buy_and_hold", {"size": 0.45}),
            ("fixed_tp_sl", {"size": 0.45, "tp_dollars": 900.0,
                             "sl_dollars": 150.0, "tp_pct": None,
                             "sl_pct": None, "entries_per_day": 8}),
            ("momentum", {"size": 0.45, "tp_dollars": 900.0,
                          "sl_dollars": 150.0, "tp_pct": None,
                          "sl_pct": None, "lookback": 30})):
        res = run_monte_carlo(bars, StrategySpec(name, params), inst, costs,
                              cfg, MonteCarloConfig(n_attempts=a.attempts,
                                                    seed=a.seed))
        print()
        print(res.report())
    return 0


# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="propsim",
        description="Monte Carlo simulator for prop-firm 24-hour challenges")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, attempts_default=10_000):
        sp.add_argument("--symbol", default="EURUSD")
        sp.add_argument("--source", default="dukascopy",
                        help="dukascopy | synthetic | path/to.csv")
        sp.add_argument("--start", default="2024-01-01")
        sp.add_argument("--end", default="2024-04-01")
        sp.add_argument("--timeframe", type=int, default=60,
                        help="bar length in seconds")
        sp.add_argument("--cache", default=DEFAULT_CACHE)
        sp.add_argument("--data-seed", type=int, default=0)
        sp.add_argument("--jobs", type=int, default=8,
                        help="parallel downloads")
        # challenge rules
        sp.add_argument("--balance", type=float, default=20_000.0)
        sp.add_argument("--target", type=float, default=1_500.0)
        sp.add_argument("--max-dd", type=float, default=300.0)
        sp.add_argument("--hours", type=float, default=24.0)
        sp.add_argument("--max-exposure", type=float, default=0.75)
        sp.add_argument("--fee", type=float, default=500.0)
        sp.add_argument("--payout", type=float, default=5_000.0)
        sp.add_argument("--dd-mode", default="trailing_equity",
                        choices=[m.value for m in DrawdownMode])
        sp.add_argument("--intrabar", default="adverse_first",
                        choices=[m.value for m in IntrabarOrder])
        sp.add_argument("--exposure-basis", default="margin",
                        choices=[m.value for m in ExposureBasis])
        # costs
        sp.add_argument("--spread", type=float, default=None,
                        help="override round-turn spread, price units")
        sp.add_argument("--commission", type=float, default=None,
                        help="round-turn commission per unit")
        sp.add_argument("--slippage", type=float, default=0.0)
        sp.add_argument("--spread-multiplier", type=float, default=1.0)
        sp.add_argument("--ignore-measured-spread", action="store_true")
        # strategy
        sp.add_argument("--strategy", default="fixed_tp_sl",
                        choices=sorted(STRATEGY_REGISTRY))
        sp.add_argument("--param", action="append",
                        help="strategy parameter, e.g. --param tp_pct=0.002")
        sp.add_argument("--seed", type=int, default=12_345)
        sp.add_argument("--attempts", type=int, default=attempts_default)

    sp = sub.add_parser("fetch", help="download and cache price data")
    common(sp)
    sp.set_defaults(func=cmd_fetch)

    sp = sub.add_parser("run", help="run a single attempt")
    common(sp)
    sp.add_argument("--start-index", type=int, default=0)
    sp.add_argument("--max-trades-shown", type=int, default=25)
    sp.set_defaults(func=cmd_run)

    sp = sub.add_parser("mc", help="Monte Carlo pass rate")
    common(sp)
    sp.add_argument("--workers", type=int, default=1)
    sp.add_argument("--min-bars", type=int, default=240)
    sp.add_argument("--csv", default=None)
    sp.set_defaults(func=cmd_mc)

    sp = sub.add_parser("sweep", help="parameter sweep + heatmap")
    common(sp, attempts_default=1_000)
    sp.add_argument("--axis", default="pct", choices=("pct", "dollars"))
    sp.add_argument("--holdout", type=float, default=0.3)
    sp.add_argument("--validate-top", type=int, default=12)
    sp.add_argument("--validation-attempts", type=int, default=4_000)
    sp.add_argument("--out", default=None, help=".svg or .png")
    sp.set_defaults(func=cmd_sweep)

    sp = sub.add_parser("demo", help="end-to-end on synthetic data")
    common(sp, attempts_default=2_000)
    sp.set_defaults(func=cmd_demo)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
