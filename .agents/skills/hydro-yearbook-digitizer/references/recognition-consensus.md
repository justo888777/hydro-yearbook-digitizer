# Multi-recognizer consensus and manual review

## Requirement

Every critical numeric cell and every folder-defining cover field must have at least two independent recognition results before automatic acceptance.

A recognition pass is independent only when it uses a different engine or a materially different evidence scope. Recommended configuration:

1. `vlm_context`: full table or full row with structural context;
2. `vlm_cell`: isolated high-resolution cell crop with no previous answer shown;
3. `ocr_local`: optional local OCR candidate.

Two prompts sent to the same model are useful as repeat readings, but they must not be described as two different models. Record the actual engine and model identifiers.

## Decision matrix

| Situation | Result |
|---|---|
| Two distinct engines agree and all deterministic checks pass | `auto_pass` |
| Engines disagree | `needs_review` |
| Engines agree but arithmetic or cross-table check fails | `needs_review` |
| Only one engine produced a usable value | `needs_review` |
| Human confirms source value | `verified` |
| Printed sources conflict | `source_conflict` |

Confidence scores may prioritize the review queue but must never silently resolve a disagreement.

Two engines can make the same crop or scan-line error. Engine agreement does
not override annual-mean arithmetic, row-slot geometry, physical-sign checks,
or a conflicting high-resolution page read. A source-confirmed blank is a
resolved decision; an OCR engine returning no token is not enough by itself.

For long monthly spreads, consensus is evaluated after blockwise row
registration. Do not compare candidates that were assigned by one global
left/right offset after a blank late-month row. Printed serial resets are
compared within their water-system section.

## Review package

Each review item must include:

- source photo and source ID;
- rectified page and table image;
- row/column identity;
- enlarged cell crop and preprocessing variants;
- every candidate value, engine, model, prompt/pass name, and confidence;
- failed validation rules;
- effect on monthly/annual statistics;
- final reviewer decision, reviewer, timestamp, and note.
