"""propsim -- Monte Carlo simulator for prop-firm 24-hour challenges."""

from .costs import DEFAULT_COSTS, ZERO_COSTS, CostModel, get_costs
from .data import INSTRUMENTS, BarSeries, Instrument, get_instrument, make_bars
from .engine import (
    CLOSE,
    BarContext,
    ChallengeConfig,
    ChallengeResult,
    DrawdownMode,
    ExitReason,
    ExposureBasis,
    IntrabarOrder,
    Order,
    Outcome,
    Position,
    SizingMode,
    Strategy,
    Trade,
    run_challenge,
)

__version__ = "0.1.0"

__all__ = [
    "BarSeries", "Instrument", "INSTRUMENTS", "get_instrument", "make_bars",
    "CostModel", "DEFAULT_COSTS", "ZERO_COSTS", "get_costs",
    "run_challenge", "ChallengeConfig", "ChallengeResult", "Outcome",
    "ExitReason", "DrawdownMode", "IntrabarOrder", "ExposureBasis",
    "SizingMode", "Order", "CLOSE", "Position", "Trade", "Strategy",
    "BarContext",
]
