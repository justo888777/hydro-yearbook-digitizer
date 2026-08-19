from __future__ import annotations

from dataclasses import dataclass
import re

from .naming import sanitize_filename_part


def strip_final_station_suffix(value: str) -> str:
    """Remove the grammatical suffix while preserving internal station text."""
    return re.sub(r"站\s*$", "", value.strip())


@dataclass(frozen=True)
class VolumeIdentityResolution:
    basin: str | None
    year: int | None
    source_title: str | None
    status: str
    warnings: tuple[str, ...]
    suggested_folder: str | None


def resolve_volume_identity(
    *,
    folder_basin: str | None,
    folder_year: int | None,
    cover_basin: str | None,
    cover_year: int | None,
    cover_title: str | None,
    cover_confirmed: bool,
) -> VolumeIdentityResolution:
    """Reconcile human folder names with cover metadata without silent renaming."""
    warnings: list[str] = []

    basin = cover_basin if cover_confirmed and cover_basin else folder_basin
    year = cover_year if cover_confirmed and cover_year else folder_year

    if cover_basin and folder_basin and cover_basin.strip() != folder_basin.strip():
        warnings.append('folder_basin_conflicts_with_cover')
    if cover_year and folder_year and cover_year != folder_year:
        warnings.append('folder_year_conflicts_with_cover')

    if basin is None or year is None:
        status = 'needs_review'
    elif warnings:
        status = 'needs_review'
    else:
        status = 'resolved'

    suggested = None
    if basin and year:
        suggested = f'{sanitize_filename_part(basin)}/{year}'

    return VolumeIdentityResolution(
        basin=basin,
        year=year,
        source_title=cover_title,
        status=status,
        warnings=tuple(warnings),
        suggested_folder=suggested,
    )
