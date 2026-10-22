"""
pdf-compressor-cli
Multi-tier interactive and scriptable PDF compression CLI tool.
"""

__version__ = "0.1.1"
__author__ = "Shubham Sharma"
__email__ = "shubham@list2shop.com"

from .core import compress_pdf, format_size, get_file_size_mb, clean_path

__all__ = [
    "compress_pdf",
    "format_size",
    "get_file_size_mb",
    "clean_path",
    "__version__",
    "__author__",
    "__email__",
]
