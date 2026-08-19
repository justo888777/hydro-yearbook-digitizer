"""Physical row ownership for a monthly table continued across two pages.

The left page usually contains station identity and early months, while the
right page contains late months and annual values. This module maps physical
row evidence before any OCR value is attached to a station row, so blank rows
and a missed serial glyph cannot shift later values.
"""

from __future__ import annotations

import math
import re
import statistics
from dataclasses import dataclass
from typing import Any


_INTEGER = re.compile(r"^\d{1,3}$")
_NUMBER = re.compile(r"^[+-]?\d+(?:\.\d+)?$")


def infer_expected_row_count(
    *,
    first_serial: int,
    observed_serials: list[int],
    physical_row_count: int | None,
    allowed_observed_excess: int = 2,
) -> tuple[int, dict[str, Any]]:
    """Prefer the measured physical row count over one noisy final serial."""
    if first_serial < 1:
        raise ValueError("first_serial must be positive")
    physical = int(physical_row_count or 0)
    if physical < 0:
        raise ValueError("physical_row_count cannot be negative")
    values = sorted({int(item) for item in observed_serials if int(item) >= first_serial})
    observed_count = values[-1] - first_serial + 1 if values else 0
    if physical:
        if observed_count <= physical + max(0, int(allowed_observed_excess)):
            chosen = max(physical, observed_count)
            source = "physical_rows_with_plausible_serial_extension" if chosen > physical else "physical_rows"
        else:
            chosen, source = physical, "physical_rows_discarded_implausible_terminal_serial"
    elif observed_count:
        chosen, source = observed_count, "observed_terminal_serial_no_physical_count"
    else:
        raise ValueError("No physical rows or valid serial observations are available")
    return chosen, {
        "first_serial": first_serial,
        "physical_row_count": physical or None,
        "observed_serial_max": values[-1] if values else None,
        "observed_implied_row_count": observed_count or None,
        "allowed_observed_excess": max(0, int(allowed_observed_excess)),
        "chosen_row_count": chosen,
        "source": source,
    }


def normal_number_text(value: object) -> str:
    """Normalize only common scan punctuation and numeric glyph variants."""
    text = str("" if value is None else value).strip().replace(" ", "")
    for source, target in (("，", "."), (",", "."), ("。", "."), ("．", "."), ("O", "0"), ("o", "0"), ("−", "-"), ("—", "-"), ("–", "-"), ("(", ""), (")", "")):
        text = text.replace(source, target)
    return text


def parse_number(value: object) -> float | int | None:
    text = normal_number_text(value)
    if not _NUMBER.fullmatch(text):
        return None
    parsed = float(text)
    return int(parsed) if math.isfinite(parsed) and parsed.is_integer() else (parsed if math.isfinite(parsed) else None)


def is_right_row_evidence(value: object) -> bool:
    return parse_number(value) is not None or normal_number_text(value) in {"-", "--"}


def _clusters(items: list[dict[str, Any]], tolerance: float) -> list[list[dict[str, Any]]]:
    rows: list[list[dict[str, Any]]] = []
    for item in sorted(items, key=lambda entry: float(entry["y"])):
        if not rows or float(item["y"]) - statistics.mean(float(entry["y"]) for entry in rows[-1]) > tolerance:
            rows.append([item])
        else:
            rows[-1].append(item)
    return rows


def right_page_row_groups(
    items: list[dict[str, Any]],
    *,
    x0: float,
    x1: float,
    height: float,
    y0: float | None = None,
    y1: float | None = None,
    tolerance: float | None = None,
) -> list[dict[str, Any]]:
    """Return physical right-page baselines from all late-month/annual fields."""
    tolerance = tolerance if tolerance is not None else max(12.0, min(20.0, 0.0062 * height))
    lower, upper = (0.14 * height if y0 is None else y0), (0.90 * height if y1 is None else y1)
    evidence = [
        item for item in items
        if x0 <= float(item["x"]) <= x1 and lower <= float(item["y"]) <= upper and is_right_row_evidence(item.get("text"))
    ]
    return [
        {"y": round(statistics.mean(float(item["y"]) for item in group), 4), "evidence_count": len(group)}
        for group in _clusters(evidence, float(tolerance))
    ]


