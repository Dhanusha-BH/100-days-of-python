"""
colors.py — Extract the top N most common colors from an image using NumPy.

The approach:
  1. Downscale the image (a full-resolution photo doesn't need per-pixel
     precision for a color histogram, and it keeps this fast).
  2. Flatten to an (N, 3) array of RGB pixels.
  3. Quantize each channel into buckets (e.g. multiples of 24) so that
     visually-identical colors that differ by JPEG noise or a slight
     gradient get counted together, instead of fragmenting into hundreds
     of near-duplicate 1-pixel "colors".
  4. Count how many pixels fall into each bucket with np.unique.
  5. For each of the top N buckets, average the *original* pixel colors
     that landed in it, so the reported color is a true representative
     rather than the bucket's quantized corner.
"""

import numpy as np
from PIL import Image


def extract_top_colors(image: Image.Image, top_n=10, bucket_size=24, max_dim=200):
    image = image.convert("RGB")

    # Downscale for speed; a color histogram doesn't need full resolution.
    resized = image.copy()
    resized.thumbnail((max_dim, max_dim))

    arr = np.asarray(resized).reshape(-1, 3).astype(np.int32)
    total_pixels = arr.shape[0]

    # Quantize into buckets to merge near-duplicate colors.
    buckets = (arr // bucket_size) * bucket_size

    # Pack each bucket's (r, g, b) into a single integer key for fast
    # counting with np.unique (much faster than hashing tuples in Python).
    keys = buckets[:, 0] * 1_000_000 + buckets[:, 1] * 1_000 + buckets[:, 2]

    unique_keys, counts = np.unique(keys, return_counts=True)

    n = min(top_n, len(unique_keys))
    top_indices = np.argsort(-counts)[:n]
    top_keys = unique_keys[top_indices]
    top_counts = counts[top_indices]

    results = []
    for key, count in zip(top_keys, top_counts):
        mask = keys == key
        avg_color = arr[mask].mean(axis=0).round().astype(int)
        r, g, b = avg_color.tolist()
        results.append({
            "hex": f"#{r:02X}{g:02X}{b:02X}",
            "rgb": (r, g, b),
            "percent": round(float(count) / total_pixels * 100, 1),
        })

    return results
