"""Conservative geometry helpers for photographed 12-month matrices."""

from __future__ import annotations

from statistics import median


def rule_anchored_daily_rows(
    strong_rules: list[float] | tuple[float, ...],
    *,
    local_top: float,
    statistics_top: float,
    measured_cell_bounds: list[tuple[float, float, float, float]] | tuple[tuple[float, float, float, float], ...] | None = None,
) -> tuple[float, ...]:
    """Address 31 daily rows from the month column's physical rule pair.

    A complete, physically valid set of month-local cell boxes is the primary
    address system.  The rule projection is only the fallback.  This prevents
    a global affine model from moving October--December values across the
    printed five-day spacer rows.
    """
    top = float(local_top)
    bottom = float(statistics_top)
    if bottom <= top:
        raise ValueError("statistics top must be below the local header")
    if measured_cell_bounds:
        centres = tuple(
            (float(bounds[1]) + float(bounds[3])) / 2.0
            for bounds in measured_cell_bounds
        )
        if len(centres) == 31 and top < centres[0] < centres[-1] < bottom:
            gaps = tuple(right - left for left, right in zip(centres, centres[1:]))
            ordinary = tuple(
                gap for index, gap in enumerate(gaps)
                if index not in {4, 9, 14, 19, 24}
            )
            pitch = median(ordinary)
            spacers = tuple(gaps[index] for index in (4, 9, 14, 19, 24))
            ordinary_valid = all(pitch * 0.55 <= gap <= pitch * 1.45 for gap in ordinary)
            spacers_valid = all(pitch * 1.15 <= gap <= pitch * 2.80 for gap in spacers)
            edges_valid = (
                pitch * 0.20 <= centres[0] - top <= pitch * 2.50
                and pitch * 0.20 <= bottom - centres[-1] <= pitch * 2.50
            )
            if pitch > 0 and ordinary_valid and spacers_valid and edges_valid:
                return centres
    upper_limit = top + max(80.0, (bottom - top) * 0.40)
    candidates = sorted(
        float(value)
        for value in strong_rules
        if top - 90.0 <= float(value) <= upper_limit
    )
    header_bottom = max(candidates, default=top)
    pitch = (bottom - header_bottom) / 36.0
    if not 9.0 <= pitch <= 55.0:
        raise ValueError("ruled daily pitch is not physically plausible")
    first = header_bottom + pitch * 0.72
    return tuple(
        first + pitch * ((day - 1) + min(5, (day - 1) // 5))
        for day in range(1, 32)
    )


def repair_daily_statistics_lines(
    lines: list[float],
    *,
    header_bottom: float,
    image_height: float,
    expected_body_ratio: float,
) -> tuple[float, ...]:
    """Select the footer top from a book-calibrated daily-body span."""
    ordered = tuple(sorted(set(float(value) for value in lines)))
    if len(ordered) < 7:
        return ordered
    gaps = [right - left for left, right in zip(ordered, ordered[1:])]
    reference = median(gaps[1:])
    if gaps[0] <= max(50.0, reference * 2.5):
        return ordered
    candidates = []
    for index, line in enumerate(ordered):
        if len(ordered[index:]) < 6:
            continue
        ratio = (line - float(header_bottom)) / float(image_height)
        if 0.44 <= ratio <= 0.60:
            candidates.append((abs(ratio - float(expected_body_ratio)), index))
    if candidates:
        _, index = min(candidates)
        return ordered[index:]
    return ordered


def complete_daily_statistics_rules(lines: list[float]) -> tuple[float, ...]:
    """Reconstruct missing rules among the first five footer rows."""
    ordered = tuple(sorted(set(float(value) for value in lines)))
    if len(ordered) < 3:
        return ordered
    gaps = [right - left for left, right in zip(ordered, ordered[1:])]
    regular = [gap for gap in gaps if 15 <= gap <= 45]
    if not regular:
        return ordered
    pitch = median(regular)
    rebuilt = [ordered[0]]
    cursor = ordered[0]
    for boundary in ordered[1:]:
        gap = boundary - cursor
        if gap < pitch * 0.55:
            continue
        remaining = 6 - len(rebuilt)
        if remaining <= 0:
            break
        steps = min(max(1, round(gap / pitch)), remaining)
        step = gap / steps
        rebuilt.extend(cursor + step * part for part in range(1, steps + 1))
        cursor = boundary
        if len(rebuilt) >= 6:
            break
    if len(rebuilt) != 6:
        return ordered
    return tuple([*rebuilt, *(value for value in ordered if value > rebuilt[-1] + 2)])


def validate_daily_row_span(
    rows: list[float] | tuple[float, ...], body_top: float, body_bottom: float
) -> float:
    """Return row coverage and reject compressed or overextended 1-31 fits."""
    if len(rows) != 31:
        raise ValueError("daily row fit must contain exactly 31 rows")
    body = float(body_bottom) - float(body_top)
    if body <= 0:
        raise ValueError("daily body bottom must be below its top")
    coverage = (float(rows[-1]) - float(rows[0])) / body
    if not 0.78 <= coverage <= 1.02:
        raise ValueError(f"daily rows cover only {coverage:.3f} of the body")
    return coverage


def select_daily_rule_window(
    rule_candidates: list[float],
    *,
    strengths: dict[float, float] | None = None,
    diagonal_scores: dict[tuple[float, float], float] | None = None,
    rule_count: int = 14,
) -> tuple[float, ...]:
    """Select the true day-plus-twelve-month rule window.

    A page edge or spine line can be longer than every table rule.  Evaluate
    every contiguous 14-rule window by lattice regularity and line-strength
    outliers.  When available, the printed diagonal in the day/month header
    cell is the semantic anchor for the first interval.

    Exactly fourteen detections are not automatically trustworthy: one page
    edge plus one missing outer table rule produces the same count.  Replace
    that edge only when the remaining thirteen gaps form a regular suffix or
    prefix.
    """
    ordered = sorted(set(float(value) for value in rule_candidates))
    if len(ordered) < rule_count:
        raise ValueError("fewer than 14 vertical-rule candidates")
    strengths = strengths or {}
    diagonal_scores = diagonal_scores or {}
    if len(ordered) == rule_count:
        gaps = [right - left for left, right in zip(ordered, ordered[1:])]
        pitch = median(gaps)
        if gaps[0] > pitch * 1.45 and max(gaps[1:]) < pitch * 1.25:
            return tuple(ordered[1:] + [ordered[-1] + pitch])
        if gaps[-1] > pitch * 1.45 and max(gaps[:-1]) < pitch * 1.25:
            return tuple([ordered[0] - pitch] + ordered[:-1])
        return tuple(ordered)

    windows = []
    for start in range(len(ordered) - rule_count + 1):
        values = ordered[start : start + rule_count]
        gaps = [right - left for left, right in zip(values, values[1:])]
        pitch = median(gaps)
        spacing_error = median(abs(gap - pitch) for gap in gaps) / max(pitch, 1.0)
        max_spacing_error = max(abs(gap - pitch) for gap in gaps) / max(pitch, 1.0)
        window_strengths = [float(strengths.get(value, 1.0)) for value in values]
        middle_strength = median(window_strengths) or 1.0
        outlier_ratio = max(window_strengths) / middle_strength
        diagonal = float(diagonal_scores.get((values[0], values[1]), 0.0))
        windows.append((values, spacing_error, max_spacing_error, outlier_ratio, diagonal))
    regular = [window for window in windows if window[2] <= 0.25]
    diagonal = max(regular or windows, key=lambda window: window[4])
    first_gap = diagonal[0][1] - diagonal[0][0]
    if diagonal[4] >= first_gap * 0.45:
        return tuple(diagonal[0])
    selected = min(windows, key=lambda window: (window[1], window[3]))
    if selected[2] > 0.40:
        raise ValueError("no regular 14-rule daily-table window")
    return tuple(selected[0])


def fit_vertical_rule_lattice(
    rule_candidates: list[float],
    image_width: float,
    horizontal_edges: tuple[float, float] | None = None,
    rule_count: int = 14,
) -> tuple[float, ...]:
    """Fit an ordered vertical-rule lattice despite faint or missing rules.

    ``horizontal_edges`` should be the left/right extent of the widest long
    printed horizontal rule.  It disambiguates a missing left edge from a
    missing right edge; without that anchor, both hypotheses can support the
    same number of detected vertical rules.
    """
    candidates = sorted(set(float(value) for value in rule_candidates))
    if len(candidates) < max(6, rule_count - 4):
        raise ValueError("insufficient vertical-rule candidates")
    width = float(image_width)
    if width <= 0:
        raise ValueError("image width must be positive")
    tolerance = max(7.0, width * 0.0055)
    best: tuple[tuple[float, ...], list[float]] | None = None
    for left_position, left in enumerate(candidates):
        for right in candidates[left_position + 1 :]:
            for index_gap in range(1, rule_count):
                step = (right - left) / index_gap
                if not width * 0.045 <= step <= width * 0.09:
                    continue
                for left_index in range(rule_count - index_gap):
                    origin = left - left_index * step
                    end = origin + (rule_count - 1) * step
                    if origin < 0 or end >= width:
                        continue
                    expected = [origin + index * step for index in range(rule_count)]
                    matched: dict[int, float] = {}
                    for value in candidates:
                        index = min(range(rule_count), key=lambda item: abs(expected[item] - value))
                        distance = abs(expected[index] - value)
                        if distance <= tolerance and (index not in matched or distance < matched[index]):
                            matched[index] = distance
                    support = len(matched)
                    if support < max(6, rule_count - 4):
                        continue
                    missing = [index for index in range(rule_count) if index not in matched]
                    internal_missing = sum(min(matched) < index < max(matched) for index in missing)
                    edge_error = (
                        abs(origin - horizontal_edges[0]) + abs(end - horizontal_edges[1])
                        if horizontal_edges else 0.0
                    )
                    rank = (-support, internal_missing, edge_error, sum(matched.values()), -step)
                    if best is None or rank < best[0]:
                        best = (rank, expected)
    if best is None:
        raise ValueError("vertical rules do not form a plausible lattice")
    expected = best[1]
    fitted = []
    for point in expected:
        nearest = min(candidates, key=lambda value: abs(value - point))
        fitted.append(nearest if abs(nearest - point) <= tolerance else point)
    if any(right <= left for left, right in zip(fitted, fitted[1:])):
        raise ValueError("fitted vertical lattice is not ordered")
    return tuple(fitted)


def template_day_rows(body_top: float, body_bottom: float) -> tuple[float, ...]:
    """Project the printed 1-31 pattern when too few day glyphs survive."""
    height = float(body_bottom) - float(body_top)
    if height <= 0:
        raise ValueError("daily body bottom must be below its top")
    first = float(body_top) + max(10.0, height * 0.0274)
    last = float(body_bottom) - max(10.0, height * 0.0256)
    gap_ratio = 0.88
    step = (last - first) / (30 + 5 * gap_ratio)
    if step <= 0:
        raise ValueError("daily body is too short for 31 printed rows")
    return tuple(
        first + step * (day - 1) + step * gap_ratio * min((day - 1) // 5, 5)
        for day in range(1, 32)
    )


def select_printed_day_rows(component_centers: list[float], image_height: float) -> tuple[float, ...]:
    """Fit the ordered 1-31 layout despite missed labels and footer noise.

    The six printed groups are 1-5, 6-10, 11-15, 16-20, 21-25, and 26-31.
    Only the first five group boundaries have a wider spacer.  A robust fit
    may reconstruct a few missed labels, but it requires at least 24 observed
    row bands and rejects header/footer bands that do not match the pattern.
    """
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("numpy is required for printed-day fitting") from exc
    ordered = np.asarray(sorted(set(float(value) for value in component_centers)), dtype=float)
    if len(ordered) < 24:
        raise ValueError("fewer than 24 printed day-row bands")
    expected = np.asarray(
        [(day - 1) + min((day - 1) // 5, 5) for day in range(1, 32)], dtype=float
    )
    gaps = np.diff(ordered)
    ordinary = gaps[(gaps >= image_height * 0.008) & (gaps <= image_height * 0.040)]
    if len(ordinary) < 10:
        raise ValueError("printed day-row pitch is not recoverable")
    pitch0 = float(np.median(ordinary))
    best: tuple[int, float, float, float] | None = None
    for pitch in np.linspace(pitch0 * 0.82, pitch0 * 1.18, 73):
        tolerance = max(5.0, pitch * 0.32)
        for candidate in ordered:
            for unit in expected:
                intercept = float(candidate - pitch * unit)
                predicted = intercept + pitch * expected
                distances = np.min(abs(predicted[:, None] - ordered[None, :]), axis=1)
                matched = distances <= tolerance
                count = int(np.sum(matched))
                residual = float(np.mean(distances[matched])) if count else float("inf")
                score = residual + abs(pitch - pitch0) * 0.02
                if best is None or count > best[0] or (count == best[0] and score < best[1]):
                    best = (count, score, intercept, float(pitch))
    if best is None or best[0] < 24:
        raise ValueError("day-row bands do not form a reliable 1-31 pattern")
    _, _, intercept, pitch = best
    for _ in range(2):
        predicted = intercept + pitch * expected
        tolerance = max(5.0, pitch * 0.32)
        nearest = np.argmin(abs(predicted[:, None] - ordered[None, :]), axis=1)
        distances = abs(ordered[nearest] - predicted)
        matched = distances <= tolerance
        if int(np.sum(matched)) < 24:
            raise ValueError("day-row fit lost too many observed labels")
        pitch, intercept = np.polyfit(expected[matched], ordered[nearest[matched]], 1)
    predicted = intercept + pitch * expected
    tolerance = max(5.0, pitch * 0.32)
    rows = []
    for value in predicted:
        nearest = float(ordered[int(np.argmin(abs(ordered - value)))])
        rows.append(nearest if abs(nearest - value) <= tolerance else float(value))
    if rows[0] < -image_height * 0.05 or rows[-1] > image_height * 0.90:
        raise ValueError("fitted day rows fall outside the daily body")
    return tuple(rows)


def fit_printed_day_sequence_boxes(
    boxes: list[dict[str, object]],
    header_floor: float,
    statistics_top: float,
) -> tuple[tuple[float, ...], float]:
    """Recover 1--31 baselines from vertically merged OCR detection boxes.

    A recognizer may merge ``1..5`` or ``1..10`` into one tall token and may
    split later five-day blocks.  The printed box geometry remains useful even
    when its text is imperfect.  The first and final block provide hard end
    anchors; all other boxes refine the known five-day lattice.
    """
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("numpy is required for day-sequence fitting") from exc
    prepared = []
    for box in boxes:
        text = str(box.get("text", ""))
        digits = "".join(character for character in text if character.isdigit())
        top = float(box["top"])
        bottom = float(box["bottom"])
        if digits and bottom > top:
            prepared.append({
                "x": float(box["x"]),
                "top": top,
                "bottom": bottom,
                "height": bottom - top,
                "center": (top + bottom) / 2,
                "digits": digits,
            })
    first_options = [row for row in prepared if row["digits"].startswith("12345")]
    if not first_options:
        raise ValueError("printed first-day block is missing")
    first = min(first_options, key=lambda row: row["center"])
    later = [row for row in prepared if row["center"] > first["center"]]
    if not later:
        raise ValueError("printed final-day block is missing")
    last = max(later, key=lambda row: row["bottom"])
    first_count = 10 if first["digits"].startswith("1234567890") else 5
    first_center = first["top"] + first["height"] / (2 * first_count)
    last_center = last["bottom"] - last["height"] / 12.0
    step = (last_center - first_center) / 30.0
    if not 8.0 <= step <= 45.0:
        raise ValueError("printed day-sequence pitch is implausible")
    rows = tuple(first_center + step * index for index in range(31))
    if rows[0] <= float(header_floor) or rows[-1] >= float(statistics_top) + 12.0:
        raise ValueError("printed day-sequence boxes leave the daily body")
    reference_x = float(np.median([row["x"] for row in prepared]))
    return rows, reference_x


def interpolate_calendar_row_surface(
    reference_x: float,
    reference_rows: tuple[float, ...],
    complete_month_rows: dict[int, tuple[float, ...]],
    month_centers: dict[int, float],
    month_day_counts: dict[int, int],
) -> dict[int, tuple[float, ...]]:
    """Interpolate daily baselines without letting short-month tails vote.

    Only calendar-valid rows from a donor month participate.  Missing 29--31
    rows are extrapolated from the target month's own recent pitch, so a
    February or 30-day donor cannot move the next month's final rows.
    """
    if len(reference_rows) != 31:
        raise ValueError("reference day column must contain 31 rows")
    output: dict[int, tuple[float, ...]] = {}
    for month in range(1, 13):
        target_x = float(month_centers[month])
        valid_days = int(month_day_counts[month])
        values = []
        for day_index in range(valid_days):
            donors = [(float(reference_x), float(reference_rows[day_index]))]
            for donor_month, rows in complete_month_rows.items():
                if day_index < int(month_day_counts[donor_month]):
                    donors.append((float(month_centers[donor_month]), float(rows[day_index])))
            donors.sort()
            left = [row for row in donors if row[0] <= target_x]
            right = [row for row in donors if row[0] >= target_x]
            if left and right:
                lo, hi = left[-1], right[0]
            elif len(left) >= 2:
                lo, hi = left[-2], left[-1]
            elif len(right) >= 2:
                lo, hi = right[0], right[1]
            elif values:
                recent = [b - a for a, b in zip(values[-6:], values[-5:])]
                values.append(values[-1] + (sum(recent) / len(recent)))
                continue
            else:
                raise ValueError(f"month {month} has no row-surface donors")
            if hi[0] == lo[0]:
                value = lo[1]
            else:
                slope = max(-0.12, min(0.12, (hi[1] - lo[1]) / (hi[0] - lo[0])))
                value = lo[1] + slope * (target_x - lo[0])
            values.append(float(value))
        recent = [b - a for a, b in zip(values[-6:], values[-5:])]
        pitch = sum(recent) / len(recent) if recent else 20.0
        while len(values) < 31:
            values.append(values[-1] + pitch)
        if any(right <= left for left, right in zip(values, values[1:])):
            raise ValueError(f"month {month} row surface is not ordered")
        output[month] = tuple(values)
    return output


def infer_january_interval_from_month_labels(
    month_label_centers: dict[int, float], boundaries: list[float] | tuple[float, ...]
) -> int:
    """Return 0 or 1 for the interval containing January.

    Photographed tables may lose the outer day-column rule.  Month labels are
    semantic evidence for the column identity, whereas a regular rule lattice
    alone cannot tell whether its first interval is January or the day column.
    """
    if len(boundaries) < 13:
        raise ValueError("at least thirteen ordered boundaries are required")
    if any(right <= left for left, right in zip(boundaries, boundaries[1:])):
        raise ValueError("boundaries must be strictly ordered")
    votes: list[int] = []
    for month, center in month_label_centers.items():
        if not 1 <= int(month) <= 12:
            continue
        interval = next(
            (
                index for index, (left, right) in enumerate(
                    zip(boundaries, boundaries[1:])
                )
                if left < float(center) < right
            ),
            None,
        )
        if interval is None:
            continue
        start = interval - (int(month) - 1)
        if start in {0, 1}:
            votes.append(start)
    if not votes or len(set(votes)) != 1:
        raise ValueError("month labels do not prove one January interval")
    return votes[0]


def project_rows_between_sloped_boundaries(
    reference_rows: list[float] | tuple[float, ...],
    reference_x: float,
    target_x: float,
    header_curve: tuple[float, float],
    statistics_curve: tuple[float, float],
) -> tuple[float, ...]:
    """Transfer daily rows through physical header/statistics line curves."""
    if len(reference_rows) != 31:
        raise ValueError("the reference daily surface must contain 31 rows")
    header_slope, header_intercept = map(float, header_curve)
    statistics_slope, statistics_intercept = map(float, statistics_curve)
    reference_header = header_slope * reference_x + header_intercept
    reference_statistics = statistics_slope * reference_x + statistics_intercept
    target_header = header_slope * target_x + header_intercept
    target_statistics = statistics_slope * target_x + statistics_intercept
    reference_span = reference_statistics - reference_header
    target_span = target_statistics - target_header
    if reference_span <= 0 or target_span <= 0:
        raise ValueError("daily body boundaries are inverted")
    scale = target_span / reference_span
    projected = tuple(
        target_header + (float(value) - reference_header) * scale
        for value in reference_rows
    )
    if any(right <= left for left, right in zip(projected, projected[1:])):
        raise ValueError("projected daily surface is not ordered")
    return projected


def project_day_rows_from_labels(
    label_centers: dict[int, float],
    body_boundaries: dict[int, tuple[float, float]],
) -> dict[int, tuple[float, ...]]:
    """Project the printed 1-31 row pattern into slanted month columns.

    The label pattern is intentionally non-uniform because many yearbooks put
    a wider spacer after each five-day block.  `body_boundaries` may omit noisy
    month columns; a low-order fit supplies their local top and bottom rules.
    """
    if len(label_centers) < 20 or min(label_centers) > 3 or max(label_centers) < 29:
        raise ValueError("printed day labels must cover most of days 1-31")
    if len(body_boundaries) < 6:
        raise ValueError("at least six month body boundaries are required")
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("numpy is required for day-label projection") from exc
    days = np.asarray(sorted(label_centers), dtype=float)
    observed = np.asarray([label_centers[int(day)] for day in days], dtype=float)
    if np.any(np.diff(observed) <= 0):
        raise ValueError("printed day labels must be vertically ordered")
    rows = np.interp(np.arange(1, 32, dtype=float), days, observed)
    pitch = float(np.median(np.diff(rows)))
    if pitch <= 0:
        raise ValueError("invalid printed day-label pitch")
    normalized = (rows - rows[0]) / (rows[-1] - rows[0])
    span_units = (rows[-1] - rows[0]) / pitch
    months = np.asarray(sorted(body_boundaries), dtype=float)
    degree = 2 if len(months) >= 8 else 1
    top_fit = np.polyfit(months, [body_boundaries[int(month)][0] for month in months], degree)
    bottom_fit = np.polyfit(months, [body_boundaries[int(month)][1] for month in months], degree)
    projected: dict[int, tuple[float, ...]] = {}
    for month in range(1, 13):
        top = float(np.polyval(top_fit, month))
        bottom = float(np.polyval(bottom_fit, month))
        local_pitch = (bottom - top) / (span_units + 2.0)
        first, last = top + local_pitch, bottom - local_pitch
        projected[month] = tuple(float(first + value * (last - first)) for value in normalized)
    return projected


def estimate_horizontal_shear(
    segments: list[tuple[float, float, float, float]],
    minimum_span: float,
    maximum_absolute_slope: float = 0.04,
) -> float:
    """Estimate table-row shear from long, nearly horizontal rule segments."""
    slopes = []
    for x0, y0, x1, y1 in segments:
        span = x1 - x0
        if abs(span) < minimum_span:
            continue
        slope = (y1 - y0) / span
        if abs(slope) <= maximum_absolute_slope:
            slopes.append(float(slope))
    if not slopes:
        raise ValueError("no reliable horizontal rule segments")
    return float(median(slopes))


def rectify_row_coordinate(y: float, x: float, slope: float, pivot_x: float) -> float:
    """Map a slanted source-row coordinate into a horizontal table frame."""
    return float(y - slope * (x - pivot_x))


def select_ordered_daily_value_rows(
    observed_centers: list[float], day_count: int
) -> tuple[float, ...]:
    """Select daily rows before footer statistics, repairing a missed day 1."""
    if day_count not in {28, 29, 30, 31} or len(observed_centers) < day_count:
        raise ValueError("insufficient ordered numeric rows")
    centers = sorted(float(value) for value in observed_centers)
    gaps = [right - left for left, right in zip(centers, centers[1:])]
    ordinary = sorted(gaps)[: max(1, len(gaps) // 2)]
    pitch = median(ordinary)
    large = [index for index, gap in enumerate(gaps, 1) if gap >= pitch * 1.45][:5]
    phases = [index % 5 for index in large]
    if len(phases) >= 4 and len(set(phases)) == 1 and phases[0] in {3, 4}:
        missing = 5 - phases[0]
        centers = [centers[0] - pitch * step for step in range(missing, 0, -1)] + centers
    selected = centers[:day_count]
    selected_gaps = [right - left for left, right in zip(selected, selected[1:])]
    block = [gap for index, gap in enumerate(selected_gaps, 1) if index in {5, 10, 15, 20, 25}]
    normal = [gap for index, gap in enumerate(selected_gaps, 1) if index not in {5, 10, 15, 20, 25}]
    normal_pitch = median(normal)
    if not block or min(block) < normal_pitch * 1.30:
        raise ValueError("ordered values do not preserve five-day spacer bands")
    return tuple(selected)


def infer_month_boundaries_from_labels(
    label_centers: dict[int, float], image_width: float
) -> tuple[float, ...]:
    """Fit all month boundaries from six or more printed month labels."""
    if len(label_centers) < 6 or max(label_centers) - min(label_centers) < 5:
        raise ValueError("at least six well-spread printed month labels are required")
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("numpy is required for label-anchored geometry") from exc
    months = np.asarray(sorted(label_centers), dtype=float)
    centers = np.asarray([label_centers[int(month)] for month in months], dtype=float)
    degree = 2 if len(months) >= 7 else 1
    fit = np.polyfit(months, centers, degree)
    predicted = np.asarray([float(np.polyval(fit, month)) for month in range(1, 13)])
    gaps = np.diff(predicted)
    residual = float(np.max(np.abs(np.polyval(fit, months) - centers)))
    if (
        np.any(gaps <= 0)
        or float(np.median(gaps)) < image_width * 0.035
        or float(np.median(gaps)) > image_width * 0.095
        or residual > image_width * 0.035
    ):
        raise ValueError("printed month labels do not form a plausible ordered grid")
    boundaries = [predicted[0] - gaps[0] / 2]
    boundaries.extend((predicted[:-1] + predicted[1:]) / 2)
    boundaries.append(predicted[-1] + gaps[-1] / 2)
    if boundaries[0] < -image_width * 0.20 or boundaries[-1] > image_width * 1.20:
        raise ValueError("label-anchored grid falls too far outside the crop")
    return tuple(float(value) for value in boundaries)


def infer_month_boundaries(header_rules: list[float], image_width: float) -> tuple[float, ...]:
    """Return thirteen month boundaries from true header-crossing rules.

    `header_rules` must come from the table header band, not the daily body.
    This distinction prevents vertically repeated zeroes from masquerading as
    table rules.  Missing rules are inferred only from a regular right-aligned
    suffix; the December edge is therefore required.
    """
    if len(header_rules) < 7:
        raise ValueError("at least seven header-crossing rules are required")
    selected = sorted(float(value) for value in header_rules)
    if any(right <= left for left, right in zip(selected, selected[1:])):
        raise ValueError("header rules must be distinct")

    if len(selected) == 13:
        pitch = median(right - left for left, right in zip(selected, selected[1:]))
        right_room = image_width - selected[-1]
        if selected[0] <= image_width * 0.12 and right_room >= pitch * 0.55:
            # The faint December border is missing while the day-column outer
            # edge is present.  Keeping all thirteen rules would silently map
            # day numbers to January and shift every month left.
            selected = selected[1:] + [image_width - 1]

    while len(selected) > 13:
        gaps = [right - left for left, right in zip(selected, selected[1:])]
        upper = [gap for gap in gaps if gap >= sorted(gaps)[max(0, len(gaps) * 3 // 10)]]
        typical = median(upper)
        if selected[-1] - selected[-2] < typical * 0.72:
            selected.pop()
        else:
            selected.pop(0)

    gaps = [right - left for left, right in zip(selected, selected[1:])]
    pitch = median(gaps)
    pitch = median(gap / max(1, round(gap / pitch)) for gap in gaps)
    steps = [max(1, round(gap / pitch)) for gap in gaps]
    covered = sum(steps)
    while covered > 12 and len(selected) > 7:
        selected.pop(0)
        gaps = [right - left for left, right in zip(selected, selected[1:])]
        pitch = median(gap / max(1, round(gap / pitch)) for gap in gaps)
        steps = [max(1, round(gap / pitch)) for gap in gaps]
        covered = sum(steps)
    if covered > 12:
        raise ValueError("header rules do not form a plausible 12-month span")

    assigned = [12 - covered]
    for step in steps:
        assigned.append(assigned[-1] + step)
    anchors = dict(zip(assigned, selected))
    boundaries: list[float] = []
    for index in range(13):
        if index in anchors:
            boundaries.append(anchors[index])
            continue
        left_indexes = [item for item in anchors if item < index]
        right_indexes = [item for item in anchors if item > index]
        if left_indexes and right_indexes:
            left_index, right_index = max(left_indexes), min(right_indexes)
            fraction = (index - left_index) / (right_index - left_index)
            boundaries.append(anchors[left_index] + fraction * (anchors[right_index] - anchors[left_index]))
        elif right_indexes:
            right_index = min(right_indexes)
            boundaries.append(anchors[right_index] - (right_index - index) * pitch)
        else:
            left_index = max(left_indexes)
            boundaries.append(anchors[left_index] + (index - left_index) * pitch)

    if not (-image_width * 0.30 <= boundaries[0] <= image_width * 0.30):
        raise ValueError("inferred January edge is implausible")
    if not image_width * 0.72 <= boundaries[-1] <= image_width * 1.02:
        raise ValueError("observed December edge is implausible")
    return tuple(boundaries)
