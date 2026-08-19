"""Deterministic monthly/annual checks for printed hydrological summaries."""
from __future__ import annotations

from calendar import isleap
from typing import Sequence


MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def day_weighted_mean(values: Sequence[float | int], year: int) -> float:
    if len(values) != 12:
        raise ValueError("exactly twelve monthly values are required")
    days = list(MONTH_DAYS)
    if isleap(year):
        days[1] = 29
    return sum(float(value) * day for value, day in zip(values, days)) / sum(days)


def printed_annual_check(
    values: Sequence[float | int | None],
    printed_annual: float | int | None,
    year: int,
    *,
    relative_limit: float = 0.08,
    absolute_limit: float = 0.02,
) -> dict[str, float | bool | str | None]:
    """Compare a printed annual value without filling missing source months."""

    if len(values) != 12:
        raise ValueError("exactly twelve monthly values are required")
    if printed_annual is None:
        return {"status": "printed_annual_missing", "calculated": None, "difference": None, "material": False}
    if any(value is None for value in values):
        return {"status": "incomplete_source_period", "calculated": None, "difference": None, "material": False}
    calculated = day_weighted_mean([value for value in values if value is not None], year)
    difference = abs(calculated - float(printed_annual))
    relative = difference / max(abs(float(printed_annual)), 1e-6)
    material = difference > absolute_limit and relative > relative_limit
    return {
        "status": "needs_source_review" if material else "passed",
        "calculated": calculated,
        "difference": difference,
        "material": material,
    }


def is_material_annual_difference(
    values: list[float | int],
    printed_annual: float | int,
    year: int,
    *,
    relative_limit: float = 0.08,
    absolute_limit: float = 0.02,
) -> bool:
    difference = abs(day_weighted_mean(values, year) - float(printed_annual))
    relative = difference / max(abs(float(printed_annual)), 1e-6)
    return difference > absolute_limit and relative > relative_limit
