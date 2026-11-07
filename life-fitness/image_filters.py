#!/usr/bin/env python3

"""
processing filters to enhance images that contain a QR
code to enable better code detection
"""

import cv2
import numpy as np

from PIL import (
    Image,
    ImageEnhance,
    ImageFilter,
    ImageOps,
)

# ============================================================
# IMAGE PROCESSING FUNCTIONS
#
# Each function accepts the original PIL image and yields
# one or more (variant_name, processed_image) pairs.
#
# Each function operates independently from the original image.
# ============================================================


def original(img):
    """Return the original image."""
    yield "original", img


def grayscale(img):
    """Convert to grayscale."""
    yield "grayscale", ImageOps.grayscale(img)


def colour_channels(img):
    """Test individual RGB channels."""

    red, green, blue = img.split()

    yield "channel_red", red.filter(
            ImageFilter.GaussianBlur(radius=3))
    yield "channel_green", green.filter(
            ImageFilter.GaussianBlur(radius=3))
    yield "channel_blue", blue.filter(
            ImageFilter.GaussianBlur(radius=3))


def contrast(img):
    """Autocontrast and additional contrast enhancement."""

    gray = ImageOps.grayscale(img)
    enhanced = ImageOps.autocontrast(gray, cutoff=1)

    yield "autocontrast", enhanced

    yield "contrast_1.5", ImageEnhance.Contrast(
        enhanced
    ).enhance(1.5)

    yield "contrast_2.0", ImageEnhance.Contrast(
        enhanced
    ).enhance(2.0)


def averaging_filters(img):
    """
    Test box averaging filters at different scales.

    All processing starts from the original grayscale image.
    """

    gray = np.asarray(
        ImageOps.grayscale(img)
    )

    # Square averaging filters
    for size in (3, 5, 7, 9):

        result = cv2.blur(
            gray,
            (size, size),
        )

        yield (
            f"average_{size}",
            Image.fromarray(result),
        )

    # Horizontal averaging
    for width in (3, 5, 7, 9):

        result = cv2.blur(
            gray,
            (width, 1),
        )

        yield (
            f"average_h_{width}",
            Image.fromarray(result),
        )

    # Vertical averaging
    for height in (3, 5, 7, 9):

        result = cv2.blur(
            gray,
            (1, height),
        )

        yield (
            f"average_v_{height}",
            Image.fromarray(result),
        )


def sharpening(img):
    """Generate several unsharp-mask sharpening variants."""

    gray = ImageOps.grayscale(img)

    for radius, percent, threshold in [
        (1, 150, 2),
        (2, 200, 3),
        (3, 150, 2),
    ]:
        sharpened = gray.filter(
            ImageFilter.UnsharpMask(
                radius=radius,
                percent=percent,
                threshold=threshold,
            )
        )

        yield f"sharpen_{radius}", sharpened


def gaussian_blur(img):
    """Generate several Gaussian blur variants."""

    gray = ImageOps.grayscale(img)

    for radius in (0.5, 1.0):
        yield (
            f"blur_{radius}",
            gray.filter(
                ImageFilter.GaussianBlur(radius=radius)
            ),
        )


def median_filter(img):
    """Generate several median-filter variants."""

    gray = ImageOps.grayscale(img)

    for size in (3, 5):
        yield (
            f"median_{size}",
            gray.filter(ImageFilter.MedianFilter(size=size)),
        )


def downscale(img):
    """Generate downscaled grayscale images."""

    gray = ImageOps.grayscale(img)

    for scale in (2, 3, 4):
        width = int(gray.width / scale)
        height = int(gray.height / scale)

        yield (
            f"downscale_{scale}",
            gray.resize(
                (width, height),
                Image.Resampling.LANCZOS,
            ),
        )


def upscale(img):
    """Generate enlarged grayscale images."""

    gray = ImageOps.grayscale(img)

    for scale in (1.5, 2.0):
        width = int(gray.width * scale)
        height = int(gray.height * scale)

        yield (
            f"upscale_{scale}",
            gray.resize(
                (width, height),
                Image.Resampling.LANCZOS,
            ),
        )


def threshold(img):
    """Generate several global threshold variants."""

    gray = ImageOps.grayscale(img)
    contrast_img = ImageOps.autocontrast(gray, cutoff=1)

    for value in (100, 128, 150, 155, 165, 175, 185, 195, 205):
        binary = contrast_img.point(
            lambda p, t=value: 255 if p > t else 0
        )

        yield f"threshold_{value}", binary


def threshold_175(img):
    """Autocontrast followed by thresholding at 175."""

    gray = ImageOps.grayscale(img)
    contrast_img = ImageOps.autocontrast(gray, cutoff=1)

    yield (
        "threshold_175",
        contrast_img.point(
            lambda p: 255 if p > 175 else 0
        ),
    )


def otsu(img):
    """Apply automatic Otsu thresholding."""

    gray = np.array(ImageOps.grayscale(img))

    _, binary = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )

    yield "otsu", Image.fromarray(binary)


def adaptive_threshold(img):
    """Generate adaptive threshold variants."""

    gray = np.array(ImageOps.grayscale(img))

    methods = [
        (
            "adaptive_gaussian",
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        ),
        (
            "adaptive_mean",
            cv2.ADAPTIVE_THRESH_MEAN_C,
        ),
    ]

    for method_name, method in methods:
        for block_size in (21, 31):
            for c in (5, 10):

                binary = cv2.adaptiveThreshold(
                    gray,
                    255,
                    method,
                    cv2.THRESH_BINARY,
                    block_size,
                    c,
                )

                yield (
                    f"{method_name}_{block_size}_{c}",
                    Image.fromarray(binary),
                )


