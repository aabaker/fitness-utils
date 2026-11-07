#!/usr/bin/env python3

"""
QR code regression tester.

Runs selected image preprocessing techniques against every image
and records whether ZBar detects a QR code.

Usage:
    python qr_regression.py /path/to/images
    python qr_regression.py /path/to/images -o results.csv
    python qr_regression.py /path/to/images --recursive

Enable or disable processing techniques using enabled_tests.
"""

import argparse
import csv
import sys

from pathlib import Path

from image_filters import *

from pyzbar.pyzbar import decode, ZBarSymbol


# ============================================================
# ENABLED PROCESSING TECHNIQUES
# ============================================================

enabled_tests = [
    "blur",
    "usm_blur",
    "median_3",
    "median_threshold_175",
    "downscale",
    "averaging_filters",
]

# ============================================================
# IMAGE FILE EXTENSIONS
# ============================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}


# ============================================================
# QR CODE DETECTION
# ============================================================

def contains_qr_code(img):
    """
    Return True if ZBar detects at least one QR code.

    The contents of the QR code are deliberately ignored.
    """

    symbols = decode(
        img,
        symbols=[ZBarSymbol.QRCODE],
    )

    return len(symbols) > 0


# ============================================================
# IMAGE DISCOVERY
# ============================================================

def find_images(directory, recursive=False):
    """Find image files in a directory."""

    if recursive:
        files = directory.rglob("*")
    else:
        files = directory.iterdir()

    return sorted(
        f for f in files
        if f.is_file()
        and f.suffix.lower() in IMAGE_EXTENSIONS
    )


# ============================================================
# IMAGE TESTING AND CSV OUTPUT
# ============================================================

def test_image(filename, csvfile, summary):
    """Test one image against every enabled preprocessing variant."""

    print(f"Testing {filename.name}")

    try:
        with Image.open(filename) as source:
            img = source.convert("RGB")

    except Exception as exc:
        print(f"  ERROR opening image: {exc}")
        summary["errors"] += 1
        return

    image_success = False
    image_results = {}

    for variant_name, candidate in generate_variants(img, enabled_tests):

        try:
            success = contains_qr_code(candidate)
            error = ""

        except Exception as exc:
            success = False
            error = str(exc)

        if error:
            print(f"  {variant_name}: ERROR ({error})")
            summary["errors"] += 1
        else:
            print(
                f"  {variant_name}: "
                f"{'PASS' if success else 'FAIL'}"
            )

        image_results[variant_name] = int(success)

        if success:
            image_success = True

            summary["variant_successes"][variant_name] = (
                summary["variant_successes"].get(
                    variant_name, 0
                ) + 1
            )

        summary["variant_tests"][variant_name] = (
            summary["variant_tests"].get(
                variant_name, 0
            ) + 1
        )

    # Initialise DictWriter and write header on first image
    if not summary.get("csv_header_written", False):

        summary["variant_names"] = list(image_results.keys())

        fieldnames = ["filename"] + summary["variant_names"]

        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        summary["csv_header_written"] = True

    else:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["filename"] + summary["variant_names"],
        )

    # Write one CSV row per image
    row = {"filename": str(filename)}
    row.update(image_results)

    writer.writerow(row)

    summary["images_tested"] += 1

    if image_success:
        summary["images_decoded"] += 1
    else:
        summary["images_failed"] += 1


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="QR code image preprocessing regression tester"
    )

    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing photographs",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("qr-regression.csv"),
        help="CSV output filename (default: qr-regression.csv)",
    )

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Search subdirectories recursively",
    )

    args = parser.parse_args()

    if not args.directory.is_dir():
        parser.error(
            f"Not a directory: {args.directory}"
        )

    # Validate enabled tests before processing images
    for test_name in enabled_tests:
        if test_name not in PROCESSING_FUNCTIONS:
            parser.error(
                f"Unknown enabled test: {test_name}"
            )

    images = find_images(
        args.directory,
        args.recursive,
    )

    if not images:
        print("No image files found.")
        return 1

    print(f"Found {len(images)} images")
    print(f"Enabled tests: {', '.join(enabled_tests)}")
    print(f"Writing results to {args.output}")
    print()

    summary = {
        "images_tested": 0,
        "images_decoded": 0,
        "images_failed": 0,
        "errors": 0,
        "variant_tests": {},
        "variant_successes": {},
        "csv_header_written": False,
        "variant_names": [],
    }

    with args.output.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:

        for filename in images:
            test_image(filename, csvfile, summary)

    # Overall summary
    print()
    print("=" * 60)
    print("REGRESSION TEST SUMMARY")
    print("=" * 60)

    print(f"Images tested:  {summary['images_tested']}")
    print(f"Images decoded: {summary['images_decoded']}")
    print(f"Images failed:  {summary['images_failed']}")
    print(f"Errors:         {summary['errors']}")

    print()
    print("SUCCESS BY VARIANT")
    print("-" * 60)

    for variant, tests in summary["variant_tests"].items():

        successes = summary["variant_successes"].get(
            variant, 0
        )

        percentage = 100 * successes / tests

        print(
            f"{variant:30s} "
            f"{successes:4d}/{tests:<4d} "
            f"({percentage:5.1f}%)"
        )

    print()
    print(f"Full results written to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

