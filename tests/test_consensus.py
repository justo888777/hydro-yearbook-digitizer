from hydro_yearbook_digitizer.consensus import (
    RecognitionCandidate,
    decide_consensus,
)


def test_two_distinct_engines_and_checks_auto_pass():
    decision = decide_consensus(
        [
            RecognitionCandidate('vlm_context', '0.085'),
            RecognitionCandidate('vlm_cell', '0.0850'),
        ],
        checks_passed=True,
    )
    assert decision.status == 'auto_pass'
    assert decision.selected_value == '0.085'


def test_disagreement_requires_review_even_with_confidence_gap():
    decision = decide_consensus(
        [
            RecognitionCandidate('vlm_context', '0.085', confidence=0.99),
            RecognitionCandidate('ocr_local', '0.065', confidence=0.40),
        ],
        checks_passed=True,
    )
    assert decision.status == 'needs_review'
    assert 'recognizer_disagreement' in decision.reasons


def test_failed_arithmetic_check_requires_review():
    decision = decide_consensus(
        [
            RecognitionCandidate('vlm_context', '12.4'),
            RecognitionCandidate('ocr_local', '12.4'),
        ],
        checks_passed=False,
    )
    assert decision.status == 'needs_review'
    assert 'deterministic_validation_failed' in decision.reasons
