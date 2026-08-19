from hydro_yearbook_digitizer.grid_daily import (
    GridReading,
    GridTemplate,
    clamp_image_roi,
    expand_compact_water_level,
    is_single_vertical_date_glyph,
    independent_model_majority,
    monthly_checks,
    row_y,
    select_regular_footer_edges,
    select_day_body_boundaries,
    source_state_evidence,
    statistics_source_conflict,
    state_month_statistics_closed,
    protected_daily_source_state,
    statistics_labels,
    strict_all_zero_statistics_proof,
    validate_month_local_rows,
)


def test_day_body_pair_uses_statistics_anchor_not_title_underline() -> None:
    rules = (69.0, 294.0, 442.0, 1252.0, 1278.0, 1304.0)
    assert select_day_body_boundaries(
        rules,
        image_height=1512,
        expected_header=69,
        expected_statistics=1252,
    ) == (442.0, 1252.0)


def test_day_body_pair_keeps_local_header_bottom_over_hough_title_line() -> None:
    rules = (207.0, 303.0, 376.0, 1238.0, 1266.0, 1294.0)
    assert select_day_body_boundaries(
        rules,
        image_height=1512,
        expected_header=207,
        expected_statistics=1238,
    ) == (376.0, 1238.0)


def test_state_month_closes_from_two_printed_statistics() -> None:
    assert state_month_statistics_closed(
        "河干",
        ("河干", "河干", 1, None, 1),
        ("河干", None, 1, 0),
        ("河干", "", "1", "0"),
    )
    assert not state_month_statistics_closed(
        "河干", ("河干", None), ("河干", None)
    )
    assert not state_month_statistics_closed(
        "河干", ("河干", "河干"), ("河干", 0.12), ("河干", "0.12")
    )


def test_independent_model_majority_requires_two_model_names() -> None:
    assert independent_model_majority({"v6": 1.23, "v5": 1.23, "v4": 1.24}) == 1.23
    assert independent_model_majority({"v6": 1.23, "v5": 1.24}) is None


def _template() -> GridTemplate:
    return GridTemplate(
        month_centers=tuple(float(index * 100) for index in range(12)),
        first_row_y=tuple(20.0 for _ in range(12)),
        month_left=-50,
        month_right=1150,
        row_step=10,
        five_day_gap=4,
    )


def test_row_geometry_keeps_the_printed_five_day_separators() -> None:
    template = _template()
    assert row_y(template, 0, 5) == 60
    assert row_y(template, 0, 6) == 74
    assert row_y(template, 0, 11) == 128


def test_monthly_checks_rejects_missing_or_unverified_values() -> None:
    readings = [GridReading(1, day, 1.0, "1", "1", "dual_read_agree") for day in range(1, 32)]
    checks = monthly_checks(
        readings,
        year=2020,
        printed_means=(1.0,) * 12,
        printed_maxima=(1.0,) * 12,
        printed_minima=(1.0,) * 12,
    )
    assert checks[0].status == "passed"
    assert checks[1].status == "needs_visual_review"


def test_sediment_observed_mean_is_not_an_arithmetic_checksum() -> None:
    readings = [GridReading(1, day, 2.0, "2", "2", "dual_read_agree") for day in range(1, 32)]
    checks = monthly_checks(
        readings,
        year=2016,
        printed_means=(9.9,) + (0.0,) * 11,
        printed_maxima=(2.0,) + (0.0,) * 11,
        printed_minima=(2.0,) + (0.0,) * 11,
        require_extrema=False,
        mean_rule="observed",
    )
    assert checks[0].calculated_mean == 2.0
    assert checks[0].printed_mean == 9.9
    assert checks[0].status == "passed"


def test_monthly_closure_includes_daily_print_rounding_interval() -> None:
    readings = [GridReading(1, day, 1.004, "1.004", "1.004", "dual_read_agree") for day in range(1, 32)]
    checks = monthly_checks(
        readings,
        year=2021,
        printed_means=(1.0,) + (0.0,) * 11,
        printed_maxima=(1.004,) + (0.0,) * 11,
        printed_minima=(1.004,) + (0.0,) * 11,
    )
    assert checks[0].status == "passed"


def test_instantaneous_extrema_bound_daily_means_without_requiring_equality() -> None:
    readings = [GridReading(1, day, 2.0, "2", "2", "dual_read_agree") for day in range(1, 32)]
    checks = monthly_checks(
        readings,
        year=2021,
        printed_means=(2.0,) + (0.0,) * 11,
        printed_maxima=(2.8,) + (0.0,) * 11,
        printed_minima=(1.4,) + (0.0,) * 11,
    )
    assert checks[0].status == "passed"


def test_daily_mean_extrema_rule_still_requires_exact_extrema() -> None:
    readings = [GridReading(1, day, 2.0, "2", "2", "dual_read_agree") for day in range(1, 32)]
    checks = monthly_checks(
        readings,
        year=2021,
        printed_means=(2.0,) + (0.0,) * 11,
        printed_maxima=(2.8,) + (0.0,) * 11,
        printed_minima=(1.4,) + (0.0,) * 11,
        extrema_rule="daily_mean_extrema",
    )
    assert checks[0].status == "needs_visual_review"


