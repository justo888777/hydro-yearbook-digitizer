# Printed daily-table routing and zero-unresolved review

Use this gate before extracting a large yearbook section containing visually
similar matrices.

1. Split a source page into logical table regions and classify each region from
   its own title strip. Accept only titles that explicitly state daily mean
   flow, daily mean suspended-sediment transport rate, or daily mean sediment
   concentration. Reject water-level, water-temperature, particle-size,
   precipitation, evaporation, comparison, and statistics-only lookalikes.
2. Read the printed serial from the leading title field. Digits in units,
   catchment area, parenthetical channel labels, and notes are not serial
   candidates. An ambiguous or missing leading serial requires a source-title
   crop decision before extraction.
3. Register each accepted 31 by 12 body from its physical rules, month labels,
   day labels, and five-day spacers. A day column plus 12 month columns must
   have exactly 14 ordered vertical rules. Retain plausible outer rules from
   0.3% of image width; a stricter cutoff can discard the true left border and
   shift January-November by one column. When one interior rule and an outer
   rule are faint, fit a 14-rule arithmetic lattice from every candidate pair
   and candidate-index gap. Rank by unique rule support, internal holes, the
   widest long horizontal rule's two edge anchors, then residual error. Never
   compress twelve observed intervals into thirteen merely to use the first
   and last detected vertical lines. Store a cell rectangle for every
   valid calendar date, including leap-day handling.
   When more than fourteen long-rule candidates survive, score every
   contiguous fourteen-rule window. Reject a window whose largest gap error
   exceeds 25% of its median pitch. Prefer the regular window whose first
   interval contains the printed day/month diagonal; otherwise minimize
   lattice error and page/spine line-strength outliers. If exactly fourteen
   candidates remain but one edge gap is over 1.45 times the regular pitch,
   treat the isolated page edge as an artifact and extrapolate the missing
   opposite outer rule. A count of fourteen alone is not a registration pass.
   If the horizontal header pair is broken, recover its top/bottom from the
   endpoints of that same printed diagonal before using row projection. A
   temporarily bridged tall header may recover the remaining geometry, but the
   returned bounds must be the real printed header bounds.
   Apply an outlier gate to the footer when the first statistics-line gap is
   greater than both 50 pixels and 2.5 times the median of the remaining row
   gaps. Do not blindly discard that first line: learn the daily-body-height
   ratio from regular tables in the same book and choose the candidate footer
   top closest to that ratio while leaving at least six footer boundaries.
   Then refit all 31 day rows; repairing only the footer still leaves the
   daily body vertically compressed.
   If the selected footer begins with an interval that is an integer multiple
   of the surviving 15-45 px footer-row pitch, insert the missing internal
   rules before reading Average, Maximum, date, Minimum, and date. A 70 px
   first interval may be three 23 px rows, not one tall Average cell.
   Finally, require the fitted day-1 to day-31 span to cover 78%-102% of the
   registered daily body. A visually regular five-day pattern can still be a
   compressed false fit in the middle of the table. Reject it and fall back to
   the verified header-to-footer 31-row template before any OCR is released.
4. Run a primary registered-table recognizer and a genuinely independent OCR
   engine. Re-read non-agreeing cells as enlarged isolated crops with two
   preprocessings. Expand tight registered bounds horizontally and vertically
   (a tested starting point is 3 and 5 pixels before enlargement) so top/bottom
   strokes and decimal points are not clipped. For Paddle 3.x on Windows,
   recognition-only batches over registered cells avoid detector/oneDNN fused
   convolution failures; keep IR optimization only when oneDNN is explicitly
   disabled. A repeat of the same model is useful segmentation evidence but is
   not independent model consensus.
5. State/ditto handling must tolerate an omitted fixed-cell result. Resolve a
   ditto glyph only from a state printed in the same logical table; do not
   inherit from another station, page, or year. In concentration tables,
   `河干` or `渠干` starts a dry-run and following printed ditto marks are source
   blanks, not numeric zero. End that run only at a directly read numeric cell
   with sufficient recognition confidence and full-glyph ink coverage, or at
   another explicit state marker; ambiguous or low-ink pseudo-zero glyphs
   inside the run stay blank and retain their source coordinates.
6. For flow and printed transport rate, require the daily arithmetic mean to
   agree with the printed monthly mean under its displayed precision and, when
   available, with the separate monthly summary table. Sediment-concentration
   monthly statistics remain independent printed values. If the independently
   verified monthly master stores only numeric values and has lost trailing
   zeros, reconstruct the documented three-significant-digit display precision
   from value magnitude; do not borrow precision from a shifted daily-stat OCR
   cell.
7. Preserve geometry-confirmed blank source cells as blank. A printed monthly
   mean/maximum of zero may prove an inked numeric cell is zero, but it may not
   turn a visually blank cell into zero.
8. Any remaining disagreement goes to a registered source review. A contact
   crop must include the month header and day label, or be traceable to an
   overlaid rectangle on the full table; a cell crop whose horizontal boundary
   is already wrong can otherwise display an adjacent month convincingly.
   Record the confirmed value and evidence. If one correction changes monthly
   closure, review the complete affected month from the registered full table;
   a matching mean alone cannot exclude compensating cell errors. Numeric
   sediment values remain nonnegative.
   A negative daily flow is blocked by default but is allowed when the same
   printed table has a negative monthly mean/minimum or the exact source cell
   has been visually confirmed. Release requires zero unresolved cells, zero
   duplicate table identities, exact calendar counts, workbook read-back
   equality, idempotent replay from an immutable recognition baseline, and a
   retained audit manifest.
