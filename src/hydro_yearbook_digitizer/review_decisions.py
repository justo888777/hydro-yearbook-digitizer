"""Reusable release gates for exact-set visual review decisions."""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Sequence


def validate_exact_review(
    payload: dict,
    pending_keys: Iterable[Sequence[Hashable]],
    *,
    key_fields: Sequence[str],
    decisions_field: str = "decisions",
    status_field: str = "review_status",
    approved_status: str = "approved",
    resolution_field: str | None = "decision",
    allowed_resolutions: set[str] | None = None,
) -> dict[tuple[Hashable, ...], dict]:
    """Return decisions by key or raise when the release set is not exact."""
    if payload.get(status_field) != approved_status:
        raise ValueError("visual review payload is not approved")
    decisions = payload.get(decisions_field, [])
    keys = [tuple(row.get(field) for field in key_fields) for row in decisions]
    if len(keys) != len(set(keys)):
        raise ValueError("visual review contains duplicate decision keys")
    expected = {tuple(key) for key in pending_keys}
    actual = set(keys)
    if actual != expected:
        missing = sorted(expected - actual, key=repr)
        extra = sorted(actual - expected, key=repr)
        raise ValueError(f"visual review key mismatch; missing={missing[:10]} extra={extra[:10]}")
    if resolution_field and allowed_resolutions is not None:
        invalid = [
            key for key, row in zip(keys, decisions, strict=True)
            if row.get(resolution_field) not in allowed_resolutions
        ]
        if invalid:
            raise ValueError(f"visual review contains invalid resolutions: {invalid[:10]}")
    return dict(zip(keys, decisions, strict=True))
