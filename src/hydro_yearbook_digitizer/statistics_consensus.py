"""Strict helpers for merging independently reread statistics blocks."""

from __future__ import annotations

import math


def proposal_payload(table: dict, requested_key: str) -> list[dict]:
    """Return a completed model proposal list, including a valid empty list.

    An empty list means that the model completed but proposed no trustworthy
    cells.  It must cause downstream month rejection, not a pipeline crash and
    not be confused with a missing model result.
    """
    matches = [
        key
        for key, value in table.items()
        if key == requested_key
        and isinstance(value, dict)
        and "provisional_cell_proposals" in value
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one statistics proposal payload, got {matches}")
    proposals = table[matches[0]]["provisional_cell_proposals"]
    if not isinstance(proposals, list):
        raise ValueError("statistics provisional_cell_proposals must be a list")
    return proposals


def should_commit_statistics_trial(
    *,
    changed: bool,
    base_passed: bool,
    trial_passed_on_current_daily: bool,
    base_date_defects: int,
    trial_date_defects: int,
) -> bool:
    """Gate a whole-month statistics replacement against current daily data."""
    return bool(
        changed
        and trial_passed_on_current_daily
        and (not base_passed or trial_date_defects < base_date_defects)
    )


def finite_numeric_proposals(items: list[dict], key: str = "value") -> list[dict]:
    """Keep only finite numeric OCR proposals before ranking or optimization."""
    return [
        item for item in items
        if isinstance(item, dict)
        and isinstance(item.get(key), (int, float))
        and not isinstance(item.get(key), bool)
        and math.isfinite(float(item[key]))
    ]
