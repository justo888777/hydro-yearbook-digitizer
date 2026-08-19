import pytest

from hydro_yearbook_digitizer.grid_geometry import (
    fit_vertical_rule_lattice,
    fit_printed_day_sequence_boxes,
    complete_daily_statistics_rules,
    infer_month_boundaries,
    infer_month_boundaries_from_labels,
    interpolate_calendar_row_surface,
    infer_january_interval_from_month_labels,
    project_rows_between_sloped_boundaries,
    project_day_rows_from_labels,
    rule_anchored_daily_rows,
    repair_daily_statistics_lines,
    select_daily_rule_window,
    select_printed_day_rows,
    template_day_rows,
    validate_daily_row_span,
)


def test_ruled_rows_ignore_displaced_recognition_cell_geometry() -> None:
    rows = rule_anchored_daily_rows(
        (210, 274, 1151, 1179), local_top=210, statistics_top=1151
    )
    assert len(rows) == 31
    assert rows[0] < 300
    assert rows[-1] < 1151
    pitch = (1151 - 274) / 36
    assert rows[5] - rows[4] == pytest.approx(pitch * 2)


def test_valid_month_local_cell_lines_override_shifted_global_projection() -> None:
    centres = []
    y = 300.0
    for day in range(1, 32):
        centres.append(y)
        y += 22.0 + (14.0 if day in {5, 10, 15, 20, 25} else 0.0)
    bounds = [(100.0, centre - 7.0, 200.0, centre + 7.0) for centre in centres]
    rows = rule_anchored_daily_rows(
        (210, 274, 1151, 1179),
        local_top=274,
        statistics_top=1040,
        measured_cell_bounds=bounds,
    )
    assert rows == tuple(centres)
    assert rows[25] - rows[24] == pytest.approx(36.0)


def test_month_labels_prove_january_is_first_rule_interval() -> None:
    boundaries = [180 + 140 * index for index in range(14)]
    labels = {1: 250, 2: 390, 6: 950, 10: 1510}
    assert infer_january_interval_from_month_labels(labels, boundaries) == 0


def test_sloped_physical_boundaries_keep_day_one_below_header() -> None:
    reference = [220 + 30 * index for index in range(31)]
    rows = project_rows_between_sloped_boundaries(
        reference,
        reference_x=200,
        target_x=1600,
        header_curve=(0.01, 198),
        statistics_curve=(-0.012, 1162),
    )
    target_header = 0.01 * 1600 + 198
    target_statistics = -0.012 * 1600 + 1162
    assert target_header < rows[0] < rows[-1] < target_statistics


def test_recovers_rows_from_merged_printed_day_boxes() -> None:
    boxes = [
        {"x": 190, "top": 398, "bottom": 512, "text": "12345"},
        {"x": 190, "top": 518, "bottom": 644, "text": "678910"},
        {"x": 189, "top": 650, "bottom": 773, "text": "1112131415"},
        {"x": 189, "top": 779, "bottom": 901, "text": "1617181920"},
        {"x": 188, "top": 907, "bottom": 1032, "text": "2122232425"},
        {"x": 188, "top": 1038, "bottom": 1183, "text": "262728293031"},
    ]
    rows, reference_x = fit_printed_day_sequence_boxes(
        boxes, header_floor=350, statistics_top=1200
    )
    assert len(rows) == 31
    assert rows[0] == pytest.approx(409.4)
    assert rows[-1] == pytest.approx(1170.9167)
    assert reference_x == pytest.approx(189)


def test_short_month_tail_does_not_vote_in_row_surface() -> None:
    reference = tuple(400 + day * 24 for day in range(31))
    february = tuple(405 + day * 24 for day in range(31))
    rows = interpolate_calendar_row_surface(
        reference_x=100,
        reference_rows=reference,
        complete_month_rows={2: february},
        month_centers={month: 100 + month * 100 for month in range(1, 13)},
        month_day_counts={
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31,
        },
    )
    assert rows[3][28] - rows[3][27] == pytest.approx(24)
    assert rows[3][30] - rows[3][29] == pytest.approx(24)


def test_discards_false_daily_body_line_before_statistics_block() -> None:
    detected = [1091, 1215, 1238, 1262, 1286, 1310, 1333]
    result = repair_daily_statistics_lines(
        detected, header_bottom=437, image_height=1462, expected_body_ratio=0.53
    )
    assert result == pytest.approx(detected[1:])


