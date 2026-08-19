# Contributing

Thank you for improving the digitizer. Please keep changes narrow, reproducible,
and tied to an observed source-layout or data-quality failure.

## Before opening a change

- Do not commit scanned yearbooks, extracted user data, personal paths, API keys,
  credentials, or hardware-specific deployment settings.
- Describe the source layout/failure mode without publishing restricted source
  images. Use a synthetic or permission-cleared fixture when a regression test is
  needed.
- Preserve the distinction between a printed source blank, a printed state, an
  unreadable cell, and a confirmed source conflict.
- Do not add a derived delivery variable unless the printed source includes it.

## Tests and documentation

Run the relevant tests plus the full suite before proposing a change:

```bash
python -m pip install -e ".[dev]"
pytest -q
```

When changing a Skill instruction, keep the entrypoint short and move
table-family-specific procedures into linked references. When changing filename
or workbook behavior, add an observable test and update the delivery profile.

## Review expectations

Changes must retain source provenance, prevent row/column shifts, and avoid
silently replacing printed values to satisfy arithmetic checks. Do not add
machine-specific acceleration settings to the reusable Skill.
