# Changelog

## 0.2.27 - 2026-08-19

- Fix the public Windows CI environment by installing NumPy, which is required
  by the daily-grid geometry regression tests.
- Supersedes `0.2.26` as the recommended stable public release; the extraction
  library and Skill behavior are otherwise unchanged.

## 0.2.26 - 2026-08-19

First public release based on the internal 0.2.25 workflow.

- Reorganized the Codex Skill into a concise public entrypoint with task-routed
  references.
- Added source-title-first identity, cross-page row-ownership, source-blank,
  and month-local daily-grid guidance.
- Standardized compact basin delivery names for daily tables, monthly summaries,
  and the basin station/directory index.
- Clarified that printed annual values are transcribed source data while
  calculated annual values are validation evidence.
- Clarified Excel numeric presentation so integers do not display artificial
  decimal points.
- Added English and Simplified Chinese public documentation, license, contributor
  guidance, and release-oriented ignore rules.

## Internal history

Internal regression notes and case-specific repair logs are intentionally not
included in this public release. They should not be treated as public examples
or public performance claims.
