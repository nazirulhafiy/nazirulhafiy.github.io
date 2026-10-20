#!/usr/bin/env python3
"""Render portfolio HTML from data/site.json and site/templates/."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from analytics_loader import render_analytics_loader  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TEMPLATES = ROOT / "site" / "templates"
SITE_JSON = DATA / "site.json"

SITE_COPY_FIELDS = (
    "title",
    "home_document_title",
    "tagline",
    "description",
    "about_lead",
)

# Published HTML written at repo root (skipped by tests/test_site_copy.py).
OUTPUTS: dict[str, str] = {
    "index.html": "index.html",
    "experience.html": "experience.html",
    "posts/index.html": "posts/index.html",
    "posts/agentic-ai-force-multiplier.html": "posts/agentic-ai-force-multiplier.html",
    "posts/becoming-ai-native.html": "posts/becoming-ai-native.html",
    "posts/build-to-learn.html": "posts/build-to-learn.html",
    "posts/directing-the-build.html": "posts/directing-the-build.html",
    "posts/the-future-of-agentic-ai.html": "posts/the-future-of-agentic-ai.html",
}


def load_site(path: Path = SITE_JSON) -> dict[str, str]:
    if not path.is_file():
        raise SystemExit(f"missing site copy file: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("data/site.json must be an object")
    site: dict[str, str] = {}
    for field in SITE_COPY_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"data/site.json is missing {field}")
        site[field] = value.strip()
    return site


def substitution_map(site: dict[str, str]) -> dict[str, str]:
    title = site["title"]
    tagline = site["tagline"]
    description = site["description"]
    about_lead = site["about_lead"]
    home_document_title = site["home_document_title"]
    return {
        "@@SITE_TITLE@@": title,
        "@@SITE_TITLE_ESC@@": html.escape(title, quote=True),
        "@@HOME_DOCUMENT_TITLE@@": home_document_title,
        "@@HOME_DOCUMENT_TITLE_ESC@@": html.escape(home_document_title, quote=True),
        "@@SITE_TAGLINE@@": tagline,
        "@@SITE_TAGLINE_ESC@@": html.escape(tagline, quote=True),
        "@@SITE_DESCRIPTION@@": description,
        "@@SITE_DESCRIPTION_ESC@@": html.escape(description, quote=True),
        "@@SITE_ABOUT_LEAD@@": about_lead,
        "@@SITE_ABOUT_LEAD_ESC@@": html.escape(about_lead, quote=True),
        "@@SITE_COPYRIGHT@@": f"© 2026 {title}",
        "@@SITE_PAGE_TITLE_SUFFIX@@": f" — {title}",
        "@@SITE_PAGE_TITLE_SUFFIX_ESC@@": html.escape(f" — {title}", quote=True),
        "@@SITE_ARIA_HOME@@": f"{title}, home",
        "@@SITE_ARIA_HOME_ESC@@": html.escape(f"{title}, home", quote=True),
        "@@SITE_WRITING_META@@": (
            f"Writing by {title} about AI-native work, project delivery, "
            "operations, and building public digital tools."
        ),
        "@@SITE_WRITING_META_ESC@@": html.escape(
            f"Writing by {title} about AI-native work, project delivery, "
            "operations, and building public digital tools.",
            quote=True,
        ),
        "@@SITE_EXPERIENCE_META@@": (
            f"The professional experience of {title} across project delivery, "
            "operations, connectivity, marketing, and digital communities."
        ),
        "@@SITE_EXPERIENCE_META_ESC@@": html.escape(
            f"The professional experience of {title} across project delivery, "
            "operations, connectivity, marketing, and digital communities.",
            quote=True,
        ),
    }


def render_template(text: str, site: dict[str, str]) -> str:
    rendered = text.replace("@@ANALYTICS_LOADER@@", render_analytics_loader())
    for key, value in substitution_map(site).items():
        rendered = rendered.replace(key, value)
    leftovers = [token for token in substitution_map(site) if token in rendered]
    if "@@ANALYTICS_LOADER@@" in rendered:
        raise SystemExit("unresolved template token: @@ANALYTICS_LOADER@@")
    if leftovers:
        raise SystemExit(f"unresolved template tokens: {', '.join(sorted(set(leftovers)))}")
    return rendered


def build(dist: Path = ROOT) -> None:
    site = load_site()
    for rel_template, rel_output in OUTPUTS.items():
        template_path = TEMPLATES / rel_template
        if not template_path.is_file():
            raise SystemExit(f"missing template: {template_path.relative_to(ROOT)}")
        out_path = dist / rel_output
        out_path.parent.mkdir(parents=True, exist_ok=True)
        rendered = render_template(template_path.read_text(encoding="utf-8"), site)
        out_path.write_text(rendered, encoding="utf-8", newline="\n")


def main() -> int:
    build()
    print(f"Built {len(OUTPUTS)} page(s) from {SITE_JSON.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
