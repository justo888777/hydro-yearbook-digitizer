---
name: hydro-yearbook-digitizer
description: Extract photographed or scanned Chinese hydrological yearbooks into source-audited Excel files. Use for station indexes, monthly and annual summaries, and 31-day daily tables when page geometry, cross-page alignment, source provenance, and numerical review matter.
metadata:
  short-description: 水文年鉴表格提取与复核
---

# Hydro Yearbook Digitizer

## Purpose

Turn one hydrological-yearbook volume into clean Excel deliverables while
preserving a source trail for every released value. The target is not an OCR
text dump: it is a table whose row, column, station identity, and value can be
rechecked against the printed source.

Use this skill for Chinese hydrological yearbooks, basin data compilations, and
similar fixed-layout scanned volumes. It covers station overviews, monthly and
annual summaries, and 31-day daily matrices. It does not authorize inventing
missing observations, deriving a variable that the source did not print, or
renaming raw sources.

## Choose the delivery profile first

Ask which profile the requester needs before exporting. The default is the
compact basin delivery:

```text
<basin>/
├─ 站点与目录索引.xlsx
├─ 提取复核记录.xlsx
├─ 数据范围与缺失说明.xlsx
├─ 处理指标记录.xlsx
└─ <year>/
   ├─ 月值/
   │  ├─ <year>-<basin>-流量-月值总表.xlsx
   │  └─ <year>-<basin>-含沙量-月值总表.xlsx
   └─ 日值/<variable>/
      └─ <serial>-<river>-<station>-<variable>-日值表.xlsx
```

- Export only variables actually printed in the requested source.
- A daily workbook is one source station-variable table; a monthly workbook is
  one variable with all stations as rows.
- Keep candidate OCR, crops, model outputs, and review records outside the
  user-facing workbooks. See [delivery profile](references/delivery-profile.md).
- Use the legacy `00_<basin>_<year>_总表.xlsx` profile only when the requester
  explicitly asks for an all-in-one workbook.

## Essential workflow

1. **Inventory and identify.** Keep raw photos/PDFs immutable. Read the cover
   and compare its basin, year, volume, and title with the folder name. A
   folder is supporting evidence, not an authority. Record a conflict; do not
   rename the original source from an OCR result.
2. **Route every page.** Determine orientation per physical page before OCR.
   Classify pages as cover, station index, variable index, monthly/annual
   summary, daily matrix, map, narrative, blank, or unknown. Inventory excluded
   pages. Stop for review when an unknown page may contain requested data.
3. **Register the printed geometry.** Rectify a page or logical table before
   assigning values. A generated browse-PDF is useful for ordering and review,
   but originals or rectified source images remain the OCR evidence.
4. **Read identity from the current source.** Treat a printed table title as an
   atomic year-specific record: serial, river, station, qualifier, variable,
   and unit belong together. Preserve parenthetical qualifiers when they
   distinguish a subtable. A previous workbook or previous year can suggest a
   spelling review, but cannot supply current values or replace the source
   identity.
5. **Recognize, validate, and adjudicate.** Use independent recognition paths
   for critical numeric and identity fields. Apply structural, calendar,
   type, and relevant arithmetic checks. Review disagreements in the original
   registered source context. Preserve an approved visual decision with its
   source location and reason.
6. **Export and read back.** Generate clean workbooks, import them again, and
   compare delivered cells with the approved release matrix. Record timing and
   actual token telemetry separately from local OCR work.

Read [workflow](references/workflow.md) for the full stage sequence and
[quality-control rules](references/qc-rules.md) for the general release policy.

## Source identity and alignment rules

Read [source identity and alignment](references/source-identity-and-alignment.md)
whenever a table spans pages, is photographed at an angle, contains blank
rows, or has station names that differ from an older delivery.

- The current printed title/row owns river and station identity. Never join
  different variable chapters by serial alone.
- A prior delivery is a comparison source, not a donor. Do not order-match a
  missing current table to an old workbook.
- Preserve blank cells and hydrological states (`河干`, `渠干`, ice, trace, and
  similar printed states). An unreadable or physically absent value is blank
  with explicit provenance, never a fabricated zero.
- Register left and right pages independently. Align by physical row evidence,
  not raw OCR token order or one global vertical offset.
- Treat a visual blank run as real row slots. A blank October--December cell or
  a section gap must not pull every following row upward.
- A revised daily row fit that moves by roughly one printed row reopens the
  whole affected month, including previously accepted values.

## Monthly and annual summaries

For a monthly table, bind each row to current-page serial/row evidence, station
fields, twelve month cells, and the printed annual value. Keep section serial
resets as explicit sections instead of treating them as duplicates.

- Derive month bands from grid rules and headers on the current page. Detect
  the annual column independently; December must not absorb it.
- For cross-page spreads, map each right-page row to a left-page row before
  reading late months. Verify the first, middle, and last rows visually.
- Read the printed annual value as source data. Compare it with a day-weighted
  mean of the twelve printed monthly values, including leap February, only
  when the variable definition makes the comparison meaningful.