def test_preserves_regular_statistics_boundaries() -> None:
    detected = [1091, 1115, 1139, 1163, 1187, 1211]
    result = repair_daily_statistics_lines(
        detected, header_bottom=300, image_height=1462, expected_body_ratio=0.53
    )
    assert result == pytest.approx(detected)


def test_preserves_true_footer_top_when_internal_rules_are_missing() -> None:
    detected = [1199, 1269, 1292, 1313, 1342, 1364, 1429]
    result = repair_daily_statistics_lines(
        detected, header_bottom=428, image_height=1462, expected_body_ratio=0.53
    )
    assert result == pytest.approx(detected)


def test_completes_two_missing_rules_in_statistics_footer() -> None:
    detected = [1199, 1269, 1292, 1313, 1342, 1364, 1429]
    result = complete_daily_statistics_rules(detected)
    assert result[:6] == pytest.approx([1199, 1222.3333, 1245.6667, 1269, 1292, 1313], abs=0.01)


def test_rejects_compressed_day_rows_inside_valid_body() -> None:
    compressed = [572 + (922 - 572) * index / 30 for index in range(31)]
    with pytest.raises(ValueError, match="cover only"):
        validate_daily_row_span(compressed, 380, 1186)


def test_accepts_rows_that_cover_the_daily_body() -> None:
    rows = list(template_day_rows(380, 1186))
    assert validate_daily_row_span(rows, 380, 1186) > 0.90


def test_selects_true_14_rule_window_and_excludes_spine_line() -> None:
    printed = [250 + 119 * index for index in range(14)]
    candidates = [31, *printed]
    strengths = {value: 100.0 for value in printed} | {31.0: 900.0}
    assert select_daily_rule_window(candidates, strengths=strengths) == pytest.approx(printed)


def test_day_header_diagonal_selects_semantic_first_interval() -> None:
    printed = [180 + 108 * index for index in range(14)]
    candidates = [72, *printed, printed[-1] + 108]
    scores = {(printed[0], printed[1]): 70.0}
    assert select_daily_rule_window(candidates, diagonal_scores=scores) == pytest.approx(printed)


def test_exact_14_rules_can_replace_page_edge_and_missing_outer_rule() -> None:
    printed = [200 + 100 * index for index in range(14)]
    detected = [20, *printed[:-1]]
    assert select_daily_rule_window(detected) == pytest.approx(printed)


def test_rule_lattice_recovers_faint_right_border_without_compression() -> None:
    candidates = [194, 302, 410, 516, 622, 727, 834, 1049, 1157, 1265, 1374, 1482]
    result = fit_vertical_rule_lattice(candidates, 1598, horizontal_edges=(193, 1577))
    assert len(result) == 14
    assert result[0] == pytest.approx(194, abs=2)
    assert result[-1] == pytest.approx(1581, abs=5)
    assert result[8] == pytest.approx(1049, abs=2)


def test_rule_lattice_recovers_faint_left_border_from_horizontal_span() -> None:
    candidates = [120, 233, 344, 454, 564, 676, 788, 898, 1008, 1120, 1230, 1341, 1447]
    result = fit_vertical_rule_lattice(candidates, 1598, horizontal_edges=(20, 1449))
    assert len(result) == 14
    assert result[0] == pytest.approx(18, abs=8)
    assert result[-1] == pytest.approx(1447, abs=3)


def test_rule_lattice_preserves_complete_detected_grid() -> None:
    candidates = [75 + 106 * index for index in range(14)]
    result = fit_vertical_rule_lattice(candidates, 1600, horizontal_edges=(74, 1454))
    assert result == pytest.approx(candidates)


def test_projects_nonuniform_day_labels_into_slanted_month_columns() -> None:
    labels = {}
    y = 80.0
    for day in range(1, 32):
        labels[day] = y
        y += 84.0 if day in {5, 10, 15, 20, 25} else 42.0
    boundaries = {month: (40.0 + 6 * month, 1700.0 + 3 * month) for month in range(1, 13)}
    rows = project_day_rows_from_labels(labels, boundaries)
    assert set(rows) == set(range(1, 13))
    assert all(len(values) == 31 for values in rows.values())
    # A five-day spacer stays roughly twice a normal row gap after projection.
    assert rows[8][5] - rows[8][4] == pytest.approx(2 * (rows[8][1] - rows[8][0]), rel=0.02)
    # Later month columns follow the fitted page slant.
    assert rows[12][0] > rows[1][0]


