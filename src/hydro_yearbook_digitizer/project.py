from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .naming import master_workbook_name

_REQUIRED_DIRS = (
    "raw/photos",
    "raw/pdf",
    "work/documents",
    "work/pages",
    "work/tables",
    "work/cells",
    "work/records",
    "work/review",
    "work/logs",
    "outputs/stations",
    "outputs/qc",
)


@dataclass(frozen=True)
class ProjectValidation:
    ok: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def initialize_project(root: Path, basin: str, year: int) -> Path:
    project_dir = root / basin / str(year)
    for relative in _REQUIRED_DIRS:
        (project_dir / relative).mkdir(parents=True, exist_ok=True)

    manifest_path = project_dir / "manifest.yaml"
    if not manifest_path.exists():
        manifest: dict[str, Any] = {
            "project": {
                "id": f"{basin}-{year}",
                "basin": basin,
                "year": year,
                "language": "zh-CN",
                "identity_status": "folder_only_unverified",
                "cover_identity": {},
                "folder_identity_conflicts": [],
            },
            "input": {
                "raw_dir": "raw",
                "sources": [],
            },
            "output": {
                "master_workbook": master_workbook_name(basin, year),
                "station_filename_pattern": "{station_order:03d}-{station_name}-{data_type}.xlsx",
            },
            "page_routing": {
                "exclude_classes": ["map", "narrative", "blank"],
                "unknown_blocks_release": True,
            },
            "recognition": {
                "minimum_distinct_engines_for_auto_pass": 2,
                "confidence_breaks_ties": False,
            },
            "quality": {
                "require_two_pass_agreement": True,
                "unresolved_items_block_release": True,
                "default_rounding_tolerance": "printed_precision",
                "required_reports": [
                    "QC_REPORT.html",
                    "QC_CHECKLIST.xlsx",
                    "completion_report.md",
                ],
            },
        }
        manifest_path.write_text(
            yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
    return project_dir


def validate_project(project_dir: Path) -> ProjectValidation:
    errors: list[str] = []
    warnings: list[str] = []

    if not project_dir.is_dir():
        return ProjectValidation(False, (f"project directory not found: {project_dir}",), ())

    for relative in _REQUIRED_DIRS:
        if not (project_dir / relative).is_dir():
            errors.append(f"missing directory: {relative}")

    manifest_path = project_dir / "manifest.yaml"
    if not manifest_path.is_file():
        errors.append("missing manifest.yaml")
        return ProjectValidation(False, tuple(errors), tuple(warnings))

    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        errors.append(f"invalid manifest.yaml: {exc}")
        return ProjectValidation(False, tuple(errors), tuple(warnings))

    project = manifest.get("project", {})
    for key in ("basin", "year"):
        if key not in project:
            errors.append(f"manifest missing project.{key}")

    raw_files = [
        path
        for relative in ("raw/photos", "raw/pdf")
        for path in (project_dir / relative).glob("*")
        if path.is_file()
    ]
    if not raw_files:
        warnings.append("no source photos or PDFs found under raw/")

    return ProjectValidation(not errors, tuple(errors), tuple(warnings))
