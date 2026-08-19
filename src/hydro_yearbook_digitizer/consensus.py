from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Iterable


@dataclass(frozen=True)
class RecognitionCandidate:
    """One independent recognition result for a single logical field or cell."""

    engine: str
    value: str
    confidence: float | None = None
    model: str | None = None
    pass_name: str | None = None


@dataclass(frozen=True)
class ConsensusDecision:
    status: str
    selected_value: str | None
    agreeing_engines: tuple[str, ...]
    reasons: tuple[str, ...]


def normalize_candidate(value: str) -> str:
    """Normalize harmless typography without guessing a different digit."""
    return (
        value.strip()
        .replace('，', ',')
        .replace('．', '.')
        .replace('−', '-')
        .replace('—', '-')
        .replace('　', '')
    )


def _numeric_equivalent(left: str, right: str) -> bool:
    try:
        return Decimal(left) == Decimal(right)
    except InvalidOperation:
        return False


def decide_consensus(
    candidates: Iterable[RecognitionCandidate],
    *,
    checks_passed: bool,
    require_distinct_engines: int = 2,
) -> ConsensusDecision:
    """Accept only independent agreement plus passed deterministic checks.

    Confidence scores never resolve a disagreement. A disagreement is routed to
    manual review even when one engine reports a much higher confidence.
    """
    items = tuple(candidates)
    if not items:
        return ConsensusDecision('needs_review', None, (), ('no_recognition_candidate',))

    groups: list[tuple[str, list[RecognitionCandidate]]] = []
    for candidate in items:
        normalized = normalize_candidate(candidate.value)
        for group_value, group_items in groups:
            if normalized == group_value or _numeric_equivalent(normalized, group_value):
                group_items.append(candidate)
                break
        else:
            groups.append((normalized, [candidate]))

    groups.sort(key=lambda item: len({c.engine for c in item[1]}), reverse=True)
    best_value, best_items = groups[0]
    engines = tuple(sorted({candidate.engine for candidate in best_items}))

    reasons: list[str] = []
    if len(engines) < require_distinct_engines:
        reasons.append('insufficient_independent_agreement')
    if len(groups) > 1:
        reasons.append('recognizer_disagreement')
    if not checks_passed:
        reasons.append('deterministic_validation_failed')

    if not reasons:
        return ConsensusDecision('auto_pass', best_value, engines, ())
    return ConsensusDecision('needs_review', None, engines, tuple(reasons))
