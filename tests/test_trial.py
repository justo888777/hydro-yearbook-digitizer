import json

import pytest

pytest.importorskip("PIL")
from PIL import Image

from hydro_yearbook_digitizer.trial import (
    estimate_gpt56_original_tokens,
    run_trial_audit,
    validate_trial_release,
)


def test_gpt56_original_token_estimate_uses_32px_patches() -> None:
    assert estimate_gpt56_original_tokens(33, 64) == 4


def test_trial_audit_has_complete_classification_and_required_reports(tmp_path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    Image.new("RGB", (100, 50), "white").save(source / "cover.jpg")
    Image.new("RGB", (100, 50), "white").save(source / "map.jpg")
    output = tmp_path / "outputs"

    records = run_trial_audit(
        source,
        output,
        project_name="fixture",
        classes={"cover.jpg": "cover", "map.jpg": "map"},
        master_workbook_path=output / "00_fixture_1962_总表.xlsx",
    )

    assert len(records) == 2
    assert len(json.loads((output / "source_inventory.json").read_text(encoding="utf-8"))) == 2
    assert (output / "QC_REPORT.html").is_file()
    assert (output / "QC_CHECKLIST.xlsx").is_file()
    assert (output / "completion_report.md").is_file()
    assert (output / "00_fixture_1962_总表.xlsx").is_file()
    assert "Unknown pages: 0" in (output / "completion_report.md").read_text(encoding="utf-8")
    assert validate_trial_release(output).ok


def test_unknown_page_blocks_release(tmp_path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    Image.new("RGB", (100, 50), "white").save(source / "unclassified.jpg")
    output = tmp_path / "outputs"

    run_trial_audit(source, output, project_name="fixture")

    result = validate_trial_release(output)
    assert not result.ok
    assert result.errors == ("unknown pages block release: 1",)