def test_estimates_and_rectifies_cross_table_row_shear() -> None:
    from hydro_yearbook_digitizer.grid_geometry import estimate_horizontal_shear, rectify_row_coordinate

    segments = [(100, 400, 1600, 414), (120, 800, 1620, 814), (200, 100, 300, 180)]
    slope = estimate_horizontal_shear(segments, minimum_span=1000)
    assert slope == pytest.approx(14 / 1500)
    left = rectify_row_coordinate(447, 325, slope, 325)
    right = rectify_row_coordinate(461, 1825, slope, 325)
    assert right == pytest.approx(left)


def test_ordered_numeric_rows_restore_a_missed_first_day() -> None:
    from hydro_yearbook_digitizer.grid_geometry import select_ordered_daily_value_rows

    rows = []
    y = 180.0
    for day in range(1, 32):
        rows.append(y)
        y += 40.0 if day in {5, 10, 15, 20, 25} else 21.0
    observed = rows[1:] + [rows[-1] + 45 + 20 * index for index in range(5)]
    selected = select_ordered_daily_value_rows(observed, 31)
    assert selected == pytest.approx(rows)


def test_selects_31_day_rows_when_ocr_merges_vertical_labels() -> None:
    rows = []
    y = 250.0
    for day in range(1, 32):
        rows.append(y)
        y += 76.0 if day in {5, 10, 15, 20, 25} else 38.0
    selected = select_printed_day_rows([80.0, 120.0, *rows, 1850.0], 2050.0)
    assert selected == pytest.approx(rows)


def test_recovers_missing_day_one_without_accepting_summary_row() -> None:
    rows = []
    y = 232.0
    for day in range(1, 32):
        rows.append(y)
        y += 76.0 if day in {5, 10, 15, 20, 25} else 38.0
    # The day-1 glyph is missed; a header and the statistic row remain.
    selected = select_printed_day_rows([158.0, *rows[1:], rows[-1] + 84.0], 2050.0)
    assert selected == pytest.approx(rows, abs=2.0)


def test_low_quality_fallback_preserves_the_five_day_blank_bands() -> None:
    rows = template_day_rows(162.0, 760.0)
    ordinary = rows[1] - rows[0]
    assert len(rows) == 31
    assert rows[5] - rows[4] == pytest.approx(ordinary * 1.88)
    assert rows[15] - rows[14] == pytest.approx(ordinary * 1.88)
    assert rows[-1] < 760.0


def test_printed_month_labels_recover_missing_january() -> None:
    labels = {
        3: 794.9,
        4: 1112.4,
        5: 1418.9,
        6: 1714.7,
        7: 2006.0,
        8: 2291.8,
        9: 2574.6,
        10: 2863.9,
        11: 3152.2,
        12: 3423.4,
    }
    result = infer_month_boundaries_from_labels(labels, 4000)
    assert len(result) == 13
    assert result[0] == pytest.approx(2, abs=20)
    assert result[-1] == pytest.approx(3560, abs=25)


def test_discards_day_column_edge() -> None:
    rules = [25, 142, 262, 384, 510, 640, 776, 920, 1070, 1229, 1398, 1572, 1744, 1892]
    result = infer_month_boundaries(rules, 2000)
    assert len(result) == 13
    assert result[0] == 142
    assert result[-1] == 1892


def test_discards_day_column_when_december_border_is_missing() -> None:
    rules = [198, 524, 838, 1144, 1442, 1734, 2023, 2310, 2596, 2883, 3171, 3460, 3745]
    result = infer_month_boundaries(rules, 4000)
    assert len(result) == 13
    assert result[0] == 524
    assert result[-1] == 3999


def test_recovers_clipped_january_edge() -> None:
    rules = [83, 226, 370, 515, 662, 810, 960, 1113, 1268, 1425, 1582, 1734]
    result = infer_month_boundaries(rules, 2000)
    assert len(result) == 13
    assert result[0] == pytest.approx(-67, abs=5)
    assert result[-1] == 1734


def test_treats_a_doubled_gap_as_one_missing_rule() -> None:
    rules = [404, 722, 873, 1021, 1169, 1316, 1462, 1609, 1756, 1901]
    result = infer_month_boundaries(rules, 2000)
    assert len(result) == 13
    assert result[0] == pytest.approx(108, abs=12)
    assert result[-1] == 1901


def test_requires_a_reliable_header_suffix() -> None:
    with pytest.raises(ValueError):
        infer_month_boundaries([100, 250, 400], 2000)
