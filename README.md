# hafiy.my

Personal portfolio and writing site for Nazirul Hafiy, a Project & Operations Manager based in Kuching, Sarawak.

The site is intentionally small: hand-written HTML, one shared CSS file, no build step, no JavaScript on the current public pages, and deployment through GitHub Pages with the custom domain `hafiy.my`.

## What is in this repo

- `index.html` — homepage with hero, contact links, experience preview, writing preview, and experiments.
- `experience.html` — full professional experience timeline.
- `posts/` — writing index and individual static article pages.
- `styles.css` — shared responsive styling, light/dark color-scheme support, typography, layout, and accessibility states.
- `assets/profile.png` — square monochrome illustrated portrait used on the homepage.
- `sitemap.xml` and `robots.txt` — search-engine discovery files.
- `CNAME` — GitHub Pages custom-domain configuration for `hafiy.my`.
- `archive.html`, `alt/`, and `alt2/` — older or alternate design snapshots kept for reference, not the primary production route.
- `docs/` — product, design, and backlog context for future changes.

## Product direction

The site should make Hafiy’s professional positioning clear quickly:

- structured execution for complex, multi-stakeholder work;
- credibility in project delivery, operations, connectivity, and ICT environments;
- thoughtful writing about AI-native work and project execution;
- lightweight proof of public digital experiments.

Read [docs/product.md](docs/product.md) before making product or content changes.

## Design direction

The current public site uses a minimalist editorial system:

- monochrome, content-first presentation;
- narrow readable measure;
- system monospace typography;
- low-motion interactions;
- automatic light/dark styling through `prefers-color-scheme`.

Read [docs/design.md](docs/design.md) before making layout, visual, or interaction changes.

## Local development

Because the site uses root-relative URLs such as `/styles.css`, preview it through a local static server instead of opening files directly:

```sh
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

## Editing workflow

1. Keep pages static unless there is a strong reason to add tooling.
2. Update repeated navigation/footer patterns consistently across pages.
3. When adding or renaming public pages, update `sitemap.xml`.
4. When changing visible content, check metadata, canonical URLs, Open Graph data, and structured data where relevant.
5. Test narrow mobile widths, desktop widths, light mode, dark mode, and keyboard focus states.

## Deployment

The `main` branch is the GitHub Pages source for `nazirulhafiy.github.io`, served through the custom domain in `CNAME`.

There is no build command. A deploy is effectively a push of static files to GitHub.

## Documentation map

- [docs/product.md](docs/product.md) — audience, positioning, content model, and product principles.
- [docs/design.md](docs/design.md) — visual language, layout rules, components, accessibility, and content style.
- [docs/backlog.md](docs/backlog.md) — practical next tasks discovered from the current repo audit.
