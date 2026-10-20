#!/usr/bin/env python3
"""Fail when portfolio site copy is hand-typed outside data/site.json."""

from __future__ import annotations

import html
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_JSON = ROOT / "data" / "site.json"

SKIP_DIR_NAMES = {
    ".git",
    "alt",
    "alt2",
    "normah",
    "__pycache__",
    ".venv",
    "node_modules",
}
SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".pdf",
    ".pyc",
}
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".json",
    ".html",
    ".css",
    ".js",
    ".txt",
    ".yml",
    ".yaml",
    ".svg",
    ".toml",
    ".cfg",
    ".ini",
    "",
}

# Build output at repo root (like dist/ in sister repos).
GENERATED_PATHS = {
    "index.html",
    "experience.html",
    "posts/index.html",
    "posts/agentic-ai-force-multiplier.html",
    "posts/becoming-ai-native.html",
    "posts/build-to-learn.html",
    "posts/directing-the-build.html",
    "posts/the-future-of-agentic-ai.html",
}

SKIP_FILES = {
    "archive.html",
}


def load_copy() -> dict[str, str]:
    payload = json.loads(SITE_JSON.read_text(encoding="utf-8"))
    required = (
        "title",
        "home_document_title",
        "tagline",
        "description",
        "about_lead",
    )
    missing = [
        key
        for key in required
        if not isinstance(payload.get(key), str) or not payload[key].strip()
    ]
    if missing:
        raise AssertionError(f"data/site.json missing fields: {', '.join(missing)}")
    return {key: payload[key].strip() for key in required}


def published_html_is_generated() -> bool:
    return (ROOT / "site" / "templates" / "index.html").is_file()


def skip_generated_paths() -> set[str]:
    return GENERATED_PATHS if published_html_is_generated() else set()


def iter_source_files() -> list[Path]:
    files: list[Path] = []
    generated = skip_generated_paths()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in SKIP_FILES or rel in generated:
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.resolve() == SITE_JSON.resolve():
            continue
        suffix = path.suffix.lower()
        if suffix in SKIP_SUFFIXES:
            continue
        if suffix not in TEXT_SUFFIXES and path.name not in {"CNAME", "Makefile", "Dockerfile"}:
            try:
                path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
        files.append(path)
    return sorted(files)


def title_pattern(title: str) -> re.Pattern[str]:
    escaped = re.escape(title)
    return re.compile(rf"(?<![A-Za-z0-9.-]){escaped}(?![A-Za-z0-9.-])")


def text_variants(value: str) -> list[str]:
    variants = {value}
    escaped = html.escape(value, quote=False)
    variants.add(escaped)
    variants.add(html.escape(value, quote=True))
    return [v for v in variants if v]


def patterns_for(label: str, value: str) -> list[tuple[str, re.Pattern[str]]]:
    if label == "title":
        return [(label, title_pattern(value))]
    out: list[tuple[str, re.Pattern[str]]] = []
    for variant in text_variants(value):
        out.append((label, re.compile(re.escape(variant))))
    return out


def find_hand_typed(path: Path, copy: dict[str, str]) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    rel = path.relative_to(ROOT).as_posix()
    hits: list[str] = []
    checks: list[tuple[str, re.Pattern[str]]] = []
    for label, value in copy.items():
        checks.extend(patterns_for(label, value))

    for line_no, line in enumerate(text.splitlines(), start=1):
        for label, pattern in checks:
            if pattern.search(line):
                hits.append(f"{rel}:{line_no}: hand-typed {label}: {line.strip()}")
    return hits


class SiteCopySourceOfTruthTests(unittest.TestCase):
    def test_site_json_has_required_fields(self):
        copy = load_copy()
        self.assertTrue(copy["title"])
        self.assertTrue(copy["about_lead"].startswith("Hi,"))

    def test_no_hand_typed_site_copy_outside_site_json(self):
        copy = load_copy()
        violations: list[str] = []
        for path in iter_source_files():
            violations.extend(find_hand_typed(path, copy))
        if violations:
            sample = "\n".join(violations[:40])
            more = "" if len(violations) <= 40 else f"\n... and {len(violations) - 40} more"
            self.fail(
                "Site copy must live only in data/site.json (built HTML is generated).\n"
                f"Found {len(violations)} hand-typed occurrence(s):\n{sample}{more}"
            )


if __name__ == "__main__":
    unittest.main()
