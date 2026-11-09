#!/usr/bin/env python3
"""Assert /contact/ GA4 custom event wiring stays scoped and nonpersonal."""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTACT_TEMPLATE = ROOT / "site" / "templates" / "contact" / "index.html"
CONTACT_BUILT = ROOT / "contact" / "index.html"

OTHER_PAGES = (
    "index.html",
    "experience.html",
    "404.html",
    "posts/index.html",
    "posts/agentic-ai-force-multiplier.html",
    "posts/becoming-ai-native.html",
    "posts/build-to-learn.html",
    "posts/directing-the-build.html",
    "posts/the-future-of-agentic-ai.html",
)

EVENTS_SCRIPT_RE = re.compile(
    r'<script\b[^>]*\bdata-sn-contact-events\b[^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)
EMAIL_MARKER_RE = re.compile(
    r'<a\b[^>]*\bhref="mailto:[^"]+"[^>]*\bdata-sn-event="email_click"[^>]*>'
    r'|<a\b[^>]*\bdata-sn-event="email_click"[^>]*\bhref="mailto:[^"]+"[^>]*>',
    re.IGNORECASE,
)


class ContactEventsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(["python3", "scripts/build.py"], cwd=ROOT, check=True)

    def test_template_and_built_page_wire_exactly_one_event(self) -> None:
        for path in (CONTACT_TEMPLATE, CONTACT_BUILT):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertEqual(text.count("data-sn-contact-events"), 1)
                self.assertEqual(text.count('data-sn-event="email_click"'), 1)
                self.assertNotIn("contact_download", text)
                self.assertRegex(text, EMAIL_MARKER_RE)
                # HTTPS / tel contact/project bars must not get custom event markers.
                self.assertNotIn('data-sn-event="whatsapp', text)
                self.assertEqual(len(re.findall(r"data-sn-event=", text)), 1)

                scripts = EVENTS_SCRIPT_RE.findall(text)
                self.assertEqual(len(scripts), 1)
                script = scripts[0]
                self.assertIn('gtag("event", name, { surface: "contact" })', script)
                self.assertIn("email_click", script)
                self.assertNotIn("contact_download", script)
                self.assertNotIn("preventDefault", script)
                self.assertNotIn("event_callback", script)
                self.assertNotIn("transport", script)
                # No personal contact values in the event payload path.
                self.assertNotIn("nazirul@hafiy.my", script)
                self.assertNotIn("60135623005", script)
                self.assertNotIn("mailto:", script)
                self.assertNotIn("tel:", script)
                self.assertNotIn(".vcf", script)

    def test_other_built_pages_do_not_ship_contact_events(self) -> None:
        for rel in OTHER_PAGES:
            text = (ROOT / rel).read_text(encoding="utf-8")
            with self.subTest(page=rel):
                self.assertNotIn("data-sn-contact-events", text)
                self.assertNotIn("data-sn-event=", text)
                self.assertNotIn("email_click", text)
                self.assertNotIn("contact_download", text)


if __name__ == "__main__":
    unittest.main()
