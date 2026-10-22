"""
pdf-compressor-cli
Multi-tier interactive and scriptable PDF compression CLI tool.
"""

__version__ = "0.1.1"

from .core import compress_pdf, format_size, get_file_size_mb, clean_path

__all__ = ["compress_pdf", "format_size", "get_file_size_mb", "clean_path", "__version__"]
