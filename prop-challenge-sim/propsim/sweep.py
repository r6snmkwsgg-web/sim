"""
sweep.py -- grid search over take-profit, stop-loss and position size.

The question the sweep exists to answer is "does ANY corner of the parameter
space clear the 10% breakeven".  That question has a trap in it: search a
200-cell grid and the best cell's pass rate is biased upward simply because it
is the best of 200 noisy estimates.  At 1,000 attempts per cell the standard
error near 5% is about 0.7 points, so the winner routinely looks 1.5-2 points
better than it is -- which is the difference between "no corner clears 10%"
and a false positive.

So the sweep is run on an in-sample segment and every promising cell is then
re-run on a held-out segment it never saw.  The in-sample number tells you
where to look; the held-out number is the one to believe.
"""

from __future__ import annotations

import math
import os
import statistics
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from .costs import CostModel
from .data import BarSeries, Instrument
from .engine import ChallengeConfig
from .montecarlo import (
    MonteCarloConfig,
    MonteCarloResult,
    run_monte_carlo,
)
from .strategies import StrategySpec


# ---------------------------------------------------------------------------
# Grid definition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SweepGrid:
    tp_values: Tuple[float, ...]
    sl_values: Tuple[float, ...]
    size_values: Tuple[float, ...]
    #: "pct" -> take_profit_pct / stop_loss_pct; "dollars" -> dollar exits.
    axis: str = "pct"

    def __len__(self) -> int:
        return len(self.tp_values) * len(self.sl_values) * len(self.size_values)

    def cells(self):
        for size in self.size_values:
            for sl in self.sl_values:
                for tp in self.tp_values:
                    yield tp, sl, size


def auto_grid(bars: BarSeries, instrument: Instrument,
              config: Optional[ChallengeConfig] = None,
              sizes: Sequence[float] = (0.10, 0.20, 0.30, 0.45, 0.60, 0.75),
              axis: str = "pct") -> SweepGrid:
    """Build a grid scaled to the drawdown limit rather than to round numbers.

    A 0.1% stop means something completely different on EURUSD at 30:1 than on
    gold at 20:1.  What is comparable across instruments is *the move that
    costs you the $300 limit*, so the grid is laid out in multiples of that.
    A stop above 1.0x is one the account cannot survive to reach.
    """
    config = config or ChallengeConfig()
    ref_price = statistics.median(bars.close)
    ref_size = 0.45
    budget = ref_size * config.starting_balance
    if instrument.margin_per_unit is not None:
        units = budget / instrument.margin_per_unit
    else:
        units = budget * instrument.leverage / (ref_price *
                                                instrument.point_value)
    dollars_per_price = max(1e-12, units * instrument.point_value)
    limit_move = config.max_drawdown / dollars_per_price      # price units
    limit_pct = limit_move / ref_price

    if axis == "dollars":
        dd = config.max_drawdown
        return SweepGrid(
            tp_values=tuple(round(dd * m, 2)
                            for m in (0.5, 1.0, 2.0, 3.5, 5.0, 8.0)),
            sl_values=tuple(round(dd * m, 2)
                            for m in (0.15, 0.3, 0.5, 0.75, 1.0, 1.5)),
            size_values=tuple(sizes), axis="dollars")

    return SweepGrid(
        tp_values=tuple(limit_pct * m for m in (0.5, 1.0, 2.0, 3.5, 5.0, 8.0)),
        sl_values=tuple(limit_pct * m for m in (0.15, 0.3, 0.5, 0.75, 1.0, 1.5)),
        size_values=tuple(sizes), axis="pct")


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

@dataclass
class SweepCell:
    tp: float
    sl: float
    size: float
    pass_rate: float
    ci_low: float
    ci_high: float
    n: int
    fail_drawdown: float
    fail_timeout: float
    mean_trades: float
    mean_costs: float
    ev: float
    #: Filled in only for cells re-run on held-out data.
    validated_pass_rate: Optional[float] = None
    validated_ci: Optional[Tuple[float, float]] = None
    validated_n: int = 0

    @property
    def best_estimate(self) -> float:
        """The number to believe: held-out where we have it."""
        return (self.validated_pass_rate if self.validated_pass_rate is not None
                else self.pass_rate)


