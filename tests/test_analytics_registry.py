#!/usr/bin/env python3
"""Tests for data/analytics.json validation and dist check."""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


analytics_registry = _load_module("analytics_registry", "scripts/analytics_registry.py")
analytics_loader = _load_module("analytics_loader", "scripts/analytics_loader.py")
check_analytics_dist = _load_module("check_analytics_dist", "scripts/check_analytics_dist.py")
build = _load_module("build", "scripts/build.py")


class AnalyticsRegistryTests(unittest.TestCase):
    def test_load_repo_registry(self):
        reg = analytics_registry.load_analytics()
        self.assertEqual(reg.version, 1)
        self.assertEqual(reg.internal_cookie, "sn_internal")
        self.assertIs(reg.spa, False)
        self.assertEqual(list(reg.hosts), ["hafiy.my"])
        entry = reg.hosts["hafiy.my"]
        self.assertEqual(entry.ga4_measurement_id, "G-JTQGL6WQYW")
        self.assertEqual(entry.cf_beacon_token, "57920823ff68472c8e325232c7b86127")
        self.assertEqual(entry.aliases, ["www.hafiy.my", "nazirulhafiy.github.io"])
        self.assertEqual(reg.primary_ga4_id(), "G-JTQGL6WQYW")
        self.assertEqual(reg.honour_cookies, ("sn_internal",))

    def test_loader_marker_and_internal_toggle(self):
        loader = analytics_loader.render_analytics_loader()
        self.assertIn(analytics_loader.ANALYTICS_LOADER_ATTR, loader)
        self.assertEqual(loader.count(analytics_loader.ANALYTICS_LOADER_ATTR), 1)
        self.assertIn("G-JTQGL6WQYW", loader)
        self.assertIn("57920823ff68472c8e325232c7b86127", loader)
        self.assertIn("sn_internal", loader)
        self.assertIn("q.get('internal')==='1'", loader)
        self.assertIn("traffic_type", loader)
        self.assertIn("if(internal)return", loader)
        self.assertIn('"hafiy.my"', loader)
        self.assertNotIn(
            '<script async src="https://www.googletagmanager.com/gtag/js',
            loader,
        )

    def test_built_pages_pass_dist_check(self):
        subprocess.run(["python3", "scripts/build.py"], cwd=ROOT, check=True)
        self.assertEqual(check_analytics_dist.main([]), 0)

    def test_dist_check_fails_on_duplicate_loader(self):
        subprocess.run(["python3", "scripts/build.py"], cwd=ROOT, check=True)
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            html = (ROOT / "index.html").read_text(encoding="utf-8")
            (dist / "index.html").write_text(html, encoding="utf-8")
            for rel in check_analytics_dist.GENERATED_PATHS[1:]:
                src = ROOT / rel
                dest = dist / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            doubled = dist / "index.html"
            doubled.write_text(doubled.read_text(encoding="utf-8") * 2, encoding="utf-8")
            self.assertEqual(check_analytics_dist.main(["--dist", str(dist)]), 1)


if __name__ == "__main__":
    unittest.main()
