import pytest

from hydro_yearbook_digitizer.statistics_consensus import (
    finite_numeric_proposals,
    proposal_payload,
    should_commit_statistics_trial,
)


def test_completed_empty_statistics_result_is_not_missing():
    table = {"model_statistics": {"provisional_cell_proposals": []}}
    assert proposal_payload(table, "model_statistics") == []


def test_missing_statistics_result_still_fails_closed():
    with pytest.raises(ValueError):
        proposal_payload({}, "model_statistics")


def test_statistics_trial_must_pass_against_current_daily_values():
    assert not should_commit_statistics_trial(
        changed=True,
        base_passed=False,
        trial_passed_on_current_daily=False,
        base_date_defects=2,
        trial_date_defects=0,
    )


def test_statistics_trial_can_replace_a_failing_month():
    assert should_commit_statistics_trial(
        changed=True,
        base_passed=False,
        trial_passed_on_current_daily=True,
        base_date_defects=2,
        trial_date_defects=2,
    )


def test_nonfinite_and_boolean_numeric_proposals_are_removed():
    rows = [
        {"value": 1.25}, {"value": float("nan")}, {"value": float("inf")},
        {"value": True}, {"value": "1.25"}, {"other": 1.25},
    ]
    assert finite_numeric_proposals(rows) == [{"value": 1.25}]
