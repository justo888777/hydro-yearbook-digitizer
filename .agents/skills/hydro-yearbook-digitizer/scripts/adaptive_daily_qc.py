"""Reusable geometry and statistic helpers for photographed daily matrices.

The caller owns OCR inference. These helpers do not fabricate cell values;
they reconstruct month geometry and label a statistic check.
"""

from __future__ import annotations

import math
import re
from statistics import median

import cv2
import numpy as np


NUMERIC = re.compile(r"^\d+(?:\.\d+)?$")


def physical_vertical_rules(image: np.ndarray) -> list[int] | None:
    """Return a plausible 13-boundary monthly grid or ``None``."""
    ink = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    rules = cv2.morphologyEx(ink, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 180)))
    indexes = np.flatnonzero((rules > 0).sum(axis=0) > 150)
    groups: list[list[int]] = []
    for index in indexes:
        if not groups or index > groups[-1][-1] + 1:
            groups.append([int(index)])
        else:
            groups[-1].append(int(index))
    raw = [round(sum(group) / len(group)) for group in groups]
    selected = [raw[0]] if raw else []
    for rule in raw[1:]:
        if rule - selected[-1] >= 100:
            selected.append(rule)
    if len(selected) == 14:
        selected = selected[-13:]
    if len(selected) == 12:
        gaps = [right - left for left, right in zip(selected, selected[1:])]
        step = median(gaps)
        if selected[1] - selected[0] > 1.8 * step:
            slope, intercept = np.polyfit(np.arange(2, 13), np.asarray(selected[1:], dtype=float), 1)
            selected = [round(intercept + slope * index) for index in range(2)] + selected[1:]
        elif max(gaps) <= 1.25 * step:
            selected.append(round(selected[-1] + step))
    if 7 <= len(selected) < 13:
        indexes = np.arange(13 - len(selected), 13)
        slope, intercept = np.polyfit(indexes, np.asarray(selected, dtype=float), 1)
        selected = [round(intercept + slope * index) for index in range(13)]
    if len(selected) != 13 or selected[0] < 0 or selected[-1] > image.shape[1] + 80:
        return None
    return selected


def numeric_text_centre_rules(tokens: list[tuple[str, float]], width: int) -> list[int]:
    """Derive 13 boundaries from `(text, x_center)` OCR pairs."""
    values = np.asarray(
        [x for text, x in tokens if NUMERIC.fullmatch(text.strip()) and width * 0.08 <= x <= width * 0.99],
        dtype=float,
    )
    if len(values) < 120:
        raise ValueError("insufficient numeric text centres")
    centres = np.quantile(values, np.linspace(0.04, 0.96, 12))
    for _ in range(80):
        nearest = np.abs(values[:, None] - centres[None, :]).argmin(axis=1)
        updated = np.asarray(
            [values[nearest == index].mean() if np.any(nearest == index) else centres[index] for index in range(12)]
        )
        if np.allclose(updated, centres, atol=0.05):
            centres = updated
            break
        centres = updated
    centres.sort()
    gaps = np.diff(centres)
    if np.any(gaps < width * 0.025):
        raise ValueError("unstable month-band centres")
    return [
        max(0, round(centres[0] - gaps[0] / 2)),
        *(round((left + right) / 2) for left, right in zip(centres, centres[1:])),
        min(width, round(centres[-1] + gaps[-1] / 2)),
    ]


def monthly_mean_validation(values: list[float], printed: float, precision: int) -> str | None:
    """Return the explicit source-compatible validation mode, else ``None``."""
    calculated = sum(values) / len(values)
    unit = 10 ** (-precision)
    if abs(calculated - printed) <= 0.5 * unit + 1e-12:
        return "rounded"
    if precision and math.trunc(calculated / unit) * unit == printed:
        return "truncated"
    if precision and abs(calculated - printed) <= unit + 1e-12:
        return "source_precision_bound"
    return None
