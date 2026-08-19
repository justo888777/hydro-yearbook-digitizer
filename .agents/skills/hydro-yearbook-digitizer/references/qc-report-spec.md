# Quality report and checklist specification

Generate all three forms:

1. `outputs/QC_REPORT.html` for visual review;
2. `outputs/QC_CHECKLIST.xlsx` for filtering, assignment, and sign-off;
3. `outputs/completion_report.md` for repository-readable summary.

## Required report sections

### Project identity

- cover-derived title, basin, year, volume;
- folder-derived basin and year;
- resolved canonical identity;
- unresolved folder/cover conflicts.

### Source inventory

- source count, hashes, dimensions, orientation, order;
- generated browsing PDF and page count;
- duplicate or missing-image warnings.

### Page classification

Counts and item lists for cover, each supported table type, maps, narrative pages, blank pages, and unknown pages.

### Extraction inventory

- tables detected and extracted;
- stations found;
- variable availability matrix;
- daily workbooks expected versus exported.

### Recognition agreement

- total critical fields/cells;
- two-engine agreement count and rate;
- disagreement count;
- single-engine-only count;
- unreadable count;
- candidate values by engine/model.

### Deterministic validation

- structural checks;
- calendar checks;
- monthly and annual arithmetic checks;
- station and variable cross-table checks;
- folder/cover identity checks.

### Manual review

- open, resolved, and waived items;
- reviewer decisions and timestamps;
- high-impact conflicts such as decimal points and extrema.

### Exclusions

List every intentionally excluded map or narrative page. Exclusion is not an error when it follows the project policy.

### Release gate

Release passes only when blocking review items are zero, required outputs exist, and all mandatory checks pass or approved source conflicts are documented.
