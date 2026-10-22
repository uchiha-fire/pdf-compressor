"""
Tests for CLI interface in pdf_compressor.cli.
"""

import subprocess
import sys
import pytest
from PIL import Image


@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = str(tmp_path / "test_doc.pdf")
    img = Image.new("RGB", (1000, 800), color=(100, 150, 200))
    img.save(pdf_path)
    return pdf_path


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "pdf_compressor.cli", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0
    assert "Multi-tier PDF Compression CLI Tool" in result.stdout


def test_cli_version():
    result = subprocess.run(
        [sys.executable, "-m", "pdf_compressor.cli", "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_cli_compress_file(sample_pdf, tmp_path):
    out_pdf = str(tmp_path / "compressed_output.pdf")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pdf_compressor.cli",
            sample_pdf,
            "-l",
            "2",
            "-o",
            out_pdf,
            "-s",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0
    assert (tmp_path / "compressed_output.pdf").exists()


def test_cli_file_not_found():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pdf_compressor.cli",
            "nonexistent.pdf",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 1
    assert "does not exist" in result.stderr


def test_cli_existing_output_without_force(sample_pdf, tmp_path):
    out_pdf = str(tmp_path / "already_exists.pdf")
    with open(out_pdf, "w") as f:
        f.write("dummy")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pdf_compressor.cli",
            sample_pdf,
            "-o",
            out_pdf,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 1
    assert "already exists" in result.stderr


def test_cli_existing_output_with_force(sample_pdf, tmp_path):
    out_pdf = str(tmp_path / "already_exists.pdf")
    with open(out_pdf, "w") as f:
        f.write("dummy")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pdf_compressor.cli",
            sample_pdf,
            "-o",
            out_pdf,
            "-f",
            "-s",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0
