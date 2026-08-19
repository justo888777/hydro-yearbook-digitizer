"""Hard gates for page-local monthly-summary row and column registration."""
from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Mapping, Sequence


def validate_serial_slots(serials: Sequence[int], first: int, last: int) -> dict[str, object]:
    """Require the complete printed serial interval, including the last page row."""

    observed = [int(value) for value in serials]
    expected = list(range(int(first), int(last) + 1))
    missing = [value for value in expected if value not in observed]
    extra = [value for value in observed if value not in expected]
    duplicates = sorted({value for value in observed if observed.count(value) > 1})
    passed = observed == expected
    return {
        "status": "passed" if passed else "blocked",
        "expected_count": len(expected),
        "observed_count": len(observed),
        "missing": missing,
        "extra": extra,
        "duplicates": duplicates,
        "first_direct_required": first,
        "last_direct_required": last,
    }


def validate_sectioned_serial_slots(
    sections: Sequence[Sequence[int]],
    expected_ranges: Sequence[Sequence[int]],
) -> dict[str, object]:
    """Validate printed serials per visual section, allowing source resets.

    Some yearbooks restart at 1 under a new printed water-system heading on
    the same page. Treating all serials as one global sequence either drops
    valid rows as duplicates or assigns the later section to the earlier one.
    """

    if len(sections) != len(expected_ranges):
        return {
            "status": "blocked",
            "expected_sections": len(expected_ranges),
            "observed_sections": len(sections),
            "sections": [],
        }
    results = []
    for serials, bounds in zip(sections, expected_ranges):
        if len(bounds) != 2:
            raise ValueError("each expected range must contain [first, last]")
        results.append(validate_serial_slots(serials, int(bounds[0]), int(bounds[1])))
    return {
        "status": "passed" if all(item["status"] == "passed" for item in results) else "blocked",
        "expected_sections": len(expected_ranges),
        "observed_sections": len(sections),
        "sections": results,
    }


def validate_numeric_column_bands(
    bands: Sequence[Sequence[float]],
    expected_count: int,
    *,
    minimum_width_ratio: float = 0.65,
    maximum_width_ratio: float = 1.50,
) -> dict[str, object]:
    """Reject overlapping or implausible month/annual cell bands."""

    normalized = [(float(item[0]), float(item[1])) for item in bands]
    widths = [right - left for left, right in normalized]
    positive = all(width > 0 for width in widths)
    non_overlapping = all(normalized[index][1] <= normalized[index + 1][0] for index in range(len(normalized) - 1))
    local_median = median(widths) if widths and positive else 0.0
    width_ratios = [width / local_median for width in widths] if local_median else []
    plausible = all(minimum_width_ratio <= ratio <= maximum_width_ratio for ratio in width_ratios)
    passed = len(normalized) == int(expected_count) and positive and non_overlapping and plausible
    return {
        "status": "passed" if passed else "blocked",
        "expected_count": int(expected_count),
        "observed_count": len(normalized),
        "positive_widths": positive,
        "non_overlapping": non_overlapping,
        "width_ratios": width_ratios,
    }


def validate_row_baseline_mapping(
    left_by_serial: Mapping[int, float],
    right_by_serial: Mapping[int, float],
    *,
    maximum_step_ratio: float = 1.8,
) -> dict[str, object]:
    """Require one monotone right baseline per left serial; forbid fixed offsets."""

    serials = sorted(int(value) for value in left_by_serial)
    missing_right = [serial for serial in serials if serial not in right_by_serial]
    left = [float(left_by_serial[serial]) for serial in serials]
    right = [float(right_by_serial[serial]) for serial in serials if serial in right_by_serial]
    left_monotone = all(a < b for a, b in zip(left, left[1:]))
    right_monotone = len(right) == len(serials) and all(a < b for a, b in zip(right, right[1:]))
    right_steps = [b - a for a, b in zip(right, right[1:])]
    step_ratio = max(right_steps) / min(right_steps) if right_steps and min(right_steps) > 0 else 1.0
    passed = not missing_right and left_monotone and right_monotone and step_ratio <= maximum_step_ratio
    return {
        "status": "passed" if passed else "blocked",
        "serial_count": len(serials),
        "missing_right": missing_right,
        "left_monotone": left_monotone,
        "right_monotone": right_monotone,
        "right_step_ratio": step_ratio,
    }