@dataclass(frozen=True)
class SerialSlot:
    serial: int
    y: float
    method: str
    observed_serials: tuple[int, ...]


def _serial_rows(
    items: list[dict[str, Any]], *, x0: float, x1: float, y0: float, y1: float, tolerance: float
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for item in items:
        text = str(item.get("text", "")).strip()
        if not _INTEGER.fullmatch(text) or not (x0 <= float(item["x"]) <= x1 and y0 <= float(item["y"]) <= y1):
            continue
        serial = int(text)
        if 1 <= serial <= 300:
            candidates.append({"serial": serial, "y": float(item["y"])})
    return [
        {"y": statistics.mean(float(item["y"]) for item in group), "serials": tuple(sorted({int(item["serial"]) for item in group}))}
        for group in _clusters(candidates, tolerance)
    ]


def _interpolate(slots: list[SerialSlot | None], first_serial: int) -> list[SerialSlot]:
    known = [(index, slot) for index, slot in enumerate(slots) if slot is not None]
    if not known:
        raise ValueError("No readable serial-glyph baseline was found on the left page")
    steps = [
        (right.y - left.y) / (right_index - left_index)
        for (left_index, left), (right_index, right) in zip(known, known[1:])
        if right_index > left_index and right.y > left.y
    ]
    step = statistics.median(steps) if steps else 30.0
    output: list[SerialSlot] = []
    for index, slot in enumerate(slots):
        if slot is not None:
            output.append(slot)
            continue
        left = next(((i, value) for i, value in reversed(known) if i < index), None)
        right = next(((i, value) for i, value in known if i > index), None)
        if left and right:
            y = left[1].y + (right[1].y - left[1].y) * (index - left[0]) / (right[0] - left[0])
        elif left:
            y = left[1].y + step * (index - left[0])
        else:
            assert right is not None
            y = right[1].y - step * (right[0] - index)
        output.append(SerialSlot(first_serial + index, float(y), "interpolated_missing_serial_glyph", ()))
    return output


def reconstruct_left_serial_slots(
    items: list[dict[str, Any]],
    *,
    serial_x0: float,
    serial_x1: float,
    y0: float,
    y1: float,
    first_serial: int,
    last_serial: int,
    tolerance: float = 12.0,
) -> tuple[list[SerialSlot], dict[str, Any]]:
    """Reconstruct continuous logical rows while retaining missed serial slots."""
    if last_serial < first_serial:
        raise ValueError("Invalid serial interval")
    rows = _serial_rows(items, x0=serial_x0, x1=serial_x1, y0=y0, y1=y1, tolerance=tolerance)
    if not rows:
        raise ValueError("No serial OCR candidates available for current source page")
    expected = list(range(first_serial, last_serial + 1))
    n, m, inf = len(expected), len(rows), 10**9
    dp = [[inf] * (m + 1) for _ in range(n + 1)]
    choice: list[list[str | None]] = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            current = dp[i][j]
            if current >= inf:
                continue
            if i < n and j < m:
                exact = expected[i] in rows[j]["serials"]
                cost = 0.0 if exact else 0.56
                if current + cost < dp[i + 1][j + 1]:
                    dp[i + 1][j + 1], choice[i + 1][j + 1] = current + cost, "match"
            if i < n and current + 0.78 < dp[i + 1][j]:
                dp[i + 1][j], choice[i + 1][j] = current + 0.78, "skip_serial"
            if j < m and current + 1.20 < dp[i][j + 1]:
                dp[i][j + 1], choice[i][j + 1] = current + 1.20, "skip_observed"
    slots: list[SerialSlot | None] = [None] * n
    skipped_observed = 0
    i, j = n, m
    while i or j:
        action = choice[i][j]
        if action == "match":
            serials = tuple(int(value) for value in rows[j - 1]["serials"])
            method = "direct_serial_anchor" if expected[i - 1] in serials else "physical_row_bad_serial_glyph"
            slots[i - 1] = SerialSlot(expected[i - 1], float(rows[j - 1]["y"]), method, serials)
            i, j = i - 1, j - 1
        elif action == "skip_serial":
            i -= 1
        elif action == "skip_observed":
            skipped_observed, j = skipped_observed + 1, j - 1
        else:
            raise ValueError("Serial-slot alignment backtracking failed")
    completed = _interpolate(slots, first_serial)
    methods = [slot.method for slot in completed]
    return completed, {
        "expected_serial_first": first_serial,
        "expected_serial_last": last_serial,
        "expected_row_count": len(expected),
        "observed_serial_baselines": len(rows),
        "direct_serial_anchor_count": methods.count("direct_serial_anchor"),
        "bad_serial_glyph_baseline_count": methods.count("physical_row_bad_serial_glyph"),
        "interpolated_missing_serial_glyph_count": methods.count("interpolated_missing_serial_glyph"),
        "discarded_serial_noise_count": skipped_observed,
        "alignment_cost": round(float(dp[n][m]), 4),
    }


def align_right_baselines(
    slots: list[SerialSlot], right_groups: list[dict[str, Any]]
) -> tuple[dict[int, float], dict[str, Any]]:
    """Monotonically attach right-page evidence to left row slots."""
    if not slots or not right_groups:
        raise ValueError("Both left slots and right-page evidence are required")
    if len(slots) == len(right_groups):
        mapping = {slot.serial: float(group["y"]) for slot, group in zip(slots, right_groups)}
        return mapping, {"method": "ranked_all_right_fields", "left_row_count": len(slots), "right_evidence_row_count": len(right_groups), "unmatched_left_slots": [], "unmatched_right_groups": 0, "top_serial": slots[0].serial, "bottom_serial": slots[-1].serial}

    n, m, inf = len(slots), len(right_groups), 10**9
    left_first, left_last = slots[0].y, slots[-1].y
    right_first, right_last = float(right_groups[0]["y"]), float(right_groups[-1]["y"])
    left_span, right_span = max(left_last - left_first, 1.0), max(right_last - right_first, 1.0)
    dp = [[inf] * (m + 1) for _ in range(n + 1)]
    choice: list[list[str | None]] = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            current = dp[i][j]
            if current >= inf:
                continue
            if i < n and j < m:
                cost = abs((slots[i].y - left_first) / left_span - (float(right_groups[j]["y"]) - right_first) / right_span) * 4.0
                if current + cost < dp[i + 1][j + 1]:
                    dp[i + 1][j + 1], choice[i + 1][j + 1] = current + cost, "match"
            if i < n and current + 0.72 < dp[i + 1][j]:
                dp[i + 1][j], choice[i + 1][j] = current + 0.72, "skip_left"
            if j < m and current + 1.25 < dp[i][j + 1]:
                dp[i][j + 1], choice[i][j + 1] = current + 1.25, "skip_right"

    mapped: list[float | None] = [None] * n
    unmatched_right = 0
    i, j = n, m
    while i or j:
        action = choice[i][j]
        if action == "match":
            mapped[i - 1], i, j = float(right_groups[j - 1]["y"]), i - 1, j - 1
        elif action == "skip_left":
            i -= 1
        elif action == "skip_right":
            unmatched_right, j = unmatched_right + 1, j - 1
        else:
            raise ValueError("Right-page baseline alignment backtracking failed")
    known = [(index, value) for index, value in enumerate(mapped) if value is not None]
    if not known:
        raise ValueError("No right-page evidence could be aligned to a left slot")
    missing = [slots[index].serial for index, value in enumerate(mapped) if value is None]
    for index, value in enumerate(mapped):
        if value is not None:
            continue
        left = next(((i, y) for i, y in reversed(known) if i < index), None)
        right = next(((i, y) for i, y in known if i > index), None)
        if left and right:
            mapped[index] = left[1] + (right[1] - left[1]) * (index - left[0]) / (right[0] - left[0])
        elif left:
            mapped[index] = left[1] + (right_last - right_first) / max(n - 1, 1) * (index - left[0])
        else:
            assert right is not None
            mapped[index] = right[1] - (right_last - right_first) / max(n - 1, 1) * (right[0] - index)
    return {slot.serial: float(mapped[index]) for index, slot in enumerate(slots)}, {
        "method": "monotone_fallback_due_to_right_blank_rows",
        "left_row_count": n,
        "right_evidence_row_count": m,
        "unmatched_left_slots": missing,
        "unmatched_right_groups": unmatched_right,
        "top_serial": slots[0].serial,
        "bottom_serial": slots[-1].serial,
        "alignment_cost": round(float(dp[n][m]), 4),
    }
