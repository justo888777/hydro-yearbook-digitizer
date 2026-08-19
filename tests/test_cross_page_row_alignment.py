from __future__ import annotations

from hydro_yearbook_digitizer import monthly_alignment as MODULE


def _serial_items(first: int, last: int, missing: set[int]) -> list[dict[str, object]]:
    return [
        {"text": str(serial), "x": 5.0, "y": 100.0 + (serial - first) * 25.0, "source": "fixture"}
        for serial in range(first, last + 1)
        if serial not in missing
    ]


def test_missing_serial_glyphs_do_not_remove_logical_rows() -> None:
    slots, audit = MODULE.reconstruct_left_serial_slots(
        _serial_items(41, 80, {65, 79}),
        serial_x0=0,
        serial_x1=10,
        y0=80,
        y1=1200,
        first_serial=41,
        last_serial=80,
    )
    assert [slot.serial for slot in slots] == list(range(41, 81))
    assert audit["interpolated_missing_serial_glyph_count"] == 2
    assert slots[24].method == "interpolated_missing_serial_glyph"
    assert slots[38].method == "interpolated_missing_serial_glyph"


def test_bad_serial_glyph_retains_its_physical_row_baseline() -> None:
    slots, audit = MODULE.reconstruct_left_serial_slots(
        [
            {"text": "1", "x": 5.0, "y": 100.0},
            {"text": "8", "x": 5.0, "y": 125.0},
            {"text": "3", "x": 5.0, "y": 150.0},
        ],
        serial_x0=0,
        serial_x1=10,
        y0=80,
        y1=200,
        first_serial=1,
        last_serial=3,
    )
    assert slots[1].y == 125.0
    assert slots[1].method == "physical_row_bad_serial_glyph"
    assert audit["bad_serial_glyph_baseline_count"] == 1


def test_numeric_zero_is_right_page_row_evidence() -> None:
    assert MODULE.is_right_row_evidence(0)


def test_right_blank_slots_are_explicit_not_a_constant_offset_shift() -> None:
    slots, _ = MODULE.reconstruct_left_serial_slots(
        _serial_items(41, 50, set()),
        serial_x0=0,
        serial_x1=10,
        y0=80,
        y1=400,
        first_serial=41,
        last_serial=50,
    )
    # Serial 45 has a fully blank right-side row and therefore no OCR baseline.
    groups = [{"y": 300.0 + 11.0 * index} for index in range(9)]
    mapping, audit = MODULE.align_right_baselines(slots, groups)
    assert audit["method"] == "monotone_fallback_due_to_right_blank_rows"
    assert audit["unmatched_left_slots"] == [45]
    assert mapping[41] == 300.0
    assert mapping[50] == 388.0
    assert 300.0 < mapping[45] < 388.0


def test_physical_rows_retain_a_missing_terminal_serial_glyph() -> None:
    count, audit = MODULE.infer_expected_row_count(
        first_serial=41,
        observed_serials=list(range(41, 80)),
        physical_row_count=40,
    )
    assert count == 40
    assert audit["observed_serial_max"] == 79
    assert audit["source"] == "physical_rows"


def test_implausible_large_serial_does_not_create_fictitious_rows() -> None:
    count, audit = MODULE.infer_expected_row_count(
        first_serial=1,
        observed_serials=[*range(1, 106), 134],
        physical_row_count=106,
    )
    assert count == 106
    assert audit["source"] == "physical_rows_discarded_implausible_terminal_serial"


def test_small_observed_excess_can_extend_a_physical_count() -> None:
    count, audit = MODULE.infer_expected_row_count(
        first_serial=1,
        observed_serials=list(range(1, 43)),
        physical_row_count=40,
    )
    assert count == 42
    assert audit["source"] == "physical_rows_with_plausible_serial_extension"
