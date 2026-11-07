#!/usr/bin/env python3
"""Validate the public contact vCard and contact-page action hrefs."""

from __future__ import annotations

import html as html_lib
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


def site_copy() -> dict[str, str]:
    payload = json.loads(SITE_JSON.read_text(encoding="utf-8"))
    required = ("title", "tagline")
    missing = [
        key
        for key in required
        if not isinstance(payload.get(key), str) or not payload[key].strip()
    ]
    if missing:
        raise AssertionError(f"data/site.json missing fields: {', '.join(missing)}")
    return {key: payload[key].strip() for key in required}


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

        title = site_copy()["title"]
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
        self.assertIn("@@SITE_TAGLINE_ESC@@", html)
        self.assertIn('<h2 id="contact-title">Contact</h2>', html)
        self.assertIn('<h2 id="projects-title">Projects</h2>', html)
        self.assertNotIn("contact-bio\">Brings together", html)
        self.assertNotIn("/experience.html", html)
        self.assertNotIn('href="/posts/"', html)
        self.assertNotIn("/in/hafiy/", html)
        self.assertNotIn("nav-toggle", html)
        self.assertNotIn(".svg", html)
        self.assertNotIn(">Portfolio<", html)
        self.assertNotIn("portfolio.png", html)
        self.assertNotIn("Save Contact", html)
        self.assertNotIn("contact_download", html)
        self.assertNotIn('download="nazirul-hafiy.vcf"', html)

        bars = re.findall(
            r'<a class="contact-bar" href="([^"]+)"[^>]*>\s*'
            r'<span class="contact-bar-thumb"[^>]*>\s*'
            r'<img src="([^"]+)"[^>]*>\s*</span>\s*'
            r'<span class="contact-bar-title">([^<]+)</span>',
            html,
            flags=re.DOTALL,
        )
        expected = [
            ("https://wa.me/60135623005", "/assets/contact/whatsapp.png?v=3", "WhatsApp"),
            ("tel:+60135623005", "/assets/contact/phone.png?v=7", "Call"),
            ("mailto:nazirul@hafiy.my", "/assets/contact/email.png?v=3", "Email"),
            (
                "https://www.linkedin.com/in/nazirulhafiy/",
                "/assets/contact/linkedin.png?v=3",
                "LinkedIn",
            ),
            ("https://pcds2030.com", "/assets/contact/pcds2030.png?v=3", "pcds2030.com"),
            ("https://sde2030.com", "/assets/contact/sde2030.png?v=3", "sde2030.com"),
            (
                "https://ai.sarawak.news",
                "/assets/contact/ai-sarawak-news.png?v=3",
                "ai.sarawak.news",
            ),
        ]
        self.assertEqual([(h, s, t.strip()) for h, s, t in bars], expected)
        self.assertRegex(bars[0][0], r"^https://wa\.me/\d+$")
        self.assertEqual(bars[1][0], "tel:+60135623005")
        # Call is a normal tel: link: no custom GA marker, no new-tab target.
        call_open = html.split('href="tel:+60135623005"', 1)[1].split("</a>", 1)[0]
        self.assertNotIn("data-sn-event", call_open)
        self.assertNotIn("target=", call_open)
        self.assertNotIn("download=", call_open)

        for _, src, _ in expected:
            path_only = src.split("?", 1)[0]
            asset = ROOT / path_only.lstrip("/")
            self.assertTrue(asset.is_file(), f"missing asset {src}")
            self.assertGreater(asset.stat().st_size, 100)
            self.assertTrue(path_only.endswith(".png"))

    def test_built_contact_page_keeps_actions(self):
        if not CONTACT_BUILT.is_file():
            self.skipTest("contact/index.html not built yet")
        copy = site_copy()
        html = CONTACT_BUILT.read_text(encoding="utf-8")
        self.assertIn('href="https://wa.me/60135623005"', html)
        self.assertIn('href="tel:+60135623005"', html)
        self.assertIn('href="mailto:nazirul@hafiy.my"', html)
        self.assertIn(">Call<", html)
        self.assertNotIn(">Portfolio<", html)
        self.assertNotIn("Save Contact", html)
        self.assertNotIn("contact_download", html)
        self.assertNotIn('download="nazirul-hafiy.vcf"', html)
        self.assertIn("/assets/contact/phone.png?v=7", html)
        self.assertIn("data-sn-analytics-loader", html)
        self.assertIn(html_lib.escape(copy["tagline"]), html)
        self.assertIn(">Contact<", html)
        self.assertIn(">Projects<", html)
        self.assertNotIn("site-header", html)
        # vCard file remains published for direct URL use; not linked from the bars.
        self.assertTrue(VCARD.is_file())


if __name__ == "__main__":
    unittest.main()