- The annual comparison is a review signal, never a replacement rule. A
  confirmed source inconsistency remains a documented source conflict.
- Use numeric cell formats that display integers without artificial `.0`.
  In Excel, `General` is normally appropriate for the monthly and annual cells.

Use [data schema](references/data-schema.md) and [quality-control rules](references/qc-rules.md)
for fields, status values, and tolerances.

## Daily matrices

Read [daily-matrix guidance](references/adaptive-daily-matrix.md) and
[printed daily routing](references/printed-daily-routing-and-review.md) before
extracting a daily table.

- Identify the printed variable from the table's own title before numeric OCR.
  Do not create transport-rate data by multiplying flow and concentration when
  the source did not print transport rate.
- Register the outer grid, 12 month columns, day labels, and statistics block.
  A 31-day visual matrix uses six physical groups: 1--5, 6--10, 11--15,
  16--20, 21--25, and 26--31. There is no spacer after day 30.
- Fit row geometry locally by month for perspective or curvature. Check the
  first and last valid row of every month; October--December and rows after
  five-day spacers are high-risk locations.
- Calendar-invalid cells remain blank. Do not shift cells to make a short month
  appear to have 31 values.
- For variables whose printed monthly statistic is an arithmetic daily mean,
  use displayed-precision closure as a check. Printed concentration means can
  be flow-weighted or reporting-defined; retain their independently read
  source value and do not force an arithmetic daily mean.
- A daily table's printed maximum/minimum can be instantaneous rather than an
  extreme of the daily-average sequence. Apply only the source-supported
  relation; never move a value to manufacture a matching occurrence date.

## Station overview and index

Station metadata must remain an atomic physical row. Parse station code, river,
station name, address, longitude, latitude, establishment date, agency, and
remarks from that row or a visibly printed ditto in the same table/page.

- Keep longitude and latitude in separate fields.
- Do not forward-fill genuinely blank address, coordinate, or date cells.
- Recover a merged coordinate only when its same-row source layout and degree/
  minute bounds prove the split; otherwise review it visually.
- A station-code or serial collision across years/variables is not a valid join
  key by itself.

Include the station inventory and a per-year/per-variable availability index in
`站点与目录索引.xlsx`. See [data schema](references/data-schema.md).

## Review and release conditions

Use [visual adjudication](references/visual-adjudication-and-reconciliation.md)
for any source decision. Decisions should be append-only and replayed from an
immutable recognition baseline; do not edit a previously delivered workbook in
place and then call it a validated extraction.

A final delivery is ready only when all of the following are true:

- required pages/tables are accounted for and expected outputs exist;
- every delivered numeric value, blank, or special state has source evidence;
- all applicable identity, calendar, geometry, type, and arithmetic checks pass,
  or a source conflict is explicitly recorded;
- no unresolved OCR or row-alignment item remains;
- every workbook has been read back and matches the approved release data;
- a QC report distinguishes confirmed source blanks from unresolved cells.

Do not claim 100% correctness merely from a high OCR confidence or an aggregate
match. If source resolution cannot support a decision, keep it unresolved and
request a clearer scan or a source review.

## Metrics and resources

Record, at minimum: source-render time, OCR/recognizer time, visual-review time,
export/read-back time, number of logical tables, completed tables, source
conflicts, confirmed blanks, unresolved items, and wall time per completed
table.

Local OCR or local acceleration is not an external API token charge. Report
external model tokens only from actual telemetry; if it is unavailable, say
`unavailable` rather than estimating from pages, characters, or image count.
Select CPU/GPU/NPU at runtime by a representative registered-cell benchmark and
decoder parity. Do not encode one laptop or device model in this skill.

## References by task

| Need | Read |
| --- | --- |
| Source inventory, cover, page routing | [workflow](references/workflow.md), [page routing](references/page-routing.md) |
| Photo ordering or browse PDF | [photo-to-PDF](references/photo-to-pdf.md), [photography guide](references/photography-guide.md) |
| Current-source identity or cross-page alignment | [source identity and alignment](references/source-identity-and-alignment.md) |
| Monthly/annual or station data fields | [data schema](references/data-schema.md), [quality-control rules](references/qc-rules.md) |
| Daily matrices | [daily-matrix guidance](references/adaptive-daily-matrix.md), [printed daily routing](references/printed-daily-routing-and-review.md) |
| Conflicting candidates or source decisions | [recognition consensus](references/recognition-consensus.md), [visual adjudication](references/visual-adjudication-and-reconciliation.md) |
| Workbook/folder names and visual layout | [delivery profile](references/delivery-profile.md) |

## Stop conditions

Pause and request clarification or better evidence when the cover identity is
ambiguous, an unknown page may contain requested data, a required table is
clipped/unreadable, or source evidence cannot distinguish a candidate from an
adjacent row or column. Do not resolve these cases with another year's values,
token order, or mathematical back-calculation.
