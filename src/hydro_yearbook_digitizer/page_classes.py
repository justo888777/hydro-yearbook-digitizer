from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PageClass(StrEnum):
    COVER = 'cover'
    STATION_INDEX = 'station_index'
    VARIABLE_INDEX = 'variable_index'
    MONTHLY_ANNUAL_SUMMARY = 'monthly_annual_summary'
    COMPARISON_TABLE = 'comparison_table'
    DAILY_MATRIX = 'daily_matrix'
    MAP = 'map'
    NARRATIVE = 'narrative'
    BLANK = 'blank'
    UNKNOWN = 'unknown'


_TABLE_CLASSES = {
    PageClass.STATION_INDEX,
    PageClass.VARIABLE_INDEX,
    PageClass.MONTHLY_ANNUAL_SUMMARY,
    PageClass.COMPARISON_TABLE,
    PageClass.DAILY_MATRIX,
}


@dataclass(frozen=True)
class PageRoute:
    page_class: PageClass
    extract_metadata: bool
    extract_table: bool
    excluded_from_ocr: bool
    reason: str


def route_page(page_class: PageClass) -> PageRoute:
    if page_class == PageClass.COVER:
        return PageRoute(page_class, True, False, False, 'extract_volume_identity_only')
    if page_class in _TABLE_CLASSES:
        return PageRoute(page_class, False, True, False, 'extract_supported_table')
    if page_class == PageClass.MAP:
        return PageRoute(page_class, False, False, True, 'map_excluded_by_project_policy')
    if page_class in {PageClass.NARRATIVE, PageClass.BLANK}:
        return PageRoute(page_class, False, False, True, 'non_table_page_excluded')
    return PageRoute(page_class, False, False, False, 'manual_classification_required')
