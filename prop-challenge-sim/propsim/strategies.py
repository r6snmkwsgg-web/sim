"""
strategies.py -- pluggable trading logic.

Each strategy is a small class over :class:`~propsim.engine.Strategy`.  They
are constructed from ``(name, params)`` pairs via :func:`make_strategy` rather
than passed as objects, because the Monte Carlo and the sweep hand them to
worker processes and a spec is trivially picklable where a closure is not.

The three baselines are deliberately dumb.  None of them has an edge, and
that is the point: they establish what the *rules and the costs alone* do to a
$20,000 account in 24 hours, which is the number the entry fee has to be
judged against.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

from .engine import CLOSE, BarContext, Order, SizingMode, Strategy, _CloseSignal

Signal = Union[None, Order, _CloseSignal]


def _sizing(mode: Union[str, SizingMode]) -> SizingMode:
    return mode if isinstance(mode, SizingMode) else SizingMode(mode)


def _fmt_exit(pct: Optional[float], dollars: Optional[float]) -> str:
    if dollars is not None:
        return f"${dollars:g}"
    return f"{pct:.3%}" if pct is not None else "none"


# ---------------------------------------------------------------------------

class FixedTPSL(Strategy):
    """Enter at random times; exit at a fixed take-profit or stop-loss.

    The entry process is Poisson: on each bar, flat, enter with probability
    ``entries_per_day / bars_per_day``.  Direction is a coin flip by default,
    which makes this an explicit zero-edge control -- whatever pass rate it
    produces is what the challenge geometry pays for pure variance.
    """

    name = "fixed_tp_sl"

    def __init__(self, tp_pct: Optional[float] = 0.002,
                 sl_pct: Optional[float] = 0.001,
                 size: float = 0.5, sizing_mode: Union[str, SizingMode] =
                 SizingMode.MARGIN_PCT, entries_per_day: float = 12.0,
                 direction: str = "random", max_trades: int = 0,
                 tp_dollars: Optional[float] = None,
                 sl_dollars: Optional[float] = None) -> None:
        self.tp_pct = tp_pct
        self.sl_pct = sl_pct
        self.tp_dollars = tp_dollars
        self.sl_dollars = sl_dollars
        self.size = size
        self.sizing_mode = _sizing(sizing_mode)
        self.entries_per_day = entries_per_day
        self.direction = direction
        self.max_trades = max_trades
        self._p_entry = 0.0
        self._n = 0

    def on_start(self, ctx: BarContext) -> None:
        bars_per_day = 86_400.0 / (ctx.bars.step_ns / 1e9)
        self._p_entry = min(1.0, self.entries_per_day / max(1.0, bars_per_day))
        self._n = 0

    def on_bar(self, ctx: BarContext) -> Signal:
        if ctx.position is not None:
            return None
        if self.max_trades and self._n >= self.max_trades:
            return None
        if ctx.rng.random() >= self._p_entry:
            return None
        self._n += 1
        if self.direction == "long":
            d = 1
        elif self.direction == "short":
            d = -1
        else:
            d = 1 if ctx.rng.random() < 0.5 else -1
        return Order(direction=d, sizing_mode=self.sizing_mode, size=self.size,
                     take_profit_pct=self.tp_pct, stop_loss_pct=self.sl_pct,
                     take_profit_dollars=self.tp_dollars,
                     stop_loss_dollars=self.sl_dollars, tag="fixed")

    def describe(self) -> str:
        return (f"FixedTPSL(tp={_fmt_exit(self.tp_pct, self.tp_dollars)}, "
                f"sl={_fmt_exit(self.sl_pct, self.sl_dollars)}, "
                f"size={self.size:g} {self.sizing_mode.value}, "
                f"{self.entries_per_day:g}/day, {self.direction})")


class Momentum(Strategy):
    """Enter on a break of the prior ``lookback``-bar range.

    Long when the close exceeds the highest high of the preceding window,
    short on the mirror image.  A cooldown after each exit stops a chopping
    range from generating a burst of entries that pays the spread repeatedly
    for nothing -- which, given a $300 limit, is itself a way to fail.
    """

    name = "momentum"

    def __init__(self, lookback: int = 30, tp_pct: Optional[float] = 0.002,
                 sl_pct: Optional[float] = 0.001, size: float = 0.5,
                 sizing_mode: Union[str, SizingMode] = SizingMode.MARGIN_PCT,
                 cooldown_bars: int = 5, allow_short: bool = True,
                 max_trades: int = 0, tp_dollars: Optional[float] = None,
                 sl_dollars: Optional[float] = None) -> None:
        self.lookback = max(2, int(lookback))
        self.tp_pct = tp_pct
        self.sl_pct = sl_pct
        self.tp_dollars = tp_dollars
        self.sl_dollars = sl_dollars
        self.size = size
        self.sizing_mode = _sizing(sizing_mode)
        self.cooldown_bars = max(0, int(cooldown_bars))
        self.allow_short = allow_short
        self.max_trades = max_trades
        self._ready_at = 0
        self._n = 0
        self._seen_trades = 0

    def on_start(self, ctx: BarContext) -> None:
        self._ready_at = ctx.start_index + self.lookback
        self._n = 0
        self._seen_trades = 0

    def on_bar(self, ctx: BarContext) -> Signal:
        if ctx.n_trades > self._seen_trades:
            # A trade closed since we last looked -- possibly inside the very
            # next bar, without the position ever being visible here.  Counting
            # closed trades is the only reliable way to notice.
            self._seen_trades = ctx.n_trades
            self._ready_at = max(self._ready_at, ctx.i + self.cooldown_bars)
        if ctx.position is not None:
            return None
        i = ctx.i
        if i < self._ready_at or i < self.lookback:
            return None
        if self.max_trades and self._n >= self.max_trades:
            return None

        lo = i - self.lookback
        price = ctx.close[i]
        d = 0
        if price > max(ctx.high[lo:i]):
            d = 1
        elif self.allow_short and price < min(ctx.low[lo:i]):
            d = -1
        if d == 0:
            return None
        self._n += 1
        return Order(direction=d, sizing_mode=self.sizing_mode, size=self.size,
                     take_profit_pct=self.tp_pct, stop_loss_pct=self.sl_pct,
                     take_profit_dollars=self.tp_dollars,
                     stop_loss_dollars=self.sl_dollars, tag="breakout")

    def describe(self) -> str:
        return (f"Momentum(lookback={self.lookback}, "
                f"tp={_fmt_exit(self.tp_pct, self.tp_dollars)}, "
                f"sl={_fmt_exit(self.sl_pct, self.sl_dollars)}, "
                f"size={self.size:g} {self.sizing_mode.value}, "
                f"cooldown={self.cooldown_bars})")


class BuyAndHold(Strategy):
    """Open once on the first bar and sit there for the whole window.

    No stop.  Under a trailing drawdown this is close to the worst possible
    structure -- the floor ratchets up behind every favourable tick and never
    comes back down -- which makes it a useful lower bound.
    """

    name = "buy_and_hold"

    def __init__(self, direction: int = 1, size: float = 0.5,
                 sizing_mode: Union[str, SizingMode] = SizingMode.MARGIN_PCT,
                 take_profit_pct: Optional[float] = None,
                 stop_loss_pct: Optional[float] = None) -> None:
        self.direction = 1 if int(direction) >= 0 else -1
        self.size = size
        self.sizing_mode = _sizing(sizing_mode)
        self.take_profit_pct = take_profit_pct
        self.stop_loss_pct = stop_loss_pct
        self._done = False

    def on_start(self, ctx: BarContext) -> None:
        self._done = False

    def on_bar(self, ctx: BarContext) -> Signal:
        if self._done or ctx.position is not None:
            return None
        self._done = True
        return Order(direction=self.direction, sizing_mode=self.sizing_mode,
                     size=self.size, take_profit_pct=self.take_profit_pct,
                     stop_loss_pct=self.stop_loss_pct, tag="hold")

    def describe(self) -> str:
        side = "long" if self.direction > 0 else "short"
        return (f"BuyAndHold({side}, size={self.size:g} "
                f"{self.sizing_mode.value})")


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

STRATEGY_REGISTRY = {
    "fixed_tp_sl": FixedTPSL,
    "momentum": Momentum,
    "buy_and_hold": BuyAndHold,
}


def make_strategy(name: str, **params: Any) -> Strategy:
    if name not in STRATEGY_REGISTRY:
        raise KeyError(f"unknown strategy {name!r}; "
                       f"known: {sorted(STRATEGY_REGISTRY)}")
    return STRATEGY_REGISTRY[name](**params)


@dataclass(frozen=True)
class StrategySpec:
    """A picklable description of a strategy, for worker processes."""

    name: str
    params: Dict[str, Any] = field(default_factory=dict)

    def build(self) -> Strategy:
        return make_strategy(self.name, **self.params)

    def describe(self) -> str:
        return self.build().describe()

    def with_params(self, **overrides: Any) -> "StrategySpec":
        merged = dict(self.params)
        merged.update(overrides)
        return StrategySpec(self.name, merged)
