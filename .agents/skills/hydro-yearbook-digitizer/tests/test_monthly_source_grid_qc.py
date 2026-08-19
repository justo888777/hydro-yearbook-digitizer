from pathlib import Path
import importlib.util


MODULE = Path(__file__).parents[1] / "scripts" / "monthly_source_grid_qc.py"
SPEC = importlib.util.spec_from_file_location("monthly_source_grid_qc", MODULE)
QC = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(QC)


def token(raw="0"):
    return {"left": 1, "top": 2, "right": 3, "bottom": 4, "raw": raw}


def test_token_may_support_multiple_fields_inside_one_serial():
    result = QC.audit_unique_token_assignments([
        {"serial": 7, "field": "month_10", "token": token()},
        {"serial": 7, "field": "month_11", "token": token()},
    ])
    assert result["status"] == "passed"
    assert result["duplicate_count"] == 0


def test_token_cannot_be_borrowed_by_adjacent_serial():
    result = QC.audit_unique_token_assignments([
        {"serial": 7, "field": "month_12", "token": token("5.48")},
        {"serial": 8, "field": "month_12", "token": token("5.48")},
    ])
    assert result["status"] == "blocked"
    assert result["duplicate_count"] == 1
