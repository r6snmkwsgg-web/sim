"""
engine.py -- one 24-hour prop-firm challenge attempt.

The single idea this file exists to get right
---------------------------------------------
The drawdown limit is checked **continuously against equity including open
position P&L**, not against closed P&L at bar close.  A trade that ends green
but goes $300+ underwater on the way is a FAIL.  Evaluating only at bar close
inflates the pass rate, and it inflates it most for exactly the high-variance
configurations a parameter sweep is drawn to -- so a close-only simulator does
not merely lose precision, it recommends the wrong strategy.

We only have OHLC bars, so within a bar we know the extremes but not their
order.  Three things follow:

1.  Each bar is walked as a sequence of *marks*: the adverse extreme, the
    favourable extreme, and the close.  Equity is recomputed and the floor and
    target tested at every one.
2.  The order of the first two is a modelling assumption, exposed as
    ``intrabar_order`` and defaulting to ``ADVERSE_FIRST`` -- the conservative
    reading, and the one that resolves the "stop and target both inside this
    bar" ambiguity in favour of the stop.
3.  A resting stop truncates the adverse excursion: once price reaches the
    stop the position is gone, so equity is marked to ``max(low, stop)`` for a
    long, not to the bar low.  Ignoring this would manufacture drawdown
    breaches that could not happen.

Equity is *net liquidation value*: balance, plus the open position marked at
the price it could actually be closed at (mid minus the half-spread), minus the
commission still owed to close it.  Defining it that way means equity is the
same quantity that governs both the floor and the target, and closing a
position at the price of a mark leaves the balance exactly equal to the equity
computed at that mark.  There is no seam.
"""

from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Union

from .costs import ZERO_COSTS, CostModel
from .data import NS_PER_HOUR, BarSeries, Instrument

#: Dollar tolerance for float comparisons against the floor and the target.
EPS = 1e-9


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Outcome(str, Enum):
    PASS = "PASS"
    FAIL_DRAWDOWN = "FAIL_DRAWDOWN"
    FAIL_TIMEOUT = "FAIL_TIMEOUT"


class ExitReason(str, Enum):
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    PROFIT_TARGET = "profit_target"      # challenge target hit while in trade
    DRAWDOWN_BREACH = "drawdown_breach"  # challenge floor hit while in trade
    STRATEGY_CLOSE = "strategy_close"
    TIMEOUT = "timeout"
    END_OF_DATA = "end_of_data"


class DrawdownMode(str, Enum):
    #: Floor fixed at ``starting_balance - max_drawdown`` for the whole attempt.
    STATIC = "static"
    #: Floor trails the high-water mark of *equity*, updated intrabar.  This is
    #: what most one-day challenge products actually enforce, and it is
    #: strictly harsher than STATIC.
    TRAILING_EQUITY = "trailing_equity"
    #: Floor trails the high-water mark of *closed balance* only.
    TRAILING_BALANCE = "trailing_balance"


class IntrabarOrder(str, Enum):
    ADVERSE_FIRST = "adverse_first"
    FAVORABLE_FIRST = "favorable_first"
    RANDOM = "random"


class ExposureBasis(str, Enum):
    #: "75% of the account" means 75% of equity in *notional* value.
    NOTIONAL = "notional"
    #: "75% of the account" means 75% of equity committed as *margin*.
    MARGIN = "margin"