## Cross-column row shear and slight perspective

Before assigning one global day-row center to all twelve month columns, measure long horizontal table rules. A slope of only `0.0015` produces about 3 px of cross-table drift on a 2000 px crop; on 15–18 px text this is already material. When the drift exceeds the safe margin, either affine-rectify the crop around its horizontal midpoint before OCR or project the 1–31 day-label lattice into each month column. Re-render the registered cells after rectification: OCR evidence produced from the old crop or old bounds is stale and must not be reused.

The check must include a first/last-column same-day comparison and a 5-day spacer regression. A typical failure signature is that January aligns while October–December read the preceding row, with empty spacer bands misreported as days 6, 11, 16, 21, or 26. Monthly-mean closure is a detector for this defect, not a license to back-calculate missing daily values.

For curved pages where one affine shear cannot flatten both the header and footer, fit rows per month column. Cluster numeric token centers, exclude the statistics rows below day 31, and preserve the five-day spacer phase. If OCR misses day 1, the spacer phase moves from indices `5,10,15,...` to `4,9,14,...`; prepend one row pitch before assigning days. Require ordered centers or at least eight independent anchors per projected column, and retain the per-column offset, scale, and anchor count in the audit record.

Curvature evidence is month-local. If a reliable curved boundary is detected for
only a subset of months, use it only for those months and retain the physical
registered bounds for every remaining month. Never exclude an otherwise valid
month merely because an adjacent month has a fitted curve.

After applying the registered header/body/footer envelope, an exact 28--31 box
count matching the calendar-valid days is strong sequence evidence. If vertical
gaps are smooth, assign those boxes top-to-bottom to days 1--N. This ordered
sequence path is forbidden until header labels and statistic tokens have been
excluded. Incomplete or merged sequences use blank-aware monotonic alignment.

## Column-local rule interpolation and footer registration

A keystoned page can move a month boundary by more than one glyph width from
day 1 to day 31. Interpolate both column rules at the target row or rectify the
month from four local rule intersections. Enlarging a fixed crop is not a
repair: it can expose the adjacent vertical rule, which recognizers often read
as a leading `1`. Mask only confirmed grid-line pixels and keep the unmasked
source crop beside every candidate.

Treat the footer as a second local grid. For each month, locate the day-31
bottom, Average, Maximum, maximum-date, Minimum and minimum-date rules at that
column's x position. Never reuse the left-side y coordinate across all months.
The review artifact must show the complete day column and all released values
on the same vertical scale. When every source day has been visually checked,
an aggregate conflict may be retained as an explicit source conflict; it may
not be resolved by changing a readable day or back-calculating a blank.

## Numeric-glyph row registration and thick-rule recovery

On small four-up tables, projecting the day-label centers across the full
width can still clip digits even after a global shear correction. Detect
connected-component y centers separately in every month column, excluding the
header and statistics block. If the ordered center count equals the month's
calendar-valid day count and adjacent offset changes stay below 0.48 ordinary
row pitches, the local sequence is a direct 1-to-N registration only when its
median offset also stays below 0.65 row pitches. Equal row counts with a
one-row median shift are a phase error, not local perspective. Otherwise
match centers monotonically within 0.25 pitches of the projected reference and
retain unmatched reference slots as possible source blanks. Do not compress
the remaining rows after a blank. Implement the fallback as ordered sequence
alignment: first maximize the number of valid row matches, then minimize total
distance. A nearest-unused assignment can cross row order after one missing or
extra component and is release-blocking.

If the first detected statistics boundary is more than 1.35 ordinary pitches
below day 31, search for a faint leading Average rule only in the intervening
band. Then merge horizontal detections separated by no more than the measured
thick-rule width (five source pixels in the North Sanhe regression). Without
this merge, the two edges of one line create an empty crop and shift Average to
Maximum even though the footer appears structurally valid.

Read every Average cell with both independent recognizers, not only when the
first result is empty. A plausible substitution such as `1.66` versus `1.86`
can survive confidence filtering. When the daily cells are independently
confirmed, displayed-precision arithmetic closure may select the unique
statistic candidate; if neither or both candidates close, keep the statistic
blocked for registered-source review.

Evaluate daily and printed-statistic candidates as pairs before ranking the
table candidate. Run variable-appropriate displayed-precision closure on each
pair. A uniquely closing pair may be selected, but the statistic remains an
independent source reading and cannot supply, shift, or back-calculate a daily
cell. A table with no readable statistic candidates must emit an explicit audit
state and continue to visual review; an empty batch is not a processing error.

Inset registered numeric crops far enough to exclude a curved rule. A rule
fragment commonly produces paired candidates such as `10` versus `0` or
`12.58` versus `2.58`. This pattern is review evidence, not a free numeric
rewrite: keep both readings and require the applicable printed mean or the
registered source column to prove the clean value. Normalize a repeated scan
punctuation only when deleting one leading/trailing mark yields exactly one
valid number and the month still closes.

An all-zero printed month needs one additional paired-glyph guard. When the
independently read Average is exactly `0`, every numeric candidate is in
`{0, 10}`, and a candidate `10` has the ink footprint of the neighboring zero
glyphs, treat it as a vertical-rule-plus-zero review candidate. Convert only
those registered numeric cells after source confirmation or exact monthly
closure. Never fill a blank, and never apply this rule if any other magnitude
occurs in the month.
