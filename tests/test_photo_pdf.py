import re

import pytest

pytest.importorskip('PIL')
from PIL import Image

from hydro_yearbook_digitizer.photo_pdf import photos_to_pdf


def test_photos_to_pdf_keeps_page_count(tmp_path):
    images = []
    for index in range(2):
        path = tmp_path / f'page_{index + 1}.jpg'
        Image.new('RGB', (120, 80), 'white').save(path)
        images.append(path)

    output = photos_to_pdf(images, tmp_path / 'volume.pdf')
    content = output.read_bytes()
    assert content.startswith(b'%PDF-')
    assert len(re.findall(rb'/Type\s*/Page\b', content)) == 2