class SizingMode(str, Enum):
    #: ``size`` is a number of lots / contracts.
    UNITS = "units"
    #: ``size`` is a dollar notional; units are derived from price.
    NOTIONAL = "notional"
    #: ``size`` is a fraction of current equity, as notional.
    ACCOUNT_PCT = "account_pct"
    #: ``size`` is a fraction of current equity committed as *margin*.  With a
    #: margin-based exposure cap this is the natural knob: ``size=0.75``
    #: saturates a 75% cap exactly, so the sweep axis runs 0 -> the limit.
    MARGIN_PCT = "margin_pct"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ChallengeConfig:
    """The rules of the challenge being simulated.

    Defaults are the brief: $20,000 account, +$1,500 target, $300 max
    drawdown, 24 hours, 75% single-symbol cap, $500 in, $5,000 out.
    """

    starting_balance: float = 20_000.0
    profit_target: float = 1_500.0
    max_drawdown: float = 300.0
    duration_hours: float = 24.0
    max_symbol_exposure_pct: float = 0.75
    entry_fee: float = 500.0
    payout: float = 5_000.0

    drawdown_mode: DrawdownMode = DrawdownMode.TRAILING_EQUITY
    intrabar_order: IntrabarOrder = IntrabarOrder.ADVERSE_FIRST
    exposure_basis: ExposureBasis = ExposureBasis.MARGIN
    #: If True the target is met the instant *equity* touches it, mid-trade.
    #: If False it must be met by realised balance after a position closes.
    target_on_equity: bool = True

    @property
    def target_equity(self) -> float:
        return self.starting_balance + self.profit_target

    @property
    def breakeven_pass_rate(self) -> float:
        """Pass rate at which the attempt is EV-neutral: fee / payout."""
        return self.entry_fee / self.payout

    def expected_value(self, pass_rate: float) -> float:
        """EV of one attempt at a given pass rate."""
        return pass_rate * self.payout - self.entry_fee


# ---------------------------------------------------------------------------
# Orders, positions, trades
# ---------------------------------------------------------------------------

class _CloseSignal:
    """Sentinel returned by a strategy to flatten at this bar's close."""

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "CLOSE"


CLOSE = _CloseSignal()


@dataclass
class Order:
    """A request to open a position at the current bar's close."""

    direction: int                       # +1 long, -1 short
    sizing_mode: SizingMode = SizingMode.ACCOUNT_PCT
    size: float = 0.5
    take_profit_pct: Optional[float] = None    # fraction of entry price
    stop_loss_pct: Optional[float] = None
    take_profit_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    #: Exits expressed as dollars of P&L instead of a price percentage.  Far
    #: more legible here, because they are directly comparable to the $300
    #: limit: a $450 stop simply cannot be reached: the account dies first.
    take_profit_dollars: Optional[float] = None
    stop_loss_dollars: Optional[float] = None
    #: Fill at this exact mid instead of the bar's close -- a resting limit
    #: order.  The engine rejects the order unless the level lies inside the
    #: signalling bar's range, so a limit that price never reached does not
    #: quietly become a market order at the close.
    fill_price: Optional[float] = None
    tag: str = ""

    def __post_init__(self) -> None:
        if self.direction not in (1, -1):
            raise ValueError("direction must be +1 or -1")
        if self.size <= 0:
            raise ValueError("size must be positive")


@dataclass
class Position:
    direction: int
    size: float
    entry_mid: float
    entry_fill: float
    entry_half_spread: float
    entry_ts: int
    entry_index: int
    take_profit: Optional[float] = None   # mid-price level
    stop_loss: Optional[float] = None     # mid-price level
    tag: str = ""
    #: Last mid at which equity was known to be inside the limits.  A breach
    #: is liquidated somewhere between here and the breaching mark.
    last_safe_mid: float = 0.0


@dataclass
class Trade:
    direction: int
    size: float
    entry_ts: int
    exit_ts: int
    entry_index: int
    exit_index: int
    entry_mid: float
    exit_mid: float
    entry_fill: float
    exit_fill: float
    gross_pnl: float          # mid-to-mid, before friction
    spread_cost: float
    commission: float
    net_pnl: float            # what actually hit the balance
    exit_reason: ExitReason
    tag: str = ""

    @property
    def bars_held(self) -> int:
        return self.exit_index - self.entry_index


# ---------------------------------------------------------------------------
# Strategy interface
# ---------------------------------------------------------------------------

