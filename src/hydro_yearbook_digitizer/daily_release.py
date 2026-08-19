from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Iterable


TARGET_TITLES = {
    "flow": ("逐日平均流量",),
    "sediment_rate": ("逐日平均悬移质输沙率", "逐日输沙率"),
    "concentration": ("逐日平均含沙量", "逐日含沙量"),
}
LOOKALIKE_TITLES = ("水位", "水温", "颗粒级配", "粒径", "降水量", "蒸发量", "对照表", "比较表")


def classify_printed_daily_title(title: str) -> str | None:
    """Route only explicitly printed target daily tables; reject lookalikes first."""
    compact = re.sub(r"\s+", "", str(title or ""))
    if any(marker in compact for marker in LOOKALIKE_TITLES):
        return None
    for variable, markers in TARGET_TITLES.items():
        if any(marker in compact for marker in markers):
            return variable
    return None


def leading_printed_serial(title: str) -> int | None:
    """Read the serial only from the leading title field, never units or notes."""
    match = re.match(r"^\s*(\d{1,3})(?=\s|[\u4e00-\u9fff])", str(title or ""))
    if not match:
        return None
    value = int(match.group(1))
    return value if 1 <= value <= 999 else None


def fixed_raw(reading: dict[str, Any] | None) -> str:
    """Return a fixed-cell OCR string when that optional pass actually exists."""
    fixed = ((reading or {}).get("fixed") or {})
    return str(fixed.get("raw") or "")


def retain_daily_vertical_rules(
    candidates: Iterable[float],
    image_width: float,
    *,
    outer_margin_ratio: float = 0.015,
) -> tuple[float, ...]:
    """Keep plausible table rules without dropping a true near-edge border."""
    lower = image_width * outer_margin_ratio
    upper = image_width * (1 - outer_margin_ratio)
    return tuple(sorted(float(value) for value in candidates if lower <= float(value) <= upper))


def has_complete_daily_columns(rules: Iterable[float]) -> bool:
    """A day-label column plus 12 month columns requires 14 vertical rules."""
    values = tuple(rules)
    return len(values) == 14 and all(left < right for left, right in zip(values, values[1:]))


def expanded_cell_bounds(
    bounds: tuple[int, int, int, int],
    image_size: tuple[int, int],
    *,
    pad_x: int = 3,
    pad_y: int = 5,
) -> tuple[int, int, int, int]:
    """Expand a registered cell to retain top/bottom strokes and clamp to image."""
    x0, y0, x1, y1 = bounds
    width, height = image_size
    return max(0, x0 - pad_x), max(0, y0 - pad_y), min(width, x1 + pad_x), min(height, y1 + pad_y)


def source_supports_negative_flow(
    value: Any,
    *,
    printed_monthly_mean: Any = None,
    printed_monthly_minimum: Any = None,
    visually_verified: bool = False,
) -> bool:
    """Allow a negative daily flow only when the same source table proves it."""
    if not isinstance(value, (int, float)) or value >= 0:
        return True
    return bool(
        visually_verified
        or (isinstance(printed_monthly_mean, (int, float)) and printed_monthly_mean < 0)
        or (isinstance(printed_monthly_minimum, (int, float)) and printed_monthly_minimum < 0)
    )


def three_significant_decimal_places(value: float) -> int:
    """Recover the displayed decimal places for a three-significant-digit value."""
    magnitude = abs(float(value))
    if magnitude == 0:
        return 0
    return max(0, 2 - math.floor(math.log10(magnitude)))


def _same(left: Any, right: Any) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=0, abs_tol=1e-12)
    return left == right and left is not None


@dataclass(frozen=True)
class CellReleaseDecision:
    status: str
    value: Any
    released: bool


def decide_cell_release(
    primary: Any,
    independent_values: Iterable[Any],
    *,
    geometry_blank: bool = False,
    printed_zero_stat: bool = False,
    visual_value: Any = None,
) -> CellReleaseDecision:
    """Apply the zero-unresolved gate to one registered daily cell."""
    if visual_value is not None:
        return CellReleaseDecision("visual_source_verified", visual_value, True)
    if primary is None and geometry_blank:
        return CellReleaseDecision("source_blank_geometry_verified", None, True)
    if any(_same(primary, value) for value in independent_values):
        return CellReleaseDecision("independent_engine_agreement", primary, True)
    if _same(primary, 0) and printed_zero_stat:
        return CellReleaseDecision("printed_zero_stat_and_ink_verified", 0, True)
    return CellReleaseDecision("blocked_pending_source_review", primary, False)
