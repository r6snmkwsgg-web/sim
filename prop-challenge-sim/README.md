# propsim — prop-firm 24-hour challenge simulator

Monte Carlo estimate of the pass rate for a $20,000 / +$1,500 / −$300 / 24-hour
prop-firm challenge, under a pluggable trading strategy, with the drawdown
limit checked **continuously against equity including open-position P&L**.

```
$500 entry fee, $5,000 payout  ->  breakeven pass rate = 10%
```

Everything the simulator reports is measured against that 10% line.

---

## Quick start

```bash
python run_tests.py                       # 99 tests, no dependencies, ~4s
python -m propsim demo                    # end-to-end on synthetic data

# real data (needs network access to Dukascopy)
python -m propsim fetch --symbol EURUSD --start 2023-01-01 --end 2025-01-01
python -m propsim mc    --symbol EURUSD --start 2023-01-01 --end 2025-01-01 \
                        --strategy fixed_tp_sl --attempts 10000 --workers 8
python -m propsim sweep --symbol EURUSD --start 2023-01-01 --end 2025-01-01 \
                        --out out/EURUSD.png
```

`pytest -q` works too. The core has **no third-party dependencies at all** —
`requirements.txt` is entirely optional extras (matplotlib for PNG heatmaps,
pandas for DataFrame interop). A scalar, path-dependent loop over bars is
faster on Python lists than on numpy arrays anyway, because every `arr[i]` on
an ndarray allocates a boxed scalar.

---

## The one thing this is built to get right

The drawdown limit is a property of the price **path**, not of bar closes.

```
bar 1  low 96.00   ->  equity 19,600   ($400 underwater — dead)
bar 1  close 101   ->  equity 20,100   (green at the close)
bar 2  close 120   ->  equity 22,000   (past the +$1,500 target)
```

Read the closes and this attempt passes. Read the path and the account was
liquidated on bar 1. `tests/test_engine.py::test_dip_below_drawdown_then_recovers_is_a_fail`
asserts **both** halves — that the engine fails it, and that a close-only
engine would have passed it.

This is not a precision issue. A close-only simulator overstates the pass rate
most for high-variance configurations, which are exactly the ones a parameter
sweep is drawn towards. It doesn't just lose accuracy; it recommends the wrong
strategy.

### How the engine does it

Each bar is walked as a sequence of **marks** — adverse extreme, favourable
extreme, close — recomputing equity and testing the floor and the target at
every one.

Equity is **net liquidation value**: balance, plus the position marked at the
price it could actually be closed at (mid minus half-spread), minus the
commission still owed to close it. One quantity governs both the floor and the
target, so closing at a mark's price leaves the balance *exactly* equal to the
equity computed at that mark. There is no seam between the mark-to-market path
and the trade log, and the tests assert the reconciliation.

Three consequences worth knowing about:

- **Intrabar ordering is an assumption, not a fact.** OHLC cannot say whether
  the high or the low came first. `intrabar_order` defaults to
  `adverse_first`, which also resolves "stop and target both inside this bar"
  against the trader — the only defensible default for a risk study.
- **A resting stop truncates the adverse excursion.** A long stopped at 99.50
  in a bar whose low is 90.00 marks to 99.50, not 90.00: the position is gone
  before price gets there. Without this the engine invents breaches that could
  not physically happen.
- **Breaches and target hits liquidate at the exact crossing price**, solved in
  closed form (equity is affine in the mid, so it inverts) rather than at the
  bar extreme. A breached account ends at exactly the floor, which is what a
  real risk engine does. The raw extreme is kept as `breach_equity` for
  diagnosis.

### Validation against a closed-form answer

For a driftless price, a static floor and a horizon long enough that the clock
never binds, this is the gambler's ruin problem: P(reach +T before −D) =
D/(T+D), independent of size and volatility. The full stack — engine, sampler,
aggregation — reproduces it:

| target / drawdown | closed form | simulated |
|---|---|---|
| $450 / $150 | 25.00% | 25.90% |
| $300 / $300 | 50.00% | 51.30% |
| $150 / $450 | 75.00% | 74.67% |

Pinned as `test_engine_reproduces_gamblers_ruin`.

---

## Modelling decisions

Two clauses in the rules admit more than one reading, and both change the
answer enormously. Both readings are implemented; the defaults are marked.

### "Max drawdown: $300" — from where?

| `drawdown_mode` | floor | |
|---|---|---|
| `trailing_equity` | peak equity − $300, ratcheting intrabar | **default** |
| `static` | fixed at $19,700 | |
| `trailing_balance` | peak *closed* balance − $300 | |

This single choice is worth about ten percentage points of pass rate — which
is to say, it is the entire question. See the results table below.

### "Max 75% of the account in any single symbol" — 75% of what?

