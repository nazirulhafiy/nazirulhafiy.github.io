#!/usr/bin/env python3
"""Single production analytics loader emitted at build time (GA4 + Cloudflare Web Analytics)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from analytics_registry import AnalyticsRegistry, load_analytics  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ANALYTICS_MAX_AGE = 31536000  # ~1 year
ANALYTICS_LOADER_ATTR = "data-sn-analytics-loader"


def analytics_registry() -> AnalyticsRegistry:
    return load_analytics()


def web_analytics_token(registry: AnalyticsRegistry | None = None) -> str:
    reg = registry if registry is not None else analytics_registry()
    env = os.environ.get("CLOUDFLARE_WEB_ANALYTICS_TOKEN", "").strip()
    return env or reg.primary_cf_token()


def render_analytics_loader(registry: AnalyticsRegistry | None = None) -> str:
    """Emit one production-only analytics loader from ``data/analytics.json``.

    - Host gate: primary host keys plus ``aliases``.
    - ``?internal=1`` sets the registry ``internal_cookie`` (~1 year);
      ``?internal=0`` clears the primary and every listed ``legacy_internal_cookies`` name.
    - While internal, GA4 sends ``traffic_type: 'internal'`` and the CF beacon is skipped.
    """
    reg = registry if registry is not None else analytics_registry()
    hosts_js = ",".join(json.dumps(h) for h in reg.hostnames)
    primary = json.dumps(reg.internal_cookie)
    honour = ",".join(json.dumps(c) for c in reg.honour_cookies)
    mid = json.dumps(reg.primary_ga4_id())
    token = json.dumps(web_analytics_token(reg))
    spa_js = "true" if reg.spa else "false"
    max_age = ANALYTICS_MAX_AGE
    return (
        f"<script {ANALYTICS_LOADER_ATTR}>(function(){{"
        f"var H=[{hosts_js}],h=location.hostname;"
        "if(H.indexOf(h)<0)return;"
        f"var C={primary},L=[{honour}],q=new URLSearchParams(location.search),"
        "sec=location.protocol==='https:'?';Secure':'';"
        "if(q.get('internal')==='1')"
        f"document.cookie=C+'=1;path=/;max-age={max_age};SameSite=Lax'+sec;"
        "else if(q.get('internal')==='0')"
        "L.forEach(function(n){document.cookie=n+'=;path=/;max-age=0;SameSite=Lax'+sec;});"
        "var internal=L.some(function(n){return document.cookie.split(';').some(function(p){"
        "return p.trim()===n+'=1';});});"
        "window.dataLayer=window.dataLayer||[];"
        "function gtag(){dataLayer.push(arguments);}"
        "window.gtag=gtag;"
        "gtag('js',new Date());"
        f"var id={mid},cfg={{}};"
        "if(internal)cfg.traffic_type='internal';"
        "gtag('config',id,cfg);"
        "var gs=document.createElement('script');gs.async=true;"
        "gs.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(id);"
        "document.head.appendChild(gs);"
        "if(internal)return;"
        "var s=document.createElement('script');s.defer=true;"
        "s.src='https://static.cloudflareinsights.com/beacon.min.js';"
        f"s.setAttribute('data-cf-beacon',JSON.stringify({{token:{token},spa:{spa_js}}}));"
        "document.head.appendChild(s);"
        "})();</script>"
    )
