# Data schema

## Common provenance fields

Every table and cell record should include:

- `project_id`, `basin`, `year`;
- `source_id`, `source_file`, `source_page`;
- `page_class`, `table_id`, `template_id`, `crop_path`;
- `raw_text`, `normalized_value`;
- `status`: `candidate`, `auto_pass`, `needs_review`, `verified`, `source_conflict`;
- `recognition_passes`, `validation_results`, `review_history`.

## Volume identity

- printed title;
- basin, river system, or region;
- hydrological year;
- volume/part/edition;
- publishing or compiling organization;
- original folder basin/year;
- suggested canonical path;
- conflicts and final approval state.

## Station index

Recommended fields:

- station order/code;
- water system, river name, inflow relationship;
- station name/category/location;
- longitude/latitude;
- distance to mouth and catchment area;
- established year/month;
- datum elevation/name;
- managing agency, data end year, remarks.

Ditto marks preserve `raw_text`, inherited `normalized_value`, and `inherited_from_row`.

## Station-variable availability index

One record per station:

- station order, river name, station name;
- Boolean fields for available water-level, flow, sediment, particle-size, and water-temperature table families;
- optional printed page number per table family;
- source, candidates, status, and review history.

A printed page number means the table family is available. The user-facing matrix may omit page numbers while retaining them in provenance.

## Monthly and annual summary

One record per station and variable with month 01-12, the independently read
printed annual mean, unit, printed precision, and provenance. A calculated
annual comparison is a QC field, not a replacement for the printed annual mean.

## Comparison table

Store station identity, data type, source columns, and a template-defined normalized metrics object.

## Daily matrix

Metadata includes station identity, table/station number, data type, unit, catchment area, year, and notes.

Daily values are stored in long form with month, day, date, value, special state, provenance, candidates, and review status.

Printed monthly and annual statistics remain separate named fields.

## Page inventory

Every source page has:

- page class and classification confidence;
- extraction action;
- exclusion reason when applicable;
- cover or table linkage;
- review status.

## Special states

- `BLANK`
- `NOT_APPLICABLE`
- `UNREADABLE`
- `RIVER_DRY`
- `TRACE`
- `MISSING_PRINTED`
