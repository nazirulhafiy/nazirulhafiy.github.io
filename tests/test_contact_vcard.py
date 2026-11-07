#!/usr/bin/env python3
"""Validate the public contact vCard and contact-page action hrefs."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VCARD = ROOT / "contact" / "nazirul-hafiy.vcf"
CONTACT_TEMPLATE = ROOT / "site" / "templates" / "contact" / "index.html"
CONTACT_BUILT = ROOT / "contact" / "index.html"
SITE_JSON = ROOT / "data" / "site.json"
CONTACT_ASSETS = ROOT / "assets" / "contact"

EXACT_BIO = (
    "Brings together experience in marketing, project management, and operations "
    "across government, enterprise, and start-up environments. PMP-trained and "
    "skilled in AI-assisted workflows, with a practical approach to planning, "
    "delivery, and performance tracking.."
)


def site_title() -> str:
    payload = json.loads(SITE_JSON.read_text(encoding="utf-8"))
    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        raise AssertionError("data/site.json missing title")
    return title.strip()


def unfold_vcard(text: str) -> list[str]:
    unfolded = re.sub(r"\r\n[ \t]", "", text)
    return [line for line in unfolded.split("\r\n") if line != ""]


class ContactVCardTests(unittest.TestCase):
    def test_vcard_uses_crlf_and_required_fields(self):
        raw = VCARD.read_bytes()
        self.assertTrue(raw.endswith(b"\r\n"), "vCard must end with CRLF")
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""), "vCard must not use bare LF")
        text = raw.decode("utf-8")
        lines = unfold_vcard(text)
        self.assertEqual(lines[0], "BEGIN:VCARD")
        self.assertEqual(lines[1], "VERSION:3.0")
        self.assertEqual(lines[-1], "END:VCARD")

        by_name: dict[str, list[str]] = {}
        for line in lines[2:-1]:
            name, _, value = line.partition(":")
            key = name.split(";", 1)[0].upper()
            by_name.setdefault(key, []).append(value)

        title = site_title()
        parts = title.split()
        family = parts[-1] if parts else title
        given = " ".join(parts[:-1]) if len(parts) >= 2 else ""
        self.assertEqual(by_name["FN"], [title])
        self.assertEqual(by_name["N"], [f"{family};{given};;;"])
        self.assertIn("+60135623005", by_name["TEL"][0])
        self.assertIn("nazirul@hafiy.my", by_name["EMAIL"][0])
        self.assertEqual(
            by_name["URL"],
            ["https://hafiy.my", "https://www.linkedin.com/in/nazirulhafiy/"],
        )
        for forbidden in ("ORG", "TITLE", "ADR", "NOTE"):
            self.assertNotIn(forbidden, by_name)

    def test_contact_page_bars_order_and_assets(self):
        html = CONTACT_TEMPLATE.read_text(encoding="utf-8")
        self.assertNotIn("site-header", html)
        self.assertIn(EXACT_BIO, html)
        self.assertNotIn("AI Native —", html)
        self.assertNotIn("Portfolio", html)
        self.assertNotIn("/experience.html", html)
        self.assertNotIn('href="/posts/"', html)
        self.assertNotIn("tel:", html)
        self.assertNotIn("/in/hafiy/", html)
        self.assertNotIn("contact-btn", html)
        self.assertNotIn("nav-toggle", html)

        bars = re.findall(
            r'<a class="contact-bar" href="([^"]+)"[^>]*>\s*'
            r'<span class="contact-bar-thumb"[^>]*>\s*'
            r'<img src="([^"]+)"[^>]*>\s*</span>\s*'
            r'<span class="contact-bar-title">([^<]+)</span>',
            html,
            flags=re.DOTALL,
        )
        expected = [
            ("https://wa.me/60135623005", "/assets/contact/whatsapp.svg", "WhatsApp"),
            ("/contact/nazirul-hafiy.vcf", "/assets/contact/download.svg", "Save Contact"),
            ("mailto:nazirul@hafiy.my", "/assets/contact/email.svg", "Email"),
            (
                "https://www.linkedin.com/in/nazirulhafiy/",
                "/assets/contact/linkedin.svg",
                "LinkedIn",
            ),
            ("https://pcds2030.com", "/assets/contact/pcds2030.png", "pcds2030.com"),
            ("https://sde2030.com", "/assets/contact/sde2030.png", "sde2030.com"),
            (
                "https://ai.sarawak.news",
                "/assets/contact/ai-sarawak-news.svg",
                "ai.sarawak.news",
            ),
        ]
        self.assertEqual([(h, s, t.strip()) for h, s, t in bars], expected)
        self.assertRegex(bars[0][0], r"^https://wa\.me/\d+$")
        self.assertIn('download="nazirul-hafiy.vcf"', html)

        for _, src, _ in expected:
            asset = ROOT / src.lstrip("/")
            self.assertTrue(asset.is_file(), f"missing asset {src}")
            self.assertGreater(asset.stat().st_size, 100)

    def test_built_contact_page_keeps_actions(self):
        if not CONTACT_BUILT.is_file():
            self.skipTest("contact/index.html not built yet")
        html = CONTACT_BUILT.read_text(encoding="utf-8")
        self.assertIn('href="https://wa.me/60135623005"', html)
        self.assertIn('href="mailto:nazirul@hafiy.my"', html)
        self.assertIn('href="/contact/nazirul-hafiy.vcf"', html)
        self.assertIn("data-sn-analytics-loader", html)
        self.assertIn(EXACT_BIO, html)
        self.assertNotIn("site-header", html)


if __name__ == "__main__":
    unittest.main()
