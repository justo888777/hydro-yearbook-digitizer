from __future__ import annotations

from hydro_yearbook_digitizer import month_cell as MODULE


def test_final_month_accepts_a_fractionally_left_ocr_centre() -> None:
    # A sub-pixel rule can be slightly right of the correct OCR centre.
    assert MODULE.numeric_center_in_month_cell(2752.0, 2752.635, 2865.0)


def test_tolerance_does_not_accept_the_previous_month_value() -> None:
    assert not MODULE.numeric_center_in_month_cell(2748.0, 2752.635, 2865.0)
    assert not MODULE.numeric_center_in_month_cell(2864.0, 2752.635, 2865.0)
