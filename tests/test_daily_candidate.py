from hydro_yearbook_digitizer.daily_candidate import OcrToken, constant_daily_candidates, map_daily_tokens


def test_maps_single_engine_daily_values_but_never_auto_accepts() -> None:
    tokens = [OcrToken(str(day), 10, day * 30, 0.99) for day in range(1, 32)]
    tokens.extend(OcrToken(str(day / 10), 100, day * 30, 0.99) for day in range(1, 32))
    records, leftovers = map_daily_tokens(
        tokens,
        source_file="page.jpg",
        table_id="top",
        month_centers=(500, 100) + (500,) * 10,
        day_column_max_x=30,
        daily_y_min=1,
        daily_y_max=1000,
    )
    assert len(records) == 31
    assert not leftovers
    assert {record.status for record in records} == {"needs_review"}


def test_fixed_row_geometry_handles_merged_day_labels() -> None:
    records, _ = map_daily_tokens(
        [OcrToken("0.962", 100, 20, 0.99)],
        source_file="page.jpg",
        table_id="top",
        month_centers=(500, 100) + (500,) * 10,
        day_column_max_x=30,
        daily_y_min=1,
        daily_y_max=1000,
        row_start=20,
        row_step=27,
    )
    assert len(records) == 1
    assert records[0].day == 1


def test_constant_candidate_respects_the_calendar() -> None:
    records = constant_daily_candidates(source_file="page.jpg", table_id="top", year=2010, value=0.0, engine="test")
    assert len(records) == 365
    assert not any(record.month == 2 and record.day == 29 for record in records)


def test_mapping_drops_nonexistent_calendar_dates() -> None:
    records, leftovers = map_daily_tokens(
        [OcrToken("7", 100, 40, 0.99)],
        source_file="page.jpg",
        table_id="top",
        month_centers=(500, 100) + (500,) * 10,
        day_column_max_x=30,
        daily_y_min=1,
        daily_y_max=1000,
        row_start=10,
        row_step=1,
        year=2010,
    )
    assert not records
    assert len(leftovers) == 1
