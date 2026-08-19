# Registered visual adjudication and immutable reconciliation

Apply this gate to every visual correction of a daily matrix.

## Registration before reading

1. Prove the logical table identity from its title and source page.
2. Prove the 14-rule day-plus-twelve-month lattice and the non-uniform day-row
   model before interpreting any numeric crop.
3. A review crop must carry enough context to prove its semantic coordinates:
   include the month header and day label, or retain a registered full-table
   image with the crop rectangle overlaid. A day label beside an isolated cell
   is insufficient because a bad vertical boundary can silently select an
   adjacent month.
4. When the cropped value disagrees with the full-table reading, inspect the
   registered full table. If the boundary is wrong, repair geometry and re-read
   the complete affected month; do not choose the more convenient candidate.

## Source values, blanks, and arithmetic

- Preserve a geometry-confirmed source blank as blank. Neither a printed mean,
  a formula, nor a neighbouring zero may fill it.
- Use printed monthly statistics as independent evidence. Arithmetic closure is
  valid only for variables whose printed definition is the arithmetic mean of
  daily values.
- Use `flow * concentration` only to create review signals for printed sediment
  transport rate. Never synthesize or replace a printed variable from it.
- A matching monthly mean does not prove all daily cells. Two wrong values can
  compensate. Any corrected value that changes closure reopens the full month
  for contextual source review.
- If a daily table and monthly summary visibly print different values, preserve
  both and record a `source_conflict`; never edit one source to match the other.

## Immutable reconciliation

1. Hash and retain the recognizer baseline before applying review decisions.
2. Store decisions append-only with table, month, day, old candidate, confirmed
   value or blank, evidence path, method, and timestamp.
3. Build every candidate release by loading the immutable baseline and replaying
   the ordered decisions exactly once. Do not use the previous release as the
   next baseline.
4. Reject duplicate contradictory decisions for the same cell unless a later
   record explicitly supersedes the earlier record and preserves both histories.
5. Run the reconciliation twice and require byte-equivalent normalized release
   JSON. A second run producing changes is a blocking non-idempotence failure.

## Final release checks

- every printed target table is classified exactly once;
- every calendar-valid cell is numeric or a source-confirmed blank;
- every changed month has a registered full-table review record;
- all applicable printed-statistic and monthly-summary checks pass or have a
  documented source conflict;
- formula signals are all source-adjudicated and zero remain blocking;
- every XLSX is read back cell by cell and at least the index plus high-risk
  daily workbooks are rendered;
- the release manifest, source conflicts, timing, and token accounting are
  saved with the delivery.
