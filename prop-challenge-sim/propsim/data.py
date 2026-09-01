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
    #: Measured bid/ask spread per bar, in price units.  Populated by tick
    #: sources; empty when the source only gives OHLC, in which case the cost
    #: model falls back to its configured spread.
    spread: List[float] = field(default_factory=list)
    timeframe: str = "1m"
    source: str = ""

    def __post_init__(self) -> None:
        n = len(self.ts)
        if not self.volume:
            self.volume = [0.0] * n
        if self.spread and len(self.spread) != n:
            raise ValueError(
                f"{self.symbol}: spread has {len(self.spread)} entries "
                f"but ts has {n}"
            )
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
            spread=self.spread[start:stop] if self.spread else [],
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
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        has_spread = bool(self.spread)
        header = ["ts_ns", "open", "high", "low", "close", "volume"]
        if has_spread:
            header.append("spread")
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            for i in range(len(self)):
                row = [self.ts[i], self.open[i], self.high[i],
                       self.low[i], self.close[i], self.volume[i]]
                if has_spread:
                    row.append(self.spread[i])
                w.writerow(row)

    @classmethod
    def from_csv(cls, path: str, symbol: str, timeframe: str = "1m",
                 source: str = "") -> "BarSeries":
        ts: List[int] = []
        o: List[float] = []
        h: List[float] = []
        l: List[float] = []
        c: List[float] = []
        v: List[float] = []
        sp: List[float] = []
        with open(path, newline="") as fh:
            for row in csv.DictReader(fh):
                ts.append(int(row["ts_ns"]))
                o.append(float(row["open"]))
                h.append(float(row["high"]))
                l.append(float(row["low"]))
                c.append(float(row["close"]))
                v.append(float(row.get("volume") or 0.0))
                if row.get("spread"):
                    sp.append(float(row["spread"]))
        return cls(symbol=symbol, ts=ts, open=o, high=h, low=l, close=c,
                   volume=v, spread=sp, timeframe=timeframe,
                   source=source or path)

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


# ---------------------------------------------------------------------------
# Dukascopy tick history
# ---------------------------------------------------------------------------
#
# Why this source.  The drawdown rule is a statement about the price *path*,
# so the answer is only as good as the resolution of the extremes.  Dukascopy
# publishes free tick history back to ~2003 for FX majors, with both bid and
# ask -- which means the spread in the cost model is measured rather than
# assumed.  The price is that it is one HTTP request per instrument-hour
# (~8,760 per symbol-year), so the first pull is slow and everything after it
# comes from the cache.
#
# Wire format: LZMA-alone compressed, then 20-byte big-endian records of
# ``(ms_since_hour: u32, ask: u32, bid: u32, ask_vol: f32, bid_vol: f32)``
# with prices as integers to be divided by a per-symbol factor.  A zero-length
# body means "no ticks this hour" -- a weekend or a holiday, not an error.

DUKASCOPY_BASE = "https://datafeed.dukascopy.com/datafeed"

#: symbol -> (dukascopy instrument code, integer price divisor, is_proxy)
DUKASCOPY_SYMBOLS = {
    "EURUSD": ("EURUSD", 1e5, False),
    "XAUUSD": ("XAUUSD", 1e3, False),
    # Dukascopy has no CME futures.  Its Nasdaq-100 CFD tracks the index and
    # is the closest free tick proxy for NQ/MNQ; results using it are labelled
    # as a proxy rather than quietly presented as futures.
    "MNQ": ("USATECHIDXUSD", 1e3, True),
    "NQ": ("USATECHIDXUSD", 1e3, True),
}

TICK_STRUCT = ">IIIff"
TICK_SIZE = 20


@dataclass
class TickSeries:
    """Raw bid/ask ticks.  ``ts`` is nanoseconds UTC."""

    symbol: str
    ts: List[int]
    bid: List[float]
    ask: List[float]
    bid_volume: List[float] = field(default_factory=list)
    ask_volume: List[float] = field(default_factory=list)
    source: str = "dukascopy"

    def __len__(self) -> int:
        return len(self.ts)


