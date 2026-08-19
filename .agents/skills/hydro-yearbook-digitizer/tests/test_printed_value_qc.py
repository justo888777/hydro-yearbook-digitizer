from scripts.printed_value_qc import candidate_is_cell_local


def test_registered_cell_candidate_is_local() -> None:
    assert candidate_is_cell_local("isolated_cell_ocr")


def test_neighbour_or_formula_candidate_is_not_local() -> None:
    assert not candidate_is_cell_local("augmented_full_raw")
    assert not candidate_is_cell_local("printed_mean_candidate")
    assert not candidate_is_cell_local("water_level_integer_carry_expansion")
