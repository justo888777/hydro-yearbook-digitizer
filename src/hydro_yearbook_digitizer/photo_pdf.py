from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


def _natural_key(path: Path) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', path.name)]


def photos_to_pdf(
    image_paths: Iterable[Path],
    output_pdf: Path,
    *,
    max_long_edge: int | None = None,
    quality: int = 92,
) -> Path:
    """Create an image-only browsing PDF while preserving source photos.

    The PDF is a derived convenience artifact. OCR should still use the original
    or rectified page images so that PDF compression cannot erase decimal points.
    """
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError('Pillow is required: pip install -e .[image]') from exc

    paths = sorted((Path(path) for path in image_paths), key=_natural_key)
    if not paths:
        raise ValueError('no images supplied')
    if not 1 <= quality <= 100:
        raise ValueError('quality must be between 1 and 100')

    pages = []
    for path in paths:
        with Image.open(path) as source:
            page = ImageOps.exif_transpose(source).convert('RGB')
            if max_long_edge and max(page.size) > max_long_edge:
                scale = max_long_edge / max(page.size)
                page = page.resize(
                    (max(1, round(page.width * scale)), max(1, round(page.height * scale))),
                    Image.Resampling.LANCZOS,
                )
            pages.append(page.copy())

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    first, *rest = pages
    first.save(
        output_pdf,
        'PDF',
        save_all=True,
        append_images=rest,
        resolution=300.0,
        quality=quality,
        optimize=True,
    )
    return output_pdf
