#!/usr/bin/env python3
"""
pack_bars.py -- encode real OHLC bars into a compact base64 blob for the page.

EURUSD minute bars are extremely low-entropy: the open almost always equals the
previous close, and the high/low/close sit within a pip or two of the open.  So
each bar is stored as four *deltas* in integer points (1e-5), zigzag-encoded as
varints, plus the gap in minutes since the previous bar.  That lands around
four bytes per bar where a naive CSV needs sixty.

Usage: python web/pack_bars.py <csv-in> <js-out> [--from YYYY-MM-DD] [--to ...]
"""

import base64
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from propsim.data import BarSeries, NS_PER_SECOND  # noqa: E402

SCALE = 100_000  # EURUSD quoted to 1e-5


def zigzag(n: int) -> int:
    return (n << 1) ^ (n >> 63)


def put_varint(out: bytearray, n: int) -> None:
    n = zigzag(n)
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return


def pack(bars: BarSeries) -> dict:
    out = bytearray()
    prev_close = None
    prev_min = None
    for i in range(len(bars)):
        o = round(bars.open[i] * SCALE)
        h = round(bars.high[i] * SCALE)
        l = round(bars.low[i] * SCALE)
        c = round(bars.close[i] * SCALE)
        minute = bars.ts[i] // (60 * NS_PER_SECOND)
        put_varint(out, 0 if prev_min is None else int(minute - prev_min))
        put_varint(out, o if prev_close is None else o - prev_close)
        put_varint(out, h - o)
        put_varint(out, l - o)
        put_varint(out, c - o)
        prev_close, prev_min = c, minute
    return {
        "n": len(bars),
        "t0": int(bars.ts[0] // (60 * NS_PER_SECOND)),
        "scale": SCALE,
        "b64": base64.b64encode(bytes(out)).decode("ascii"),
        "raw_bytes": len(out),
    }


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    lo = hi = None
    if "--from" in sys.argv:
        lo = datetime.fromisoformat(sys.argv[sys.argv.index("--from") + 1]) \
            .replace(tzinfo=timezone.utc).timestamp() * NS_PER_SECOND
    if "--to" in sys.argv:
        hi = datetime.fromisoformat(sys.argv[sys.argv.index("--to") + 1]) \
            .replace(tzinfo=timezone.utc).timestamp() * NS_PER_SECOND

    bars = BarSeries.from_csv(src, "EURUSD", timeframe="1m", source="histdata")
    if lo or hi:
        keep = [i for i in range(len(bars))
                if (lo is None or bars.ts[i] >= lo) and (hi is None or bars.ts[i] < hi)]
        bars = bars.slice(keep[0], keep[-1] + 1)

    blob = pack(bars)
    js = (f"// Real EURUSD 1-minute bars, HistData.com via github.com/adampy/fx-ml.\n"
          f"// {blob['n']:,} bars, {bars.span_days:.0f} days, packed as zigzag varint\n"
          f"// deltas in 1e-5 points: {blob['raw_bytes'] / blob['n']:.2f} bytes per bar.\n"
          f"const REAL_BARS = {{n:{blob['n']},t0:{blob['t0']},scale:{blob['scale']},"
          f"b64:\"{blob['b64']}\"}};\n")
    with open(dst, "w") as fh:
        fh.write(js)
    print(f"{blob['n']:,} bars  {bars.span_days:.0f} days  "
          f"raw {blob['raw_bytes'] / 1e6:.2f} MB  "
          f"base64 {len(blob['b64']) / 1e6:.2f} MB  "
          f"({blob['raw_bytes'] / blob['n']:.2f} B/bar)")


if __name__ == "__main__":
    main()
