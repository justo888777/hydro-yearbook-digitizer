from hydro_yearbook_digitizer.daily_release import (
    classify_printed_daily_title,
    decide_cell_release,
    expanded_cell_bounds,
    fixed_raw,
    has_complete_daily_columns,
    leading_printed_serial,
    retain_daily_vertical_rules,
    source_supports_negative_flow,
    three_significant_decimal_places,
)


def test_routes_only_printed_target_titles() -> None:
    assert classify_printed_daily_title("2 安固里河 张北站 逐日平均流量表") == "flow"
    assert classify_printed_daily_title("79 饮马河 丰镇 逐日平均悬移质输沙率表") == "sediment_rate"
    assert classify_printed_daily_title("3 安固里河 张北（河道）逐日平均含沙量表") == "concentration"
    assert classify_printed_daily_title("逐日平均水位表") is None
    assert classify_printed_daily_title("悬移质泥沙颗粒级配表") is None


def test_serial_comes_from_title_lead_not_note_or_unit() -> None:
    assert leading_printed_serial("24 桑干河 东榆林水库（坝下）流量 m³/s") == 24
    assert leading_printed_serial("44 饮马河 丰镇（饮三）") == 44
    assert leading_printed_serial("集水面积 350 km² 流量 m³/s") is None


def test_optional_fixed_cell_is_null_safe() -> None:
    assert fixed_raw({"fixed": None}) == ""
    assert fixed_raw(None) == ""
    assert fixed_raw({"fixed": {"raw": "河干"}}) == "河干"


def test_zero_unresolved_release_gate() -> None:
    assert decide_cell_release(0.864, [0.864]).released
    assert decide_cell_release(None, [], geometry_blank=True).released
    assert decide_cell_release(0, [], printed_zero_stat=True).released
    assert not decide_cell_release(0.864, [0.804]).released


def test_true_outer_left_rule_survives_near_edge_filter() -> None:
    rules = retain_daily_vertical_rules([14, 47, 154, 262, 370, 478, 586, 694, 802, 910, 1018, 1126, 1234, 1342, 1443], 1500)
    assert rules[0] == 47
    assert len(rules) == 14
    assert has_complete_daily_columns(rules)


def test_incomplete_shifted_daily_boundaries_are_blocked() -> None:
    assert not has_complete_daily_columns([154 + 108 * index for index in range(13)])


def test_context_crop_expands_top_and_bottom_strokes() -> None:
    assert expanded_cell_bounds((1, 2, 20, 18), (100, 80)) == (0, 0, 23, 23)


def test_negative_flow_requires_same_source_support() -> None:
    assert not source_supports_negative_flow(-0.18)
    assert source_supports_negative_flow(-0.18, printed_monthly_minimum=-0.21)
    assert source_supports_negative_flow(-0.18, visually_verified=True)
    assert source_supports_negative_flow(0)


def test_three_significant_precision_survives_lost_trailing_zero() -> None:
    assert three_significant_decimal_places(0.403) == 3
    assert three_significant_decimal_places(16) == 1
    assert three_significant_decimal_places(100) == 0
