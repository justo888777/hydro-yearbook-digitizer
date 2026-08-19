from hydro_yearbook_digitizer.calendar_rules import expected_special_state, is_valid_date


def test_leap_year() -> None:
    assert is_valid_date(1960, 2, 29)
    assert not is_valid_date(1961, 2, 29)


def test_invalid_month_end() -> None:
    assert expected_special_state(1962, 4, 31) == "NOT_APPLICABLE"
    assert expected_special_state(1962, 5, 31) is None
