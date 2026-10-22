"""
Core compression engine for pdf_compressor.
"""

import io
import os
import sys
from typing import Callable, Dict, Optional, Any
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError


# Backward-compatible resampling filter for Pillow
RESAMPLE_FILTER = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.LANCZOS)


def clean_path(path_str: str) -> str:
    """Clean and normalize a user-entered path.

    Handles:
    - Enclosing quotes (' or ")
    - Shell-escaped spaces (e.g. \\ ) from drag-and-drop or bash autocomplete
    - Tilde expansion (~) to user home directory
    """
    if not path_str:
        return ""
    p = path_str.strip()
    # Strip enclosing single or double quotes
    if len(p) >= 2 and ((p[0] == '"' and p[-1] == '"') or (p[0] == "'" and p[-1] == "'")):
        p = p[1:-1].strip()
    # If literal path does not exist on disk and has backslash-escaped spaces, unescape them
    if "\\ " in p and not os.path.exists(p):
        p = p.replace("\\ ", " ")
    # Expand user home directory (~)
    p = os.path.expanduser(p)
    return p


def get_file_size_mb(path: str) -> float:
    """Return file size in megabytes."""
    return os.path.getsize(clean_path(path)) / (1024 * 1024)


def format_size(mb: float) -> str:
    """Format size in MB or KB for user display."""
    if mb < 1.0:
        return f"{mb * 1024:.1f} KB"
    return f"{mb:.2f} MB"


def compress_pdf(
    input_path: str,
    output_path: str,
    level: int = 2,
    quality: Optional[int] = None,
    max_dim: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    strip_metadata: bool = True,
) -> Dict[str, Any]:
    """Compress a PDF file using stream compression and image optimization.

    Args:
        input_path: Path to the input PDF file.
        output_path: Path to save the compressed PDF.
        level: Compression tier (1=Light, 2=Medium, 3=Aggressive).
        quality: Optional custom JPEG quality (1-100), overrides preset level.
        max_dim: Optional custom maximum image dimension in pixels, overrides preset level.
        progress_callback: Optional callback receiving (current_page, total_pages).
        strip_metadata: Whether to strip metadata to reduce file size.

    Returns:
        Dict with execution summary (orig_bytes, final_bytes, saved_pct, etc.)

    Raises:
        FileNotFoundError: If input_path does not exist.
        ValueError: If input is not a PDF or level is invalid.
        PdfReadError: If the PDF cannot be read or is corrupted.
    """
    input_path = clean_path(input_path)
    output_path = clean_path(output_path)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not input_path.lower().endswith(".pdf"):
        raise ValueError(f"File is not a PDF: {input_path}")

    if level not in (1, 2, 3) and quality is None and max_dim is None:
        raise ValueError(f"Invalid compression level '{level}'. Choose 1, 2, or 3.")

    # Image settings mapping based on level presets
    img_settings = {
        1: None,
        2: {"quality": 75, "max_dim": 1600},
        3: {"quality": 40, "max_dim": 1000},
    }

    selected_setting = img_settings.get(level, img_settings[2])
    if selected_setting is not None:
        selected_setting = selected_setting.copy()

    # Apply custom overrides if provided
    if quality is not None or max_dim is not None:
        if selected_setting is None:
            selected_setting = {"quality": quality or 75, "max_dim": max_dim or 1600}
        else:
            if quality is not None:
                selected_setting["quality"] = max(1, min(100, quality))
            if max_dim is not None:
                selected_setting["max_dim"] = max(100, max_dim)

    try:
        reader = PdfReader(input_path)
    except Exception as e:
        raise PdfReadError(f"Failed to read PDF file '{input_path}': {e}") from e

    if reader.is_encrypted:
        raise ValueError(f"PDF is encrypted or password-protected: {input_path}")

    writer = PdfWriter()
    total_pages = len(reader.pages)

    for page_idx, reader_page in enumerate(reader.pages, start=1):
        # Add page to writer first so it is attached to the writer
        writer_page = writer.add_page(reader_page)

        if selected_setting is not None:
            try:
                images_dict = writer_page.images
            except Exception:
                images_dict = {}

            for img_name, img_obj in list(images_dict.items()):
                try:
                    raw_img = Image.open(io.BytesIO(img_obj.data))

                    # Normalize color modes to RGB for JPEG compression
                    if raw_img.mode in ("RGBA", "LA"):
                        bg = Image.new("RGB", raw_img.size, (255, 255, 255))
                        bg.paste(raw_img, mask=raw_img.split()[-1])
                        raw_img = bg
                    elif raw_img.mode in ("P", "CMYK"):
                        raw_img = raw_img.convert("RGB")
                    elif raw_img.mode not in ("RGB", "L", "1"):
                        raw_img = raw_img.convert("RGB")

                    w, h = raw_img.size
                    target_max_dim = selected_setting["max_dim"]
                    resized = False
                    if max(w, h) > target_max_dim:
                        scaling = target_max_dim / float(max(w, h))
                        new_w = max(1, int(w * scaling))
                        new_h = max(1, int(h * scaling))
                        raw_img = raw_img.resize((new_w, new_h), RESAMPLE_FILTER)
                        resized = True

                    # Verify that re-encoding saves bytes or downscaled
                    test_io = io.BytesIO()
                    raw_img.save(
                        test_io,
                        format="JPEG",
                        quality=selected_setting["quality"],
                        optimize=True,
                    )
                    test_size = len(test_io.getvalue())

                    if resized or test_size < len(img_obj.data):
                        writer_page.images[img_name].replace(
                            raw_img, quality=selected_setting["quality"]
                        )
                except Exception:
                    # In case of inline images, unsupported color filters, or read errors
                    continue

        try:
            writer_page.compress_content_streams()
        except Exception:
            pass

        if progress_callback:
            progress_callback(page_idx, total_pages)

    # Losslessly deduplicate identical objects (e.g. repeated fonts, headers, background images)
    try:
        writer.compress_identical_objects()
    except Exception:
        pass

    if strip_metadata:
        writer.add_metadata({})
    elif reader.metadata:
        try:
            writer.add_metadata(reader.metadata)
        except Exception:
            pass

    # Ensure target parent directory exists
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "wb") as f_out:
        writer.write(f_out)

    orig_bytes = os.path.getsize(input_path)
    final_bytes = os.path.getsize(output_path)
    saved_bytes = max(0, orig_bytes - final_bytes)
    saved_pct = (saved_bytes / orig_bytes * 100.0) if orig_bytes > 0 else 0.0

    return {
        "input_path": input_path,
        "output_path": output_path,
        "level": level,
        "pages": total_pages,
        "orig_bytes": orig_bytes,
        "final_bytes": final_bytes,
        "orig_mb": orig_bytes / (1024 * 1024),
        "final_mb": final_bytes / (1024 * 1024),
        "saved_bytes": saved_bytes,
        "saved_pct": saved_pct,
    }
