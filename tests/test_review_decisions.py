import pytest

from hydro_yearbook_digitizer.review_decisions import validate_exact_review


PENDING = {("table-1", 1, 2), ("table-2", 3, 4)}


def valid_payload():
    return {
        "review_status": "approved",
        "decisions": [
            {"table_id": "table-1", "month": 1, "day": 2, "decision": "source_visual_approved"},
            {"table_id": "table-2", "month": 3, "day": 4, "decision": "source_visual_approved"},
        ],
    }


def validate(payload):
    return validate_exact_review(
        payload,
        PENDING,
        key_fields=("table_id", "month", "day"),
        allowed_resolutions={"source_visual_approved"},
    )


def test_accepts_exact_approved_set():
    result = validate(valid_payload())
    assert set(result) == PENDING


def test_rejects_draft():
    payload = valid_payload()
    payload["review_status"] = "draft_not_approved"
    with pytest.raises(ValueError, match="not approved"):
        validate(payload)


def test_rejects_missing_or_extra_key():
    payload = valid_payload()
    payload["decisions"].pop()
    with pytest.raises(ValueError, match="key mismatch"):
        validate(payload)


def test_rejects_duplicate_and_invalid_resolution():
    payload = valid_payload()
    payload["decisions"][1] = dict(payload["decisions"][0])
    with pytest.raises(ValueError, match="duplicate"):
        validate(payload)
    payload = valid_payload()
    payload["decisions"][0]["decision"] = "draft_not_approved"
    with pytest.raises(ValueError, match="invalid resolutions"):
        validate(payload)
