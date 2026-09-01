"""
montecarlo.py -- pass rate, confidence, and expected value over many attempts.

Two statistical points drive the design.

**Overlapping windows are not independent samples.**  Ten thousand 24-hour
windows drawn from three months of data reuse the same few hundred days over
and over.  A binomial interval computed as if they were independent will be
several times too narrow, and it will be narrow in the flattering direction --
it makes a 6% pass rate look reliably distinguishable from 10% when it is not.
So two intervals are reported: the Wilson binomial one, and a cluster
bootstrap that resamples whole start-days.  The gap between them is the honest
measure of how much the dataset actually supports.

**Not every start time is a valid attempt.**  A window opening at 21:00 on a
Friday contains almost no tradable data.  Those draws are rejected and
recorded rather than silently counted as timeout failures, which would be an
artefact of the sampling rather than a fact about the challenge.
"""

from __future__ import annotations

import math
import os
import random
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .costs import CostModel
from .data import NS_PER_DAY, NS_PER_HOUR, BarSeries, Instrument
from .engine import ChallengeConfig, ChallengeResult, Outcome, run_challenge
from .strategies import StrategySpec

Z_95 = 1.959963984540054


# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MonteCarloConfig:
    n_attempts: int = 10_000
    seed: int = 12_345
    #: Reject a start whose 24h window contains fewer bars than this.  240
    #: 1-minute bars is four hours of trading -- below that the attempt is
    #: measuring the calendar, not the strategy.
    min_bars_in_window: int = 240
    #: Draws to attempt before giving up on finding valid starts.
    max_resample_factor: int = 20
    n_jobs: int = 1
    bootstrap_samples: int = 2_000
    keep_examples: int = 3


@dataclass
class Attempt:
    """Compact per-attempt record.  Full results are far too big to keep
    10,000 of, and everything downstream needs only these fields."""

    outcome: Outcome
    start_ts: int
    net_profit: float
    max_drawdown: float
    total_costs: float
    n_trades: int
    bars_in_window: int
    bars_in_market: int


