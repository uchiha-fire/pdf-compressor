"""
Command line interface for pdf_compressor.
"""

import argparse
import os
import sys
from typing import Tuple

from . import __version__
from .core import compress_pdf, format_size, get_file_size_mb


def interactive_mode() -> Tuple[str, str, int]:
    """Interactive CLI wizard for guiding users through compression."""
    print("=" * 60)
    print(f"      PDF COMPRESSION UTILITY (v{__version__}) - INTERACTIVE      ")
    print("=" * 60)

    while True:
        try:
            input_file = input("Enter path to PDF file: ").strip().strip('"').strip("'")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(130)

        if not input_file:
            continue

        if not os.path.exists(input_file):
            print(f"Error: File '{input_file}' does not exist. Please try again.")
            continue

        if not input_file.lower().endswith(".pdf"):
            print("Error: Input file must have a .pdf extension. Please try again.")
            continue

        break

    orig_size = get_file_size_mb(input_file)
    print(f"\nOriginal Size: {format_size(orig_size)}")
    print("-" * 60)
    print(" [1] Light      (~10-20% reduction, lossless stream compression)")
    print(" [2] Medium     (~40-60% reduction, 150 DPI, 75% quality)")
    print(" [3] Aggressive (~70-85% reduction, 96 DPI, 40% quality)")
    print("-" * 60)

    while True:
        try:
            choice = input("Select compression tier (1, 2, or 3) [default: 2]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(130)

        if not choice:
            level = 2
            break
        if choice in ("1", "2", "3"):
            level = int(choice)
            break
        print("Invalid selection. Please enter 1, 2, or 3.")

    base, ext = os.path.splitext(input_file)
    default_out = f"{base}_compressed_level{level}{ext}"

    try:
        out_prompt = input(f"Output path [Enter for '{default_out}']: ").strip().strip('"').strip("'")
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")
        sys.exit(130)

    output_file = out_prompt if out_prompt else default_out

    if os.path.exists(output_file):
        try:
            overwrite = input(f"File '{output_file}' already exists. Overwrite? (y/N): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(130)

        if overwrite not in ("y", "yes"):
            print("Aborted by user.")
            sys.exit(0)

    return input_file, output_file, level


def build_parser() -> argparse.ArgumentParser:
    """Construct command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="pdfcompress",
        description="Multi-tier PDF Compression CLI Tool",
        epilog="Run without arguments to launch interactive wizard.",
    )
    parser.add_argument("input", nargs="?", help="Path to input PDF file")
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        choices=[1, 2, 3],
        help="Compression tier (1=Light, 2=Medium, 3=Aggressive)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path for compressed output PDF",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        help="Custom JPEG quality (1-100), overrides tier default",
    )
    parser.add_argument(
        "-d",
        "--max-dim",
        type=int,
        help="Custom maximum image dimension in px, overrides tier default",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force overwrite of output file if it exists",
    )
    parser.add_argument(
        "--keep-metadata",
        action="store_true",
        help="Retain original document metadata (by default stripped for size)",
    )
    parser.add_argument(
        "-s",
        "--quiet",
        action="store_true",
        help="Quiet mode; suppress progress information",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main() -> None:
    """CLI Entry point."""
    parser = build_parser()
    args = parser.parse_args()

    # If no input file supplied, launch interactive wizard
    if args.input is None:
        input_file, output_file, level = interactive_mode()
        quiet = False
        quality = None
        max_dim = None
        keep_metadata = False
    else:
        input_file = args.input.strip().strip('"').strip("'")
        if not os.path.exists(input_file):
            print(f"Error: Input file does not exist: {input_file}", file=sys.stderr)
            sys.exit(1)
        if not input_file.lower().endswith(".pdf"):
            print(f"Error: Input file must be a PDF: {input_file}", file=sys.stderr)
            sys.exit(1)

        level = args.level if args.level is not None else 2
        quality = args.quality
        max_dim = args.max_dim
        keep_metadata = args.keep_metadata
        quiet = args.quiet

        if args.output:
            output_file = args.output
        else:
            base, ext = os.path.splitext(input_file)
            output_file = f"{base}_compressed_level{level}{ext}"

        if os.path.exists(output_file) and not args.force:
            print(
                f"Error: Output file already exists: '{output_file}'. Use -f/--force to overwrite.",
                file=sys.stderr,
            )
            sys.exit(1)

    orig_size_mb = get_file_size_mb(input_file)

    if not quiet:
        print(f"\nCompressing: {input_file}")
        print(f"Original size: {format_size(orig_size_mb)}")
        print(f"Applying compression tier: Level {level}...")

    def progress_callback(current: int, total: int) -> None:
        if not quiet:
            pct = int((current / total) * 100) if total else 0
            sys.stdout.write(f"\rProcessing page {current}/{total} ({pct}%)...")
            sys.stdout.flush()

    try:
        stats = compress_pdf(
            input_path=input_file,
            output_path=output_file,
            level=level,
            quality=quality,
            max_dim=max_dim,
            progress_callback=progress_callback,
            strip_metadata=not keep_metadata,
        )
    except Exception as err:
        if not quiet:
            sys.stdout.write("\n")
        print(f"\nError during compression: {err}", file=sys.stderr)
        sys.exit(1)

    if not quiet:
        sys.stdout.write("\n\n")
        print("=" * 45)
        print("          COMPRESSION COMPLETE")
        print("=" * 45)
        print(f" Output file:     {stats['output_path']}")
        print(f" Pages processed: {stats['pages']}")
        print(f" Original size:   {format_size(stats['orig_mb'])}")
        print(f" Compressed size: {format_size(stats['final_mb'])}")
        print(f" Space saved:     {stats['saved_pct']:.1f}%")
        print("=" * 45 + "\n")


if __name__ == "__main__":
    main()
