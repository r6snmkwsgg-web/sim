"""
costs.py -- transaction costs.

Every price in a :class:`~propsim.data.BarSeries` is a **mid** price.  All
friction is applied here so that it is visible, configurable, and impossible to
forget:

* ``spread``  -- full round-turn spread in *price units*.  Half is paid on
  entry and half on exit, so a position marked to market immediately after
  opening is already down the full spread.
* ``commission_per_side`` -- dollars per unit (lot / contract) per side.  The
  brief specifies $5 round-turn, i.e. $2.50 a side, which is the default.
* ``slippage`` -- extra adverse price movement per side, in price units.  Zero
  by default; raise it to stress-test stop fills.
* ``session_widening`` -- multipliers on the spread by UTC hour, so the
  rollover/illiquid-hours blowout can be modelled instead of assumed away.

The engine consumes a *per-bar half-turn cost in price units* -- the quantity
``spread/2 * widening + slippage`` -- precomputed once per series so the hot
loop is a list index.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from .data import NS_PER_HOUR, BarSeries

NS_PER_DAY = 24 * NS_PER_HOUR


@dataclass(frozen=True)
class CostModel:
    """Spread + commission + slippage for one instrument."""

    #: Full round-turn spread, in price units (EURUSD 0.00008 == 0.8 pip).
    spread: float
    #: Dollars per unit per side.  $2.50 == $5.00 round turn.
    commission_per_side: float = 2.50
    #: Extra adverse price movement per side, in price units.
    slippage: float = 0.0
    #: ``(start_hour_utc, end_hour_utc, multiplier)`` triples, end exclusive.
    #: Ranges may wrap past midnight.
    session_widening: Tuple[Tuple[int, int, float], ...] = ()
    #: When the series carries a measured bid/ask spread, use it in preference
    #: to the configured constant.  Tick sources give the real thing; assuming
    #: a spread when the data knows it is a needless source of error.
    use_measured_spread: bool = True
    #: Multiplier applied on top of whichever spread is used.  Stress knob:
    #: 2.0 asks what happens if execution is twice as bad as assumed.
    spread_multiplier: float = 1.0

    @property
    def round_turn_commission(self) -> float:
        return 2.0 * self.commission_per_side

    def widening_at(self, ts_ns: int) -> float:
        if not self.session_widening:
            return 1.0
        hour = (ts_ns % NS_PER_DAY) // NS_PER_HOUR
        mult = 1.0
        for start, end, m in self.session_widening:
            inside = (start <= hour < end) if start < end else (hour >= start or hour < end)
            if inside:
                mult = max(mult, m)
        return mult

    def half_spread_at(self, ts_ns: int) -> float:
        """Half-turn cost in price units at a point in time."""
        return (0.5 * self.spread * self.widening_at(ts_ns)
                * self.spread_multiplier + self.slippage)

    def half_spread_series(self, bars: BarSeries) -> List[float]:
        """Precompute the per-bar half-turn cost for a whole series.

        Measured spreads already contain the session widening that the
        synthetic schedule only approximates, so the multiplier table is not
        applied on top of them.
        """
        if self.use_measured_spread and bars.spread:
            m, slip = 0.5 * self.spread_multiplier, self.slippage
            return [s * m + slip for s in bars.spread]
        if not self.session_widening:
            return [0.5 * self.spread * self.spread_multiplier
                    + self.slippage] * len(bars)
        return [self.half_spread_at(t) for t in bars.ts]

    # -- reporting ----------------------------------------------------------

    def round_turn_cost(self, size: float, point_value: float) -> float:
        """Dollar cost of opening and closing ``size`` units, ex-widening."""
        return (self.spread + 2.0 * self.slippage) * point_value * abs(size) \
            + self.round_turn_commission * abs(size)

    def describe(self, point_value: float, size: float = 1.0) -> str:
        return (
            f"spread={self.spread:g} px ({self.spread * point_value * size:,.2f} $"
            f"/{size:g}u), commission=${self.round_turn_commission:,.2f}/u RT, "
            f"slippage={self.slippage:g} px/side "
            f"-> ${self.round_turn_cost(size, point_value):,.2f} round turn"
        )


#: Retail-realistic defaults.  Spreads are typical *raw/ECN* values for the
#: liquid session; commission is the brief's $5 round turn.  Widen the FX
#: spread ~3x across the 21:00-01:00 UTC rollover, which is where a
#: 24-hour challenge is most likely to be sitting in a position.
DEFAULT_COSTS = {
    "EURUSD": CostModel(
        spread=0.00008,                      # 0.8 pip
        commission_per_side=2.50,
        session_widening=((21, 1, 3.0),),
    ),
    "XAUUSD": CostModel(
        spread=0.30,                         # 30 cents
        commission_per_side=2.50,
        session_widening=((21, 1, 2.5),),
    ),
    "MNQ": CostModel(
        spread=0.25,                         # one tick
        commission_per_side=2.50,
        session_widening=((21, 22, 2.0),),   # CME maintenance break
    ),
    "NQ": CostModel(
        spread=0.25,
        commission_per_side=2.50,
        session_widening=((21, 22, 2.0),),
    ),
}

#: A frictionless model.  Only ever appropriate inside unit tests and as an
#: explicit control -- a frictionless simulation of this challenge is
#: worthless.  ``use_measured_spread`` is off deliberately: otherwise a series
#: carrying real bid/ask would quietly reintroduce the spread and a model
#: named ZERO_COSTS would charge for execution.
ZERO_COSTS = CostModel(spread=0.0, commission_per_side=0.0, slippage=0.0,
                       use_measured_spread=False)


def get_costs(symbol: str) -> CostModel:
    key = symbol.upper().replace("=X", "").replace("-", "")
    if key not in DEFAULT_COSTS:
        raise KeyError(f"no default cost model for {symbol!r}")
    return DEFAULT_COSTS[key]
