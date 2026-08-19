# Header-line disambiguation

Use this rule before assigning any value to a month column.

1. Read the printed month labels first. When at least six well-spread labels
   are recognized, fit the twelve month centres from label positions and use
   those semantic centres as the primary column anchor.
2. Detect candidate vertical rules in the month-header band and require each
   retained rule to cross both the header and a portion of the daily body.
3. Never estimate month boundaries from a full-body vertical morphology pass
   alone. Repeated `0` glyphs can form a high-confidence false vertical line.
4. Treat fourteen header rules as the optional day-index edge plus thirteen
   month boundaries. Remove only the day-index edge.
5. Thirteen detected rules can still be wrong: if the first rule is the table
   outer edge and the right margin can hold another column boundary, discard
   that day-index outer edge and restore the faint December border. This avoids
   silently mapping day numbers to January on visually all-zero tables.
6. If fewer than thirteen rules remain, anchor the reconstruction at the
   observed December edge. Count doubled gaps as missing interior rules and
   extrapolate only the missing leading boundaries.
7. Re-rectify from the inferred January and observed December edges. Re-read
   the twelve printed month labels; reject a crop beginning at February or
   ending before December.
8. A page-level quadrilateral fallback is allowed only when the complete table
   is visually present. Save the reviewed corner coordinates and the resulting
   crop as audit evidence.
9. Do not run multiple CPU-heavy Paddle/Rapid instances on the same host unless
   a benchmark proves a wall-time benefit. Record failed parallel trials.

Release remains blocked until all twelve columns, calendar-valid daily cells,
printed monthly statistics, and station-variable identity have been checked.
