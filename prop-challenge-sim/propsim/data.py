"""
data.py -- instruments, bar containers, and the local data cache.

The whole simulator runs on plain Python lists of floats.  That is a deliberate
choice, not a limitation: the challenge engine is a scalar, path-dependent loop
over bars, and element-by-element access on a Python list is several times
faster than the same access on a numpy array (every ``arr[i]`` on an ndarray
allocates a boxed scalar).  numpy/pandas are used only at the edges -- loading,
reporting, plotting -- and are optional imports everywhere.
"""

from __future__ import annotations

import bisect
import csv
import math
import os
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional, Sequence, Tuple

NS_PER_SECOND = 1_000_000_000
NS_PER_MINUTE = 60 * NS_PER_SECOND
NS_PER_HOUR = 60 * NS_PER_MINUTE
NS_PER_DAY = 24 * NS_PER_HOUR


# ---------------------------------------------------------------------------
# Instruments
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Instrument:
    """A tradable symbol and the contract arithmetic that goes with it.

    ``point_value`` is the dollar P&L produced by a 1.0 move in price for one
    unit (one standard FX lot, one futures contract, one 100oz gold lot).  It is
    the only number that converts price space into account space, so getting it
    right matters more than anything else in this file.
    """

    symbol: str
    point_value: float
    unit_name: str = "lot"
    min_size: float = 0.01
    size_step: float = 0.01
    # Used only when exposure is measured on a margin basis.
    leverage: float = 30.0
    margin_per_unit: Optional[float] = None
    tick_size: float = 1e-5
    price_decimals: int = 5
    description: str = ""

    def round_size(self, size: float) -> float:
        """Round *down* to a tradable size.  Rounding down never accidentally
        breaches the exposure cap."""
        if self.size_step <= 0:
            return size
        steps = math.floor(size / self.size_step + 1e-9)
        return max(0.0, steps * self.size_step)

    def notional(self, size: float, price: float) -> float:
        return abs(size) * price * self.point_value

    def margin_required(self, size: float, price: float) -> float:
        if self.margin_per_unit is not None:
            return abs(size) * self.margin_per_unit
        if self.leverage <= 0:
            return self.notional(size, price)
        return self.notional(size, price) / self.leverage


#: Contract specs for the instruments the study covers.
#:
#: EURUSD  1 standard lot = 100,000 EUR  -> $100,000 per 1.00 price move.
#: XAUUSD  1 lot = 100 troy oz           -> $100 per $1.00 move.
#: MNQ     Micro E-mini Nasdaq-100       -> $2 per index point.
#: NQ      E-mini Nasdaq-100             -> $20 per index point.
INSTRUMENTS = {
    "EURUSD": Instrument(
        symbol="EURUSD", point_value=100_000.0, unit_name="lot",
        min_size=0.01, size_step=0.01, leverage=30.0,
        tick_size=1e-5, price_decimals=5,
        description="EUR/USD spot, 1 lot = 100,000 EUR",
    ),
    "XAUUSD": Instrument(
        symbol="XAUUSD", point_value=100.0, unit_name="lot",
        min_size=0.01, size_step=0.01, leverage=20.0,
        tick_size=0.01, price_decimals=2,
        description="Spot gold, 1 lot = 100 troy oz",
    ),
    "MNQ": Instrument(
        symbol="MNQ", point_value=2.0, unit_name="contract",
        min_size=1.0, size_step=1.0, margin_per_unit=2_400.0,
        tick_size=0.25, price_decimals=2,
        description="Micro E-mini Nasdaq-100, $2 per index point",
    ),
    "NQ": Instrument(
        symbol="NQ", point_value=20.0, unit_name="contract",
        min_size=1.0, size_step=1.0, margin_per_unit=24_000.0,
        tick_size=0.25, price_decimals=2,
        description="E-mini Nasdaq-100, $20 per index point",
    ),
}


def get_instrument(symbol: str) -> Instrument:
    key = symbol.upper().replace("=X", "").replace("-", "")
    if key in INSTRUMENTS:
        return INSTRUMENTS[key]
    raise KeyError(
        f"unknown instrument {symbol!r}; known: {sorted(INSTRUMENTS)}"
    )


# ---------------------------------------------------------------------------
# Bar series
# ---------------------------------------------------------------------------

