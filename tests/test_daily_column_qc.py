import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "hydro-yearbook-digitizer" / "scripts" / "daily_column_qc.py"
SPEC = importlib.util.spec_from_file_location("daily_column_qc", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_thick_statistics_rule_is_one_rule():
    assert MODULE.merge_rule_runs([2007, 2009, 2029.5, 2051.5]) == (2008, 2029.5, 2051.5)


def test_missing_leading_mean_rule_gate():
    assert MODULE.leading_mean_rule_is_missing(1790.25, 1825, 16)
    assert not MODULE.leading_mean_rule_is_missing(1985, 2000, 17.5)


def test_column_local_centers_accept_smooth_warp():
    base = [100, 116, 132, 148]
    observed = [100, 115, 130, 145]
    selected, audit = MODULE.choose_column_centers(base, observed, 16)
    assert selected == tuple(observed)
    assert audit["direct_sequence"] is True


def test_column_local_centers_do_not_shift_source_blank():
    base = [100, 116, 132, 148]
    observed = [100, 132, 148]
    selected, audit = MODULE.choose_column_centers(base, observed, 16)
    assert selected[1] == 116
    assert audit["component_aligned_rows"] == 3


def test_column_local_centers_reject_whole_row_phase_shift():
    base = [100, 116, 132, 148]
    observed = [116, 132, 148, 164]
    selected, audit = MODULE.choose_column_centers(base, observed, 16)
    assert audit["direct_sequence"] is False
    assert selected[0] == 100


def test_column_local_centers_accept_half_row_local_table_offset():
    base = [100, 116, 132, 148]
    observed = [109, 125, 141, 157]
    selected, audit = MODULE.choose_column_centers(base, observed, 16)
    assert audit["direct_sequence"] is True
    assert selected == tuple(observed)


def test_column_local_fallback_keeps_matches_monotone():
    selected, audit = MODULE.choose_column_centers([100, 116], [97, 115], 16)
    assert selected == (97, 115)
    assert audit["component_aligned_rows"] == 2


def test_gridline_and_punctuation_normalization():
    assert MODULE.remove_leading_rule_digit("10", "0") == "0"
    assert MODULE.remove_leading_rule_digit("1 2.58", "2.58") == "2.58"
    assert MODULE.normalize_repeated_decimal(".0.971") == "0.971"
    assert MODULE.normalize_repeated_decimal("49.6.") == "49.6"
    assert MODULE.normalize_repeated_decimal("-1.47N") == "-1.47"
    assert MODULE.normalize_repeated_decimal("0:453") == "0.453"
    assert MODULE.normalize_repeated_decimal("6.58°") == "6.58"


def test_zero_mean_month_removes_only_gridline_tens_and_preserves_blanks():
    assert MODULE.zero_mean_gridline_indices([0, 10, None, 0, 10], [0.06, 0.07, 0, 0.05, 0.16]) == (1,)
    assert MODULE.zero_mean_gridline_indices([0, 10, 0.2], [0.06, 0.07, 0.06]) == ()


def test_concentration_dry_marker_controls_only_same_month_run():
    actions = MODULE.concentration_dry_actions(["河干", '"', "n", "0", "0"], [False, False, False, True, True])
    assert actions == ("source_dry_marker", "source_dry_ditto", "source_dry_ditto", "numeric", "keep")
    assert MODULE.concentration_dry_actions(["渠干", '"', "0"], [False, False, True]) == (
        "source_dry_marker",
        "source_dry_ditto",
        "numeric",
    )
    assert MODULE.concentration_dry_actions(
        ["河干", '"', "0", '"'],
        [False, False, True, False],
        [0.99, 0.8, 0.12, 0.8],
        [0.15, 0.03, 0.03, 0.03],
    ) == ("source_dry_marker", "source_dry_ditto", "source_dry_ditto", "source_dry_ditto")
    assert MODULE.concentration_dry_actions(["果于", '"'], [False, False]) == (
        "source_dry_marker",
        "source_dry_ditto",
    )
    assert MODULE.concentration_dry_actions(["集十", '"'], [False, False]) == (
        "source_dry_marker",
        "source_dry_ditto",
    )
    assert MODULE.concentration_dry_actions(["梁十", '"'], [False, False]) == (
        "source_dry_marker",
        "source_dry_ditto",
    )


def test_daily_closure_selects_unique_printed_stat_candidate():
    assert MODULE.choose_statistic_by_daily_closure(1.864, 1.66, 1.86, 0.01) == "alternative"
    assert MODULE.choose_statistic_by_daily_closure(1.864, 1.86, 1.86, 0.01) is None
