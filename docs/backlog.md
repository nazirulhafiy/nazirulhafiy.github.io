# Backlog

Practical next tasks from the current repo audit. Keep this list grounded in maintenance, clarity, and small product improvements.

## Must fix before larger content expansion

- [ ] Remove stale README assumptions from future edits. The old README mentioned an `about.html` page that no longer exists; this has been corrected, but future documentation should keep matching the actual route map.
- [ ] Decide whether `archive.html`, `alt/`, and `alt2/` should stay publicly reachable. If they remain, document their purpose clearly; if not, decide whether to move them out of public serving without losing the reference snapshots.
- [ ] Standardize metadata theme colors. The homepage uses `#f7f5f0` / `#1f2428`, while inner pages use `#ffffff` / `#111111`; choose whether this difference is intentional.

## Should improve soon

- [ ] Add a lightweight internal-link check to the verification workflow. A small script or manual checklist is enough; avoid adding a heavy toolchain just for this.
- [ ] Review all public pages for repeated header/footer markup and define a safe manual update pattern in the README if the site stays framework-free.
- [ ] Refresh `sitemap.xml` `lastmod` values whenever public pages materially change.
- [ ] Consider adding Open Graph image support if sharing previews become important. Keep it optional unless there is a clear social-sharing need.
- [ ] Review article reading times after any substantial article edits.

## Content opportunities

- [ ] Add one stronger professional case-study-style page only if there is polished content with clear constraints, actions, and outcomes.
- [ ] Add a short note explaining the PCDS 2030 Project Tracker as a public experiment if it helps connect the experiment to Hafiy’s professional story.
- [ ] Consider one article about applying AI-native workflows to project operations, risk registers, or stakeholder reporting.
- [ ] Keep homepage writing previews current when new articles are published.

## Design polish

- [ ] Test the portrait crop across common mobile widths and high-density displays.
- [ ] Review whether the homepage hero greeting should allow wrapping on very narrow-but-not-stacked widths.
- [ ] Confirm dark-mode contrast for muted text, borders, and icon links on real devices.
- [ ] Keep animation subtle; current hover movement is enough unless a specific usability issue appears.

## Technical cleanup

- [ ] Remove `.DS_Store` from the repository if it is tracked; otherwise ensure `.gitignore` prevents it from being added.
- [ ] If CSS changes, update the `styles.css?v=17` cache-busting query consistently across public pages.
- [ ] Consider centralizing repeated SVG icons only if duplication becomes painful; avoid adding build tooling solely for this.
- [ ] Keep `robots.txt`, `CNAME`, Google verification file, and sitemap intact during cleanup.

## Done

- [x] Created project documentation structure: `AGENTS.md`, `README.md`, `docs/product.md`, `docs/design.md`, and `docs/backlog.md`.
