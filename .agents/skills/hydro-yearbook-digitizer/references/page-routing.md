# Page routing and exclusions

Classify every photographed page before OCR. Do not assume every page is a table.

## Classes

- `cover`: extract volume identity only;
- `station_index`: extract station master data;
- `variable_index`: extract station-by-variable availability;
- `monthly_annual_summary`: extract monthly and annual summary values;
- `comparison_table`: extract variable-specific comparison metrics;
- `daily_matrix`: extract daily station values;
- `map`: inventory and archive only, never OCR or extract by default;
- `narrative`: inventory only;
- `blank`: inventory only;
- `unknown`: manual classification required.

A page classified as `map` must appear in `excluded_pages` in the quality report with source ID, image path, reason, and classification confidence. It must not silently disappear from the inventory.

## Cover identity

The cover is authoritative evidence for:

- printed title;
- basin, river system, or region;
- hydrological year;
- volume, part, or edition;
- publishing or compiling organization when useful.

Compare cover-derived identity with the human folder path. A mismatch blocks automatic folder renaming and creates a metadata review item. Never overwrite or move the original folder solely on a model prediction.