@dataclass
class MonteCarloResult:
    config: ChallengeConfig
    mc_config: MonteCarloConfig
    strategy: str
    symbol: str
    data_source: str

    attempts: List[Attempt] = field(default_factory=list)
    rejected_starts: int = 0
    n_independent_windows: int = 0
    examples: List[ChallengeResult] = field(default_factory=list)

    # -- headline numbers ---------------------------------------------------

    @property
    def n(self) -> int:
        return len(self.attempts)

    @property
    def n_pass(self) -> int:
        return sum(1 for a in self.attempts if a.outcome is Outcome.PASS)

    @property
    def n_fail_drawdown(self) -> int:
        return sum(1 for a in self.attempts
                   if a.outcome is Outcome.FAIL_DRAWDOWN)

    @property
    def n_fail_timeout(self) -> int:
        return sum(1 for a in self.attempts
                   if a.outcome is Outcome.FAIL_TIMEOUT)

    @property
    def pass_rate(self) -> float:
        return self.n_pass / self.n if self.n else 0.0

    @property
    def breakeven_pass_rate(self) -> float:
        return self.config.breakeven_pass_rate

    @property
    def ev_per_attempt(self) -> float:
        return self.config.expected_value(self.pass_rate)

    def wilson_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """Wilson score interval -- behaves at small p where the normal
        approximation produces negative lower bounds."""
        n = self.n
        if not n:
            return (0.0, 0.0)
        z = Z_95 if abs(confidence - 0.95) < 1e-9 else _z_for(confidence)
        p = self.pass_rate
        denom = 1.0 + z * z / n
        centre = (p + z * z / (2 * n)) / denom
        half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
        return (max(0.0, centre - half), min(1.0, centre + half))

    def cluster_interval(self, confidence: float = 0.95,
                         samples: Optional[int] = None,
                         seed: int = 99) -> Tuple[float, float]:
        """Bootstrap over start-days rather than over attempts.

        Attempts whose windows overlap share most of their price path, so the
        effective sample size is closer to the number of distinct days in the
        data than to ``n_attempts``.  Resampling whole days with replacement
        propagates that.
        """
        if not self.attempts:
            return (0.0, 0.0)
        by_day: Dict[int, List[int]] = {}
        for a in self.attempts:
            by_day.setdefault(a.start_ts // NS_PER_DAY, []).append(
                1 if a.outcome is Outcome.PASS else 0)
        days = list(by_day.values())
        if len(days) < 2:
            return self.wilson_interval(confidence)

        rng = random.Random(seed)
        b = samples if samples is not None else self.mc_config.bootstrap_samples
        rates: List[float] = []
        k = len(days)
        for _ in range(b):
            hits = 0
            total = 0
            for _ in range(k):
                block = days[rng.randrange(k)]
                hits += sum(block)
                total += len(block)
            rates.append(hits / total if total else 0.0)
        rates.sort()
        alpha = (1.0 - confidence) / 2.0
        lo = rates[max(0, int(alpha * len(rates)) - 1)]
        hi = rates[min(len(rates) - 1, int((1 - alpha) * len(rates)))]
        return (lo, hi)

    # -- descriptive --------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        dd = [a.max_drawdown for a in self.attempts]
        costs = [a.total_costs for a in self.attempts]
        trades = [a.n_trades for a in self.attempts]
        wl, wh = self.wilson_interval()
        cl, ch = self.cluster_interval()
        return {
            "strategy": self.strategy,
            "symbol": self.symbol,
            "source": self.data_source,
            "n_attempts": self.n,
            "rejected_starts": self.rejected_starts,
            "independent_windows": self.n_independent_windows,
            "pass_rate": self.pass_rate,
            "wilson_95": (wl, wh),
            "cluster_95": (cl, ch),
            "breakeven": self.breakeven_pass_rate,
            "ev_per_attempt": self.ev_per_attempt,
            "ev_95": (self.config.expected_value(cl),
                      self.config.expected_value(ch)),
            "fail_drawdown": self.n_fail_drawdown / self.n if self.n else 0.0,
            "fail_timeout": self.n_fail_timeout / self.n if self.n else 0.0,
            "median_max_dd": statistics.median(dd) if dd else 0.0,
            "mean_costs": statistics.fmean(costs) if costs else 0.0,
            "mean_trades": statistics.fmean(trades) if trades else 0.0,
        }

    def report(self) -> str:
        s = self.summary()
        wl, wh = s["wilson_95"]
        cl, ch = s["cluster_95"]
        be = s["breakeven"]
        verdict = ("CLEARS breakeven" if cl > be else
                   "below breakeven" if ch < be else
                   "indistinguishable from breakeven")
        bar = _rate_bar(self.pass_rate, be)
        lines = [
            "=" * 72,
            f"  {self.strategy}",
            f"  {self.symbol}   data: {self.data_source}",
            "=" * 72,
            f"  attempts            {self.n:>10,}   "
            f"({self.rejected_starts:,} starts rejected)",
            f"  independent windows {self.n_independent_windows:>10,}   "
            f"<- the real sample size",
            "",
            f"  PASS                {self.n_pass:>10,}   "
            f"{self.pass_rate:>8.2%}",
            f"  FAIL_DRAWDOWN       {self.n_fail_drawdown:>10,}   "
            f"{s['fail_drawdown']:>8.2%}",
            f"  FAIL_TIMEOUT        {self.n_fail_timeout:>10,}   "
            f"{s['fail_timeout']:>8.2%}",
            "",
            f"  pass rate           {self.pass_rate:>8.2%}",
            f"    95% Wilson        [{wl:>7.2%}, {wh:>7.2%}]  "
            f"(assumes independent attempts)",
            f"    95% day-cluster   [{cl:>7.2%}, {ch:>7.2%}]  "
            f"(honest: accounts for overlap)",
            f"  breakeven           {be:>8.2%}   <- {verdict}",
            "",
            bar,
            "",
            f"  EV per ${self.config.entry_fee:,.0f} attempt   "
            f"${s['ev_per_attempt']:>9,.2f}   "
            f"[${s['ev_95'][0]:,.2f}, ${s['ev_95'][1]:,.2f}]",
            f"  median max drawdown ${s['median_max_dd']:>9,.2f} "
            f"(limit ${self.config.max_drawdown:,.0f})",
            f"  mean costs paid     ${s['mean_costs']:>9,.2f}",
            f"  mean trades         {s['mean_trades']:>10.1f}",
            "=" * 72,
        ]
        return "\n".join(lines)


def _z_for(confidence: float) -> float:
    """Inverse normal CDF via bisection -- avoids depending on scipy."""
    target = 0.5 + confidence / 2.0
    lo, hi = 0.0, 8.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        cdf = 0.5 * (1.0 + math.erf(mid / math.sqrt(2.0)))
        if cdf < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _rate_bar(rate: float, breakeven: float, width: int = 60) -> str:
    """One-line visual of the pass rate against the breakeven marker."""
    top = max(rate, breakeven) * 1.6 + 1e-9
    fill = int(round(width * min(1.0, rate / top)))
    mark = int(round(width * min(1.0, breakeven / top)))
    row = ["-"] * width
    for k in range(fill):
        row[k] = "#"
    if 0 <= mark < width:
        row[mark] = "|"
    return (f"  0%  [{''.join(row)}]\n"
            f"       {' ' * max(0, mark - 4)}^ breakeven {breakeven:.0%}")


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def valid_start_range(bars: BarSeries, config: ChallengeConfig) -> int:
    """Highest index whose 24h window is fully covered by the dataset."""
    horizon = int(round(config.duration_hours * NS_PER_HOUR))
    cutoff = bars.ts[-1] - horizon
    lo, hi = 0, len(bars) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if bars.ts[mid] <= cutoff:
            lo = mid
        else:
            hi = mid - 1
    return lo


