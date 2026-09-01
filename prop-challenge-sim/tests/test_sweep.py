"""Tests for the grid search, the hold-out logic and the heatmap output."""

from __future__ import annotations

import os
import sys
import tempfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from propsim.costs import get_costs
from propsim.data import INSTRUMENTS, generate_synthetic
from propsim.engine import ChallengeConfig
from propsim.strategies import StrategySpec
from propsim.sweep import (
    SweepCell,
    SweepGrid,
    SweepResult,
    _viridis,
    auto_grid,
    run_sweep,
)

CFG = ChallengeConfig()
INST = INSTRUMENTS["EURUSD"]
COSTS = get_costs("EURUSD")
SPEC = StrategySpec("fixed_tp_sl", {"entries_per_day": 12})


def assert_close(a, b, tol=1e-6, what="value"):
    assert abs(a - b) <= tol, f"{what}: expected {b!r}, got {a!r}"


def _cell(pass_rate, validated=None, tp=0.01, sl=0.005, size=0.5):
    return SweepCell(tp=tp, sl=sl, size=size, pass_rate=pass_rate,
                     ci_low=max(0.0, pass_rate - 0.01),
                     ci_high=pass_rate + 0.01, n=1000, fail_drawdown=0.9,
                     fail_timeout=0.05, mean_trades=3.0, mean_costs=40.0,
                     ev=CFG.expected_value(pass_rate),
                     validated_pass_rate=validated,
                     validated_ci=(max(0.0, (validated or 0) - 0.01),
                                   (validated or 0) + 0.01)
                     if validated is not None else None,
                     validated_n=4000 if validated is not None else 0)


def _result(cells):
    return SweepResult(cells=cells, grid=SweepGrid((0.01,), (0.005,), (0.5,)),
                       config=CFG, strategy="test", symbol="EURUSD",
                       data_source="fixture", in_sample_days=60.0,
                       holdout_days=30.0)


# ---------------------------------------------------------------------------
# Grid construction
# ---------------------------------------------------------------------------

def test_auto_grid_scales_to_the_drawdown_limit():
    """Halve the limit and every level should halve with it -- the grid is
    laid out in units of "the move that costs you the account", not in round
    percentages that mean different things per instrument."""
    bars = generate_synthetic("EURUSD", days=10, seed=1)
    wide = auto_grid(bars, INST, ChallengeConfig(max_drawdown=600.0))
    tight = auto_grid(bars, INST, ChallengeConfig(max_drawdown=300.0))
    for a, b in zip(wide.sl_values, tight.sl_values):
        assert_close(a, 2 * b, 1e-9, "sl scales with the limit")


def test_auto_grid_dollar_axis_is_anchored_on_the_limit():
    bars = generate_synthetic("EURUSD", days=10, seed=1)
    g = auto_grid(bars, INST, CFG, axis="dollars")
    assert g.axis == "dollars"
    assert 300.0 in g.sl_values, "a stop exactly at the limit is on the grid"
    assert max(g.sl_values) > 300.0, "and some beyond it, which cannot fill"


def test_grid_enumerates_every_combination():
    g = SweepGrid((1, 2, 3), (4, 5), (6, 7, 8, 9))
    cells = list(g.cells())
    assert len(cells) == len(g) == 24
    assert len(set(cells)) == 24


# ---------------------------------------------------------------------------
# Selection bias handling
# ---------------------------------------------------------------------------

def test_leaderboard_prefers_validated_cells():
    """An unvalidated 5% must never outrank a validated 3%.

    Ranking them together would reinstate exactly the selection bias the
    hold-out exists to remove.
    """
    res = _result([_cell(0.05, tp=0.02), _cell(0.04, validated=0.03,
                                               tp=0.01)])
    top = res.top(5)
    assert len(top) == 1, "only validated cells are ranked once any exist"
    assert top[0].validated_pass_rate == 0.03


def test_leaderboard_falls_back_to_in_sample_without_validation():
    res = _result([_cell(0.05, tp=0.02), _cell(0.04, tp=0.01)])
    top = res.top(5)
    assert len(top) == 2
    assert_close(top[0].pass_rate, 0.05, 1e-12, "best in sample")


def test_clearing_breakeven_needs_the_lower_bound_not_the_point_estimate():
    """12% with an interval straddling 10% is not a finding."""
    straddling = _result([_cell(0.12, validated=0.12)])
    straddling.cells[0].validated_ci = (0.08, 0.16)
    assert straddling.any_cell_clears_breakeven() is False

    clear = _result([_cell(0.20, validated=0.20)])
    clear.cells[0].validated_ci = (0.15, 0.25)
    assert clear.any_cell_clears_breakeven() is True


