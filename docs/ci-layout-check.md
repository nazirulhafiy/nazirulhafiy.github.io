# CI: layout check

Pull requests run the **layout-check** job in [`.github/workflows/layout-check.yml`](../.github/workflows/layout-check.yml).

## What it does

The job serves the static site from the repository root, then runs `npm run layout-check` (`scripts/layout-check.mjs`) in **Chromium** and **WebKit** (in parallel). It does not deploy GitHub Pages.

Pages checked:

- `/` (home)
- `/experience.html`
- `/posts/`
- `/contact/`

Viewports: 375×667, 390×844, 390×680, and 1280×800. Each combination is tested in **light** and **dark** (`prefers-color-scheme`).

## Failure conditions

The script fails when any checked page has:

- horizontal document overflow;
- overlapping `[data-box]` border boxes (nested boxes are ignored);
- a clipped `[data-box]` (scroll size exceeds the client box on a clipping overflow axis, or a clipping ancestor cuts the border box);
- a `[data-one-line]` element that wraps onto more than one line;
- no `[data-box]` markers on the page.

Markers live in `site/templates/` for the homepage, experience page, writing index, and contact hub. Run `python3 scripts/build.py` after changing templates.

## Local run

```bash
npm ci
npx playwright install chromium webkit
npm run layout-check
npm run contact-events-check
```

Optional environment variables:

- `LAYOUT_CHECK_URL` — use an already-running server instead of starting `python3 -m http.server`
- `LAYOUT_CHECK_PORT` — port for the local server (default `8765`)
- `LAYOUT_CHECK_BROWSERS` — comma-separated list (`chromium`, `webkit`)
- `LAYOUT_CHECK_LABEL` — label printed in the report (for proof runs)
- `CONTACT_EVENTS_CHECK_PORT` — port for the contact-events runtime check server (default `8766`)

## Contact events runtime check

The same workflow also runs `npm run contact-events-check` after the layout pass. That script opens `/contact/` in Chromium against a local static server and injects a `gtag`/`dataLayer` stub (it does not load `googletagmanager.com` or send production hits). It asserts:

- one `email_click` with `{ surface: "contact" }` per successful activation;
- repeated activations emit one event each (no double-registered listeners);
- WhatsApp, Call (`tel:`), LinkedIn, and project HTTPS bars do not emit those custom events;
- absent, non-function, and throwing `gtag` leave mailto default actions unprevented and do not surface uncaught page errors;
- emitted event params contain no PII (email, phone, contact URLs, vCard payload).

Default-action preservation is checked by reading `event.defaultPrevented` on a **document** bubble-phase probe registered after the page script (the implementation is also a document bubble listener; an anchor-target probe would run too early). The probe calls `preventDefault` only after that observation so the test stays inside Chromium. An isolated harness injects a temporary canceling document listener (not committed product code) and asserts the probe sees `defaultPrevented === true`, proving the oracle would catch a regression that cancelled the default.

## Runtime

The job is sized to finish in about two minutes on `ubuntu-latest`. Browser installs dominate wall time; the check step itself is usually under half a minute.
