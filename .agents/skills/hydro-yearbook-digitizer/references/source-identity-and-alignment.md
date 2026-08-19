# Source identity and alignment

Use this reference for photographed tables, multi-page monthly spreads, daily
matrices, and any case where an older delivery uses a different station name.

## Current source is authoritative

Build each table identity from the current printed source:

- volume/year/basin;
- source page and logical-table position;
- printed serial within its visual section;
- river, station, and any parenthetical qualifier;
- printed variable title and unit.

Retain the complete source title and its normalized identity separately. A
station list, a previous year, or a legacy workbook can propose a spelling
candidate, but it cannot replace a current source identity or donate a value.
Do not join flow, concentration, and transport-rate tables with serial alone:
serials may restart or be reused in different source sections.

When two names appear similar, compare their current source title strips and,
when available, station code/river/area from the same volume. Record an explicit
alias decision only after that comparison. Preserve qualifiers that distinguish
subtables (for example a canal, gate, or reservoir suffix).

## Monthly-table row ownership

For each current-page row, retain a physical row slot even when some fields are
blank. Attach its serial, river/station fields, area, month cells, annual cell,
and page geometry to the same row key.

- Use visual subheadings and large whitespace gaps to split a table into blocks.
  A serial restart in a new block is a new section, not automatically a duplicate.
- Establish left-page and right-page baselines independently. Never use one
  constant y-offset across a photographed spread.
- Map late-month/annual cells to a row only after the right-page baseline is
  monotonically aligned to the left-side row slots.
- Inspect the first, middle, and last row of every page. Check every row near a
  blank run, a section boundary, or a page seam.
- If a late-month cell has no printed ink, preserve it as a source blank in its
  own row. It must not borrow the value above/below or shift later rows.

An annual-mean mismatch is an alarm for source review. It does not authorize
moving a neighbouring late-month or annual value into another row.

## Daily-table date ownership

Register the table before recognizing values:

1. correct orientation and rectify the printed outer grid;
2. identify each month column from local physical rules and month headers;
3. map the 31 day labels with six physical groups (spacers after 5, 10, 15, 20,
   and 25 only);
4. locate the footer/statistics block separately for each month;
5. read only the calendar-valid day cells from the final local grid.

Use a local row model for each month when perspective, curvature, or a partial
page changes row geometry. If re-registration changes the day position by a
material fraction of a row, re-read the complete month. Do not transplant a
formerly accepted OCR value into a newly registered row simply because its
digits still look plausible.

A candidate belongs to a date only when its crop lies inside that date's final
physical cell. Do not concatenate vertically adjacent digits, pull values from
the statistics footer, or use the first N OCR tokens as day order.

## Blank, state, and source-conflict handling

Use an explicit status for each nonnumeric release value:

- `source_blank`: printed cell is blank;
- `source_scan_missing`: requested cell/table is physically absent or clipped;
- `state`: a printed hydrological state such as dry channel or ice;
- `source_conflict`: source cells are readable but internally inconsistent.

Do not use a numeric zero for any of these states. A ditto may propagate only
within the same registered table and only where its glyph is visibly printed.
If the source is unreadable rather than blank, retain `needs_review`; it is not
eligible for release.
