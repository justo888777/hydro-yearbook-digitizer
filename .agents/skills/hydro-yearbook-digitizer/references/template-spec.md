# Template specification

## Principle

Hard-code the **canonical logical template**, not absolute coordinates in the original photograph.

Each source table is first rectified into a canonical rectangle. Cell regions are then defined in normalized coordinates from 0 to 1.

## Template families

### `station_index_v1`

Expected features:

- multi-row header;
- station-order rows;
- narrow code and coordinate columns;
- frequent ditto marks;
- possible continuation across facing pages.

### `variable_index_v1`

Expected features:

- title similar to “水位、流量、泥沙、水温资料索引表”;
- continuation across facing pages;
- station order, river, and station name columns;
- narrow variable columns containing page numbers or blanks;
- each nonblank page-number cell implies that the station has that variable/table family.

Extract both optional page numbers and normalized Boolean availability flags.

### `monthly_annual_summary_v1`

Expected features:

- station rows;
- catchment-area column;
- 12 month columns;
- annual mean column;
- optional continuation or comparison table on the facing page.

### `daily_matrix_v1`

Expected features:

- title containing table/station number, river, station, and variable;
- 12 month columns;
- day rows 1—31;
- monthly statistic rows;
- annual-statistics block;
- notes block.

### `daily_matrix_two_up_v1`

Layout wrapper for two daily tables on one page. It splits the page into two table regions, then applies `daily_matrix_v1` independently.

## Required template keys

```yaml
id: daily_matrix_v1
family: daily_matrix
canonical_size: [2400, 1800]
anchors:
  - outer_border
  - month_header
  - day_column
regions:
  title: [x0, y0, x1, y1]
  metadata: [x0, y0, x1, y1]
  daily_grid: [x0, y0, x1, y1]
  monthly_stats: [x0, y0, x1, y1]
  annual_stats: [x0, y0, x1, y1]
  notes: [x0, y0, x1, y1]
grid:
  rows: 31
  columns: 12
```

## Template acceptance

A template registration is accepted only when:

- outer border or sufficient internal lines are detected;
- at least 10 of 12 month headers are geometrically consistent;
- the day column supports the expected sequence;
- grid line count is within configured tolerance;
- title or neighboring context identifies the table type.

A failed registration must not proceed to blind extraction.
