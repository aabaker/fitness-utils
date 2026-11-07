#!/usr/bin/env python3

"""
QR code variant coverage analyser.

Reads the CSV produced by qr_regression.py and determines
which variants provide the greatest incremental image coverage.

The algorithm is greedy:
    1. Select the variant decoding the most images.
    2. Remove those images from the remaining dataset.
    3. Select the best variant for the remaining images.
    4. Repeat until no further images can be decoded.

Usage:
    python qr_coverage.py results.csv

    python qr_coverage.py results.csv -v
"""

import argparse
import csv

from pathlib import Path


def read_results(filename):
    """Read CSV results and return image data and variant names."""

    with filename.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as csvfile:

        reader = csv.DictReader(csvfile)

        if not reader.fieldnames:
            raise ValueError("CSV file has no header")

        if "filename" not in reader.fieldnames:
            raise ValueError("CSV must contain a filename column")

        variants = [
            name for name in reader.fieldnames
            if name != "filename"
        ]

        images = []

        for row in reader:

            results = {}

            for variant in variants:
                value = row[variant].strip()

                results[variant] = value in ("1", "True", "true")

            images.append({
                "filename": row["filename"],
                "results": results,
            })

    return images, variants


def analyse_coverage(images, variants, verbose=False):
    """
    Repeatedly select the variant decoding the most remaining images.

    Returns the ordered list of selected variants.
    """

    remaining = set(range(len(images)))
    selected = []

    print()
    print("=" * 70)
    print("QR CODE VARIANT COVERAGE ANALYSIS")
    print("=" * 70)

    print(f"Total images:   {len(images)}")
    print(f"Total variants: {len(variants)}")

    print()
    print("OPTIMAL GREEDY VARIANT SELECTION")
    print("-" * 70)

    iteration = 1

    while remaining:

        best_variant = None
        best_count = 0
        best_images = []

        # Find the variant decoding the most remaining images
        for variant in variants:

            decoded = [
                index
                for index in remaining
                if images[index]["results"][variant]
            ]

            count = len(decoded)

            if count > best_count:
                best_variant = variant
                best_count = count
                best_images = decoded

        # No variant can decode any further images
        if best_count == 0:
            break

        # Record the selected variant
        selected.append({
            "variant": best_variant,
            "count": best_count,
            "remaining_before": len(remaining),
            "images": best_images,
        })

        print(
            f"{iteration:2d}. "
            f"{best_variant:35s} "
            f"{best_count:5d} images"
        )

        if verbose:
            for index in best_images:
                print(
                    f"      {images[index]['filename']}"
                )

        # Remove images successfully decoded by this variant
        remaining.difference_update(best_images)

        iteration += 1

    # Final summary
    print()
    print("-" * 70)
    print("SUMMARY")
    print("-" * 70)

    total_decoded = len(images) - len(remaining)

    print(f"Images decoded:    {total_decoded}/{len(images)}")

    if images:
        print(
            f"Overall coverage:  "
            f"{100 * total_decoded / len(images):.1f}%"
        )

    print(f"Variants required: {len(selected)}")
    print(f"Images remaining:  {len(remaining)}")

    if remaining:
        print()
        print("IMAGES NOT DECODED BY ANY VARIANT")
        print("-" * 70)

        for index in sorted(remaining):
            print(f"  {images[index]['filename']}")

    return selected, remaining


def main():

    parser = argparse.ArgumentParser(
        description="Analyse incremental QR code variant coverage"
    )

    parser.add_argument(
        "csvfile",
        type=Path,
        help="CSV file produced by qr_regression.py",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="List the images decoded by each selected variant",
    )

    args = parser.parse_args()

    if not args.csvfile.is_file():
        parser.error(f"File not found: {args.csvfile}")

    try:
        images, variants = read_results(args.csvfile)

    except (ValueError, csv.Error) as exc:
        parser.error(str(exc))

    if not variants:
        parser.error("CSV contains no variant columns")

    if not images:
        parser.error("CSV contains no image records")

    analyse_coverage(
        images,
        variants,
        args.verbose,
    )


if __name__ == "__main__":
    main()

