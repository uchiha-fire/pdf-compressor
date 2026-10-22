"""
pdf-compressor-cli
Multi-tier interactive and scriptable PDF compression CLI tool.
"""

__version__ = "0.1.3"
__author__ = "Zephyrus Labs"
__maintainer__ = "Shubham Sharma"
__email__ = "zephyrus.labs@gmail.com"
__developer_email__ = "sharmashubham25962@gmail.com"

from .core import compress_pdf, format_size, get_file_size_mb, clean_path

__all__ = [
    "compress_pdf",
    "format_size",
    "get_file_size_mb",
    "clean_path",
    "__version__",
    "__author__",
    "__maintainer__",
    "__email__",
    "__developer_email__",
]
