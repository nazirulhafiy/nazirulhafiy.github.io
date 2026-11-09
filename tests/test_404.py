#!/usr/bin/env python3
"""Assert the custom GitHub Pages 404 page contract."""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "site" / "templates" / "404.html"
BUILT = ROOT / "404.html"
SITEMAP = ROOT / "sitemap.xml"

ABSOLUTE_ATTR_RE = re.compile(
    r"""\b(?:href|src)=(["'])(?!https?:|mailto:|tel:|#|/)([^"']+)\1""",
    re.IGNORECASE,
)


class Custom404Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(["python3", "scripts/build.py"], cwd=ROOT, check=True)

    def test_template_and_built_page_exist_with_heading(self) -> None:
        for path in (TEMPLATE, BUILT):
            self.assertTrue(path.is_file(), f"missing {path.relative_to(ROOT)}")
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertIn("<h1>Page not found</h1>", text)
                self.assertIn(
                    "The page you're looking for doesn't exist or has moved.",
                    text,
                )
                self.assertRegex(
                    text,
                    re.compile(
                        r'<meta\s+name="robots"\s+content="noindex"\s*/?>',
                        re.IGNORECASE,
                    ),
                )
                self.assertIn('href="/"', text)
                self.assertIn("← Home", text)
                self.assertIn("site-header", text)
                self.assertIn("site-footer", text)
                self.assertNotIn("data-sn-contact-events", text)
                self.assertNotIn("data-sn-event=", text)

        template_text = TEMPLATE.read_text(encoding="utf-8")
        built_text = BUILT.read_text(encoding="utf-8")
        self.assertIn("@@ANALYTICS_LOADER@@", template_text)
        self.assertEqual(built_text.count("data-sn-analytics-loader"), 1)

    def test_absolute_asset_and_nav_paths(self) -> None:
        for path in (TEMPLATE, BUILT):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                relative = ABSOLUTE_ATTR_RE.findall(text)
                self.assertEqual(
                    relative,
                    [],
                    f"{path.relative_to(ROOT)} has relative href/src values "
                    f"(GitHub Pages serves 404.html under nested URLs): {relative}",
                )
                self.assertIn('/styles.css?v=', text)
                self.assertIn('/assets/favicon.ico?v=', text)
                self.assertIn('href="/experience.html"', text)
                self.assertIn('href="/posts/"', text)
                self.assertIn('href="/#experiments"', text)

    def test_not_listed_in_sitemap(self) -> None:
        tree = ET.parse(SITEMAP)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text or "" for el in tree.findall(".//sm:loc", ns)]
        for loc in locs:
            self.assertNotIn("404", loc)
            self.assertFalse(loc.rstrip("/").endswith("/404.html"))


if __name__ == "__main__":
    unittest.main()
