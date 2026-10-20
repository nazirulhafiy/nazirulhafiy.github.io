# CI: layout check

Pull requests run the **layout-check** job in [`.github/workflows/layout-check.yml`](../.github/workflows/layout-check.yml).

## What it does

The job serves the static site from the repository root, then runs `npm run layout-check` (`scripts/layout-check.mjs`) in **Chromium** and **WebKit** (in parallel). It does not deploy GitHub Pages.

Pages checked:

- `/` (home)
- `/experience.html`
- `/posts/`

Viewports: 375×667, 390×844, 390×680, and 1280×800. Each combination is tested in **light** and **dark** (`prefers-color-scheme`).

## Failure conditions

The script fails when any checked page has:

- horizontal document overflow;
- overlapping `[data-box]` border boxes (nested boxes are ignored);
- a clipped `[data-box]` (scroll size exceeds the client box on a clipping overflow axis, or a clipping ancestor cuts the border box);
- a `[data-one-line]` element that wraps onto more than one line;
- no `[data-box]` markers on the page.

Markers live in `site/templates/` for the homepage, experience page, and writing index. Run `python3 scripts/build.py` after changing templates.

## Local run

```bash
npm ci
npx playwright install chromium webkit
npm run layout-check
```

Optional environment variables:

- `LAYOUT_CHECK_URL` — use an already-running server instead of starting `python3 -m http.server`
- `LAYOUT_CHECK_PORT` — port for the local server (default `8765`)
- `LAYOUT_CHECK_BROWSERS` — comma-separated list (`chromium`, `webkit`)
- `LAYOUT_CHECK_LABEL` — label printed in the report (for proof runs)

## Runtime

The job is sized to finish in about two minutes on `ubuntu-latest`. Browser installs dominate wall time; the check step itself is usually under half a minute.
