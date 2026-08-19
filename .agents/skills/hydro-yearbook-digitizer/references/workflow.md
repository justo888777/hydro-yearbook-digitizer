# Processing workflow

## Stage 0: source inventory and cover identity

Assign stable source IDs and hashes. Find the volume cover, recognize title/basin/year/volume independently, and compare them with folder and manifest metadata. Do not silently trust or rename a human-created folder.

## Stage 1: optional browsing PDF

Create a derived `source_browse.pdf` from ordered photographs for convenient review. Retain originals and use originals or rectified images for OCR.

## Stage 2: page routing

Classify every page as cover, supported table type, map, narrative, blank, or unknown. Maps and non-table pages are inventoried but excluded from extraction. Unknown pages require review.

## Stage 3: page preparation

A photograph may contain one page, a two-page spread, one page with two daily tables, or a spread containing four daily tables. Produce one rectified page image and one rectified image per logical table.

## Stage 4: template registration

Map lines and anchors to normalized coordinates. Reject registration when expected header or grid structure is missing.

## Stage 5: extraction

Extract station master data, station-variable availability, summary tables, comparison metrics, and daily matrices. Preserve raw and normalized values with source provenance.

Before extraction, inventory the variable titles actually printed in the
current source. An absent variable is omitted, not derived. Build a current-year
river/station vocabulary and require every daily identity to match it or enter
source review.

## Stage 6: independent recognition

Run contextual visual recognition and isolated-field recognition independently. Add a local OCR candidate when useful. Store every candidate; do not let one pass overwrite another.

## Stage 7: consensus and deterministic validation

Automatic acceptance requires two distinct engines to agree and all applicable checks to pass. Disagreement, single-engine output, or failed checks creates a review item.

For monthly spreads, first split rows into visual blocks, preserve omitted
late-month blank slots, and validate serials within each printed water-system
section. Run printed annual closure after final cell assignment. Continue the
review loop until the unresolved-item count is zero; confirmed source blanks
remain blank rather than becoming numeric zero.

## Stage 8: human review

Review decisions are append-only. Re-run arithmetic and cross-table checks after edits.

## Stage 9: export

Export the master workbook, station-variable workbooks, variable availability matrix, source/exclusion inventories, and audit records.

Use `General` for numeric cells, keep source blanks blank, retain the printed
annual value, and import each generated workbook for cell-by-cell read-back.

## Stage 10: quality report and release

Generate HTML, Excel, and Markdown QC outputs. Release only when blocking items are zero and required outputs are complete.

For each run, record wall time per extracted table and local OCR API tokens.
Report Codex/session token consumption only from available telemetry; otherwise
mark it unavailable.
