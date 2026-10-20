# CI: docs check

Pull requests run the **docs-check** job in [`.github/workflows/docs-check.yml`](../.github/workflows/docs-check.yml) on `opened`, `synchronize`, `reopened`, `labeled`, and `unlabeled`.

## What it enforces

If a pull request changes a watched design or behaviour file, it must also change at least one file under `docs/`.

The check uses a three-dot diff (`base.sha...head.sha`). The workflow checks out the full history so both commits are available.

## Watched patterns

Kept in sync at the top of the workflow and in [`scripts/docs_check_pr.py`](../scripts/docs_check_pr.py):

- `*.css` in any directory (`styles.css` and any later stylesheet)
- `*.js` in any directory (any script added under the repo root)

## Not watched

Portfolio page bodies, article copy, images, `sitemap.xml`, `robots.txt`, and `CNAME` are content or publishing files, so the check leaves them alone. Site-wide title, tagline, description, and intro lead are not watched here; see [ci-site-copy.md](ci-site-copy.md).

These paths are watched in addition to `*.css` and `*.js` (see `scripts/docs_check_pr.py`):

- `site/templates/*`
- `scripts/build.py`, `scripts/analytics_registry.py`, `scripts/analytics_loader.py`, `scripts/check_analytics_dist.py`, `scripts/docs_check_pr.py`
- `.github/workflows/*`
- `data/site.json`, `data/analytics.json`

## Escape hatch

Add the **`no-docs-needed`** label when a pull request touches watched files and truly needs no `docs/` update. The workflow creates the label if it is missing.

Use the label only for that case. A real layout, colour, type, or interaction change still needs `docs/design.md` (or another file under `docs/`) in the same PR.

## Failure message

When the check fails, CI prints:

> This PR changes how the site looks or behaves but doesn't update docs/. Update docs/design.md, or add the no-docs-needed label if no doc change is needed.
