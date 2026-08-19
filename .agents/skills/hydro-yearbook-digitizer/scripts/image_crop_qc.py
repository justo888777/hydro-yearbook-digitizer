"""Coordinate-only crop validation shared by OCR backends."""

from __future__ import annotations

from collections.abc import Sequence


def clamp_crop_bounds(
    width: int,
    height: int,
    bounds: Sequence[float],
    *,
    pad_x: int = 0,
    pad_y: int = 0,
) -> tuple[int, int, int, int] | None:
    """Return image-safe integer bounds, or ``None`` for an empty interval."""
    if width <= 0 or height <= 0 or len(bounds) != 4:
        return None
    x0, y0, x1, y1 = (int(value) for value in bounds)
    left = max(0, min(width, x0 - pad_x))
    right = max(0, min(width, x1 + pad_x))
    top = max(0, min(height, y0 - pad_y))
    bottom = max(0, min(height, y1 + pad_y))
    if right <= left or bottom <= top:
        return None
    return left, top, right, bottom
