#!/usr/bin/env python3
"""Validate the public contact vCard and contact-page action hrefs."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VCARD = ROOT / "contact" / "nazirul-hafiy.vcf"
CONTACT_TEMPLATE = ROOT / "site" / "templates" / "contact" / "index.html"
CONTACT_BUILT = ROOT / "contact" / "index.html"
SITE_JSON = ROOT / "data" / "site.json"


def site_title() -> str:
    import json

    payload = json.loads(SITE_JSON.read_text(encoding="utf-8"))
    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        raise AssertionError("data/site.json missing title")
    return title.strip()


def unfold_vcard(text: str) -> list[str]:
    """Unfold RFC 2425/6350 soft line breaks and return logical lines."""
    # Soft wrap: CRLF + space/tab
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
        # No invented org/job-title/address fields (vCard TITLE property).
        for forbidden in ("ORG", "TITLE", "ADR", "NOTE"):
            self.assertNotIn(forbidden, by_name)

    def test_contact_page_action_order_and_hrefs(self):
        html = CONTACT_TEMPLATE.read_text(encoding="utf-8")
        # Built page should match after build; assert template source of truth.
        actions = re.findall(
            r'<a class="contact-btn"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
            html,
        )
        self.assertEqual(
            [(href, label.strip()) for href, label in actions],
            [
                ("https://wa.me/60135623005", "WhatsApp"),
                ("/contact/nazirul-hafiy.vcf", "Save Contact"),
                ("mailto:nazirul@hafiy.my", "Email"),
                ("https://www.linkedin.com/in/nazirulhafiy/", "LinkedIn"),
            ],
        )
        wa = actions[0][0]
        self.assertRegex(wa, r"^https://wa\.me/\d+$")
        self.assertEqual(wa, "https://wa.me/60135623005")
        self.assertIn('download="nazirul-hafiy.vcf"', html)
        self.assertNotIn("tel:", html)
        self.assertNotIn("/in/hafiy/", html)
        self.assertNotIn('class="project"', html)

    def test_built_contact_page_keeps_actions(self):
        if not CONTACT_BUILT.is_file():
            self.skipTest("contact/index.html not built yet")
        html = CONTACT_BUILT.read_text(encoding="utf-8")
        self.assertIn('href="https://wa.me/60135623005"', html)
        self.assertIn('href="mailto:nazirul@hafiy.my"', html)
        self.assertIn('href="/contact/nazirul-hafiy.vcf"', html)
        self.assertIn("data-sn-analytics-loader", html)


if __name__ == "__main__":
    unittest.main()
