# AGENTS.md

Guidance for AI coding assistants and contributors working in this repository.

## Project snapshot

This is the source for `hafiy.my`, a static personal portfolio and writing site for Nazirul Hafiy.

The production site is hand-authored HTML and CSS:

- no package manager;
- no build step;
- no framework;
- no production JavaScript on current public pages;
- hosted with GitHub Pages and the custom domain in `CNAME`.

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
- Keep current public pages accessible without JavaScript.
- Keep routes and links root-relative where the current site already uses that style.
- Treat `archive.html`, `alt/`, and `alt2/` as historical/reference variants unless the task explicitly targets them.
- Do not remove older variants or verification files unless asked.
- Preserve the custom domain setup in `CNAME`.

## Content rules

- Maintain the positioning around project delivery, operations, ICT/connectivity work, AI-native practice, and Sarawak-related public digital experiments.
- Keep claims specific and defensible. Be careful with metrics such as `87,000+ users`, `10,000+ new accounts per day`, `20% backlog reduction`, and `eight figures in MYR`.
- If changing professional experience copy, keep dates and role hierarchy consistent between `index.html` and `experience.html`.
- If adding writing, update both `posts/index.html` and the homepage writing preview when appropriate.

## Design rules

- Use `styles.css` for shared styling.
- Respect the existing design system: narrow readable width, monochrome palette, system monospace font stack, subtle borders, dashed underlines, and automatic light/dark colors.
- Keep responsive behavior simple and test small screens.
- Preserve keyboard focus styles, skip links, semantic headings, and descriptive link labels.

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
