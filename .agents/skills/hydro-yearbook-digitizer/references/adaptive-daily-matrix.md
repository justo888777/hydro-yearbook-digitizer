# Adaptive daily-matrix recovery

Use this reference for photographed 31-by-12 hydrological daily tables when a
standard line-aware registration cannot certify all calendar-valid cells.

## Required audit fields

- source image and immutable rectified crop path;
- crop variant and orientation action;
- `grid_source` (`physical_rules` or `numeric_text_centres`);
- physical or inferred 13 month boundaries;
- two recognizer candidates for every disputed cell;
- printed statistic candidates, calculated statistic and validation mode;
- visual-review override identity and reviewer basis, when used;
- local elapsed seconds, local API-token count and image-token budget estimate.

## Decision sequence

1. Inspect image rotation and correct it before cropping.
2. Rectify the outer table. Keep an expanded crop if any first/last daily group
   or header is clipped.
3. Use physical vertical rules from the month-header band when they form a
   plausible 13-rule grid. Do not accept a full-body rule unless it also
   crosses the header; repeated zeroes otherwise masquerade as table lines. A
   retained day-index edge makes 14 rules; discard only that edge. If one
   interior rule and an outer border are faint, fit the missing-line-tolerant
   14-rule lattice and anchor its two ends with the widest long horizontal
   printed rule. A first/last-only fit is forbidden because it can silently
   compress late-month columns.
4. For broken leading rules, extrapolate from the contiguous right-hand rule
   suffix, count doubled gaps as missing interior rules, and re-rectify using
   the inferred January and observed December edges. Re-read the twelve month
   labels. If any boundary remains outside the source, cluster numeric OCR
   x-centres into twelve month bands and require contextual visual review.
5. Read the printed 1-31 labels in the day column. Preserve their five-day
   spacer pattern, fit each month column's local daily-body top/bottom rules,
   and project the labeled row pattern into that slanted column. Assign OCR
   text only after those row centers are registered. When OCR merges vertical
   groups (`12345`, `1617181920`), isolate the day-number column, remove long
   table rules, cluster digit connected components by y overlap, and robustly
   fit the 1-31 pattern. Require at least 24 observed row bands; reconstruct only
   missing labels consistent with the five wider gaps after days 5, 10, 15, 20,
   and 25. The last group is 26-31. Reject header/footer bands and any run
   entering mean/max/min/date statistics.
   Retain compact day-label components up to 18 raster rows on the normalized
   crop; a 14-row ceiling can discard days 29-31 and trigger a false fallback.
   If fewer than 24 labels survive, use a normalized printed-layout template:
   first/last centres at about 2.74%/97.44% of the daily body and an extra
   five-day spacer about 0.88 of one ordinary row step. Never use 31 equal rows.
   On a strongly tilted or curved photograph, locate the statistics-top rule
   before the header-bottom rule and constrain their separation to a plausible
   day-body height. Do not let an early title underline cap the Hough search.
   Fit the twelve local tops/bottoms as physical curves and block release when
   any month has a one-row-scale residual until that month is fully regridded
   and reread.
   A month-local largest body gap outranks a page-wide Hough header candidate.
   When the local header-bottom rule is missing, interpolate from neighbouring
   months with physical pairs; do not reuse a title underline or the
   month-header top rule. Apply a robust cross-month curve with a tolerance
   smaller than one daily row, and fail the geometry audit if OCR reads a month
   label from any daily cell.
6. Independently re-read failed months at cell level. Whole-month replacement
   needs every calendar-valid cell plus a source-statistic validation.
7. Apply `rounded`, `truncated`, or `source_precision_bound` only to variables
   whose printed monthly statistic is defined as the arithmetic mean of daily
   values. Daily mean flow normally uses this gate. Sediment concentration may
   be flow weighted or report derived; its printed monthly mean must be
   independently read but must not be used to rewrite or reject correctly read
   daily concentrations. Record the selected variable rule in the audit.
   For arithmetic closure, compare the overlap of printed-value intervals:
   include the rounding uncertainty of every daily value as well as that of
   the printed mean. Do not demand exact equality of already-rounded numbers.
8. Remaining issues are visual-review tasks. Reviewer changes are append-only
   and must trigger a complete monthly revalidation.
   A nonnumeric state month is the narrow exception: if two printed monthly
   statistics independently contain the same state and no conflicting decimal
   or numeric day exists, the tiny ditto sequence may close as that state.
   Keep mixed state/numeric months on the explicit-glyph review path.
9. Create a workbook only for a variable title printed in the source. Never
   derive a missing sediment-transport-rate table from flow and concentration.
   The relation `Q*C ~= Qs` is a review signal and cannot replace printed Qs.
10. When part of the grid is absent because the source scan is clipped or
    blacked out, retain explicit source-missing blanks. Do not borrow the same
    station/month from another year.

## Delivery gate

Export a compact daily-data sheet and a compact monthly-QC sheet only after
all calendar-valid cells are present and every month is validated or explicitly
approved as a source conflict. Keep candidates, crop images, token metrics and
review changes in the audit package rather than the clean data workbook.