@dataclass
class BarSeries:
    """OHLCV bars, UTC, ascending, ``ts`` is the bar OPEN time in nanoseconds.

    Prices are treated as **mid** throughout the simulator; the spread is
    applied by the cost model, never baked into the series.
    """

    symbol: str
    ts: List[int]
    open: List[float]
    high: List[float]
    low: List[float]
    close: List[float]
    volume: List[float] = field(default_factory=list)
    timeframe: str = "1m"
    source: str = ""

    def __post_init__(self) -> None:
        n = len(self.ts)
        if not self.volume:
            self.volume = [0.0] * n
        for name in ("open", "high", "low", "close", "volume"):
            if len(getattr(self, name)) != n:
                raise ValueError(
                    f"{self.symbol}: {name} has {len(getattr(self, name))} "
                    f"entries but ts has {n}"
                )

    def __len__(self) -> int:
        return len(self.ts)

    # -- integrity ----------------------------------------------------------

    def validate(self) -> None:
        """Raise on anything that would make the intrabar logic lie."""
        n = len(self)
        if n == 0:
            raise ValueError(f"{self.symbol}: empty series")
        for i in range(n):
            o, h, l, c = self.open[i], self.high[i], self.low[i], self.close[i]
            if not (h >= max(o, c) - 1e-12 and l <= min(o, c) + 1e-12 and h >= l):
                raise ValueError(
                    f"{self.symbol}: bar {i} violates OHLC ordering "
                    f"(o={o} h={h} l={l} c={c})"
                )
            if i and self.ts[i] <= self.ts[i - 1]:
                raise ValueError(
                    f"{self.symbol}: timestamps not strictly ascending at {i}"
                )

    # -- views --------------------------------------------------------------

    def slice(self, start: int, stop: Optional[int] = None) -> "BarSeries":
        stop = len(self) if stop is None else stop
        return BarSeries(
            symbol=self.symbol, ts=self.ts[start:stop],
            open=self.open[start:stop], high=self.high[start:stop],
            low=self.low[start:stop], close=self.close[start:stop],
            volume=self.volume[start:stop],
            timeframe=self.timeframe, source=self.source,
        )

    def index_at_or_after(self, ts_ns: int) -> int:
        return bisect.bisect_left(self.ts, ts_ns)

    @property
    def step_ns(self) -> int:
        """Modal bar spacing, in nanoseconds.  Robust to session gaps."""
        if len(self) < 2:
            return NS_PER_MINUTE
        counts = {}
        for i in range(1, min(len(self), 500)):
            d = self.ts[i] - self.ts[i - 1]
            counts[d] = counts.get(d, 0) + 1
        return max(counts.items(), key=lambda kv: kv[1])[0]

    @property
    def span_days(self) -> float:
        if len(self) < 2:
            return 0.0
        return (self.ts[-1] - self.ts[0]) / NS_PER_DAY

    def describe(self) -> str:
        if not len(self):
            return f"{self.symbol}: empty"
        t0 = datetime.fromtimestamp(self.ts[0] / 1e9, timezone.utc)
        t1 = datetime.fromtimestamp(self.ts[-1] / 1e9, timezone.utc)
        return (
            f"{self.symbol} {self.timeframe}: {len(self):,} bars, "
            f"{t0:%Y-%m-%d %H:%M} -> {t1:%Y-%m-%d %H:%M} UTC "
            f"({self.span_days:.1f} days, source={self.source or 'n/a'})"
        )

    # -- persistence --------------------------------------------------------

    def to_csv(self, path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["ts_ns", "open", "high", "low", "close", "volume"])
            for i in range(len(self)):
                w.writerow([
                    self.ts[i], self.open[i], self.high[i],
                    self.low[i], self.close[i], self.volume[i],
                ])

    @classmethod
    def from_csv(cls, path: str, symbol: str, timeframe: str = "1m",
                 source: str = "") -> "BarSeries":
        ts: List[int] = []
        o: List[float] = []
        h: List[float] = []
        l: List[float] = []
        c: List[float] = []
        v: List[float] = []
        with open(path, newline="") as fh:
            for row in csv.DictReader(fh):
                ts.append(int(row["ts_ns"]))
                o.append(float(row["open"]))
                h.append(float(row["high"]))
                l.append(float(row["low"]))
                c.append(float(row["close"]))
                v.append(float(row.get("volume") or 0.0))
        return cls(symbol=symbol, ts=ts, open=o, high=h, low=l, close=c,
                   volume=v, timeframe=timeframe, source=source or path)

    # -- optional pandas interop -------------------------------------------

    def to_dataframe(self):
        import pandas as pd  # optional dependency
        return pd.DataFrame(
            {"open": self.open, "high": self.high, "low": self.low,
             "close": self.close, "volume": self.volume},
            index=pd.to_datetime(self.ts, unit="ns", utc=True),
        )

    @classmethod
    def from_dataframe(cls, df, symbol: str, timeframe: str = "1m",
                       source: str = "pandas") -> "BarSeries":
        import pandas as pd  # optional dependency
        idx = pd.to_datetime(df.index, utc=True)
        cols = {c.lower(): c for c in df.columns}
        return cls(
            symbol=symbol,
            ts=[int(x) for x in idx.view("int64")],
            open=[float(x) for x in df[cols["open"]]],
            high=[float(x) for x in df[cols["high"]]],
            low=[float(x) for x in df[cols["low"]]],
            close=[float(x) for x in df[cols["close"]]],
            volume=[float(x) for x in df[cols["volume"]]] if "volume" in cols
            else [0.0] * len(df),
            timeframe=timeframe, source=source,
        )


# ---------------------------------------------------------------------------
# Bar construction helpers (used by tests and by the synthetic generator)
# ---------------------------------------------------------------------------

def make_bars(symbol: str, ohlc: Sequence[Sequence[float]],
              start: str = "2024-01-02T00:00:00Z",
              step_ns: int = NS_PER_MINUTE,
              timeframe: str = "1m") -> BarSeries:
    """Build a BarSeries from literal ``(o, h, l, c)`` tuples.

    Tests use this to write price paths by hand, which is the only way to
    assert on intrabar behaviour deterministically.
    """
    t0 = int(datetime.fromisoformat(start.replace("Z", "+00:00"))
             .timestamp() * NS_PER_SECOND)
    ts = [t0 + i * step_ns for i in range(len(ohlc))]
    return BarSeries(
        symbol=symbol, ts=ts,
        open=[float(b[0]) for b in ohlc],
        high=[float(b[1]) for b in ohlc],
        low=[float(b[2]) for b in ohlc],
        close=[float(b[3]) for b in ohlc],
        volume=[float(b[4]) if len(b) > 4 else 1.0 for b in ohlc],
        timeframe=timeframe, source="literal",
    )
