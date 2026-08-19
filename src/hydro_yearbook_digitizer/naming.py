from __future__ import annotations

import re
from pathlib import Path

_INVALID_WINDOWS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WHITESPACE = re.compile(r"\s+")


def sanitize_filename_part(value: str) -> str:
    """Return a stable filename-safe text component without changing source metadata."""
    cleaned = _INVALID_WINDOWS_CHARS.sub("_", value.strip())
    cleaned = _WHITESPACE.sub("", cleaned)
    cleaned = cleaned.rstrip(". ")
    return cleaned or "未命名"


def station_workbook_name(station_order: int, station_name: str, data_type: str) -> str:
    if station_order < 1:
        raise ValueError("station_order must be >= 1")
    return (
        f"{station_order:03d}-"
        f"{sanitize_filename_part(station_name)}-"
        f"{sanitize_filename_part(data_type)}.xlsx"
    )


def daily_station_workbook_name(
    station_order: int,
    river_name: str,
    station_name: str,
    variable: str,
) -> str:
    """Return the standard public-delivery filename for one daily table.

    The current source title supplies the river and station identity.  Callers
    must not use this helper to hide an unresolved identity collision by
    producing a suffixed filename.
    """
    if station_order < 1:
        raise ValueError("station_order must be >= 1")
    return (
        f"{station_order:03d}-"
        f"{sanitize_filename_part(river_name)}-"
        f"{sanitize_filename_part(station_name)}-"
        f"{sanitize_filename_part(variable)}-日值表.xlsx"
    )


def monthly_summary_workbook_name(basin: str, year: int, variable: str) -> str:
    """Return the standard public-delivery filename for a monthly summary."""
    if year < 1800 or year > 2200:
        raise ValueError("year is outside the supported range")
    return (
        f"{year}-{sanitize_filename_part(basin)}-"
        f"{sanitize_filename_part(variable)}-月值总表.xlsx"
    )


def station_index_workbook_name() -> str:
    """Return the basin-root station and delivery-index workbook name."""
    return "站点与目录索引.xlsx"


def master_workbook_name(basin: str, year: int) -> str:
    if year < 1800 or year > 2200:
        raise ValueError("year is outside the supported range")
    return f"00_{sanitize_filename_part(basin)}_{year}_总表.xlsx"


def ensure_unique_path(path: Path) -> Path:
    """Return path or a numbered sibling if the path already exists."""
    if not path.exists():
        return path
    index = 2
    while True:
        candidate = path.with_name(f"{path.stem}_{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1
