from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "hydro-yearbook-digitizer" / "scripts" / "monthly_annual_qc.py"
SPEC = importlib.util.spec_from_file_location("monthly_annual_qc", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_day_weighted_mean_honours_leap_february() -> None:
    values = [0, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert MODULE.day_weighted_mean(values, 2020) > MODULE.day_weighted_mean(values, 2021)


def test_material_difference_requires_relative_and_absolute_failure() -> None:
    assert not MODULE.is_material_annual_difference([1] * 12, 1.01, 2024)
    assert MODULE.is_material_annual_difference([100] * 12, 1, 2024)


def test_printed_annual_check_does_not_impute_a_missing_month() -> None:
    result = MODULE.printed_annual_check([1] * 11 + [None], 1, 2024)
    assert result["status"] == "incomplete_source_period"
    assert result["calculated"] is None