@dataclass
class SweepResult:
    cells: List[SweepCell]
    grid: SweepGrid
    config: ChallengeConfig
    strategy: str
    symbol: str
    data_source: str
    in_sample_days: float = 0.0
    holdout_days: float = 0.0

    @property
    def validated_cells(self) -> List[SweepCell]:
        return [c for c in self.cells if c.validated_pass_rate is not None]

    def top(self, k: int = 10, validated: bool = True) -> List[SweepCell]:
        """Best cells.

        Once validation has run, the leaderboard is drawn *from the validated
        cells only*.  Ranking a validated 2% against an unvalidated 3% would
        reinstate exactly the selection bias the hold-out exists to remove --
        the unvalidated cells are the ones that never had to prove anything.
        """
        pool = self.cells
        key = lambda c: c.pass_rate                                # noqa: E731
        if validated and self.validated_cells:
            pool = self.validated_cells
            key = lambda c: c.best_estimate                        # noqa: E731
        return sorted(pool, key=key, reverse=True)[:k]

    @property
    def breakeven(self) -> float:
        return self.config.breakeven_pass_rate

    def any_cell_clears_breakeven(self, validated: bool = True) -> bool:
        """Clearing means the *lower* bound is above breakeven, not the point
        estimate.  A point estimate above 10% with an interval straddling it
        is not a finding.

        A validated cell is judged on its held-out interval; an unvalidated
        one on its in-sample interval, which is the permissive direction, so a
        NO here is a genuine NO.
        """
        for c in self.cells:
            if validated and c.validated_pass_rate is not None:
                if c.validated_ci and c.validated_ci[0] > self.breakeven:
                    return True
            elif c.ci_low > self.breakeven:
                return True
        return False

    # -- output -------------------------------------------------------------

    def to_csv(self, path: str) -> None:
        import csv
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".",
                    exist_ok=True)
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["tp", "sl", "size", "pass_rate", "ci_low", "ci_high",
                        "n", "fail_drawdown", "fail_timeout", "mean_trades",
                        "mean_costs", "ev_per_attempt", "validated_pass_rate",
                        "validated_n"])
            for c in sorted(self.cells, key=lambda c: -c.best_estimate):
                w.writerow([c.tp, c.sl, c.size, c.pass_rate, c.ci_low,
                            c.ci_high, c.n, c.fail_drawdown, c.fail_timeout,
                            c.mean_trades, c.mean_costs, c.ev,
                            c.validated_pass_rate if c.validated_pass_rate
                            is not None else "", c.validated_n])

    def report(self, k: int = 12) -> str:
        be = self.breakeven
        unit = "%" if self.grid.axis == "pct" else "$"
        best = max(self.cells, key=lambda c: c.pass_rate)
        validated = self.validated_cells
        best_v = (max(validated, key=lambda c: c.validated_pass_rate)
                  if validated else None)
        lines = [
            "=" * 78,
            f"  PARAMETER SWEEP -- {self.strategy}",
            f"  {self.symbol}   data: {self.data_source}",
            f"  {len(self.cells):,} cells x {self.cells[0].n:,} attempts "
            f"= {sum(c.n for c in self.cells):,} simulated challenges",
            f"  in-sample {self.in_sample_days:.0f}d / held-out "
            f"{self.holdout_days:.0f}d",
            "=" * 78,
            "",
            f"  best in-sample pass rate   {best.pass_rate:>7.2%}  "
            f"(tp={_fmt(best.tp, unit)} sl={_fmt(best.sl, unit)} "
            f"size={best.size:.2f})",
        ]
        if best_v is not None:
            shrink = best.pass_rate - best_v.validated_pass_rate
            lines.append(
                f"  best held-out pass rate    "
                f"{best_v.validated_pass_rate:>7.2%}  "
                f"(tp={_fmt(best_v.tp, unit)} sl={_fmt(best_v.sl, unit)} "
                f"size={best_v.size:.2f})")
            lines.append(
                f"  selection bias             {shrink:>7.2%}  "
                f"(how much the in-sample winner shrank on unseen data)")
        lines += [
            f"  breakeven                  {be:>7.2%}",
            "",
            f"  ANY CORNER CLEARING BREAKEVEN?   "
            f"{'YES' if self.any_cell_clears_breakeven() else 'NO'}",
            "",
            ("  leaderboard: held-out re-runs of the top in-sample cells"
             if validated else "  leaderboard: in-sample only (no hold-out)"),
            f"  {'tp':>10} {'sl':>10} {'size':>6} {'in-samp':>9} "
            f"{'held-out':>9} {'95% CI':>18} {'DD fail':>8} {'EV':>10}",
            "  " + "-" * 74,
        ]
        for c in self.top(k):
            v = ("     n/a " if c.validated_pass_rate is None
                 else f"{c.validated_pass_rate:>8.2%} ")
            ci = (c.validated_ci if c.validated_ci else (c.ci_low, c.ci_high))
            lines.append(
                f"  {_fmt(c.tp, unit):>10} {_fmt(c.sl, unit):>10} "
                f"{c.size:>6.2f} {c.pass_rate:>8.2%} {v}"
                f"[{ci[0]:>6.2%},{ci[1]:>7.2%}] {c.fail_drawdown:>7.1%} "
                f"${c.ev:>8,.0f}")
        lines.append("=" * 78)
        return "\n".join(lines)

    # -- heatmap ------------------------------------------------------------

    def heatmap(self, path: str, title: Optional[str] = None) -> str:
        """Write a pass-rate heatmap.  PNG via matplotlib when it is
        installed, otherwise a self-contained SVG that needs nothing."""
        if path.endswith(".png"):
            try:
                return self._heatmap_matplotlib(path, title)
            except ImportError:
                path = path[:-4] + ".svg"
        return self._heatmap_svg(path, title)

    def _grid_values(self):
        lookup = {(c.tp, c.sl, c.size): c for c in self.cells}
        return lookup

    def _heatmap_matplotlib(self, path: str, title: Optional[str]) -> str:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import Normalize

        g = self.grid
        lookup = self._grid_values()
        vmax = max(max(c.pass_rate for c in self.cells), self.breakeven * 1.2)
        norm = Normalize(0.0, vmax)
        n = len(g.size_values)
        cols = min(3, n)
        rows = (n + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(5.2 * cols, 4.4 * rows),
                                 squeeze=False)
        unit = "%" if g.axis == "pct" else "$"
        for idx, size in enumerate(g.size_values):
            ax = axes[idx // cols][idx % cols]
            data = [[lookup[(tp, sl, size)].pass_rate for tp in g.tp_values]
                    for sl in g.sl_values]
            im = ax.imshow(data, cmap="viridis", norm=norm, origin="lower",
                           aspect="auto")
            ax.set_xticks(range(len(g.tp_values)))
            ax.set_xticklabels([_fmt(v, unit) for v in g.tp_values],
                               rotation=45, ha="right", fontsize=8)
            ax.set_yticks(range(len(g.sl_values)))
            ax.set_yticklabels([_fmt(v, unit) for v in g.sl_values],
                               fontsize=8)
            ax.set_xlabel("take profit")
            ax.set_ylabel("stop loss")
            ax.set_title(f"size {size:.0%} of margin cap", fontsize=10)
            for r, sl in enumerate(g.sl_values):
                for cc, tp in enumerate(g.tp_values):
                    val = lookup[(tp, sl, size)].pass_rate
                    ax.text(cc, r, f"{val:.1%}", ha="center", va="center",
                            fontsize=7,
                            color="white" if val < vmax * 0.6 else "black",
                            fontweight="bold" if val >= self.breakeven
                            else "normal")
        for idx in range(n, rows * cols):
            axes[idx // cols][idx % cols].axis("off")
        cb = fig.colorbar(im, ax=axes, shrink=0.8)
        cb.set_label(f"pass rate (breakeven {self.breakeven:.0%})")
        fig.suptitle(title or f"{self.symbol} -- {self.strategy}", fontsize=12)
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".",
                    exist_ok=True)
        fig.savefig(path, dpi=140, bbox_inches="tight")
        plt.close(fig)
        return path

    def _heatmap_svg(self, path: str, title: Optional[str]) -> str:
        g = self.grid
        lookup = self._grid_values()
        vmax = max(max(c.pass_rate for c in self.cells), self.breakeven * 1.2)
        unit = "%" if g.axis == "pct" else "$"

        cw, ch = 76, 40
        pad_l, pad_t, pad_b = 92, 46, 54
        panel_w = pad_l + cw * len(g.tp_values) + 20
        panel_h = pad_t + ch * len(g.sl_values) + pad_b
        cols = min(3, len(g.size_values))
        rows = (len(g.size_values) + cols - 1) // cols
        width = panel_w * cols + 130
        height = panel_h * rows + 74

        out = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" '
            f'font-family="ui-sans-serif,system-ui,Helvetica,Arial">',
            f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
            f'<text x="16" y="26" font-size="16" font-weight="600">'
            f'{_esc(title or f"{self.symbol} - {self.strategy}")}</text>',
            f'<text x="16" y="46" font-size="11" fill="#555">pass rate; '
            f'cells at or above the {self.breakeven:.0%} breakeven are '
            f'outlined in red</text>',
        ]
        for idx, size in enumerate(g.size_values):
            ox = (idx % cols) * panel_w + 16
            oy = (idx // cols) * panel_h + 60
            out.append(f'<text x="{ox + pad_l}" y="{oy + 16}" font-size="12" '
                       f'font-weight="600">size {size:.0%} of margin cap</text>')
            for r, sl in enumerate(g.sl_values):
                yy = oy + pad_t + (len(g.sl_values) - 1 - r) * ch
                out.append(
                    f'<text x="{ox + pad_l - 8}" y="{yy + ch / 2 + 4}" '
                    f'font-size="10" text-anchor="end" fill="#333">'
                    f'{_esc(_fmt(sl, unit))}</text>')
                for c, tp in enumerate(g.tp_values):
                    cell = lookup[(tp, sl, size)]
                    xx = ox + pad_l + c * cw
                    fill = _viridis(cell.pass_rate / vmax if vmax else 0.0)
                    hot = cell.pass_rate >= self.breakeven
                    stroke = "#d1132b" if hot else "#ffffff"
                    out.append(
                        f'<rect x="{xx}" y="{yy}" width="{cw - 2}" '
                        f'height="{ch - 2}" fill="{fill}" stroke="{stroke}" '
                        f'stroke-width="{2 if hot else 1}"/>')
                    lum = cell.pass_rate / vmax if vmax else 0.0
                    out.append(
                        f'<text x="{xx + (cw - 2) / 2}" y="{yy + ch / 2 + 4}" '
                        f'font-size="10" text-anchor="middle" '
                        f'fill="{"#111" if lum > 0.62 else "#fff"}">'
                        f'{cell.pass_rate:.1%}</text>')
            for c, tp in enumerate(g.tp_values):
                xx = ox + pad_l + c * cw + (cw - 2) / 2
                yb = oy + pad_t + len(g.sl_values) * ch + 16
                out.append(
                    f'<text x="{xx}" y="{yb}" font-size="10" '
                    f'text-anchor="end" fill="#333" '
                    f'transform="rotate(-40 {xx} {yb})">'
                    f'{_esc(_fmt(tp, unit))}</text>')
            out.append(
                f'<text x="{ox + pad_l + cw * len(g.tp_values) / 2}" '
                f'y="{oy + pad_t + len(g.sl_values) * ch + 44}" font-size="11" '
                f'text-anchor="middle" fill="#333">take profit</text>')
            out.append(
                f'<text x="{ox + 16}" y="{oy + pad_t + len(g.sl_values) * ch / 2}" '
                f'font-size="11" text-anchor="middle" fill="#333" '
                f'transform="rotate(-90 {ox + 16} '
                f'{oy + pad_t + len(g.sl_values) * ch / 2})">stop loss</text>')

        # colour bar
        bx = width - 96
        for k in range(120):
            t = 1.0 - k / 119.0
            out.append(f'<rect x="{bx}" y="{74 + k * 2}" width="16" '
                       f'height="2" fill="{_viridis(t)}"/>')
        out.append(f'<text x="{bx + 22}" y="{80}" font-size="10" '
                   f'fill="#333">{vmax:.0%}</text>')
        out.append(f'<text x="{bx + 22}" y="{318}" font-size="10" '
                   f'fill="#333">0%</text>')
        be_y = 74 + (1.0 - min(1.0, self.breakeven / vmax)) * 238
        out.append(f'<line x1="{bx - 6}" y1="{be_y}" x2="{bx + 18}" '
                   f'y2="{be_y}" stroke="#d1132b" stroke-width="2"/>')
        out.append(f'<text x="{bx + 22}" y="{be_y + 4}" font-size="10" '
                   f'fill="#d1132b">breakeven</text>')
        out.append("</svg>")

        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".",
                    exist_ok=True)
        with open(path, "w") as fh:
            fh.write("\n".join(out))
        return path


