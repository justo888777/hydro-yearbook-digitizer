# Hydro Yearbook Digitizer

[简体中文](README_CN.md) | English

Hydro Yearbook Digitizer is an auditable workflow and Codex skill for turning
scanned or photographed hydrological yearbooks into clean Excel workbooks. It
is designed for station inventories, monthly/annual summaries, and 31-day daily
tables where table geometry and source traceability matter as much as OCR text.

## What it does

- reads the cover and inventories every source page before extraction;
- handles page rotation, two-page spreads, photographed skew, blank rows, and
  daily matrices with non-uniform five-day spacer bands;
- extracts only variables printed by the source, including printed annual values;
- keeps river/station identity tied to the current printed source title or row;
- uses independent readings, deterministic calendar/geometry checks, and
  registered-source review for disagreements;
- produces clean Excel delivery files plus separate QC/audit records.

## Accuracy boundary

This project prevents silent guessing; it does not make an unreadable scan
readable. A source value is released only with source evidence and applicable
checks. Printed blanks and states remain blank/text, and a confirmed source
inconsistency is recorded rather than overwritten to satisfy a formula.

## Install

```bash
python -m pip install -e ".[image,dev]"
pytest -q
```

Optional OCR backends are intentionally separated:

```bash
python -m pip install -e ".[ocr]"
# or, in a separately validated environment:
python -m pip install -e ".[table]"
```

Use the environment and accelerator that pass a representative registered-cell
parity test. Hardware names and device-specific settings belong in local
deployment configuration, not in the reusable workflow.

## Codex skill

The skill entrypoint is:

```text
.agents/skills/hydro-yearbook-digitizer/SKILL.md
```

Copy that skill folder into the appropriate Codex skill location or keep this
repository as the active workspace and invoke:

```text
$hydro-yearbook-digitizer
```

Read the skill's linked references only for the table family being processed.
The public entrypoint is deliberately concise; detailed source-alignment and
delivery requirements live beside it.

## Standard output

```text
<basin>/
├─ 站点与目录索引.xlsx
├─ 提取复核记录.xlsx
├─ 数据范围与缺失说明.xlsx
├─ 处理指标记录.xlsx
└─ <year>/
   ├─ 月值/<year>-<basin>-<variable>-月值总表.xlsx
   └─ 日值/<variable>/<serial>-<river>-<station>-<variable>-日值表.xlsx
```

The monthly workbook keeps the independently transcribed printed annual value.
Any calculated annual comparison is a QC record and does not replace the
source value. Daily data use a 31-by-12 calendar matrix; calendar-invalid dates
stay blank.

## Command-line utilities

```bash
hydro-yearbook init --root ./资料库 --basin 永定河流域 --year 1962
hydro-yearbook photos-to-pdf raw/photos/*.jpg --output work/documents/source_browse.pdf
hydro-yearbook --help
```

The generated browse PDF is an aid for page-order review. Preserve the original
photos/PDFs and use originals or rectified derivatives as recognition evidence.

## Development

```bash
python -m pip install -e ".[dev]"
pytest -q
```

The public source archive contains no raw yearbooks, user output, API keys, or
machine-specific deployment profiles. See [CONTRIBUTING.md](CONTRIBUTING.md)
before opening a change.

## Release candidate status

This directory is the `v0.2.27` public release source. See
[CHANGELOG.md](CHANGELOG.md) for the release scope and
[the GitHub repository](https://github.com/justo888777/hydro-yearbook-digitizer)
for source and issue tracking.

The release ZIP contains the Codex Skill and all public documentation. The
Python wheel contains the reusable library and CLI; install the Skill folder
from the ZIP when using Codex.

## License

[MIT](LICENSE)
