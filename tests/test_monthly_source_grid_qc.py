from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "hydro-yearbook-digitizer" / "scripts" / "monthly_source_grid_qc.py"
SPEC = importlib.util.spec_from_file_location("monthly_source_grid_qc", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_terminal_serial_omission_blocks_release() -> None:
    result = MODULE.validate_serial_slots(list(range(121, 148)), 121, 148)
    assert result["status"] == "blocked"
    assert result["missing"] == [148]
    assert MODULE.validate_serial_slots(list(range(121, 149)), 121, 148)["status"] == "passed"


def test_overlapping_month_bands_block_duplicate_cell_assignment() -> None:
    assert MODULE.validate_numeric_column_bands([(0, 10), (9, 19)], 2)["status"] == "blocked"
    assert MODULE.validate_numeric_column_bands([(0, 10), (10, 20)], 2)["status"] == "passed"


def test_right_page_mapping_requires_one_monotone_baseline_per_serial() -> None:
    left = {1: 100, 2: 120, 3: 140}
    assert MODULE.validate_row_baseline_mapping(left, {1: 110, 2: 131, 3: 151})["status"] == "passed"
    assert MODULE.validate_row_baseline_mapping(left, {1: 110, 3: 151})["status"] == "blocked"


def test_ditto_expansion_does_not_fill_a_true_blank() -> None:
    assert MODULE.expand_same_table_ditto('"', "潮河") == "潮河"
    assert MODULE.expand_same_table_ditto("", "潮河") == ""


def test_source_serial_resets_are_validated_per_visual_section() -> None:
    sections = [list(range(1, 87)), list(range(1, 12)), list(range(1, 14))]
    result = MODULE.validate_sectioned_serial_slots(sections, [(1, 86), (1, 11), (1, 13)])
    assert result["status"] == "passed"
    assert result["observed_sections"] == 3


def test_blockwise_alignment_preserves_an_unprinted_right_row_slot() -> None:
    result = MODULE.align_blockwise_row_baselines(
        [[100, 120, 140], [220, 240, 260]],
        [[110, 130, 150], [230, 270]],
    )
    assert result["status"] == "passed"
    assert result["blocks"][1]["missing_left_indices"] == [1]