class BarContext:
    """What a strategy can see at bar ``i``.

    Deliberately mutable and reused across bars: allocating one of these per
    bar would dominate the runtime of a 10,000-attempt Monte Carlo.

    A strategy must only read ``close[:i+1]`` and friends.  Reading past ``i``
    is lookahead; the engine cannot prevent it, but every shipped strategy is
    written against ``i`` and the tests assert entries fill at ``close[i]``.
    """

    __slots__ = (
        "bars", "instrument", "config", "rng", "i", "start_index",
        "ts", "open", "high", "low", "close", "volume",
        "balance", "equity", "position", "deadline_ns", "half_spread",
        "state", "n_trades",
    )

    def __init__(self, bars: BarSeries, instrument: Instrument,
                 config: ChallengeConfig, rng: random.Random,
                 start_index: int, deadline_ns: int,
                 half_spread: Sequence[float]) -> None:
        self.bars = bars
        self.instrument = instrument
        self.config = config
        self.rng = rng
        self.start_index = start_index
        self.deadline_ns = deadline_ns
        self.half_spread = half_spread
        self.ts = bars.ts
        self.open = bars.open
        self.high = bars.high
        self.low = bars.low
        self.close = bars.close
        self.volume = bars.volume
        self.i = start_index
        self.balance = config.starting_balance
        self.equity = config.starting_balance
        self.position: Optional[Position] = None
        #: Trades closed so far this attempt.  A strategy cannot see the trade
        #: log, but it does need to know that a position it opened has since
        #: been closed -- a take-profit inside the very next bar closes and
        #: reopens without the strategy ever observing an open position.
        self.n_trades = 0
        #: Free scratch space for strategies; cleared between attempts.
        self.state: Dict[str, Any] = {}

    # -- conveniences -------------------------------------------------------

    @property
    def price(self) -> float:
        """Current mid price (this bar's close) -- the price an order fills at."""
        return self.close[self.i]

    @property
    def bar_number(self) -> int:
        """Bars elapsed since the attempt started."""
        return self.i - self.start_index

    @property
    def bars_remaining_estimate(self) -> int:
        step = self.bars.step_ns
        return max(0, int((self.deadline_ns - self.ts[self.i]) // step))

    def window(self, lookback: int) -> slice:
        """Slice covering the ``lookback`` bars *before* the current one."""
        lo = max(self.start_index - 0, self.i - lookback)
        return slice(max(0, lo), self.i)


class Strategy(ABC):
    """Pluggable trading logic.

    ``on_bar`` is called once per bar, after the bar has been marked for
    drawdown, and may return ``None``, an :class:`Order`, or :data:`CLOSE`.
    Orders fill at that bar's close, so a strategy cannot see the outcome of
    its own entry.
    """

    name: str = "strategy"

    def on_start(self, ctx: BarContext) -> None:
        """Called once before the first bar.  Reset per-attempt state here."""

    @abstractmethod
    def on_bar(self, ctx: BarContext) -> Union[None, Order, _CloseSignal]:
        ...

    def describe(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class ChallengeResult:
    outcome: Outcome
    start_ts: int
    end_ts: int
    bars_in_window: int

    final_balance: float
    final_equity: float
    peak_equity: float
    min_equity: float
    #: Largest peak-to-trough equity excursion seen anywhere on the path,
    #: including intrabar marks.  Mode-independent diagnostic.
    max_drawdown_reached: float
    #: Largest shortfall below the starting balance (0.0 if never below).
    max_drawdown_from_start: float

    commission_paid: float
    spread_paid: float
    trades: List[Trade] = field(default_factory=list)
    equity_ts: List[int] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)

    breach_ts: Optional[int] = None
    breach_equity: Optional[float] = None
    #: True if the dataset ran out before the 24h clock did.  Such an attempt
    #: is not a valid sample and Monte Carlo discards it.
    truncated: bool = False
    orders_rejected: int = 0
    bars_in_market: int = 0
    config: Optional[ChallengeConfig] = None

    @property
    def total_costs(self) -> float:
        return self.commission_paid + self.spread_paid

    @property
    def passed(self) -> bool:
        return self.outcome is Outcome.PASS

    @property
    def net_profit(self) -> float:
        start = self.config.starting_balance if self.config else 20_000.0
        return self.final_balance - start

    @property
    def attempt_pnl(self) -> float:
        """Cash result of buying one attempt: payout if passed, minus the fee."""
        if not self.config:
            return 0.0
        return (self.config.payout if self.passed else 0.0) - self.config.entry_fee

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "start_ts": self.start_ts,
            "bars_in_window": self.bars_in_window,
            "final_balance": round(self.final_balance, 2),
            "net_profit": round(self.net_profit, 2),
            "peak_equity": round(self.peak_equity, 2),
            "min_equity": round(self.min_equity, 2),
            "max_drawdown_reached": round(self.max_drawdown_reached, 2),
            "total_costs": round(self.total_costs, 2),
            "n_trades": len(self.trades),
            "bars_in_market": self.bars_in_market,
            "truncated": self.truncated,
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return (
            f"<{self.outcome.value} bal={self.final_balance:,.2f} "
            f"maxDD={self.max_drawdown_reached:,.2f} "
            f"trades={len(self.trades)} costs={self.total_costs:,.2f}>"
        )


# ---------------------------------------------------------------------------
# The engine
# ---------------------------------------------------------------------------

def run_challenge(
    bars: BarSeries,
    strategy: Strategy,
    instrument: Instrument,
    cost_model: Optional[CostModel] = None,
    config: Optional[ChallengeConfig] = None,
    rng: Optional[random.Random] = None,
    start_index: int = 0,
    half_spread: Optional[Sequence[float]] = None,
    collect_equity_curve: bool = True,
) -> ChallengeResult:
    """Run one attempt starting at ``bars[start_index]`` and return the verdict.

    ``half_spread`` may be precomputed once by the caller and reused across
    thousands of attempts on the same series; it is derived from
    ``cost_model`` when omitted.
    """
    cfg = config if config is not None else ChallengeConfig()
    cm = cost_model if cost_model is not None else ZERO_COSTS
    rng = rng if rng is not None else random.Random()

    ts, op, hi, lo, cl = bars.ts, bars.open, bars.high, bars.low, bars.close
    n = len(ts)
    if not 0 <= start_index < n:
        raise IndexError(f"start_index {start_index} out of range for {n} bars")
    if half_spread is None:
        half_spread = cm.half_spread_series(bars)

    start_ts = ts[start_index]
    deadline = start_ts + int(round(cfg.duration_hours * NS_PER_HOUR))
    target_equity = cfg.target_equity
    pv = instrument.point_value
    comm_side = cm.commission_per_side
    max_dd_limit = cfg.max_drawdown

    trailing_eq = cfg.drawdown_mode is DrawdownMode.TRAILING_EQUITY
    trailing_bal = cfg.drawdown_mode is DrawdownMode.TRAILING_BALANCE
    order_mode = cfg.intrabar_order
    target_on_equity = cfg.target_on_equity
    margin_basis = cfg.exposure_basis is ExposureBasis.MARGIN

    balance = cfg.starting_balance
    equity = balance
    peak_equity = balance
    peak_balance = balance
    min_equity = balance
    max_dd = 0.0
    floor = balance - max_dd_limit

    pos: Optional[Position] = None
    trades: List[Trade] = []
    commission_paid = 0.0
    spread_paid = 0.0
    orders_rejected = 0
    bars_in_market = 0
    outcome: Optional[Outcome] = None
    breach_ts: Optional[int] = None
    breach_equity: Optional[float] = None
    equity_ts: List[int] = []
    equity_vals: List[float] = []

    ctx = BarContext(bars, instrument, cfg, rng, start_index, deadline,
                     half_spread)
    strategy.on_start(ctx)

    def _close_position(exit_mid: float, exit_ts: int, exit_index: int,
                        hs: float, reason: ExitReason) -> None:
        """Realise the open position at ``exit_mid``.

        Post-condition: ``balance`` equals the equity that was marked at this
        same mid.  The two accounting paths agree by construction.
        """
        nonlocal balance, commission_paid, spread_paid, pos, peak_balance, floor
        p = pos
        assert p is not None
        d = p.direction
        exit_fill = exit_mid - d * hs
        gross = d * (exit_mid - p.entry_mid) * pv * p.size
        spread_cost = (p.entry_half_spread + hs) * pv * p.size
        commission = 2.0 * comm_side * p.size
        net = d * (exit_fill - p.entry_fill) * pv * p.size - comm_side * p.size

        balance += net
        commission_paid += comm_side * p.size      # exit half
        spread_paid += spread_cost
        trades.append(Trade(
            direction=d, size=p.size, entry_ts=p.entry_ts, exit_ts=exit_ts,
            entry_index=p.entry_index, exit_index=exit_index,
            entry_mid=p.entry_mid, exit_mid=exit_mid,
            entry_fill=p.entry_fill, exit_fill=exit_fill,
            gross_pnl=gross, spread_cost=spread_cost, commission=commission,
            net_pnl=gross - spread_cost - commission,
            exit_reason=reason, tag=p.tag,
        ))
        pos = None
        if balance > peak_balance:
            peak_balance = balance
            if trailing_bal:
                floor = peak_balance - max_dd_limit

    i = start_index
    last_index = start_index
    bars_in_window = 0

    while i < n and ts[i] < deadline:
        last_index = i
        bars_in_window += 1
        hs = half_spread[i]

        # -- 1. Mark the open position through this bar --------------------
        if pos is not None:
            bars_in_market += 1
            d = pos.direction
            entry_fill = pos.entry_fill
            size = pos.size
            pending_exit_comm = comm_side * size
            unit = pv * size

            if d > 0:
                adverse_mid = lo[i]
                stop_hit = pos.stop_loss is not None and adverse_mid <= pos.stop_loss
                if stop_hit:
                    adverse_mid = pos.stop_loss
                favorable_mid = hi[i]
                tp_hit = pos.take_profit is not None and favorable_mid >= pos.take_profit
                if tp_hit:
                    favorable_mid = pos.take_profit
            else:
                adverse_mid = hi[i]
                stop_hit = pos.stop_loss is not None and adverse_mid >= pos.stop_loss
                if stop_hit:
                    adverse_mid = pos.stop_loss
                favorable_mid = lo[i]
                tp_hit = pos.take_profit is not None and favorable_mid <= pos.take_profit
                if tp_hit:
                    favorable_mid = pos.take_profit

            if order_mode is IntrabarOrder.ADVERSE_FIRST:
                adverse_first = True
            elif order_mode is IntrabarOrder.FAVORABLE_FIRST:
                adverse_first = False
            else:
                adverse_first = rng.random() < 0.5

            if adverse_first:
                marks = ((adverse_mid, stop_hit, ExitReason.STOP_LOSS),
                         (favorable_mid, tp_hit, ExitReason.TAKE_PROFIT),
                         (cl[i], False, ExitReason.TIMEOUT))
            else:
                marks = ((favorable_mid, tp_hit, ExitReason.TAKE_PROFIT),
                         (adverse_mid, stop_hit, ExitReason.STOP_LOSS),
                         (cl[i], False, ExitReason.TIMEOUT))

            for mid, hit, reason in marks:
                eq = balance + d * ((mid - d * hs) - entry_fill) * unit \
                    - pending_exit_comm

                if eq > peak_equity:
                    peak_equity = eq
                    if trailing_eq:
                        floor = peak_equity - max_dd_limit

                if eq <= floor + EPS:
                    # The firm liquidates the instant equity touches the
                    # limit, so the account dies *at* the floor, not at the
                    # bar extreme that price may only reach afterwards.
                    # ``breach_equity`` keeps the raw mark for diagnosis.
                    breach_equity = eq
                    exit_mid = _clamp_between(
                        _solve_mid_for_equity(floor, balance, d, entry_fill,
                                              hs, unit, pending_exit_comm),
                        mid, pos.last_safe_mid)
                    _close_position(exit_mid, ts[i], i, hs,
                                    ExitReason.DRAWDOWN_BREACH)
                    outcome = Outcome.FAIL_DRAWDOWN
                    breach_ts = ts[i]
                    equity = balance
                    if equity < min_equity:
                        min_equity = equity
                    dd = peak_equity - equity
                    if dd > max_dd:
                        max_dd = dd
                    break

                if eq < min_equity:
                    min_equity = eq
                dd = peak_equity - eq
                if dd > max_dd:
                    max_dd = dd

                if target_on_equity and eq >= target_equity - EPS:
                    exit_mid = _clamp_between(
                        _solve_mid_for_equity(target_equity, balance, d,
                                              entry_fill, hs, unit,
                                              pending_exit_comm),
                        pos.last_safe_mid, mid)
                    _close_position(exit_mid, ts[i], i, hs,
                                    ExitReason.PROFIT_TARGET)
                    outcome = Outcome.PASS
                    equity = balance
                    break

                pos.last_safe_mid = mid
                equity = eq

                if hit:
                    _close_position(mid, ts[i], i, hs, reason)
                    equity = balance
                    if not target_on_equity and balance >= target_equity - EPS:
                        outcome = Outcome.PASS
                    break

            if outcome is not None:
                if collect_equity_curve:
                    equity_ts.append(ts[i])
                    equity_vals.append(equity)
                break
        else:
            # Flat.  Every realising path above closes at a price that was
            # already marked and cleared, so this should be unreachable -- but
            # a trailing floor can in principle ratchet above a realised
            # balance, and an account that is already dead must not be allowed
            # to keep trading.
            equity = balance
            if equity <= floor + EPS:
                outcome = Outcome.FAIL_DRAWDOWN
                breach_ts = ts[i]
                breach_equity = equity
                if collect_equity_curve:
                    equity_ts.append(ts[i])
                    equity_vals.append(equity)
                break

        # -- 2. Strategy acts at this bar's close --------------------------
        ctx.i = i
        ctx.balance = balance
        ctx.equity = equity
        ctx.position = pos
        ctx.n_trades = len(trades)
        signal = strategy.on_bar(ctx)

        if signal is not None:
            if signal is CLOSE or isinstance(signal, _CloseSignal):
                if pos is not None:
                    _close_position(cl[i], ts[i], i, hs,
                                    ExitReason.STRATEGY_CLOSE)
                    equity = balance
                    if not target_on_equity and balance >= target_equity - EPS:
                        outcome = Outcome.PASS
            elif pos is not None:
                # A strategy must flatten before it can reverse.  Silently
                # ignoring the order keeps the position model unambiguous.
                orders_rejected += 1
            elif (signal.fill_price is not None
                  and not (lo[i] - EPS <= signal.fill_price <= hi[i] + EPS)):
                # A resting limit the bar never traded through.
                orders_rejected += 1
            else:
                mid = cl[i] if signal.fill_price is None else signal.fill_price
                size = _resolve_size(signal, instrument, mid, equity)
                size = _cap_exposure(size, instrument, mid, equity,
                                     cfg.max_symbol_exposure_pct, margin_basis)
                size = instrument.round_size(size)
                if size < instrument.min_size - 1e-12 or size <= 0.0:
                    orders_rejected += 1
                else:
                    d = signal.direction
                    entry_fill = mid + d * hs
                    tp, sl = _resolve_levels(signal, mid, d, size, pv)
                    balance -= comm_side * size
                    commission_paid += comm_side * size
                    pos = Position(
                        direction=d, size=size, entry_mid=mid,
                        entry_fill=entry_fill, entry_half_spread=hs,
                        entry_ts=ts[i], entry_index=i,
                        take_profit=tp, stop_loss=sl, tag=signal.tag,
                        last_safe_mid=mid,
                    )
                    # Mark immediately: the round-turn friction is already a
                    # real loss and can itself breach a tight floor.
                    eq = balance - (2.0 * hs) * pv * size - comm_side * size
                    equity = eq
                    if eq <= floor + EPS:
                        breach_equity = eq
                        _close_position(mid, ts[i], i, hs,
                                        ExitReason.DRAWDOWN_BREACH)
                        outcome = Outcome.FAIL_DRAWDOWN
                        breach_ts = ts[i]
                        equity = balance
                    if equity < min_equity:
                        min_equity = equity
                    dd = peak_equity - equity
                    if dd > max_dd:
                        max_dd = dd

        if collect_equity_curve:
            equity_ts.append(ts[i])
            equity_vals.append(equity)

        if outcome is not None:
            break
        i += 1

    truncated = outcome is None and i >= n and (n == 0 or ts[n - 1] < deadline)

    # -- 3. The clock ran out (or the data did) ----------------------------
    if outcome is None:
        if pos is not None:
            reason = ExitReason.END_OF_DATA if truncated else ExitReason.TIMEOUT
            _close_position(cl[last_index], ts[last_index], last_index,
                            half_spread[last_index], reason)
            equity = balance
            if collect_equity_curve and equity_vals:
                equity_vals[-1] = equity
        outcome = (Outcome.PASS if balance >= target_equity - EPS
                   else Outcome.FAIL_TIMEOUT)

    if equity < min_equity:
        min_equity = equity

    return ChallengeResult(
        outcome=outcome,
        start_ts=start_ts,
        end_ts=ts[last_index] if n else start_ts,
        bars_in_window=bars_in_window,
        final_balance=balance,
        final_equity=equity,
        peak_equity=peak_equity,
        min_equity=min_equity,
        max_drawdown_reached=max_dd,
        max_drawdown_from_start=max(0.0, cfg.starting_balance - min_equity),
        commission_paid=commission_paid,
        spread_paid=spread_paid,
        trades=trades,
        equity_ts=equity_ts,
        equity_curve=equity_vals,
        breach_ts=breach_ts,
        breach_equity=breach_equity,
        truncated=truncated,
        orders_rejected=orders_rejected,
        bars_in_market=bars_in_market,
        config=cfg,
    )


# ---------------------------------------------------------------------------
# Sizing helpers
# ---------------------------------------------------------------------------

def _resolve_size(order: Order, instrument: Instrument, price: float,
                  equity: float) -> float:
    """Translate an order's sizing request into units (lots / contracts)."""
    mode = order.sizing_mode
    if mode is SizingMode.UNITS:
        return order.size
    denom = price * instrument.point_value
    if denom <= 0:
        return 0.0
    if mode is SizingMode.NOTIONAL:
        return order.size / denom
    if mode is SizingMode.ACCOUNT_PCT:
        return max(0.0, equity) * order.size / denom
    if mode is SizingMode.MARGIN_PCT:
        budget = max(0.0, equity) * order.size
        if instrument.margin_per_unit is not None:
            return budget / instrument.margin_per_unit
        return budget * instrument.leverage / denom
    raise ValueError(f"unknown sizing mode {mode!r}")


def _cap_exposure(size: float, instrument: Instrument, price: float,
                  equity: float, max_pct: float, margin_basis: bool) -> float:
    """Clamp ``size`` to the single-symbol exposure cap.

    Scaling down rather than rejecting matches how a broker's risk engine
    behaves and keeps the cap from silently turning into "no trade at all".
    """
    if size <= 0 or equity <= 0:
        return 0.0
    cap = max_pct * equity
    used = (instrument.margin_required(size, price) if margin_basis
            else instrument.notional(size, price))
    if used <= cap or used <= 0:
        return size
    return size * (cap / used)


def _resolve_levels(order: Order, entry_mid: float, direction: int,
                    size: float = 0.0, point_value: float = 0.0):
    """Take-profit and stop-loss as absolute *mid-price* levels.

    Explicit prices win, then dollar distances, then percentages.  Percentages
    are applied to the entry mid, so a 0.1% stop on a long at 1.10000 rests at
    1.09890 regardless of instrument.
    """
    tp = order.take_profit_price
    sl = order.stop_loss_price
    unit = point_value * size
    if tp is None and order.take_profit_dollars is not None and unit > 0:
        tp = entry_mid + direction * (order.take_profit_dollars / unit)
    if sl is None and order.stop_loss_dollars is not None and unit > 0:
        sl = entry_mid - direction * (order.stop_loss_dollars / unit)
    if tp is None and order.take_profit_pct is not None:
        tp = entry_mid * (1.0 + direction * order.take_profit_pct)
    if sl is None and order.stop_loss_pct is not None:
        sl = entry_mid * (1.0 - direction * order.stop_loss_pct)
    return tp, sl


def _solve_mid_for_equity(target_eq: float, balance: float, direction: int,
                          entry_fill: float, half_spread: float,
                          unit: float, pending_commission: float) -> float:
    """Mid price at which open-position equity equals ``target_eq``.

    Equity is affine and strictly monotonic in the mid price, so the crossing
    is exact rather than searched for::

        eq(mid) = balance + d*((mid - d*hs) - entry_fill)*unit - pending

    Inverting gives the price at which the account first touches the floor or
    the target -- which is where a real risk engine would act, and it makes
    ``final_balance`` land exactly on the limit instead of somewhere past it.
    """
    if unit == 0.0:
        return entry_fill
    return (direction * half_spread + entry_fill
            + direction * (target_eq + pending_commission - balance) / unit)


def _clamp_between(x: float, a: float, b: float) -> float:
    """Clamp ``x`` into the closed interval spanned by ``a`` and ``b``."""
    lo, hi = (a, b) if a <= b else (b, a)
    return lo if x < lo else (hi if x > hi else x)
