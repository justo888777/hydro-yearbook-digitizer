# Daily/monthly release gate

Use this checklist after OCR and before workbook export. It is a release gate,
not a method for repairing a number by inference.

## 1. Printed-variable inventory

- Record each daily-table title and its source page.
- `source_has_table=true` permits transcription; `false` means omit the table.
- Never generate sediment transport rate from flow and concentration.
- A damaged or wholly obscured printed table stays omitted or blank with a
  source-damage record.

## 2. Geometry and calendar

- Correct page rotation before locating the outer grid.
- Register January through December from printed headers and vertical rules.
- Register days 1--31 from the day column and wider gaps after days 5, 10, 15,
  20, and 25.
- Leave calendar-invalid day cells blank. A blank is not zero.
- Verify the first and last daily rows plus all month boundaries from the
  source image; numeric OCR token order is never a grid coordinate.

## 3. Identity

- Read the current table's serial, river, station, qualifier, variable, unit,
  and page.
- Compare river/station identity with the current year's monthly and station
  vocabularies.
- Treat year-specific suffixes and station numbering as source truth. Do not
  propagate identity by a previous year's serial.

## 4. Value and statistic checks

- Require two independent readings or a locked visual decision for disputed
  cells.
- Flow and printed transport rate: arithmetic monthly-mean closure applies.
- Concentration: the printed monthly mean is independently transcribed and is
  not the arithmetic mean of daily concentrations unless the source explicitly
  defines it that way.
- Concentration and printed transport rate are nonnegative. A negative daily
  flow is permitted only when the same table's printed minimum/mean or an
  exact-cell visual decision independently proves the source value.
- Use `Q*C` versus printed transport rate only to prioritize source review.
  Keep the printed rate in the deliverable even when the check fails.

## 5. Monthly/annual summary checks

- Attach late-month and annual cells to left-page serial slots before reading
  values from a facing page.
- Preserve consecutive source blanks and prove top/bottom mapping.
- Read the annual mean from the source. For twelve complete months, compare it
  with the day-weighted monthly mean, including leap February.
- Do not calculate a full-year value for an incomplete printed period.
- Keep a source-confirmed discrepancy as an audited source conflict.
- When the daily table's own printed mean conflicts with a separate monthly
  summary, close daily cells against the statistic printed on that same daily
  table and report the summary conflict separately. A cross-page-shifted
  summary must never overwrite a source-readable daily statistic.

## 6. Release evidence

- Zero unresolved OCR, geometry, identity, or cross-page alignment flags.
- Append-only source decisions retained.
- Every XLSX imported and compared with release data.
- Representative daily, flow-summary, sediment-summary, and source-damage
  sheets rendered and visually inspected.
- Numeric format is `General`; integers display without a trailing decimal.
- Report table count, wall time, average time per table, local OCR API tokens,
  and Codex/session tokens only when telemetry exists.
