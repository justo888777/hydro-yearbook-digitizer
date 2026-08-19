from hydro_yearbook_digitizer.identity import resolve_volume_identity, strip_final_station_suffix


def test_station_suffix_normalization_preserves_internal_station_name():
    assert strip_final_station_suffix("于桥水库（电站）站") == "于桥水库（电站）"
    assert strip_final_station_suffix("东堤头（闸上）站") == "东堤头（闸上）"


def test_cover_folder_conflict_is_never_silent():
    result = resolve_volume_identity(
        folder_basin='永定河流域',
        folder_year=1961,
        cover_basin='金沙江流域',
        cover_year=1962,
        cover_title='水文资料汇编',
        cover_confirmed=True,
    )
    assert result.status == 'needs_review'
    assert result.basin == '金沙江流域'
    assert result.year == 1962
    assert len(result.warnings) == 2


def test_consistent_cover_and_folder_resolve():
    result = resolve_volume_identity(
        folder_basin='金沙江流域',
        folder_year=1962,
        cover_basin='金沙江流域',
        cover_year=1962,
        cover_title='水文资料汇编',
        cover_confirmed=True,
    )
    assert result.status == 'resolved'
    assert result.suggested_folder == '金沙江流域/1962'
