from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "hydro-yearbook-digitizer" / "scripts" / "low_resource.py"
SPEC = importlib.util.spec_from_file_location("low_resource", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_affinity_mask_never_exceeds_requested_core_count() -> None:
    assert MODULE.affinity_mask(16, 2) == 0b11
    assert MODULE.affinity_mask(1, 2) == 0b1
    assert MODULE.affinity_mask(8, 0) == 0b1


def test_medium_policy_is_capped_and_never_uses_the_full_machine() -> None:
    assert MODULE.resource_core_limit(16, "medium") == 4
    assert MODULE.resource_core_limit(4, "medium") == 2
    assert MODULE.resource_core_limit(2, "medium") == 1


def test_two_thirds_policy_respects_user_requested_cap() -> None:
    assert MODULE.resource_core_limit(16, "two_thirds") == 10
    assert MODULE.resource_core_limit(8, "two_thirds") == 5
    assert MODULE.resource_core_limit(2, "two_thirds") == 1


def test_three_quarters_policy_respects_user_requested_cap() -> None:
    assert MODULE.resource_core_limit(16, "three_quarters") == 12
    assert MODULE.resource_core_limit(8, "three_quarters") == 6
    assert MODULE.resource_core_limit(2, "three_quarters") == 1
