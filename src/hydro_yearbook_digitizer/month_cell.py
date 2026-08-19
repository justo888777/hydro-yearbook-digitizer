"""Narrow, auditable tolerances for inferred monthly-cell boundaries."""

from __future__ import annotations


def numeric_center_in_month_cell(
    x: float,
    x0: float,
    x1: float,
    *,
    left_tolerance_px: float = 3.0,
    right_inset_px: float = 2.0,
) -> bool:
    """Return whether a numeric OCR centre belongs to one month cell.

    A small left tolerance compensates for sub-pixel rule estimates; the strict
    right inset prevents borrowing a value from the next month.
    """
    if x1 <= x0:
        raise ValueError("month-cell bounds must increase")
    if left_tolerance_px < 0 or right_inset_px < 0:
        raise ValueError("edge tolerances must be non-negative")
    return x0 - left_tolerance_px <= x <= x1 - right_inset_px
