from scripts.monthly_photo_grid_qc import (
    fit_column_first_row_offsets,
    geometry_fingerprint,
)


def test_fit_diagonal_ignores_row_two_first_token():
    offsets = fit_column_first_row_offsets(
        [100, 200, 300, 400], [320, 324, 328, 384], 320, 52,
    )
    assert offsets == [0, 4, 8, 12]


def test_geometry_cache_changes_with_crop_target():
    rows = [{"row": 1, "area_target": {"cx": 10}, "month_targets": [], "annual_target": {"cx": 20}}]
    original = geometry_fingerprint(rows)
    rows[0]["annual_target"] = {"cx": 21}
    assert geometry_fingerprint(rows) != original
