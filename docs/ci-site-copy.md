# CI: site copy

Pull requests and pushes to `main` run the **site-copy** job in [`.github/workflows/site-copy.yml`](../.github/workflows/site-copy.yml).

## What it enforces

1. `python3 scripts/build.py` must reproduce the committed homepage, experience page, and writing pages from `site/templates/` and `data/site.json`.
2. [`tests/test_site_copy.py`](../tests/test_site_copy.py) must pass: canonical site copy must not appear hand-typed outside `data/site.json`.

## Canonical fields

`data/site.json` owns:

- `title` — brand name in headers, footers, Open Graph / Twitter titles, and JSON-LD `name`
- `home_document_title` — homepage `<title>`
- `tagline` — hero pitch and social descriptions on the homepage
- `description` — homepage meta description
- `about_lead` — homepage hero greeting (`<h1>`)

## Generated HTML

The job treats root `index.html`, `experience.html`, and `posts/*.html` as build output (like `dist/` in sister repos). Templates under `site/templates/` use `@@…@@` tokens; the build substitutes escaped values.

Historical paths (`archive.html`, `alt/`, `alt2/`) and `/normah/` are out of scope for the copy scan.
