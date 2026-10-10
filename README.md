# hafiy.my

Personal portfolio and writing site for Nazirul Hafiy, a Project & Operations Manager based in Kuching, Sarawak.

Live site: [https://hafiy.my](https://hafiy.my)

The site is hand-written HTML and CSS. There is no package manager, no framework, no CSS library, no build step, and no environment variables. GitHub Pages publishes the `main` branch of the user site `nazirulhafiy.github.io` (legacy Pages, source `/`) and serves it on the custom domain in `CNAME`.

## What is in this repo

- `index.html` — homepage with hero, contact links, experience preview, writing preview, and experiments. The homepage has no site header.
- `experience.html` — full professional experience timeline.
- `posts/` — writing index and individual static article pages.
- `styles.css` — shared styling for the portfolio pages.
- `normah/` — unlisted, `noindex` microsite. See below.
- `assets/profile.png` — square monochrome illustrated portrait used on the homepage.
- `sitemap.xml` and `robots.txt` — search-engine discovery files. `/normah/` is omitted.
- `CNAME` — GitHub Pages custom domain `hafiy.my`.
- `archive.html`, `alt/`, and `alt2/` — older or alternate design snapshots kept for reference, not the primary production route.
- `docs/` — product, design, backlog, and CI notes.

The portfolio pages (`/`, `/experience.html`, `/posts/`) do not use JavaScript. `/normah/` loads `normah/script.js` for its carousels.

## `/normah/`

[https://hafiy.my/normah/](https://hafiy.my/normah/) is a marketing-suggestions page for Normah Medical Specialist Centre, dated 28 August 2026. It covers corporate identity, email-signature campaigns, and hyperlocal event promotion.

It lives in this repo (`normah/index.html`, `normah/styles.css`, `normah/script.js`). It uses its own stylesheet (green accent, wider page) and a small carousel script. It is not linked from the homepage, sends `noindex, nofollow, noarchive`, and is not in `sitemap.xml`.

## Paths published from other repositories

GitHub Pages also serves other repositories as project sites on this same host. Those URLs are not files in this repo. Leave them in their own repositories.

### `/cat-pinball-game/`

Published from [nazirulhafiy/cat-pinball-game](https://github.com/nazirulhafiy/cat-pinball-game). The public play URL for that game is [https://polah.app/balls/](https://polah.app/balls/). This repo does not build or deploy it.

### `/sifir` and `/kracked`

The public games are [https://polah.app/sifir/](https://polah.app/sifir/) (Sifir Sprint) and [https://polah.app/kracked/](https://polah.app/kracked/) (Kracked Quest). Old links on `hafiy.my` and `nazirulhafiy.github.io` are meant to send people there, because those games moved to polah.app and the short path is the public URL.

The redirect is a client script in the other repos' published HTML, not a page in this repo:

- [nazirulhafiy/sifir-sprint](https://github.com/nazirulhafiy/sifir-sprint) is published at `/sifir-sprint/`. On `hafiy.my` or `nazirulhafiy.github.io`, the script rewrites `/sifir-sprint` to `/sifir`, then replaces the location with `https://polah.app` plus that path, query, and hash. Cloudflare on polah.app proxies `/sifir` back to the Pages origin `/sifir-sprint`.
- [nazirulhafiy/kracked-quest](https://github.com/nazirulhafiy/kracked-quest) is published at `/kracked-quest/` and does the same rewrite from `/kracked-quest` to `/kracked`, then to `https://polah.app/kracked/`.

`/sifir` and `/kracked` are not files in this repository, so this site does not answer those short paths. The redirect runs when the project-site page loads (`/sifir-sprint/`, `/kracked-quest/`), which is the HTML that contains the script.

## Product direction

The site should make Hafiy’s professional positioning clear quickly:

- structured execution for complex, multi-stakeholder work;
- credibility in project delivery, operations, connectivity, and ICT environments;
- thoughtful writing about AI-native work and project execution;
- lightweight proof of public digital experiments.

Read [docs/product.md](docs/product.md) before making product or content changes.

## Design direction

The current public portfolio uses a minimalist editorial system:

- monochrome, content-first presentation;
- narrow readable measure;
- system monospace for the interface, system sans for article text;
- low-motion interactions;
- automatic light/dark styling through `prefers-color-scheme`.

`/normah/` keeps the same typography habits and uses a green accent of its own. Read [docs/design.md](docs/design.md) before making layout, visual, or interaction changes.

## Local development

Because the site uses root-relative URLs such as `/styles.css`, preview it through a local static server instead of opening files directly:

```sh
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

## Build

There is no build step. Edit the HTML and CSS, then refresh the local server.

## Environment variables

None.

## Editing workflow

1. Keep pages static unless there is a strong reason to add tooling.
2. Update repeated navigation/footer patterns consistently across pages.
3. When adding or renaming public pages, update `sitemap.xml`.
4. When changing visible content, check metadata, canonical URLs, Open Graph data, and structured data where relevant.
5. Test narrow mobile widths, desktop widths, light mode, dark mode, and keyboard focus states.
6. Design or behaviour changes on watched CSS and JS files must update `docs/` in the same pull request. See [docs/ci-docs-check.md](docs/ci-docs-check.md).

## Deployment

GitHub Pages (legacy) publishes the `main` branch from `/`. The live hostname is `hafiy.my`, from `CNAME`, with HTTPS enforced. There is no deploy workflow in this repo. A deploy is a push of static files to `main`. DNS for the domain is outside this repository.

## Documentation map

- [docs/product.md](docs/product.md) — audience, positioning, content model, and product principles.
- [docs/design.md](docs/design.md) — visual language, layout rules, components, accessibility, and content style.
- [docs/backlog.md](docs/backlog.md) — practical next tasks discovered from the current repo audit.
- [docs/ci-docs-check.md](docs/ci-docs-check.md) — docs-check workflow, watched paths, and the `no-docs-needed` label.