def decode_bi5(payload: bytes, divisor: float, hour_start_ns: int,
               symbol: str = "") -> TickSeries:
    """Decode one Dukascopy hourly tick file.

    Split out as a pure function precisely so it can be tested without the
    network: the tests build a payload with the documented layout and assert
    it round-trips.
    """
    import lzma
    import struct

    if not payload:
        return TickSeries(symbol=symbol, ts=[], bid=[], ask=[])
    try:
        raw = lzma.decompress(payload, format=lzma.FORMAT_ALONE)
    except lzma.LZMAError:
        # Some hours are served already-decompressed.
        raw = payload
    if len(raw) % TICK_SIZE:
        raise ValueError(
            f"{symbol}: tick payload is {len(raw)} bytes, not a multiple of "
            f"{TICK_SIZE}"
        )

    n = len(raw) // TICK_SIZE
    ts: List[int] = []
    bid: List[float] = []
    ask: List[float] = []
    bvol: List[float] = []
    avol: List[float] = []
    unpack = struct.Struct(TICK_STRUCT).unpack_from
    for k in range(n):
        ms, a, b, av, bv = unpack(raw, k * TICK_SIZE)
        ts.append(hour_start_ns + ms * 1_000_000)
        ask.append(a / divisor)
        bid.append(b / divisor)
        avol.append(av)
        bvol.append(bv)
    return TickSeries(symbol=symbol, ts=ts, bid=bid, ask=ask,
                      bid_volume=bvol, ask_volume=avol)


def _dukascopy_url(code: str, dt: datetime) -> str:
    # Dukascopy months are zero-indexed.  This has cost more people more
    # debugging time than any other detail of the format.
    return (f"{DUKASCOPY_BASE}/{code}/{dt.year:04d}/{dt.month - 1:02d}/"
            f"{dt.day:02d}/{dt.hour:02d}h_ticks.bi5")


def _cache_path(cache_dir: str, code: str, dt: datetime) -> str:
    return os.path.join(cache_dir, "dukascopy", code, f"{dt.year:04d}",
                        f"{dt.month:02d}", f"{dt.day:02d}",
                        f"{dt.hour:02d}h_ticks.bi5")


def _fetch_hour(code: str, dt: datetime, cache_dir: str,
                timeout: float = 30.0, retries: int = 3) -> bytes:
    """Fetch (or read from cache) one hour of ticks."""
    import urllib.error
    import urllib.request

    path = _cache_path(cache_dir, code, dt)
    if os.path.exists(path):
        with open(path, "rb") as fh:
            return fh.read()

    url = _dukascopy_url(code, dt)
    req = urllib.request.Request(url, headers={
        "User-Agent": "propsim/0.1 (research)",
        "Referer": "https://www.dukascopy.com/",
    })
    last: Optional[Exception] = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read()
            break
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                body = b""      # no data for this hour; cache the absence
                break
            last = exc
        except Exception as exc:                       # noqa: BLE001
            last = exc
        time_sleep = 2.0 ** attempt
        try:
            import time as _t
            _t.sleep(time_sleep)
        except Exception:                              # pragma: no cover
            pass
    else:
        raise RuntimeError(f"failed to fetch {url}: {last}")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "wb") as fh:
        fh.write(body)
    os.replace(tmp, path)
    return body


def fetch_dukascopy_ticks(symbol: str, start: datetime, end: datetime,
                          cache_dir: str = "cache", jobs: int = 8,
                          progress=None) -> TickSeries:
    """Download (and cache) tick history for ``[start, end)``.

    Hours are fetched concurrently -- the job is entirely network-bound, so
    threads are the right tool and 8 of them turn a multi-hour first pull into
    a manageable one.  Results are reassembled in chronological order.
    """
    from concurrent.futures import ThreadPoolExecutor

    if symbol.upper() not in DUKASCOPY_SYMBOLS:
        raise KeyError(f"no Dukascopy mapping for {symbol!r}")
    code, divisor, is_proxy = DUKASCOPY_SYMBOLS[symbol.upper()]

    hours: List[datetime] = []
    cur = start.replace(minute=0, second=0, microsecond=0,
                        tzinfo=start.tzinfo or timezone.utc)
    while cur < end:
        # Skip the weekend outright: the request would 404 anyway and there
        # are 48 of them every week.
        if not (cur.weekday() == 5 or (cur.weekday() == 6 and cur.hour < 21)
                or (cur.weekday() == 4 and cur.hour >= 21)):
            hours.append(cur)
        cur += timedelta(hours=1)

    payloads: List[Optional[bytes]] = [None] * len(hours)
    done = 0
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        futures = {pool.submit(_fetch_hour, code, h, cache_dir): k
                   for k, h in enumerate(hours)}
        for fut, k in futures.items():
            payloads[k] = fut.result()
            done += 1
            if progress and done % 50 == 0:
                progress(done, len(hours))

    ts: List[int] = []
    bid: List[float] = []
    ask: List[float] = []
    bvol: List[float] = []
    avol: List[float] = []
    for h, payload in zip(hours, payloads):
        hour_ns = int(h.timestamp()) * NS_PER_SECOND
        chunk = decode_bi5(payload or b"", divisor, hour_ns, symbol)
        ts.extend(chunk.ts)
        bid.extend(chunk.bid)
        ask.extend(chunk.ask)
        bvol.extend(chunk.bid_volume)
        avol.extend(chunk.ask_volume)

    src = "dukascopy-proxy" if is_proxy else "dukascopy"
    return TickSeries(symbol=symbol, ts=ts, bid=bid, ask=ask,
                      bid_volume=bvol, ask_volume=avol, source=src)