def median_3(img):
    """Apply a 3x3 median filter."""

    gray = ImageOps.grayscale(img)

    yield (
        "median_3",
        gray.filter(ImageFilter.MedianFilter(size=3)),
    )


def cv_median_3(img):
    """Apply OpenCV 3x3 median filtering."""

    gray = np.array(ImageOps.grayscale(img))

    median = cv2.medianBlur(gray, 3)

    yield "cv_median_3", Image.fromarray(median)


def directional_sharpening(img):
    """Apply horizontal and vertical directional sharpening."""

    gray = np.array(ImageOps.grayscale(img))

    kernels = {
        "horizontal": np.array([
            [0, 0, 0],
            [-1, 2, -1],
            [0, 0, 0],
        ], dtype=np.float32),

        "vertical": np.array([
            [0, -1, 0],
            [0, 2, 0],
            [0, -1, 0],
        ], dtype=np.float32),
    }

    for name, kernel in kernels.items():

        detail = cv2.filter2D(
            gray,
            -1,
            kernel,
        )

        sharpened = cv2.addWeighted(
            gray,
            1.0,
            detail,
            0.5,
            0,
        )

        yield (
            f"directional_{name}",
            Image.fromarray(sharpened),
        )


def bilateral(img):
    """Apply bilateral filtering with different parameters."""

    gray = np.array(ImageOps.grayscale(img))

    for sigma in (25, 40):

        filtered = cv2.bilateralFilter(
            gray,
            d=5,
            sigmaColor=sigma,
            sigmaSpace=25,
        )

        yield (
            f"bilateral_{sigma}",
            Image.fromarray(filtered),
        )


def median_bilateral(img):
    """Apply median filtering followed by bilateral filtering."""

    gray = np.array(ImageOps.grayscale(img))

    median = cv2.medianBlur(gray, 3)

    filtered = cv2.bilateralFilter(
        median,
        d=5,
        sigmaColor=25,
        sigmaSpace=25,
    )

    yield "median_bilateral", Image.fromarray(filtered)


def median_autocontrast(img):
    """Apply median filtering followed by autocontrast."""

    gray = ImageOps.grayscale(img)

    median = gray.filter(
        ImageFilter.MedianFilter(size=3)
    )

    yield (
        "median_autocontrast",
        ImageOps.autocontrast(median, cutoff=1),
    )


def median_threshold_175(img):
    """Apply median filtering, autocontrast and thresholding."""

    gray = ImageOps.grayscale(img)

    median = gray.filter(
        ImageFilter.MedianFilter(size=3)
    )

    contrast_img = ImageOps.autocontrast(
        median,
        cutoff=1,
    )

    yield (
        "median_threshold_175",
        contrast_img.point(
            lambda p: 255 if p > 175 else 0
        ),
    )


def usm(img):
    """Apply strong unsharp-mask sharpening."""

    gray = ImageOps.grayscale(img)

    sharpened = gray.filter(
        ImageFilter.UnsharpMask(
            radius=8,
            percent=800,
            threshold=0,
        )
    )

    yield "usm", sharpened


def usm_blur(img):
    """Apply strong unsharp masking followed by Gaussian blur."""

    gray = ImageOps.grayscale(img)

    sharpened = gray.filter(
        ImageFilter.UnsharpMask(
            radius=8,
            percent=800,
            threshold=0,
        )
    )

    yield (
        "usm_blur",
        sharpened.filter(
            ImageFilter.GaussianBlur(radius=3)
        ),
    )


def blur(img):
    """Apply Gaussian blur with radius 3."""

    gray = ImageOps.grayscale(img)

    yield (
        "blur",
        gray.filter(
            ImageFilter.GaussianBlur(radius=3)
        ),
    )


# ============================================================
# PROCESSING FUNCTION REGISTRY
# ============================================================

PROCESSING_FUNCTIONS = {
    "original": original,
    "grayscale": grayscale,
    "colour_channels": colour_channels,
    "contrast": contrast,
    "averaging_filters": averaging_filters,
    "sharpening": sharpening,
    "gaussian_blur": gaussian_blur,
    "median_filter": median_filter,
    "downscale": downscale,
    "upscale": upscale,
    "threshold": threshold,
    "threshold_175": threshold_175,
    "otsu": otsu,
    "adaptive_threshold": adaptive_threshold,
    "median_3": median_3,
    "cv_median_3": cv_median_3,
    "directional_sharpening": directional_sharpening,
    "bilateral": bilateral,
    "median_bilateral": median_bilateral,
    "median_autocontrast": median_autocontrast,
    "median_threshold_175": median_threshold_175,
    "usm": usm,
    "usm_blur": usm_blur,
    "blur": blur,
}


def generate_variants(img, enabled_tests):
    """Generate variants using only enabled processing functions."""

    for test_name in enabled_tests:

        if test_name not in PROCESSING_FUNCTIONS:
            raise ValueError(
                f"Unknown processing test: {test_name}"
            )

        yield from PROCESSING_FUNCTIONS[test_name](img)
