from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "hydro-yearbook-digitizer" / "scripts" / "printed_value_qc.py"
SPEC = importlib.util.spec_from_file_location("printed_value_qc", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_unprinted_variable_is_omitted_instead_of_derived() -> None:
    assert MODULE.extraction_decision(source_has_table=False) == "omit_unprinted"


def test_concentration_mean_is_an_independent_printed_statistic() -> None:
    assert MODULE.monthly_mean_rule("含沙量") == "printed_independent"
    assert MODULE.monthly_mean_rule("输沙率") == "arithmetic"


def test_sediment_identity_check_never_replaces_the_printed_rate() -> None:
    result = MODULE.sediment_identity_check(2, 3, 5)
    assert result["status"] == "needs_source_review"
    assert result["expected_for_qc"] == 6
    assert result["printed_release_value"] == 5
