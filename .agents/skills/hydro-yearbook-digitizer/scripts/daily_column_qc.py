from __future__ import annotations

import re
import statistics
from collections.abc import Sequence


def merge_rule_runs(values: Sequence[float], maximum_gap: float = 5.0) -> tuple[float, ...]:
    """Collapse multiple detections of one thick printed horizontal rule."""
    groups: list[list[float]] = []
    for value in sorted(float(item) for item in values):
        if not groups or value - statistics.mean(groups[-1]) > maximum_gap:
            groups.append([value])
        else:
            groups[-1].append(value)
    return tuple(statistics.mean(group) for group in groups)


def leading_mean_rule_is_missing(day31_center: float, detected_top: float, ordinary_pitch: float) -> bool:
    return detected_top - day31_center > ordinary_pitch * 1.35


def choose_column_centers(
    base_centers: Sequence[float],
    observed_centers: Sequence[float],
    ordinary_pitch: float,
) -> tuple[tuple[float, ...], dict[str, float | int | bool | None]]:
    """Align one month to its own printed glyph rows without shifting blanks."""
    base = [float(value) for value in base_centers]
    observed = [float(value) for value in observed_centers]
    direct = False
    smoothness = None
    median_offset = None
    if len(observed) == len(base) and base:
        offsets = [observed[index] - base[index] for index in range(len(base))]
        median_offset = statistics.median(offsets)
        smoothness = max(
            (abs(offsets[index + 1] - offsets[index]) for index in range(len(offsets) - 1)),
            default=0.0,
        )
        direct = smoothness <= ordinary_pitch * 0.48 and abs(median_offset) <= ordinary_pitch * 0.65
    if direct:
        selected = observed
        matched = len(observed)
    else:
        rows, cols = len(base), len(observed)
        dp: list[list[tuple[int, float, tuple[tuple[int, int], ...]]]] = [
            [(0, 0.0, ()) for _ in range(cols + 1)] for _ in range(rows + 1)
        ]
        for i in range(1, rows + 1):
            for j in range(1, cols + 1):
                candidates = [dp[i - 1][j], dp[i][j - 1]]
                distance = abs(base[i - 1] - observed[j - 1])
                if distance <= ordinary_pitch * 0.25:
                    count, total, pairs = dp[i - 1][j - 1]
                    candidates.append((count + 1, total + distance, pairs + ((i - 1, j - 1),)))
                dp[i][j] = max(candidates, key=lambda item: (item[0], -item[1]))
        aligned = {base_index: observed[observed_index] for base_index, observed_index in dp[rows][cols][2]}
        selected = [aligned.get(index, expected) for index, expected in enumerate(base)]
        matched = len(aligned)
    return tuple(selected), {
        "observed_row_centers": len(observed),
        "component_aligned_rows": matched,
        "direct_sequence": direct,
        "direct_sequence_smoothness": smoothness,
        "direct_sequence_median_offset": median_offset,
    }


def remove_leading_rule_digit(primary_text: str, secondary_text: str) -> str | None:
    """Return the clean candidate when a vertical rule is read as leading 1."""
    primary = re.sub(r"\s+", "", str(primary_text))
    secondary = re.sub(r"\s+", "", str(secondary_text))
    for contaminated, clean in ((primary, secondary), (secondary, primary)):
        if contaminated.startswith("1") and contaminated[1:] == clean and clean:
            return clean
        try:
            if contaminated.startswith("1") and float(contaminated[1:]) == float(clean):
                return clean
        except ValueError:
            pass
    return None


def zero_mean_gridline_indices(values: Sequence[float | int | None], ink_ratios: Sequence[float]) -> tuple[int, ...]:
    """Flag false 10 values caused by a leading gridline in an all-zero month.

    Call this only after the printed monthly mean has independently been read
    as exactly zero. Blanks are never synthesized because only numeric cells
    with single-glyph-like ink coverage are returned.
    """
    numeric = [float(value) for value in values if isinstance(value, (int, float))]
    if not numeric or not set(numeric).issubset({0.0, 10.0}):
        return ()
    return tuple(
        index
        for index, (value, ink) in enumerate(zip(values, ink_ratios))
        if isinstance(value, (int, float)) and float(value) == 10.0 and 0.018 <= float(ink) <= 0.13
    )


def concentration_dry_actions(
    raw_texts: Sequence[str],
    direct_numeric: Sequence[bool],
    scores: Sequence[float] | None = None,
    ink_ratios: Sequence[float] | None = None,
) -> tuple[str, ...]:
    """Classify 河干 plus same-column ditto runs without inventing values."""
    dry_run = False
    actions: list[str] = []
    scores = scores or [1.0] * len(raw_texts)
    ink_ratios = ink_ratios or [1.0] * len(raw_texts)
    for raw, is_direct_numeric, score, ink in zip(raw_texts, direct_numeric, scores, ink_ratios):
        text = str(raw)
        if "干" in text or (
            any(marker in text for marker in ("河", "渠", "果", "集", "梁"))
            and any(suffix in text for suffix in ("十", "于"))
        ):
            dry_run = True
            actions.append("source_dry_marker")
        elif dry_run and is_direct_numeric and float(score) >= 0.75 and float(ink) >= 0.04:
            dry_run = False
            actions.append("numeric")
        elif dry_run:
            actions.append("source_dry_ditto")
        else:
            actions.append("keep")
    return tuple(actions)


def choose_statistic_by_daily_closure(
    daily_mean: float,
    primary: float | int | None,
    alternative: float | int | None,
    tolerance: float,
) -> str | None:
    """Select one independently read statistic only when exactly it closes."""
    primary_passes = isinstance(primary, (int, float)) and abs(float(daily_mean) - float(primary)) <= tolerance
    alternative_passes = isinstance(alternative, (int, float)) and abs(float(daily_mean) - float(alternative)) <= tolerance
    if primary_passes == alternative_passes:
        return None
    return "primary" if primary_passes else "alternative"


def normalize_repeated_decimal(text: str) -> str | None:
    """Normalize scan punctuation or one trailing OCR residue conservatively."""
    value = re.sub(r"\s+", "", str(text)).replace("，", ".").replace(",", ".")
    if re.fullmatch(r"-?\d+:\d+", value):
        return value.replace(":", ".")
    if re.fullmatch(r"\.0\.\d+", value):
        return value[1:]
    if re.fullmatch(r"\d+(?:\.\d+)?\.+", value):
        return value.rstrip(".")
    if match := re.fullmatch(r"(-?\d+(?:\.\d+)?)[A-Za-z]", value):
        return match.group(1)
    if match := re.fullmatch(r"(-?\d+(?:\.\d+)?)[°º]", value):
        return match.group(1)
    return None