_VIRIDIS = ((68, 1, 84), (72, 40, 120), (62, 74, 137), (49, 104, 142),
            (38, 130, 142), (31, 158, 137), (53, 183, 121), (109, 205, 89),
            (180, 222, 44), (253, 231, 37))


def _viridis(t: float) -> str:
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    x = t * (len(_VIRIDIS) - 1)
    i = min(len(_VIRIDIS) - 2, int(x))
    f = x - i
    a, b = _VIRIDIS[i], _VIRIDIS[i + 1]
    return "#%02x%02x%02x" % tuple(int(round(a[k] + f * (b[k] - a[k])))
                                   for k in range(3))


def _fmt(v: float, unit: str) -> str:
    return f"{v:.3%}" if unit == "%" else f"${v:,.0f}"


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------------------
# Running the sweep
# ---------------------------------------------------------------------------

def _params_for(cell, grid: SweepGrid) -> Dict[str, Any]:
    tp, sl, size = cell
    if grid.axis == "dollars":
        return {"tp_pct": None, "sl_pct": None, "tp_dollars": tp,
                "sl_dollars": sl, "size": size}
    return {"tp_pct": tp, "sl_pct": sl, "tp_dollars": None,
            "sl_dollars": None, "size": size}


def run_sweep(bars: BarSeries, base_spec: StrategySpec,
              instrument: Instrument, cost_model: CostModel,
              config: Optional[ChallengeConfig] = None,
              grid: Optional[SweepGrid] = None,
              attempts_per_cell: int = 1_000,
              holdout_frac: float = 0.3,
              validate_top: int = 12,
              validation_attempts: int = 4_000,
              seed: int = 4_242,
              progress: Optional[Callable[[int, int], None]] = None
              ) -> SweepResult:
    """Grid-search the strategy, then re-test the leaders on unseen data."""
    config = config or ChallengeConfig()
    grid = grid or auto_grid(bars, instrument, config)

    split = int(len(bars) * (1.0 - holdout_frac))
    in_sample = bars.slice(0, split) if holdout_frac > 0 else bars
    holdout = bars.slice(split) if holdout_frac > 0 else None
    if holdout is not None and holdout.span_days < config.duration_hours / 24.0 * 3:
        holdout = None                      # too small to validate on

    cells: List[SweepCell] = []
    total = len(grid)
    for k, cell in enumerate(grid.cells()):
        spec = base_spec.with_params(**_params_for(cell, grid))
        mc = MonteCarloConfig(n_attempts=attempts_per_cell, seed=seed + k,
                              bootstrap_samples=400, keep_examples=0)
        res = run_monte_carlo(in_sample, spec, instrument, cost_model,
                              config, mc)
        s = res.summary()
        lo, hi = res.wilson_interval()
        tp, sl, size = cell
        cells.append(SweepCell(
            tp=tp, sl=sl, size=size, pass_rate=res.pass_rate,
            ci_low=lo, ci_high=hi, n=res.n,
            fail_drawdown=s["fail_drawdown"], fail_timeout=s["fail_timeout"],
            mean_trades=s["mean_trades"], mean_costs=s["mean_costs"],
            ev=res.ev_per_attempt))
        if progress:
            progress(k + 1, total)

    result = SweepResult(
        cells=cells, grid=grid, config=config,
        strategy=f"{base_spec.name} (tp/sl/size swept)", symbol=bars.symbol,
        data_source=bars.source or "unknown",
        in_sample_days=in_sample.span_days,
        holdout_days=holdout.span_days if holdout is not None else 0.0,
    )

    if holdout is not None and validate_top > 0:
        for c in result.top(validate_top, validated=False):
            spec = base_spec.with_params(
                **_params_for((c.tp, c.sl, c.size), grid))
            mc = MonteCarloConfig(n_attempts=validation_attempts,
                                  seed=seed + 900_001,
                                  bootstrap_samples=500, keep_examples=0)
            try:
                res = run_monte_carlo(holdout, spec, instrument, cost_model,
                                      config, mc)
            except ValueError:
                continue
            c.validated_pass_rate = res.pass_rate
            c.validated_ci = res.cluster_interval()
            c.validated_n = res.n

    return result