def independent_window_count(bars: BarSeries,
                             config: ChallengeConfig) -> int:
    """How many disjoint 24h windows the dataset actually contains."""
    if len(bars) < 2:
        return 0
    span = bars.ts[-1] - bars.ts[0]
    horizon = int(round(config.duration_hours * NS_PER_HOUR))
    return max(0, int(span // horizon))


def _bars_in_window(bars: BarSeries, start: int, horizon: int) -> int:
    deadline = bars.ts[start] + horizon
    lo, hi = start, len(bars)
    while lo < hi:
        mid = (lo + hi) // 2
        if bars.ts[mid] < deadline:
            lo = mid + 1
        else:
            hi = mid
    return lo - start


def sample_starts(bars: BarSeries, config: ChallengeConfig,
                  mc: MonteCarloConfig) -> Tuple[List[int], int]:
    """Draw start indices uniformly, rejecting windows that are mostly closed."""
    rng = random.Random(mc.seed)
    horizon = int(round(config.duration_hours * NS_PER_HOUR))
    top = valid_start_range(bars, config)
    if top <= 0:
        raise ValueError(
            f"dataset spans {bars.span_days:.1f} days; not enough for a "
            f"{config.duration_hours:g}h window"
        )
    starts: List[int] = []
    rejected = 0
    budget = mc.n_attempts * mc.max_resample_factor
    while len(starts) < mc.n_attempts and budget > 0:
        budget -= 1
        i = rng.randint(0, top)
        if _bars_in_window(bars, i, horizon) < mc.min_bars_in_window:
            rejected += 1
            continue
        starts.append(i)
    if len(starts) < mc.n_attempts:
        raise ValueError(
            f"only found {len(starts)} valid starts out of "
            f"{mc.n_attempts} requested -- the dataset is too sparse "
            f"(min_bars_in_window={mc.min_bars_in_window})"
        )
    return starts, rejected


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------

_W: Dict[str, Any] = {}


def _init_worker(bars, spec, instrument, cost_model, config):
    _W["bars"] = bars
    _W["spec"] = spec
    _W["instrument"] = instrument
    _W["costs"] = cost_model
    _W["config"] = config
    _W["hs"] = cost_model.half_spread_series(bars)
    _W["strategy"] = spec.build()


def _run_indices(payload):
    seed, indices = payload
    out = []
    for k, start in indices:
        out.append(_compact(_run_single(seed, k, start)))
    return out


def _run_single(seed: int, k: int, start: int) -> ChallengeResult:
    return run_challenge(
        _W["bars"], _W["strategy"], _W["instrument"],
        cost_model=_W["costs"], config=_W["config"],
        rng=random.Random(seed * 1_000_003 + k),
        start_index=start, half_spread=_W["hs"],
        collect_equity_curve=False,
    )


def _compact(res: ChallengeResult) -> Attempt:
    return Attempt(
        outcome=res.outcome, start_ts=res.start_ts,
        net_profit=res.net_profit, max_drawdown=res.max_drawdown_reached,
        total_costs=res.total_costs, n_trades=len(res.trades),
        bars_in_window=res.bars_in_window, bars_in_market=res.bars_in_market,
    )


def run_monte_carlo(bars: BarSeries, spec: StrategySpec,
                    instrument: Instrument, cost_model: CostModel,
                    config: Optional[ChallengeConfig] = None,
                    mc: Optional[MonteCarloConfig] = None,
                    progress=None) -> MonteCarloResult:
    """Run ``mc.n_attempts`` challenge attempts from randomised start times."""
    config = config or ChallengeConfig()
    mc = mc or MonteCarloConfig()

    starts, rejected = sample_starts(bars, config, mc)
    result = MonteCarloResult(
        config=config, mc_config=mc, strategy=spec.describe(),
        symbol=bars.symbol, data_source=bars.source or "unknown",
        rejected_starts=rejected,
        n_independent_windows=independent_window_count(bars, config),
    )

    _init_worker(bars, spec, instrument, cost_model, config)

    if mc.n_jobs > 1:
        from concurrent.futures import ProcessPoolExecutor
        chunk = max(1, len(starts) // (mc.n_jobs * 4))
        payloads = [
            (mc.seed, list(enumerate(starts))[a:a + chunk])
            for a in range(0, len(starts), chunk)
        ]
        with ProcessPoolExecutor(
                max_workers=mc.n_jobs, initializer=_init_worker,
                initargs=(bars, spec, instrument, cost_model, config)) as pool:
            for k, part in enumerate(pool.map(_run_indices, payloads)):
                result.attempts.extend(part)
                if progress:
                    progress(len(result.attempts), len(starts))
    else:
        strategy = _W["strategy"]
        for k, start in enumerate(starts):
            res = _run_single(mc.seed, k, start)
            if len(result.examples) < mc.keep_examples and \
                    res.outcome is Outcome.FAIL_DRAWDOWN:
                res.config = config
                result.examples.append(res)
            result.attempts.append(_compact(res))
            if progress and (k + 1) % 1000 == 0:
                progress(k + 1, len(starts))

    return result
