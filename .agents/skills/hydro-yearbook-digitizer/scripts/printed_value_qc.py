"""Release-policy helpers for printed daily hydrological variables.

These checks may flag values for review. They never synthesize a delivery
value that is absent from the source table.
"""
from __future__ import annotations


CELL_LOCAL_CANDIDATE_SOURCES = {
    "fixed_cell",
    "isolated_cell_ocr",
    "ppocrv6_medium_rec",
    "source_strong_multivariant",
    "shape_zero",
}


def candidate_is_cell_local(source: str) -> bool:
    """Return whether a candidate is derived only from the registered cell."""

    return str(source or "") in CELL_LOCAL_CANDIDATE_SOURCES


def extraction_decision(*, source_has_table: bool) -> str:
    """Return the only allowed action for a requested variable."""

    return "extract_printed" if source_has_table else "omit_unprinted"


def monthly_mean_rule(variable: str) -> str:
    """Return the validation rule for a normalized printed daily variable."""

    normalized = variable.strip().lower()
    if normalized in {"flow", "流量", "sediment_transport_rate", "输沙率", "悬移质输沙率"}:
        return "arithmetic"
    if normalized in {"sediment_concentration", "含沙量", "悬移质含沙量"}:
        return "printed_independent"
    return "source_definition_required"


def sediment_identity_check(
    flow: float,
    concentration: float,
    printed_transport_rate: float,
    *,
    relative_limit: float = 0.03,
    absolute_limit: float = 0.001,
) -> dict[str, float | str]:
    """Flag Q*C versus printed Qs; retain the printed Qs as the release value."""

    expected_for_qc = float(flow) * float(concentration)
    difference = abs(expected_for_qc - float(printed_transport_rate))
    scale = max(abs(expected_for_qc), abs(float(printed_transport_rate)), 1e-12)
    tolerance = max(float(absolute_limit), float(relative_limit) * scale)
    return {
        "status": "passed" if difference <= tolerance else "needs_source_review",
        "expected_for_qc": expected_for_qc,
        "printed_release_value": float(printed_transport_rate),
        "difference": difference,
    }