def test_best_estimate_is_the_held_out_number_when_there_is_one():
    assert_close(_cell(0.09, validated=0.02).best_estimate, 0.02, 1e-12,
                 "held out wins")
    assert_close(_cell(0.09).best_estimate, 0.09, 1e-12, "in sample otherwise")


# ---------------------------------------------------------------------------
# End to end
# ---------------------------------------------------------------------------

def test_sweep_covers_the_grid_and_validates_the_leaders():
    bars = generate_synthetic("EURUSD", days=30, seed=3)
    grid = SweepGrid(tp_values=(0.0006, 0.0020), sl_values=(0.0002, 0.0006),
                     size_values=(0.45,))
    res = run_sweep(bars, SPEC, INST, COSTS, CFG, grid,
                    attempts_per_cell=60, holdout_frac=0.3,
                    validate_top=2, validation_attempts=60, seed=5)
    assert len(res.cells) == 4
    assert {(c.tp, c.sl) for c in res.cells} == {
        (0.0006, 0.0002), (0.0006, 0.0006),
        (0.0020, 0.0002), (0.0020, 0.0006)}
    assert len(res.validated_cells) == 2
    assert res.in_sample_days > res.holdout_days > 0
    for c in res.cells:
        assert c.n == 60
        assert 0.0 <= c.pass_rate <= 1.0
        assert_close(c.fail_drawdown + c.fail_timeout + c.pass_rate, 1.0,
                     1e-9, "outcomes partition")


def test_sweep_without_a_holdout_skips_validation():
    bars = generate_synthetic("EURUSD", days=20, seed=4)
    grid = SweepGrid((0.002,), (0.0006,), (0.45,))
    res = run_sweep(bars, SPEC, INST, COSTS, CFG, grid,
                    attempts_per_cell=40, holdout_frac=0.0, seed=6)
    assert res.validated_cells == []
    assert res.holdout_days == 0.0
    assert "in-sample only" in res.report()


def test_report_answers_the_headline_question():
    bars = generate_synthetic("EURUSD", days=25, seed=9)
    grid = SweepGrid((0.002,), (0.0006,), (0.3, 0.6))
    res = run_sweep(bars, SPEC, INST, COSTS, CFG, grid,
                    attempts_per_cell=40, holdout_frac=0.3, validate_top=1,
                    validation_attempts=40, seed=8)
    text = res.report()
    assert "ANY CORNER CLEARING BREAKEVEN?" in text
    assert "breakeven" in text


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def test_svg_heatmap_is_well_formed_and_has_a_cell_per_combination():
    cells = [_cell(0.01 * k, tp=tp, sl=sl, size=size)
             for k, (tp, sl, size) in enumerate(
                 SweepGrid((0.001, 0.002), (0.0005, 0.001), (0.3, 0.6)).cells())]
    res = SweepResult(cells=cells,
                      grid=SweepGrid((0.001, 0.002), (0.0005, 0.001),
                                     (0.3, 0.6)),
                      config=CFG, strategy="test", symbol="EURUSD",
                      data_source="fixture")
    with tempfile.TemporaryDirectory() as d:
        path = res.heatmap(os.path.join(d, "hm.svg"))
        assert path.endswith(".svg")
        root = ET.parse(path).getroot()
        rects = [e for e in root.iter()
                 if e.tag.endswith("rect") and e.get("stroke")]
        assert len(rects) == 8, f"one rect per cell, got {len(rects)}"


def test_png_request_falls_back_to_svg_without_matplotlib():
    cells = [_cell(0.02)]
    res = SweepResult(cells=cells, grid=SweepGrid((0.01,), (0.005,), (0.5,)),
                      config=CFG, strategy="t", symbol="EURUSD",
                      data_source="fixture")
    with tempfile.TemporaryDirectory() as d:
        path = res.heatmap(os.path.join(d, "hm.png"))
        assert os.path.exists(path)
        assert path.endswith(".png") or path.endswith(".svg")


def test_csv_export_lists_every_cell():
    import csv
    cells = [_cell(0.01, tp=0.001), _cell(0.02, validated=0.005, tp=0.002)]
    res = _result(cells)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "cells.csv")
        res.to_csv(path)
        with open(path) as fh:
            rows = list(csv.DictReader(fh))
    assert len(rows) == 2
    assert rows[0]["validated_pass_rate"] in ("0.005", "")


def test_colour_ramp_spans_the_range():
    assert _viridis(0.0) == "#440154"
    assert _viridis(1.0) == "#fde725"
    assert _viridis(-5.0) == _viridis(0.0), "clamped below"
    assert _viridis(5.0) == _viridis(1.0), "clamped above"
