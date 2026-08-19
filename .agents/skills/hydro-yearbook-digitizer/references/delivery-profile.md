# Delivery profile

The delivery is intentionally small and easy to inspect. Put provenance,
candidate OCR, crop images, and reviewer notes in the audit tree; do not fill a
data workbook with OCR diagnostics.

## Standard folder structure

```text
<basin>/
├─ 站点与目录索引.xlsx
├─ 提取复核记录.xlsx
├─ 数据范围与缺失说明.xlsx
├─ 处理指标记录.xlsx
└─ <year>/
   ├─ 月值/
   │  └─ <year>-<basin>-<variable>-月值总表.xlsx
   └─ 日值/
      └─ <variable>/
         └─ <serial>-<river>-<station>-<variable>-日值表.xlsx
```

Use the helpers in `hydro_yearbook_digitizer.naming` for new filenames:

- `daily_station_workbook_name(serial, river, station, variable)`;
- `monthly_summary_workbook_name(basin, year, variable)`;
- `station_index_workbook_name()`.

An identity collision is a review issue, not a reason to silently add `_2` to a
daily or monthly data filename. Filename sanitization is for Windows-safe
rendering only; preserve the unsanitized printed identity in workbook metadata
and the audit record.

## Monthly summary workbook

One workbook represents one printed variable for one year. Its primary sheet
has one source station row and these columns:

```text
序号 | 水系/分区 | 河名 | 站名 | 站号 | 集水面积 | 1月 ... 12月 | 年均值 | 单位 | 来源页
```

- `年均值` is the independently transcribed printed annual value.
- A calculated annual comparison belongs in the audit/QC report, not a new
  user-facing value column unless the requester asks for it.
- Keep formula or section-heading rows identifiable; do not force them into a
  station row.
- Preserve source blanks and printed states. Do not convert them to zero.

## Daily station-variable workbook

One workbook represents one printed station-variable daily table. Keep it
compact with these sheets:

- `逐日数据`: a 31-by-12 calendar matrix, leaving calendar-invalid dates blank;
- `月统计`: printed monthly statistic(s), source annual value when present, and
  the requested calculated checks clearly labelled as checks;
- `元数据`: basin/year/source page/table ID/printed title/river/station/variable/
  unit and source status;
- `说明`: a short description of states, blanks, source conflicts, and audit
  location.

When a value is a state string, retain the printed text in the date cell. Do
not replace it with `0`, `None`, or a calculated value.

## Basin-root index workbooks

`站点与目录索引.xlsx` contains a station sheet and a table-availability sheet.
Recommended station fields are station code, water system, river, station,
address, separate longitude/latitude, establishment time, agency, source year/
page, and review status. The availability sheet lists each year, variable,
table type, workbook path, source page, and completion status.

`提取复核记录.xlsx` is the user-readable summary of source conflicts and source
blanks. Detailed machine provenance may stay in JSON/JSONL audit files.

## Excel presentation

- Use a single restrained header colour, alternating body stripes, thin grid
  lines, frozen header row, and sensible column widths.
- Use `General` or a per-cell numeric format: integers display as `0`, decimals
  as `0.######`. Do not force all values to `0.0`.
- Do not add hidden helper sheets or temporary OCR columns to deliverables.
- Reopen each workbook after writing and verify both values and number formats.
