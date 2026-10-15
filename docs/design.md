# Design guide

## Design intent

The site should feel like a precise, quiet professional notebook: minimal, readable, deliberate, and confident. It should not feel like a generic startup landing page or a dense resume template.

The current public design is closer to editorial documentation than marketing collateral.

## Visual language

- Monochrome palette with soft surfaces and subtle borders.
- System monospace typography for the interface. Article decks and article bodies use the system sans stack (`--sans`).
- Narrow content measure for readability.
- Generous vertical spacing.
- Dashed underlines and light hover movement as the main interaction language.
- Automatic dark mode through `prefers-color-scheme`, not a visible theme control.

## Layout system

- Shared page width is controlled by `--page` in `styles.css`.
- Horizontal padding is controlled by `--gutter`.
- The homepage hero uses a two-column layout on wider screens and stacks on small screens. The homepage has no site header.
- Experience, writing, and article pages share a header: site name plus a primary nav (Experience, Writing, Experiments). At `38rem` and below the nav becomes a CSS checkbox menu. There is no menu script.
- Secondary pages use a centered article-style column.
- Sections are separated by thin borders and clear headings.

When adding new sections, prefer the existing patterns:

- `.section`
- `.section-heading`
- `.writing-list`
- `.post`
- `.project`
- `.history-company`
- `.history-role`
- `.article-page`
- `.article-body`

## Typography

Interface font stack (`--mono`):

```css
ui-monospace, "SFMono-Regular", "Cascadia Code", "Roboto Mono", Consolas, "Liberation Mono", Menlo, monospace
```

Article text (`--sans`):

```css
-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
```

Guidance:

- Keep headings compact with slight negative letter spacing.
- Keep body text readable and calm; avoid very small paragraph text.
- Use uppercase micro-labels sparingly for dates and section context.
- Prefer short paragraphs and concrete verbs.

## Color and theming

The site defines light and dark variables in `:root` and a `prefers-color-scheme: dark` media query.

Portfolio tokens in `styles.css`:

| Token | Light | Dark |
| --- | --- | --- |
| `--background` | `#ffffff` | `#111111` |
| `--surface` | `#f6f6f6` | `#1b1b1b` |
| `--foreground` | `#111111` | `#f5f5f5` |
| `--muted` | `#5f5f5f` | `#b4b4b4` |
| `--border` | `#dedede` | `#2d2d2d` |
| `--accent` | `#111111` | `#f5f5f5` |
| `--accent-soft` | `#f1f1f1` | `#1a1a1a` |

Do not hard-code one-off colors unless there is a strong reason. New UI should remain legible in both light and dark mode.

## Components

### Hero

The hero should remain concise:

- square monochrome portrait;
- greeting;
- one professional pitch;
- icon contact links.

Avoid adding multiple CTAs, badges, or long summaries here.

### Experience preview

The homepage preview should summarize, not duplicate, the full experience page. Keep it focused on the strongest and most recent signals.

### Writing cards

Writing previews should include:

- title;
- date;
- reading time when available;
- one short summary.

### Project links

Experiment links should be simple block links with a title and one-sentence description. Do not add category, location, or other kicker labels above project titles.

## Navigation

Experience and writing pages use the shared header in `styles.css`:

- wide screens show the links in a row;
- narrow screens (`max-width: 38rem`) show a menu button. Checking `#nav-toggle` opens the nav and a backdrop. Both are `<label>` elements, so the menu works without JavaScript;
- the current page sets `aria-current="page"`.

The homepage does not include this header.

## `/normah/`

`/normah/` is a separate page with its own stylesheet and script. It is not part of the portfolio chrome.

- Wider page (`--page: 72rem`) and a green accent (`#0b5d38` light, `#82d0a2` dark). Surfaces lean slightly green rather than pure grey.
- Same mono interface stack. Sans is used inside cards and panels.
- Three carousels (corporate identity, email-signature campaigns, hyperlocal event promotion). `normah/script.js` wires previous/next, dots, arrow keys, and scroll sync. It respects `prefers-reduced-motion`.
- `noindex`. Not linked from the homepage.

## Accessibility

Preserve:

- skip links;
- semantic headings in order;
- descriptive `aria-label` values for icon-only links;
- visible `:focus-visible` outlines;
- readable color contrast in light and dark modes;
- `prefers-reduced-motion` handling.

Avoid interactions that require hover only, precise pointer use, or JavaScript to access important content.

## Content tone

The writing style should be:

- direct;
- grounded;
- practical;
- first-person where appropriate;
- specific about outcomes and constraints.

Avoid inflated claims, buzzword-heavy copy, and generic portfolio language.

## Historical variants

`archive.html`, `alt/`, and `alt2/` contain older or alternate visual directions. Use them as references only when explicitly exploring design alternatives. The current production direction is the minimalist shared-CSS version at `/`, `/experience.html`, and `/posts/`.

`/cat-pinball-game/`, `/sifir-sprint/`, and `/kracked-quest/` are published from other repositories. They are not part of this design system. Where those games send visitors, and why, is in `README.md`.

## Analytics

- Google Analytics 4: measurement ID `G-JTQGL6WQYW`, tag in `<head>` of every served HTML page (home, archive, experience, posts, alt, alt2, normah). Add it to any new page.
- Cloudflare Web Analytics: hafiy.my is on GitHub Pages (not proxied by Cloudflare), so each page loads the beacon manually with token `57920823ff68472c8e325232c7b86127` (Web Analytics site for hafiy.my).
- No Content-Security-Policy is set; if one is added, allow `www.googletagmanager.com`, `*.google-analytics.com` and `static.cloudflareinsights.com`.
