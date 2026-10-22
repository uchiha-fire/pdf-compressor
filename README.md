# pdfcompress-cli

[![PyPI version](https://img.shields.io/pypi/v/pdfcompress-cli.svg)](https://pypi.org/project/pdfcompress-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/pdfcompress-cli.svg)](https://pypi.org/project/pdfcompress-cli/)
[![GitHub stars](https://img.shields.io/github/stars/uchiha-fire/pdf-compressor?style=social)](https://github.com/uchiha-fire/pdf-compressor)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A multi-tier interactive and scriptable PDF compression CLI tool for Linux, macOS, and Windows.

Reduce bulky PDF documents by up to 85% with smart lossless content-stream optimization, identical object deduplication, and intelligent image downsampling.

---

## Features

- 🚀 **Interactive Wizard**: Just run `pdfcompress` with no flags to launch a guided prompt with automatic default naming.
- 🎛️ **Multi-Tier Compression**: 3 curated compression presets from gentle lossless stream optimization to aggressive size reduction.
- 🖼️ **Image Resampling & JPEG Compression**: Optimizes embedded images, normalizes color spaces (RGB/RGBA/CMYK), and applies high-quality Lanczos resampling.
- ⚡ **Zero External Binary Dependencies**: Pure Python built on `pypdf` and `Pillow`—no `ghostscript` or `qpdf` system binaries needed!
- 🔗 **Smart Path Handling**: Seamlessly accepts shell-escaped paths with spaces (`\ `), drag-and-dropped files, and tilde (`~`) home paths.
- 📦 **Python Library API**: Import `compress_pdf` directly into your own Python applications.
- 📊 **Real-Time Progress & Statistics**: Single-line dynamic page counter with percentage and exact byte/percentage savings report.

---

## Installation

Install directly via `pip`:

```bash
pip install pdfcompress-cli
```

---

## Quick Start

### 1. Interactive Mode
Run the command without any arguments:

```bash
pdfcompress
```

The interactive wizard will prompt you for:
1. Input PDF file path (supports drag-and-drop from file managers)
2. Desired compression level
3. Output destination (with automatic default naming)

### 2. Command Line Usage

Compress a PDF using Medium compression (Level 2, default):
```bash
pdfcompress document.pdf
# Creates document_compressed_level2.pdf
```

Specify a custom compression level and output destination:
```bash
pdfcompress report.pdf -l 3 -o report_small.pdf
```

Force overwrite of existing output:
```bash
pdfcompress report.pdf -l 2 -o report_small.pdf -f
```

---

## Compression Tiers

| Tier | Name | Target Savings | Technique | Ideal For |
| :---: | :--- | :---: | :--- | :--- |
| **1** | **Light** | ~10–20% | Lossless stream compression & object deduplication; retains images 100% untouched | Official documents, legal filings, text/vector PDFs |
| **2** | **Medium** *(Default)* | ~40–60% | Stream compression + images scaled to max 1600px @ 75% quality | Scanned books, email attachments, web uploads |
| **3** | **Aggressive** | ~70–85% | Stream compression + images scaled to max 1000px @ 40% quality | Maximum storage conservation, mobile bandwidth, quick previews |

### Advanced Image Fine-Tuning
You can override preset defaults with custom image quality and dimension flags:

```bash
# Custom 80% JPEG quality and max 1200px dimension
pdfcompress document.pdf -q 80 -d 1200 -o custom.pdf
```

---

## CLI Options Reference

```
usage: pdfcompress [-h] [-l {1,2,3}] [-o OUTPUT] [-q QUALITY] [-d MAX_DIM] [-f]
                   [--keep-metadata] [-s] [-v]
                   [input]

Multi-tier PDF Compression CLI Tool

positional arguments:
  input                 Path to input PDF file

options:
  -h, --help            show this help message and exit
  -l, --level {1,2,3}   Compression tier (1=Light, 2=Medium, 3=Aggressive)
  -o, --output OUTPUT   Path for compressed output PDF
  -q, --quality QUALITY Custom JPEG quality (1-100), overrides tier default
  -d, --max-dim MAX_DIM Custom maximum image dimension in px, overrides tier default
  -f, --force           Force overwrite of output file if it exists
  --keep-metadata       Retain original document metadata (by default stripped for size)
  -s, --quiet           Quiet mode; suppress progress information
  -v, --version         show program's version number and exit
```

---

## Python API Usage

You can also use `pdfcompress-cli` directly in your Python applications:

```python
from pdf_compressor import compress_pdf, format_size

result = compress_pdf(
    input_path="input.pdf",
    output_path="output.pdf",
    level=2,  # 1=Light, 2=Medium, 3=Aggressive
    strip_metadata=True
)

print(f"Original size:   {format_size(result['orig_mb'])}")
print(f"Compressed size: {format_size(result['final_mb'])}")
print(f"Space saved:     {result['saved_pct']:.1f}%")
```

---

## Author & Maintainer

Developed and maintained by **Shubham Sharma**:

- 💻 GitHub: [@uchiha-fire](https://github.com/uchiha-fire)
- 💼 LinkedIn: [Shubham Sharma](https://www.linkedin.com/in/shubham-sharma)
- ✉️ Email: [shubham@list2shop.com](mailto:shubham@list2shop.com)

If you find this tool helpful, please give it a ⭐️ on [GitHub](https://github.com/uchiha-fire/pdf-compressor)!

---

## Acknowledgements & Attributions

This tool builds upon and credits the exceptional work of open-source projects:

- **[pypdf](https://github.com/py-pdf/pypdf)**: Pure Python PDF library used for low-level PDF parsing, stream compression (`compress_content_streams`), and object deduplication (`compress_identical_objects`). Licensed under BSD-3-Clause.
- **[Pillow](https://github.com/python-pillow/Pillow)**: The friendly PIL fork used for image format decoding, Lanczos resampling, and JPEG optimization. Licensed under HPND.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
