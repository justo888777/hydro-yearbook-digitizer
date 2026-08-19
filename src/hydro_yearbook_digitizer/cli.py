from __future__ import annotations

import argparse
from pathlib import Path

from .photo_pdf import photos_to_pdf
from .project import initialize_project, validate_project
from .trial import run_trial_audit, validate_trial_release
from .daily_candidate import constant_daily_candidates, map_daily_tokens, normalized_crop, normalized_quad_crop, read_ocr_tokens, write_daily_candidate_workbook


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hydro-yearbook")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="initialize a basin-year project")
    init_parser.add_argument("--root", type=Path, required=True)
    init_parser.add_argument("--basin", required=True)
    init_parser.add_argument("--year", type=int, required=True)

    validate_parser = subparsers.add_parser(
        "validate-project", help="validate project structure and manifest"
    )
    validate_parser.add_argument("project_dir", type=Path)

    pdf_parser = subparsers.add_parser(
        "photos-to-pdf", help="create a derived browsing PDF from ordered photos"
    )
    pdf_parser.add_argument("photos", nargs="+", type=Path)
    pdf_parser.add_argument("--output", type=Path, required=True)
    pdf_parser.add_argument("--max-long-edge", type=int)
    pdf_parser.add_argument("--quality", type=int, default=92)

    audit_parser = subparsers.add_parser("trial-audit", help="inventory immutable trial images and generate QC outputs")
    audit_parser.add_argument("source_dir", type=Path)
    audit_parser.add_argument("--output-dir", type=Path, required=True)
    audit_parser.add_argument("--project-name", required=True)
    audit_parser.add_argument("--classes", type=Path, help="JSON object mapping filename to PageClass")
    audit_parser.add_argument("--master-workbook", type=Path, help="optional auditable master workbook path")

    trial_validate_parser = subparsers.add_parser("validate-trial", help="apply the no-silent-uncertainty release gate")
    trial_validate_parser.add_argument("output_dir", type=Path)

    daily_parser = subparsers.add_parser("extract-daily-candidate", help="export a review-only daily-matrix OCR candidate workbook")
    daily_parser.add_argument("image", type=Path)
    daily_parser.add_argument("--output", type=Path, required=True)
    daily_parser.add_argument("--work-dir", type=Path, required=True)
    daily_parser.add_argument("--basin", required=True)
    daily_parser.add_argument("--year", type=int, required=True)
    daily_parser.add_argument("--table-id", required=True)
    daily_parser.add_argument("--region", type=float, nargs=4, required=True, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"))
    daily_parser.add_argument("--quad", type=float, nargs=8, metavar=("TL_X", "TL_Y", "TR_X", "TR_Y", "BR_X", "BR_Y", "BL_X", "BL_Y"))
    daily_parser.add_argument("--month-centers", type=float, nargs=12, required=True)
    daily_parser.add_argument("--day-column-max-x", type=float, required=True)
    daily_parser.add_argument("--daily-y-min", type=float, required=True)
    daily_parser.add_argument("--daily-y-max", type=float, required=True)
    daily_parser.add_argument("--daily-row-start", type=float)
    daily_parser.add_argument("--daily-row-step", type=float)

    constant_parser = subparsers.add_parser("extract-constant-daily-candidate", help="export a review-only constant daily matrix after documented dual reading")
    constant_parser.add_argument("source_file", type=Path)
    constant_parser.add_argument("--output", type=Path, required=True)
    constant_parser.add_argument("--crop-path", type=Path, required=True)
    constant_parser.add_argument("--basin", required=True)
    constant_parser.add_argument("--year", type=int, required=True)
    constant_parser.add_argument("--table-id", required=True)
    constant_parser.add_argument("--value", type=float, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "init":
        project_dir = initialize_project(args.root, args.basin, args.year)
        print(project_dir)
        return 0

    if args.command == "validate-project":
        result = validate_project(args.project_dir)
        for warning in result.warnings:
            print(f"WARNING: {warning}")
        for error in result.errors:
            print(f"ERROR: {error}")
        print("OK" if result.ok else "FAILED")
        return 0 if result.ok else 1

    if args.command == "photos-to-pdf":
        output = photos_to_pdf(
            args.photos,
            args.output,
            max_long_edge=args.max_long_edge,
            quality=args.quality,
        )
        print(output)
        return 0

    if args.command == "trial-audit":
        classes = None
        if args.classes:
            classes = __import__("json").loads(args.classes.read_text(encoding="utf-8"))
        records = run_trial_audit(
            args.source_dir,
            args.output_dir,
            project_name=args.project_name,
            classes=classes,
            master_workbook_path=args.master_workbook,
        )
        print(f"inventoried {len(records)} source images")
        return 0

    if args.command == "validate-trial":
        result = validate_trial_release(args.output_dir)
        for warning in result.warnings:
            print(f"WARNING: {warning}")
        for error in result.errors:
            print(f"ERROR: {error}")
        print("OK" if result.ok else "FAILED")
        return 0 if result.ok else 1

    if args.command == "extract-daily-candidate":
        crop_path = args.work_dir / "tables" / f"{args.image.stem}_{args.table_id}.jpg"
        if args.quad:
            normalized_quad_crop(args.image, crop_path, tuple(args.quad))
        else:
            normalized_crop(args.image, crop_path, tuple(args.region))
        tokens = read_ocr_tokens(crop_path)
        records, leftovers = map_daily_tokens(
            tokens,
            source_file=args.image.name,
            table_id=args.table_id,
            month_centers=tuple(args.month_centers),
            day_column_max_x=args.day_column_max_x,
            daily_y_min=args.daily_y_min,
            daily_y_max=args.daily_y_max,
            row_start=args.daily_row_start,
            row_step=args.daily_row_step,
            year=args.year,
        )
        write_daily_candidate_workbook(
            args.output,
            basin=args.basin,
            year=args.year,
            table_id=args.table_id,
            source_file=args.image.name,
            crop_path=crop_path,
            records=records,
            leftovers=leftovers,
        )
        print(f"mapped {len(records)} daily candidates; {len(leftovers)} OCR tokens need review")
        return 0

    if args.command == "extract-constant-daily-candidate":
        records = constant_daily_candidates(
            source_file=args.source_file.name,
            table_id=args.table_id,
            year=args.year,
            value=args.value,
            engine="visual_context_gpt+rapidocr_onnxruntime",
        )
        write_daily_candidate_workbook(
            args.output,
            basin=args.basin,
            year=args.year,
            table_id=args.table_id,
            source_file=args.source_file.name,
            crop_path=args.crop_path,
            records=records,
            leftovers=[],
        )
        print(f"mapped {len(records)} constant daily candidates; release remains blocked pending review")
        return 0

    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
