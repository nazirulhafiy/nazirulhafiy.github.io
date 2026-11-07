# CI: site copy

Pull requests and pushes to `main` run the **site-copy** job in [`.github/workflows/site-copy.yml`](../.github/workflows/site-copy.yml).

## What it enforces

1. `python3 scripts/build.py` must reproduce the committed homepage, experience page, contact hub, and writing pages from `site/templates/` and `data/site.json`.
2. [`tests/test_site_copy.py`](../tests/test_site_copy.py) must pass: canonical site copy must not appear hand-typed outside `data/site.json`.
3. `python3 scripts/check_analytics_dist.py` must pass on the built portfolio HTML (exactly one `data-sn-analytics-loader` per page; IDs and cookie name match `data/analytics.json`).
4. [`tests/test_analytics_registry.py`](../tests/test_analytics_registry.py) must pass.
5. [`tests/test_contact_events.py`](../tests/test_contact_events.py) and [`tests/test_contact_vcard.py`](../tests/test_contact_vcard.py) must pass (contact markers / script contract and vCard fields). Runtime click behaviour for the contact custom events lives in the layout-check job (`npm run contact-events-check`); see [ci-layout-check.md](ci-layout-check.md).
6. [`tests/test_favicon.py`](../tests/test_favicon.py) must pass: approved original-PFP favicon SHA-256 hashes, ICO↔PNG frame parity, and icon / apple-touch link presence on templates and built pages.

## Canonical fields

`data/site.json` owns:

- `title` — brand name in headers, footers, Open Graph / Twitter titles, and JSON-LD `name`
- `home_document_title` — homepage `<title>`
- `tagline` — hero pitch and social descriptions on the homepage
- `description` — homepage meta description
- `about_lead` — homepage hero greeting (`<h1>`)

## Generated HTML

The job treats root `index.html`, `experience.html`, and `posts/*.html` as build output (like `dist/` in sister repos). Templates under `site/templates/` use `@@…@@` tokens; the build substitutes escaped values.

Only portfolio templates, `data/site.json`, and other scanned text files are in scope; paths published from other repositories are not part of this repo.