def ticks_to_bars(ticks: TickSeries, seconds: int = 60,
                  timeframe: Optional[str] = None) -> BarSeries:
    """Resample ticks into mid-price OHLC bars with a measured mean spread.

    OHLC is built from the *mid*, matching the engine's convention that the
    series is mid and the cost model owns the spread.  The mean spread inside
    each bar is carried alongside, so execution cost is data rather than
    assumption.
    """
    step = seconds * NS_PER_SECOND
    out_ts: List[int] = []
    o: List[float] = []
    h: List[float] = []
    l: List[float] = []
    c: List[float] = []
    v: List[float] = []
    sp: List[float] = []

    bucket = -1
    spread_sum = 0.0
    count = 0
    for k in range(len(ticks)):
        mid = 0.5 * (ticks.bid[k] + ticks.ask[k])
        b = (ticks.ts[k] // step) * step
        if b != bucket:
            if bucket >= 0:
                sp.append(spread_sum / count)
                v.append(float(count))
            bucket = b
            out_ts.append(b)
            o.append(mid)
            h.append(mid)
            l.append(mid)
            c.append(mid)
            spread_sum = 0.0
            count = 0
        else:
            if mid > h[-1]:
                h[-1] = mid
            elif mid < l[-1]:
                l[-1] = mid
            c[-1] = mid
        spread_sum += ticks.ask[k] - ticks.bid[k]
        count += 1
    if bucket >= 0:
        sp.append(spread_sum / count)
        v.append(float(count))

    if timeframe is None:
        timeframe = f"{seconds}s" if seconds < 60 else f"{seconds // 60}m"
    return BarSeries(symbol=ticks.symbol, ts=out_ts, open=o, high=h, low=l,
                     close=c, volume=v, spread=sp, timeframe=timeframe,
                     source=ticks.source)


# ---------------------------------------------------------------------------
# Synthetic data
# ---------------------------------------------------------------------------
#
# A generator earns its place here for two reasons.  It makes the whole
# pipeline verifiable end to end without a network, and -- more usefully -- it
# is a *null model*: a driftless market with realistic volatility structure
# and honest costs.  If a strategy clears the 10% breakeven on synthetic data
# it has found an artefact of the cost model or the rules, not an edge, and
# that is worth knowing before trusting the same number on real prices.
#
# Bars are built by simulating sub-bar steps and aggregating them, never by
# decorating a close with a made-up range.  The whole study lives or dies on
# intrabar extremes, so those have to come from a simulated path.

SYNTHETIC_PARAMS = {
    #             start price, annualised vol, base spread (price units)
    "EURUSD": (1.0850, 0.07, 0.00008),
    "XAUUSD": (2350.0, 0.16, 0.30),
    "MNQ":    (18500.0, 0.22, 0.25),
    "NQ":     (18500.0, 0.22, 0.25),
}

#: Rough intraday volatility shape by UTC hour: Asia quiet, London open,
#: London/NY overlap busiest, late NY fading.
_SESSION_VOL = [
    0.55, 0.50, 0.50, 0.55, 0.65, 0.75, 0.85, 1.00,   # 00-07
    1.20, 1.25, 1.15, 1.05, 1.10, 1.45, 1.55, 1.40,   # 08-15
    1.20, 1.05, 0.90, 0.80, 0.70, 0.60, 0.55, 0.55,   # 16-23
]


def _fx_market_open(dt: datetime) -> bool:
    """Sunday 21:00 UTC to Friday 21:00 UTC."""
    wd = dt.weekday()
    if wd == 5:
        return False
    if wd == 6:
        return dt.hour >= 21
    if wd == 4:
        return dt.hour < 21
    return True


def generate_synthetic(symbol: str, days: int = 60,
                       start: str = "2024-01-01T00:00:00Z",
                       seed: int = 0, bar_seconds: int = 60,
                       substeps: int = 10,
                       jumps_per_day: float = 2.0) -> BarSeries:
    """Driftless price path with volatility clustering, jumps and sessions.

    * log-price is a martingale -- no edge is baked in;
    * an AR(1) on log volatility produces the clustering that drives fat
      drawdown tails, which a constant-vol GBM would understate badly;
    * jumps arrive as a Poisson process, sized in units of the current bar's
      sigma, so news gaps blow through stops the way they really do;
    * the spread widens on the same session schedule as the volatility.
    """
    if symbol.upper() not in SYNTHETIC_PARAMS:
        raise KeyError(f"no synthetic parameters for {symbol!r}")
    p0, ann_vol, base_spread = SYNTHETIC_PARAMS[symbol.upper()]
    rng = random.Random(seed)

    t0 = datetime.fromisoformat(start.replace("Z", "+00:00"))
    step_ns = bar_seconds * NS_PER_SECOND
    n_bars = int(days * 86_400 // bar_seconds)

    seconds_per_year = 252.0 * 24.0 * 3600.0
    dt_sub = (bar_seconds / substeps) / seconds_per_year
    sigma_base = ann_vol * math.sqrt(dt_sub)

    rho, sigma_v = 0.97, 0.30
    log_vol = 0.0
    jump_p = jumps_per_day / (86_400.0 / bar_seconds)

    ts: List[int] = []
    o: List[float] = []
    h: List[float] = []
    l: List[float] = []
    c: List[float] = []
    v: List[float] = []
    sp: List[float] = []

    price = p0
    for k in range(n_bars):
        when = t0 + timedelta(seconds=k * bar_seconds)
        if not _fx_market_open(when):
            continue

        log_vol = rho * log_vol + math.sqrt(1.0 - rho * rho) * sigma_v * \
            rng.gauss(0.0, 1.0)
        session = _SESSION_VOL[when.hour]
        sigma = sigma_base * session * math.exp(log_vol)

        bar_open = price
        bar_high = price
        bar_low = price
        for _ in range(substeps):
            price *= math.exp(-0.5 * sigma * sigma + sigma * rng.gauss(0.0, 1.0))
            if price > bar_high:
                bar_high = price
            elif price < bar_low:
                bar_low = price
        if rng.random() < jump_p:
            shock = rng.gauss(0.0, 1.0) * sigma * math.sqrt(substeps) * 6.0
            price *= math.exp(shock)
            if price > bar_high:
                bar_high = price
            elif price < bar_low:
                bar_low = price

        ts.append(int(when.timestamp()) * NS_PER_SECOND)
        o.append(bar_open)
        h.append(bar_high)
        l.append(bar_low)
        c.append(price)
        v.append(float(substeps))
        # Spread is inverse to activity, with an extra kick over the
        # 21:00-22:00 UTC rollover where liquidity genuinely evaporates.
        widen = 0.35 + 0.75 / session
        if when.hour in (21, 22):
            widen *= 2.5
        sp.append(base_spread * widen)

    return BarSeries(symbol=symbol.upper(), ts=ts, open=o, high=h, low=l,
                     close=c, volume=v, spread=sp,
                     timeframe=f"{bar_seconds}s" if bar_seconds < 60
                     else f"{bar_seconds // 60}m",
                     source=f"synthetic(seed={seed})")


# ---------------------------------------------------------------------------
# Cache-backed loading
# ---------------------------------------------------------------------------

DEFAULT_CACHE = os.environ.get("PROPSIM_CACHE", "cache")


def load_bars(symbol: str, source: str = "dukascopy",
              start: str = "2024-01-01", end: str = "2024-04-01",
              timeframe_seconds: int = 60, cache_dir: str = DEFAULT_CACHE,
              seed: int = 0, jobs: int = 8, refresh: bool = False,
              progress=None) -> BarSeries:
    """Load bars, using the local cache when possible.

    ``source`` is one of ``dukascopy`` (tick history, resampled),
    ``synthetic`` (offline null model) or a path to a CSV written by
    :meth:`BarSeries.to_csv`.
    """
    if os.path.exists(source) and source.endswith(".csv"):
        return BarSeries.from_csv(source, symbol,
                                  timeframe=f"{timeframe_seconds}s")

    tag = f"{symbol.upper()}_{timeframe_seconds}s_{start}_{end}_{source}"
    if source == "synthetic":
        tag += f"_seed{seed}"
    bar_path = os.path.join(cache_dir, "bars", tag.replace(":", "") + ".csv")
    if os.path.exists(bar_path) and not refresh:
        return BarSeries.from_csv(bar_path, symbol.upper(),
                                  timeframe=f"{timeframe_seconds}s",
                                  source=source)

    if source == "synthetic":
        d0 = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
        d1 = datetime.fromisoformat(end).replace(tzinfo=timezone.utc)
        bars = generate_synthetic(
            symbol, days=max(1, int((d1 - d0).total_seconds() // 86_400)),
            start=d0.strftime("%Y-%m-%dT%H:%M:%SZ"), seed=seed,
            bar_seconds=timeframe_seconds)
    elif source == "dukascopy":
        d0 = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
        d1 = datetime.fromisoformat(end).replace(tzinfo=timezone.utc)
        ticks = fetch_dukascopy_ticks(symbol, d0, d1, cache_dir=cache_dir,
                                      jobs=jobs, progress=progress)
        if not len(ticks):
            raise RuntimeError(
                f"Dukascopy returned no ticks for {symbol} {start}..{end}. "
                f"Check the symbol mapping and that the range is not entirely "
                f"weekend/holiday."
            )
        bars = ticks_to_bars(ticks, timeframe_seconds)
    else:
        raise ValueError(f"unknown source {source!r}")

    bars.validate()
    bars.to_csv(bar_path)
    return bars


# ---------------------------------------------------------------------------
# HistData ASCII M1
# ---------------------------------------------------------------------------
#
# HistData.com publishes free 1-minute OHLC bars back to 2000 as semicolon
# separated ASCII:
#
#     YYYYMMDD HHMMSS;open;high;low;close;volume
#
# Two properties matter and both are easy to get wrong:
#
# * Timestamps are **EST, fixed at UTC-5, with no daylight saving** -- they do
#   not shift in summer.  Treating them as UTC puts every session five hours
#   out and silently misaligns the spread-widening schedule.
# * Prices are **bid only**.  There is no ask, so unlike the Dukascopy tick
#   path the spread has to be modelled rather than measured; the series
#   carries no ``spread`` column and the cost model falls back to its
#   configured value.
#
# Volume is always 0 for FX and is ignored.

HISTDATA_UTC_OFFSET_HOURS = 5


def parse_histdata_m1(path: str, symbol: str = "EURUSD") -> "BarSeries":
    """Parse one HistData ASCII M1 file into a mid-less (bid) BarSeries."""
    ts: List[int] = []
    o: List[float] = []
    h: List[float] = []
    l: List[float] = []
    c: List[float] = []
    shift = HISTDATA_UTC_OFFSET_HOURS * NS_PER_HOUR

    with open(path, "r", newline="") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            if len(parts) < 5:
                continue
            stamp = parts[0]
            if len(stamp) != 15 or stamp[8] != " ":
                continue                      # header or status-report line
            try:
                y, mo, d = int(stamp[0:4]), int(stamp[4:6]), int(stamp[6:8])
                hh, mi, ss = int(stamp[9:11]), int(stamp[11:13]), int(stamp[13:15])
                bar_o, bar_h, bar_l, bar_c = (float(parts[1]), float(parts[2]),
                                              float(parts[3]), float(parts[4]))
            except ValueError:
                continue
            when = datetime(y, mo, d, hh, mi, ss, tzinfo=timezone.utc)
            ts.append(int(when.timestamp()) * NS_PER_SECOND + shift)
            o.append(bar_o)
            h.append(bar_h)
            l.append(bar_l)
            c.append(bar_c)

    if not ts:
        raise ValueError(f"{path}: no HistData M1 rows found")
    return BarSeries(symbol=symbol, ts=ts, open=o, high=h, low=l, close=c,
                     volume=[0.0] * len(ts), timeframe="1m",
                     source="histdata")


def load_histdata_dir(root: str, symbol: str = "EURUSD") -> "BarSeries":
    """Parse and concatenate every HistData M1 CSV under ``root``.

    Files are ordered by the period embedded in their name, de-duplicated on
    timestamp (a yearly file and its monthly siblings overlap), and validated.
    """
    import glob

    paths = sorted(glob.glob(os.path.join(root, "**", "*.csv"), recursive=True))
    paths = [p for p in paths
             if f"_{symbol.upper()}_M1_" in os.path.basename(p).upper()]
    if not paths:
        raise FileNotFoundError(
            f"no DAT_ASCII_{symbol.upper()}_M1_*.csv under {root}")

    merged: Dict[int, Tuple[float, float, float, float]] = {}
    for p in paths:
        part = parse_histdata_m1(p, symbol)
        for i in range(len(part)):
            merged[part.ts[i]] = (part.open[i], part.high[i],
                                  part.low[i], part.close[i])

    order = sorted(merged)
    bars = BarSeries(
        symbol=symbol.upper(), ts=order,
        open=[merged[t][0] for t in order], high=[merged[t][1] for t in order],
        low=[merged[t][2] for t in order], close=[merged[t][3] for t in order],
        volume=[0.0] * len(order), timeframe="1m",
        source=f"histdata ({len(paths)} files)",
    )
    bars.validate()
    return bars
