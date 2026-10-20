# AGENTS.md

Guidance for AI coding assistants and contributors working in this repository.

## Project snapshot

This is the source for `hafiy.my`, a static personal portfolio and writing site. Homepage title, tagline, meta description, and intro lead live only in `data/site.json`; `scripts/build.py` fills every wired surface from that file.

The production site is static HTML and CSS:

- no package manager;
- a small Python build (`scripts/build.py`) renders homepage, experience, and writing pages from `data/site.json` and `site/templates/`; run it after changing site-wide copy;
- no framework and no CSS library;
- no environment variables;
- no JavaScript on the portfolio pages (`/`, `/experience.html`, `/posts/`);
- `/normah/` is the exception: it loads `normah/script.js` for its carousels;
- hosted as the GitHub Pages user site `nazirulhafiy.github.io`, with the custom domain in `CNAME` (`hafiy.my`).

`/cat-pinball-game/` is published from [nazirulhafiy/cat-pinball-game](https://github.com/nazirulhafiy/cat-pinball-game), not from this repo. `/sifir-sprint/` and `/kracked-quest/` are published from their own repos and client-redirect to `https://polah.app/sifir/` and `https://polah.app/kracked/`. The short paths `/sifir` and `/kracked` are not files here. See `README.md`.

## Read first

Before making meaningful changes, read:

1. `README.md`
2. `docs/product.md`
3. `docs/design.md`
4. `docs/backlog.md`

These files define the product intent, design direction, and known maintenance priorities.

## Working rules

- Keep the site static by default. Do not introduce a framework, bundler, package manager, or CMS unless explicitly requested.
- Preserve the minimalist, content-first identity. Avoid decorative UI, heavy animation, or feature creep.
- Prefer small, targeted changes over broad rewrites.
- Keep the portfolio pages usable without JavaScript. Add JavaScript only when a page cannot work without it, as `/normah/` does for its carousels.
- Keep routes and links root-relative where the current site already uses that style.
- Treat `archive.html`, `alt/`, and `alt2/` as historical/reference variants unless the task explicitly targets them.
- Do not remove older variants or verification files unless asked.
- Preserve the custom domain setup in `CNAME`.
- Do not add `/sifir`, `/kracked`, or `/cat-pinball-game` to this repo. They are published from other repositories.
- Design or behaviour changes (CSS, templates, app JS, build scripts, config) must update docs/ (usually docs/design.md) in the same PR. Use the `no-docs-needed` label only for changes that truly need no docs.

The docs-check workflow enforces that rule for CSS, JS, templates, build scripts, and analytics registry paths. Details and the watched patterns are in `docs/ci-docs-check.md`.

## Analytics (internal traffic)

When agents, QA, or cloud agents open the **live** portfolio site ([https://hafiy.my/](https://hafiy.my/)), append `?internal=1` (for example `https://hafiy.my/?internal=1` or `https://hafiy.my/experience.html?internal=1`). That sets the registry cookie from `data/analytics.json` (`sn_internal`, ~1 year) so GA4 receives `traffic_type: 'internal'` and the Cloudflare Web Analytics beacon is **not** loaded. Use `?internal=0` to clear the cookie. Both trackers load only on `hafiy.my`, `www.hafiy.my`, and `nazirulhafiy.github.io`. Details: [docs/design.md](docs/design.md) (Analytics).

## Content rules

- Maintain the positioning around project delivery, operations, ICT/connectivity work, AI-native practice, and Sarawak-related public digital experiments.
- Keep claims specific and defensible. Be careful with metrics such as `87,000+ users`, `10,000+ new accounts per day`, `20% backlog reduction`, and `eight figures in MYR`.
- If changing professional experience copy, keep dates and role hierarchy consistent between `index.html` and `experience.html`.
- If adding writing, update both `posts/index.html` and the homepage writing preview when appropriate.
- Keep `/normah/` unlisted: `noindex`, not in the homepage nav, and not in `sitemap.xml`, unless a task says otherwise.

## Design rules

- Use `styles.css` for shared portfolio styling. `/normah/` uses `normah/styles.css` and does not share the portfolio stylesheet.
- Respect the existing design system: narrow readable width, monochrome palette, system monospace font stack for the interface, system sans for article text, subtle borders, dashed underlines, and automatic light/dark colors.
- Keep responsive behavior simple and test small screens.
- Preserve keyboard focus styles, skip links, semantic headings, and descriptive link labels.
- The inner-page menu is a checkbox in the HTML, styled in CSS. Do not replace it with JavaScript.

## SEO and publishing rules

- Public pages should have a useful `<title>`, meta description, canonical URL, and relevant social metadata.
- Articles should include article metadata and JSON-LD when following the existing article pattern.
- Update `sitemap.xml` when adding, removing, or materially changing public URLs.
- Keep `robots.txt` pointing to the canonical sitemap.
- If changing CSS and relying on GitHub Pages/browser cache refresh, update the cache-busting query string in page links consistently.

## Verification checklist

After changes, verify as relevant:

- `git diff --check`
- local preview with `python3 -m http.server 8000`
- homepage loads at `/`
- `/experience.html` loads
- `/posts/` and article pages load
- no broken internal links
- mobile layout remains readable
- dark mode remains legible
- keyboard focus remains visible