def align_blockwise_row_baselines(
    left_blocks: Sequence[Sequence[float]],
    right_blocks: Sequence[Sequence[float]],
    *,
    maximum_missing_per_block: int = 1,
    maximum_residual_ratio: float = 0.45,
) -> dict[str, object]:
    """Align late-month rows inside visual blocks and expose missing slots.

    A right-page row can be absent because October--December and annual are
    all blank. A single global y offset then shifts every later row. This
    helper fits each visually separated block independently, assigns observed
    right baselines to normalized left positions, and reports the unprinted
    row slots instead of collapsing them.
    """

    if len(left_blocks) != len(right_blocks):
        return {
            "status": "blocked",
            "reason": "block_count_mismatch",
            "blocks": [],
        }
    block_results = []
    passed = True
    for block_index, (left_values, right_values) in enumerate(zip(left_blocks, right_blocks), start=1):
        left = [float(value) for value in left_values]
        right = [float(value) for value in right_values]
        if not left or len(right) > len(left) or len(left) - len(right) > maximum_missing_per_block:
            block_results.append({
                "block": block_index,
                "status": "blocked",
                "reason": "implausible_row_count",
                "left_count": len(left),
                "right_count": len(right),
            })
            passed = False
            continue
        if len(left) == 1:
            assignments = [0] if right else []
            residual_ratio = 0.0
        else:
            left_span = left[-1] - left[0]
            if left_span <= 0 or any(a >= b for a, b in zip(left, left[1:])) or any(a >= b for a, b in zip(right, right[1:])):
                block_results.append({"block": block_index, "status": "blocked", "reason": "non_monotone_block"})
                passed = False
                continue
            if len(right) <= 1:
                assignments = [min(range(len(left)), key=lambda index: abs(left[index] - left[len(left) // 2]))] if right else []
                residual_ratio = 0.0
            else:
                right_span = right[-1] - right[0]
                if right_span <= 0:
                    block_results.append({"block": block_index, "status": "blocked", "reason": "non_positive_right_span"})
                    passed = False
                    continue
                left_normalized = [(value - left[0]) / left_span for value in left]
                right_normalized = [(value - right[0]) / right_span for value in right]
                assignments = []
                residuals = []
                previous = -1
                for value in right_normalized:
                    candidates = range(previous + 1, len(left))
                    chosen = min(candidates, key=lambda index: abs(left_normalized[index] - value))
                    assignments.append(chosen)
                    residuals.append(abs(left_normalized[chosen] - value))
                    previous = chosen
                typical_step = median(
                    b - a for a, b in zip(left_normalized, left_normalized[1:])
                )
                residual_ratio = max(residuals, default=0.0) / typical_step if typical_step else 0.0
        missing = [index for index in range(len(left)) if index not in assignments]
        block_passed = residual_ratio <= maximum_residual_ratio and len(missing) <= maximum_missing_per_block
        passed = passed and block_passed
        block_results.append({
            "block": block_index,
            "status": "passed" if block_passed else "blocked",
            "left_count": len(left),
            "right_count": len(right),
            "right_to_left_indices": assignments,
            "missing_left_indices": missing,
            "residual_step_ratio": residual_ratio,
        })
    return {"status": "passed" if passed else "blocked", "blocks": block_results}


def expand_same_table_ditto(value: str | None, previous: str | None) -> str:
    """Expand a printed ditto mark, but preserve a genuinely empty source cell."""

    text = "" if value is None else str(value).strip()
    if text in {'"', "''", "“", "”", "〃"}:
        return "" if previous is None else str(previous)
    return text


def audit_unique_token_assignments(
    cells: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Reject one OCR glyph box assigned to more than one logical serial."""

    owners: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for cell in cells:
        token = cell.get("token")
        if not isinstance(token, Mapping):
            continue
        key = (
            round(float(token["left"]), 3),
            round(float(token["top"]), 3),
            round(float(token["right"]), 3),
            round(float(token["bottom"]), 3),
            str(token.get("raw", "")),
        )
        owners[key].append({"serial": int(cell["serial"]), "field": cell.get("field")})
    duplicates = [
        {"token": key, "cells": values}
        for key, values in owners.items()
        if len({int(value["serial"]) for value in values}) > 1
    ]
    return {
        "status": "passed" if not duplicates else "blocked",
        "duplicate_count": len(duplicates),
        "duplicates": duplicates,
    }
