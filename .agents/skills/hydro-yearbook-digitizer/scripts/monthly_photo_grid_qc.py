"""Deterministic helpers for photographed monthly-summary spreads."""
from __future__ import annotations

import hashlib
import json
from typing import Mapping, Sequence


def fit_column_first_row_offsets(
    columns: Sequence[float],
    first_centers: Sequence[float | None],
    reference_y: float,
    row_step: float,
) -> list[float]:
    """Fit a perspective diagonal while rejecting a later-row first token."""

    if len(columns) != len(first_centers):
        raise ValueError("columns and first_centers must have the same length")
    if row_step <= 0:
        raise ValueError("row_step must be positive")
    points = [(float(x), float(y)) for x, y in zip(columns, first_centers) if y is not None]
    if not points:
        return [0.0] * len(columns)
    slopes = []
    for index, (x0, y0) in enumerate(points):
        for x1, y1 in points[index + 1:]:
            if x1 != x0 and abs(y1 - y0) <= 0.90 * row_step:
                slopes.append((y1 - y0) / (x1 - x0))
    slope = sorted(slopes)[len(slopes) // 2] if slopes else 0.0
    intercepts = sorted(y - slope * x for x, y in points)
    keep = max(1, (len(intercepts) + 1) // 2)
    intercept = intercepts[:keep][keep // 2]
    offsets = []
    for x, observed in zip(columns, first_centers):
        predicted = intercept + slope * float(x)
        if observed is not None and abs(float(observed) - predicted) <= 0.45 * row_step:
            predicted = float(observed)
        offsets.append(predicted - float(reference_y))
    return offsets


def geometry_fingerprint(rows: Sequence[Mapping[str, object]]) -> str:
    """Fingerprint only fields that define registered extraction crops."""

    geometry = [
        {
            "row": row.get("row"),
            "area": row.get("area_target"),
            "months": row.get("month_targets"),
            "annual": row.get("annual_target"),
        }
        for row in rows
    ]
    encoded = json.dumps(
        geometry, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