def test_compact_water_level_carries_the_latest_explicit_integer() -> None:
    value, prefix = expand_compact_water_level("10.15", None)
    assert (value, prefix) == (10.15, 10)
    value, prefix = expand_compact_water_level("03", prefix)
    assert (value, prefix) == (10.03, 10)
    value, prefix = expand_compact_water_level("9.80", prefix)
    assert (value, prefix) == (9.8, 9)
    assert expand_compact_water_level("51", prefix) == (9.51, 9)
    assert expand_compact_water_level("1028.00", 1027) == (1028.0, 1028)


def test_month_local_rows_require_five_spacers_and_both_edges() -> None:
    centers = []
    position = 10.0
    for day in range(1, 32):
        centers.append(position)
        position += 18.0 if day in {5, 10, 15, 20, 25} else 10.0
    assert validate_month_local_rows(tuple(centers), body_top=5.0, body_bottom=370.0)
    shifted = tuple(value + 20.0 for value in centers)
    assert not validate_month_local_rows(shifted, body_top=5.0, body_bottom=370.0)


def test_geometry_search_roi_clamps_negative_top_without_numpy_wraparound() -> None:
    assert clamp_image_roi((12, -14, 80, 100), (120, 200, 3)) == (12, 0, 80, 100)
    assert clamp_image_roi((12, -14, 80, -2), (120, 200, 3)) is None


def test_all_zero_proof_rejects_a_ten_zero_two_nonzero_seasonal_table() -> None:
    means = (0.0,) * 10 + (0.584, 0.022)
    maxima = (0.0,) * 10 + (4.02, 0.217)
    assert not strict_all_zero_statistics_proof(means, maxima)
    assert strict_all_zero_statistics_proof((0.0,) * 12, (0.0,) * 12)


def test_sediment_statistics_do_not_consume_annual_summary_rows() -> None:
    assert statistics_labels("sediment_rate") == ("平均", "最大", "最大日期")
    assert len(statistics_labels("concentration")) == 5
    assert len(statistics_labels("flow")) == 5


def test_statistics_reread_preserves_states_and_existing_decimal_points() -> None:
    assert statistics_source_conflict(
        existing_raw="渠干", existing_value="渠干",
        candidate_raw="8", candidate_value=8,
    ) == "existing_hydrological_state"
    assert statistics_source_conflict(
        existing_raw="8.92", existing_value=8.92,
        candidate_raw="892", candidate_value=892,
    ) == "candidate_drops_existing_decimal"
    assert statistics_source_conflict(
        existing_raw="7", existing_value=7,
        candidate_raw="1", candidate_value=1,
        label="最小日期", year=2010, month=11, candidate_score=0.914293,
    ) == "low_confidence_plausible_date_conflict"
    assert statistics_source_conflict(
        existing_raw="2.51", existing_value=2.51,
        candidate_raw="31", candidate_value=31,
        label="最大日期", year=2010, month=8, candidate_score=0.99936,
    ) is None


def test_month_local_reread_never_fills_source_absence_or_state_text() -> None:
    assert protected_daily_source_state("source_blank", None)
    assert protected_daily_source_state("source_slot_absent", None)
    assert protected_daily_source_state("source_scan_missing", None)
    assert protected_daily_source_state("source_blank_visual_verified", None)
    assert protected_daily_source_state("state_pass", "渠干")
    assert not protected_daily_source_state("unresolved_ink", None)


def test_state_carry_requires_direct_text_or_an_explicit_ditto_glyph() -> None:
    assert source_state_evidence("部分河干V") == "direct_state"
    assert source_state_evidence("〃") == "explicit_ditto"
    assert source_state_evidence("", explicit_ditto=True) == "explicit_ditto"
    assert source_state_evidence("-") is None
    assert source_state_evidence("_") is None
    assert source_state_evidence("—") is None
    assert source_state_evidence("") is None
    assert source_state_evidence("〃", source_blank=True) is None


def test_month_local_footer_edges_skip_false_rules_without_shifting_rows() -> None:
    assert select_regular_footer_edges(
        (1264, 1278, 1292, 1319, 1346, 1373, 1400, 1428),
        start=1264, row_count=5,
    ) == (1264.0, 1292.0, 1319.0, 1346.0, 1373.0, 1400.0)
    assert select_regular_footer_edges(
        (1048, 1075, 1102, 1128, 1154, 1181, 1235),
        start=1048, row_count=5,
    ) == (1048.0, 1075.0, 1102.0, 1128.0, 1154.0, 1181.0)
    assert statistics_source_conflict(
        existing_raw="", existing_value=None,
        candidate_raw="27", candidate_value=27,
        label="最小日期", year=2010, month=12, candidate_score=0.999776,
    ) is None
    assert statistics_source_conflict(
        existing_raw="0.89", existing_value=0.89,
        candidate_raw="21", candidate_value=21,
        label="最大日期", year=2010, month=7, candidate_score=0.887419,
    ) is None
    assert statistics_source_conflict(
        existing_raw="部分河干", existing_value="部分河干",
        candidate_raw="16", candidate_value=16,
        label="最小日期", year=2010, month=10, candidate_score=0.999855,
    ) is None


def test_date_one_geometry_rejects_dashes_and_multi_digit_dates() -> None:
    assert is_single_vertical_date_glyph(
        ((20, 3, 3, 13, 22),), cell_width=50, cell_height=20,
    )
    assert not is_single_vertical_date_glyph(
        ((10, 8, 25, 2, 38),), cell_width=50, cell_height=20,
    )
    assert not is_single_vertical_date_glyph(
        ((18, 3, 3, 13, 22), (25, 3, 3, 13, 22)),
        cell_width=50, cell_height=20,
    )