| `exposure_basis` | meaning | |
|---|---|---|
| `margin` | 75% of equity committed as margin | **default** |
| `notional` | 75% of equity as notional value | |

Under the notional reading the challenge is not hard, it is *impossible*: at
$15,000 of notional, EURUSD needs a 1,080-pip move in 24 hours (daily range is
~70), gold needs $240, and MNQ cannot trade even one contract ($40,000
notional against a $15,000 cap). The pass rate is a flat 0% everywhere and the
sweep is vacuous. The margin reading is what makes it a real question.

### Costs

Applied on both sides, always:

- **spread** — half on entry, half on exit, in price units. When the data
  carries a real bid/ask (Dukascopy ticks do), the *measured* spread is used
  in preference to any assumed constant.
- **commission** — $2.50 a side, i.e. the specified $5 round turn per lot or
  contract.
- **slippage** — extra adverse price per side, zero by default.
- **session widening** — spread multipliers by UTC hour, so the rollover
  blowout is modelled rather than assumed away. A 24-hour challenge is very
  likely to be holding something across it.

`--spread-multiplier 2` stress-tests the whole study against execution being
twice as bad as assumed. `ZERO_COSTS` exists as an explicit control and is
genuinely zero.

---

## Data

**Implemented: Dukascopy tick history**, via `urllib` + `lzma` — no `yfinance`
dependency. LZMA-alone compressed, 20-byte big-endian records, and note that
**Dukascopy months are zero-indexed**, which is the single most common way to
silently fetch the wrong month. Everything is cached hour-by-hour under
`cache/`, so the slow first pull happens once.

| source | resolution | history | cost | catch |
|---|---|---|---|---|
| **Dukascopy** | true tick, bid **and** ask | ~2003 FX, ~2010 gold | free | one request per instrument-hour (~8,760/symbol-year); no CME futures — NQ/MNQ fall back to a Nasdaq CFD, flagged as a proxy |
| yfinance | 1m | **~30 days** | free | see below; FX highs/lows are quote-derived and unreliable, and the highs and lows *are* the answer here |
| HistData | 1m | 2000→ | free | bid only, so the spread stays an assumption; form-token POST, brittle |
| Databento / Polygon | tick, real CME NQ+MNQ | years | paid | the only honest NQ source |

The yfinance problem is **sample independence**, not convenience. Thirty days
of 1-minute data contains ~30 non-overlapping 24-hour windows. Drawing 10,000
attempts from it yields 10,000 numbers and about 30 units of information.
Which is why:

> Every Monte Carlo report prints **two** intervals — a Wilson binomial one
> that assumes independent attempts, and a **day-cluster bootstrap** that
> resamples whole start-days. The gap between them is the honest measure of
> how much the dataset actually supports. It also prints
> `independent windows`, the real sample size.

Start times whose 24-hour window is mostly weekend are **rejected and
counted**, not silently recorded as timeout failures — that would be an
artefact of the sampling rather than a fact about the challenge.

A **synthetic generator** is included as a null model: driftless (a
martingale — no edge is baked in), with AR(1) volatility clustering, Poisson
jumps, session-shaped intraday volatility and a spread that widens when
liquidity thins. Bars are built by simulating sub-bar steps and aggregating,
never by decorating a close with a fabricated range — the whole study lives on
intrabar extremes. If a strategy clears 10% on synthetic data it has found an
artefact of the cost model or the rules, not an edge.

---

## Results

**Synthetic data only.** The environment this was built in blocks PyPI and
every market-data host, so no real prices have been run through it yet. These
numbers characterise the machinery and the rulebook; they are not claims about
EURUSD. Re-run the commands above with `--source dukascopy` for real ones.

180 days of synthetic EURUSD, 10,000 attempts per row, position at 45% of the
margin cap, costs on:

| strategy | rulebook | pass rate | 95% cluster CI | DD fail | timeout | EV / $500 attempt |
|---|---|---|---|---|---|---|
| buy and hold | trailing equity | 0.38% | [0.12%, 0.74%] | 99.6% | 0.0% | −$481 |
| buy and hold | **static** | **10.62%** | **[7.69%, 13.47%]** | 82.1% | 7.3% | +$31 |
| fixed tp/sl | trailing equity | 0.40% | [0.26%, 0.54%] | 96.8% | 2.8% | −$480 |
| fixed tp/sl | static | 3.93% | [3.39%, 4.49%] | 75.0% | 21.0% | −$304 |
| momentum | trailing equity | 0.34% | [0.15%, 0.56%] | 99.6% | 0.1% | −$483 |
| momentum | static | 7.02% | [5.65%, 8.49%] | 85.8% | 7.2% | −$149 |

Three things stand out.

