#!/usr/bin/env python3
"""Assert the portfolio stays light-only (no system-dark CSS or dual theme-color)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLES = ROOT / "styles.css"

HTML_PATHS = [
    "site/templates/index.html",
    "site/templates/experience.html",
    "site/templates/404.html",
    "site/templates/contact/index.html",
    "site/templates/posts/index.html",
    "site/templates/posts/agentic-ai-force-multiplier.html",
    "site/templates/posts/becoming-ai-native.html",
    "site/templates/posts/build-to-learn.html",
    "site/templates/posts/directing-the-build.html",
    "site/templates/posts/the-future-of-agentic-ai.html",
    "index.html",
    "experience.html",
    "404.html",
    "contact/index.html",
    "posts/index.html",
    "posts/agentic-ai-force-multiplier.html",
    "posts/becoming-ai-native.html",
    "posts/build-to-learn.html",
    "posts/directing-the-build.html",
    "posts/the-future-of-agentic-ai.html",
]

LIGHT_TOKENS = {
    "--background": "#ffffff",
    "--surface": "#f6f6f6",
    "--foreground": "#111111",
    "--muted": "#5f5f5f",
    "--border": "#dedede",
    "--accent": "#111111",
    "--accent-soft": "#f1f1f1",
}

CSS_CACHE = "v=45"


class ThemeLightOnlyCssTest(unittest.TestCase):
    def test_color_scheme_light_only(self) -> None:
        css = STYLES.read_text(encoding="utf-8")
        self.assertIn("color-scheme: light;", css)
        self.assertNotIn("color-scheme: light dark;", css)
        self.assertNotRegex(css, r"prefers-color-scheme\s*:\s*dark")

    def test_light_tokens_present(self) -> None:
        css = STYLES.read_text(encoding="utf-8")
        for token, value in LIGHT_TOKENS.items():
            self.assertRegex(
                css,
                rf"{re.escape(token)}\s*:\s*{re.escape(value)}\s*;",
                f"missing light token {token}",
            )
            # Dark palette values must not appear as token assignments.
        for dark_value in ("#1b1b1b", "#f5f5f5", "#b4b4b4", "#2d2d2d", "#1a1a1a"):
            self.assertNotRegex(
                css,
                rf"--(?:background|surface|foreground|muted|border|accent|accent-soft)\s*:\s*{re.escape(dark_value)}\s*;",
                f"unexpected dark token value {dark_value}",
            )


class ThemeLightOnlyHtmlTest(unittest.TestCase):
    def test_single_light_theme_color_and_cache_bust(self) -> None:
        pattern = re.compile(
            r'<meta\s+name="theme-color"\s+content="([^"]+)"(?:\s+media="([^"]*)")?\s*/?>',
            re.IGNORECASE,
        )
        for rel in HTML_PATHS:
            text = (ROOT / rel).read_text(encoding="utf-8")
            metas = pattern.findall(text)
            self.assertEqual(
                len(metas),
                1,
                f"{rel} should declare exactly one theme-color meta, found {metas}",
            )
            content, media = metas[0]
            self.assertEqual(content.lower(), "#ffffff", f"{rel} theme-color")
            self.assertEqual(media, "", f"{rel} must not media-gate theme-color")
            self.assertNotIn("prefers-color-scheme", text, f"{rel} leftover preference media")
            self.assertIn(
                f'/styles.css?{CSS_CACHE}',
                text,
                f"{rel} missing styles.css?{CSS_CACHE}",
            )


if __name__ == "__main__":
    unittest.main()
