from scripts.image_crop_qc import clamp_crop_bounds


def test_partially_outside_bounds_are_clamped() -> None:
    assert clamp_crop_bounds(200, 100, (-5, 10, 30, 110)) == (0, 10, 30, 100)


def test_fully_outside_bounds_are_empty() -> None:
    assert clamp_crop_bounds(200, 100, (220, 10, 240, 30)) is None


def test_reversed_bounds_are_empty() -> None:
    assert clamp_crop_bounds(200, 100, (80, 50, 40, 70)) is None