1. **Under a trailing floor, nothing survives.** Every zero-edge strategy
   lands near 0.4%, and ~99% of failures are drawdown breaches, not timeouts.
   The 5:1 ratio between the target and the limit is not the binding
   constraint; the ratchet is. Getting $500 ahead leaves you $300 of room from
   *there*, not $800.
2. **Under a static floor the picture changes completely.** Buy-and-hold at
   10.62% straddles breakeven — and that is not a strategy, it is the gambler's
   ruin bound (300/1800 = 16.7%, less what the 24-hour clock and the costs take
   out). The product is priced close to the fair value of pure variance under
   that rulebook.
3. **Trading more makes it worse.** Fixed TP/SL takes more entries than
   buy-and-hold and does worse under both rulebooks: it pays the round-turn
   friction repeatedly against a $300 limit. With $300 of room, roughly 23
   round turns at 45% size is the whole account, before the market moves at all.

### Parameter sweep

216 cells (6 take-profit × 6 stop-loss × 6 position sizes), 800 attempts each,
grid laid out in multiples of *the move that costs you the $300 limit* rather
than in round percentages that mean different things per instrument:

```
best in-sample pass rate     1.12%
best held-out pass rate      0.55%
selection bias               0.57%   <- how much the in-sample winner shrank
breakeven                   10.00%

ANY CORNER CLEARING BREAKEVEN?   NO
```

The sweep runs on an in-sample segment and re-runs its leaders on a **held-out
segment they never saw**. This matters: search 216 noisy cells and the best one
is biased upward simply for being the best of 216 — at 800 attempts near a 1%
pass rate that bias is comparable to the signal. Here the in-sample winner
halves on unseen data. The leaderboard ranks validated cells only, because
ranking a validated 2% against an unvalidated 3% would reinstate exactly the
bias the hold-out exists to remove. And "clearing breakeven" requires the
*lower bound* to be above 10%, not the point estimate.

---

## Layout

| module | |
|---|---|
| `data.py` | instruments and contract maths, `BarSeries`, Dukascopy tick fetch + decode, tick→bar resampling, synthetic generator, cache |
| `costs.py` | spread, commission, slippage, session widening, measured-spread preference |
| `engine.py` | one attempt: intrabar marking, floor/target, sizing, exposure cap, trade log, equity curve |
| `strategies.py` | `Strategy` base + the three baselines + a picklable `StrategySpec` |
| `montecarlo.py` | start sampling, Wilson and day-cluster intervals, EV, failure breakdown |
| `sweep.py` | grid search, hold-out validation, heatmap (matplotlib PNG or dependency-free SVG) |
| `cli.py` | `fetch` / `run` / `mc` / `sweep` / `demo` |

### Writing a strategy

```python
from propsim import Strategy, Order, SizingMode, CLOSE

class MyStrategy(Strategy):
    name = "mine"

    def on_start(self, ctx):        # once per attempt
        self.armed = True

    def on_bar(self, ctx):          # once per bar, after drawdown marking
        if ctx.position is not None:
            return None
        if ctx.close[ctx.i] > max(ctx.high[ctx.i - 20:ctx.i]):
            return Order(direction=1, sizing_mode=SizingMode.MARGIN_PCT,
                         size=0.5, take_profit_dollars=900,
                         stop_loss_dollars=150)
        return None                 # or CLOSE to flatten at this bar's close
```

Orders fill at the close of the bar that signalled them, so a strategy can
never see the outcome of its own entry. `test_strategy_cannot_see_the_future`
pins this down by mutating bars *after* the decision bar and asserting the
decision is unchanged.

Sizing modes: `UNITS` (lots/contracts), `NOTIONAL` (dollars), `ACCOUNT_PCT`
(fraction of equity as notional), `MARGIN_PCT` (fraction of equity as margin —
`size=0.75` saturates a 75% margin cap exactly, which is what makes it the
natural sweep axis). Exits can be percentages of price or dollars of P&L;
dollars are far more legible here because they are directly comparable to the
$300 limit — a $450 stop simply cannot be reached, the account dies first.

---

## Known limitations

- **Single symbol, single position.** The exposure cap is enforced per symbol,
  but the engine does not run a portfolio. The brief's rules are per-symbol, so
  this is faithful, but a multi-symbol variant would need a different engine.
- **No real data has been run through it.** See Results.
- **NQ/MNQ via Dukascopy is a CFD proxy**, flagged as such in
  `DUKASCOPY_SYMBOLS` and in the series `source`. Real futures need a paid
  feed.
- **Intrabar path is bounded, not known.** Marking the extremes is the best
  OHLC allows. Resampling ticks to 1-second bars (`--timeframe 1`) tightens the
  bound considerably and is worth doing before trusting a final number;
  the machinery already supports it.
- **Order queue position, partial fills and rejects are not modelled.** At the
  sizes the margin cap permits on liquid instruments this is a second-order
  effect, but it is not zero at the 21:00 UTC rollover.
