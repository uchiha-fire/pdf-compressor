"""
Unit tests for pdf_compressor.core module.
"""

import os
import tempfile
import pytest
from PIL import Image
from pypdf import PdfReader

from pdf_compressor.core import (
    clean_path,
    compress_pdf,
    format_size,
    get_file_size_mb,
)


@pytest.fixture
def sample_pdf(tmp_path):
    """Create a temporary multi-page PDF containing large uncompressed images."""
    pdf_path = str(tmp_path / "sample.pdf")
    # Create two large images with gradients/colors
    img1 = Image.new("RGB", (2200, 1600), color=(200, 50, 50))
    img2 = Image.new("RGB", (2000, 1400), color=(50, 200, 50))
    img1.save(pdf_path, save_all=True, append_images=[img2], quality=100)
    return pdf_path


def test_format_size():
    assert format_size(0.5) == "512.0 KB"
    assert format_size(1.0) == "1.00 MB"
    assert format_size(2.75) == "2.75 MB"


def test_get_file_size_mb(sample_pdf):
    mb = get_file_size_mb(sample_pdf)
    assert mb > 0.0


def test_compress_pdf_level_1(sample_pdf, tmp_path):
    out_path = str(tmp_path / "out_l1.pdf")
    stats = compress_pdf(sample_pdf, out_path, level=1)

    assert os.path.exists(out_path)
    assert stats["pages"] == 2
    assert stats["level"] == 1
    assert stats["final_bytes"] > 0

    reader = PdfReader(out_path)
    assert len(reader.pages) == 2


def test_compress_pdf_level_2(sample_pdf, tmp_path):
    out_path = str(tmp_path / "out_l2.pdf")
    calls = []

    def callback(curr, total):
        calls.append((curr, total))

    stats = compress_pdf(sample_pdf, out_path, level=2, progress_callback=callback)

    assert os.path.exists(out_path)
    assert stats["pages"] == 2
    assert len(calls) == 2
    assert calls[-1] == (2, 2)

    reader = PdfReader(out_path)
    assert len(reader.pages) == 2


def test_compress_pdf_level_3(sample_pdf, tmp_path):
    out_path = str(tmp_path / "out_l3.pdf")
    stats = compress_pdf(sample_pdf, out_path, level=3)

    assert os.path.exists(out_path)
    assert stats["pages"] == 2
    assert stats["final_bytes"] > 0

    reader = PdfReader(out_path)
    assert len(reader.pages) == 2


def test_compress_custom_settings(sample_pdf, tmp_path):
    out_path = str(tmp_path / "out_custom.pdf")
    stats = compress_pdf(sample_pdf, out_path, quality=50, max_dim=800)

    assert os.path.exists(out_path)
    assert stats["pages"] == 2
    reader = PdfReader(out_path)
    assert len(reader.pages) == 2


def test_compress_file_not_found():
    with pytest.raises(FileNotFoundError):
        compress_pdf("non_existent_file.pdf", "out.pdf")


def test_compress_non_pdf_file(tmp_path):
    txt_file = str(tmp_path / "document.txt")
    with open(txt_file, "w") as f:
        f.write("hello")
    with pytest.raises(ValueError, match="not a PDF"):
        compress_pdf(txt_file, "out.pdf")


def test_compress_invalid_level(sample_pdf, tmp_path):
    out_path = str(tmp_path / "out.pdf")
    with pytest.raises(ValueError, match="Invalid compression level"):
        compress_pdf(sample_pdf, out_path, level=9)


def test_clean_path(tmp_path):
    # Test tilde expansion
    assert clean_path("~") == os.path.expanduser("~")
    # Test quotes stripping
    assert clean_path('"quoted/path.pdf"') == "quoted/path.pdf"
    assert clean_path("'single/quoted.pdf'") == "single/quoted.pdf"
    # Test backslash space unescaping
    spaced_dir = tmp_path / "my folder"
    spaced_dir.mkdir()
    pdf_file = spaced_dir / "doc.pdf"
    pdf_file.write_text("dummy")

    escaped_str = str(spaced_dir).replace(" ", "\\ ") + "/doc.pdf"
    cleaned = clean_path(escaped_str)
    assert os.path.exists(cleaned)
    assert cleaned == str(pdf_file)
