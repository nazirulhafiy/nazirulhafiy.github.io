#!/usr/bin/env python3
"""Assert approved original-PFP favicon hashes, ICO frame parity, and declarations."""

from __future__ import annotations

import hashlib
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

# Approved original-PFP favicon set (owner decision t2604u, 7 Nov 2026).
EXPECTED_SHA256 = {
    "favicon.ico": "f87d5026bd0075f21d924db4bd5dfeefd4dc3a0acff0c3ff23ce3bc7f290f545",
    "favicon-16.png": "3cee6117406396deb249b5d64c8e0a32e7992ae71618ad1a22879ce9c71214c3",
    "favicon-32.png": "0386f04b8b4715ff9d6263787e0c3005ba1da6b7ca3a475e8bd4899d36fd777a",
    "favicon-48.png": "f84a7e62d65c98815c5d3d678455b62c74334afdb5abe5580635c4c00e26b918",
    "favicon-180.png": "73e439e625d2d3338772fd59135fee6846c4a2e4c07f86ee54df4ccf7f904010",
}

# Path aliases declared in HTML (must match the sized PNG bytes).
ALIAS_SHA256 = {
    "favicon.png": EXPECTED_SHA256["favicon-32.png"],
    "apple-touch-icon.png": EXPECTED_SHA256["favicon-180.png"],
}

ICON_CACHE = "v=3"

REQUIRED_HREFS = (
    f'/assets/favicon.ico?{ICON_CACHE}',
    f'/assets/favicon-16.png?{ICON_CACHE}',
    f'/assets/favicon.png?{ICON_CACHE}',
    f'/assets/favicon-48.png?{ICON_CACHE}',
    f'/assets/apple-touch-icon.png?{ICON_CACHE}',
)

# Templates and built pages that must declare the favicon set.
HTML_PATHS = [
    "site/templates/index.html",
    "site/templates/experience.html",
    "site/templates/contact/index.html",
    "site/templates/posts/index.html",
    "site/templates/posts/agentic-ai-force-multiplier.html",
    "site/templates/posts/becoming-ai-native.html",
    "site/templates/posts/build-to-learn.html",
    "site/templates/posts/directing-the-build.html",
    "site/templates/posts/the-future-of-agentic-ai.html",
    "index.html",
    "experience.html",
    "contact/index.html",
    "posts/index.html",
    "posts/agentic-ai-force-multiplier.html",
    "posts/becoming-ai-native.html",
    "posts/build-to-learn.html",
    "posts/directing-the-build.html",
    "posts/the-future-of-agentic-ai.html",
]

FORBIDDEN_HREFS = (
    "/assets/favicon-64.png",
    "/assets/favicon-192.png",
    "/assets/favicon-512.png",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ico_png_frames(path: Path) -> list[tuple[int, int, bytes]]:
    data = path.read_bytes()
    reserved, typ, count = struct.unpack_from("<HHH", data, 0)
    if reserved != 0 or typ != 1:
        raise ValueError(f"not an ICO: {path}")
    frames: list[tuple[int, int, bytes]] = []
    for i in range(count):
        offset = 6 + i * 16
        width, height, _colors, _res, _planes, _bitcount, nbytes, blob_off = (
            struct.unpack_from("<BBBBHHII", data, offset)
        )
        width = width or 256
        height = height or 256
        blob = data[blob_off : blob_off + nbytes]
        frames.append((width, height, blob))
    return frames


class FaviconAssetsTest(unittest.TestCase):
    def test_approved_asset_hashes(self) -> None:
        for name, digest in EXPECTED_SHA256.items():
            path = ASSETS / name
            self.assertTrue(path.is_file(), f"missing {path}")
            self.assertEqual(sha256_file(path), digest, f"hash mismatch for {name}")

    def test_alias_hashes(self) -> None:
        for name, digest in ALIAS_SHA256.items():
            path = ASSETS / name
            self.assertTrue(path.is_file(), f"missing {path}")
            self.assertEqual(sha256_file(path), digest, f"hash mismatch for {name}")

    def test_ico_frames_match_pngs(self) -> None:
        frames = ico_png_frames(ASSETS / "favicon.ico")
        by_size = {w: blob for w, _h, blob in frames}
        self.assertEqual(set(by_size), {16, 32, 48})
        for size, png_name in (
            (16, "favicon-16.png"),
            (32, "favicon-32.png"),
            (48, "favicon-48.png"),
        ):
            blob = by_size[size]
            self.assertTrue(blob.startswith(b"\x89PNG\r\n\x1a\n"), f"ICO {size} not PNG")
            self.assertEqual(
                blob,
                (ASSETS / png_name).read_bytes(),
                f"ICO {size}x{size} frame must match {png_name} byte-for-byte",
            )

    def test_profile_png_not_replaced_by_favicon_set(self) -> None:
        # Page portrait stays the social/PFP asset; favicon-180 must not overwrite it.
        profile = ASSETS / "profile.png"
        self.assertTrue(profile.is_file())
        self.assertNotEqual(
            sha256_file(profile),
            EXPECTED_SHA256["favicon-180.png"],
            "profile.png must remain the full portrait, not a favicon size",
        )

    def test_removed_silhouette_paths_absent(self) -> None:
        for name in ("favicon-64.png", "favicon-192.png", "favicon-512.png"):
            self.assertFalse(
                (ASSETS / name).exists(),
                f"unexpected leftover silhouette asset: {name}",
            )


class FaviconDeclarationsTest(unittest.TestCase):
    def test_pages_declare_icon_links(self) -> None:
        for rel in HTML_PATHS:
            text = (ROOT / rel).read_text(encoding="utf-8")
            for href in REQUIRED_HREFS:
                self.assertIn(href, text, f"{rel} missing {href}")
            for href in FORBIDDEN_HREFS:
                self.assertNotIn(href, text, f"{rel} still references {href}")
            self.assertIn('sizes="16x16 32x32 48x48"', text, f"{rel} ICO sizes")
            self.assertIn('sizes="16x16"', text, f"{rel} 16 PNG sizes")
            self.assertIn('sizes="32x32"', text, f"{rel} 32 PNG sizes")
            self.assertIn('sizes="48x48"', text, f"{rel} 48 PNG sizes")
            self.assertIn('sizes="180x180"', text, f"{rel} apple-touch sizes")


if __name__ == "__main__":
    unittest.main()
