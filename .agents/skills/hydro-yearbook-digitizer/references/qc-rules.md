# Quality-control rules

## Quality objective

No photographic transcription system can honestly guarantee perfect recognition from every image. The operational target is:

1. maximize correct automatic acceptance;
2. route every uncertainty or inconsistency to review;
3. release a final dataset only after required review items are resolved.

## Structural checks

- Expected row and column counts.
- Month labels ordered January through December.
- Day labels ordered 1 through 31.
- Statistical rows occur below the daily grid.
- Table title, station identity, variable, and unit are present or resolved from adjacent pages.
- Split a two-page spread into visual row blocks at subheadings and large gaps;
  validate left/right row baselines inside each block.
- Treat a printed serial restart under a new water-system heading as a new
  section, not a duplicate. Export the section identity with the source serial.
- If the right half omits an all-blank late-month row, preserve its left-side
  identity slot and source blanks instead of shifting every following row.

## Calendar checks

- Reject February 30 and 31.
- Apply leap-year rules to February 29.
- Reject day 31 for April, June, September, and November.
- Mark structurally invalid dates as `NOT_APPLICABLE`, not zero.

## Type checks

- Daily flow, sediment transport rate, suspended-sediment concentration, and precipitation are nonnegative; an apparent negative daily cell requires exact-crop review.
- Monthly mean flow and monthly mean sediment transport rate are also nonnegative. A negative sign on these summary rows remains a review item even when two OCR engines agree, because both may reproduce the same scan-line artifact.
- A negative value in a monthly algebraic balance, storage-change, or difference row may be legitimate. Decide it from the row identity and source, not a universal sign rule.
- Water level may be negative depending on the printed datum; do not apply a universal nonnegative rule.
- Preserve printed precision.
- Normalize OCR variants such as `O` versus `0` only when the visual evidence and field type agree.

## Arithmetic checks

Where derivable, recompute:

- monthly mean;
- monthly maximum and occurrence date;
- monthly minimum and occurrence date;
- annual mean;
- annual extrema;
- runoff or sediment metrics when the formula and units are unambiguous.

Arithmetic checks never authorize creation of an unprinted delivery variable.
In particular, `flow * concentration` may flag a printed transport-rate value
for review but may not synthesize or replace that value.

A successful aggregate closure does not prove the underlying daily cells.
Compensating transcription errors can leave the same monthly mean. After any
cell correction that changes an arithmetic result, re-read the complete month
from a registered full-table view before closing the review item.

Use decimal arithmetic and a tolerance based on printed precision. Do not compare binary floating-point values for exact equality.

Agreement between recognizers is necessary but not sufficient. If a printed
annual value fails the day-weighted twelve-month check by a material amount,
review the exact monthly and annual cells even when both engines agree. This
gate catches shared decimal-point and sign artifacts that confidence or voting
cannot detect.

## Cross-table checks

- Station order, code, name, river, and catchment area must agree with the station index.
- Monthly/annual summary values should agree with the corresponding daily table after rounding.
- Units must agree between title, summary table, and workbook metadata.
- Comparison-table annual values should agree with summary or daily-derived values when they represent the same definition.
- A station-index blank remains blank unless the source cell contains an
  explicit ditto mark. Do not forward fill address or coordinate fields.
- Longitude and latitude must occupy separate output fields.

## Recognition consensus

Recommended states:

- `auto_pass`: two independent readings agree and all applicable checks pass;
- `needs_review`: readings disagree or a check fails;
- `verified`: a reviewer confirmed the value;
- `source_conflict`: the printed source is internally inconsistent and the conflict is documented.

## Review priority

1. station identity and unit conflicts;
2. decimal point and order-of-magnitude conflicts;
3. cells affecting monthly maxima/minima;
4. cells causing monthly-mean mismatch;
5. remaining model disagreements;
6. cosmetic or noncritical metadata.

## Release gate

A final release must report:

- source images and pages;
- tables processed;
- cells extracted;
- automatic acceptance rate;
- manually reviewed cells;
- unresolved cells;
- source conflicts;
- validation failures;
- software and template version.

For a final delivery, unresolved cells, unexplained row slots, and workbook
read-back mismatches must all equal zero. A recognition percentage below 100%
may describe work in progress but cannot satisfy this gate.

An exact registered-source inspection may prove that a requested cell or table
is physically absent or unprinted. Record this as `source_scan_missing`, keep
the released value blank, and retain the source crop plus reviewer basis. This
is a resolved source exception, not an unresolved OCR cell. Never infer it from
nearby values, replace it with zero, or borrow it from another row, month, page,
station, or year.

The final release must be rebuilt by replaying append-only decisions from an
immutable recognition baseline. Re-running the replay must produce no further
normalized data changes; otherwise the release is non-idempotent and blocked.


## Cover and folder identity checks

- Cover basin/year/title must be compared with folder and manifest values.
- A conflict is blocking until human approval.
- Never silently rename a source folder from model output.

## Variable-availability checks

- A nonblank printed page number implies availability for that station-variable family.
- An extracted daily or summary table should be represented in the availability index when that index exists.
- An availability flag without a corresponding photographed table is reported as potentially missing source coverage, not automatically treated as an OCR error.

## Page routing checks

- Source inventory count must equal the count of classified pages/photos after declared split rules.
- Maps and narrative pages must be listed as exclusions.
- Unknown pages block release when they may contain required data.

## Consensus checks

- Auto-pass requires at least two distinct engines, not merely two prompts to the same engine.
- Confidence cannot resolve disagreement.
- Every manual override must preserve all original candidates.

## Quality report outputs

Release requires `QC_REPORT.html`, `QC_CHECKLIST.xlsx`, and `completion_report.md`.
