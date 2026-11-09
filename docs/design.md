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
- Light-only presentation. The site does not follow `prefers-color-scheme: dark` and has no theme toggle.

## Interaction motion

Portfolio **hover / press** polish is CSS-only (no JavaScript). It is separate from the one-shot load entrance (see Hero / Contact below). Shared tokens in `styles.css`:

| Token | Value | Role |
| --- | --- | --- |
| `--ease-out` | `cubic-bezier(0.23, 1, 0.32, 1)` | Strong ease-out for UI feedback |
| `--duration-ui` | `160ms` | Color / border / background transitions |
| `--duration-press` | `140ms` | Transform / press feedback |
| `--ease-load` | `ease-out` | Evil Rabbit load easing (direct recipe) |
| `--duration-load` | `500ms` | Load entrance duration (Evil Rabbit direct) |
| `--load-rise` | `10px` | Load entrance `translateY` distance |

Rules:

- Transition only the properties that change (never `transition: all`).
- Hover **transforms** (lift / nudge) are gated behind `@media (hover: hover) and (pointer: fine)` so touch devices do not stick mid-lift. Color and underline hover can stay outside that query.
- Pressable bars and similar links (`.contact-bar`, `.inline-links a`, `.section-index-link`, `.project`, writing title links) use `:active { transform: scale(0.97) }` with the press duration.
- Under `prefers-reduced-motion: reduce`, drop interaction transforms (hover lift, press scale, focus nudge) while keeping near-instant color/underline changes via the global short `transition-duration`. The same reduce block also disables load entrances.

## Layout system

- Shared page width is controlled by `--page` in `styles.css`.
- Horizontal padding is controlled by `--gutter`.
- The homepage hero uses a two-column layout on wider screens and stacks on small screens. The homepage has no site header.
- Experience, writing, and article pages share a header: site name plus a primary nav (Experience, Writing, Experiments). At `38rem` and below the nav becomes a CSS checkbox menu. There is no menu script.
- The custom GitHub Pages 404 page (`404.html`) uses that same header and footer, with absolute `/…` asset and nav paths so styles and links still resolve when Pages serves the file under a nested missing URL.
- The contact microsite (`/contact/`) has no site header. It uses a centred portrait, one bio paragraph, stacked rounded-rectangular bars (left square thumbnail + centred title), and a Projects list of public experiment domains. It borrows link-hub bar geometry, not third-party branding, and does not change homepage or shared nav on other pages.
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

The site is light-only. `:root` sets `color-scheme: light` and the approved light tokens. There is no `prefers-color-scheme: dark` override in `styles.css`. Public pages declare a single `theme-color` of `#ffffff` (no dark media alternate).

Portfolio tokens in `styles.css`:

| Token | Value |
| --- | --- |
| `--background` | `#ffffff` |
| `--surface` | `#f6f6f6` |
| `--foreground` | `#111111` |
| `--muted` | `#5f5f5f` |
| `--border` | `#dedede` |
| `--accent` | `#111111` |
| `--accent-soft` | `#f1f1f1` |

Do not hard-code one-off colors unless there is a strong reason. New UI should stay within these light tokens.

## Components

### Hero

The hero should remain concise:

- square monochrome portrait;
- greeting (`about_lead` in `data/site.json`);
- one professional pitch (`tagline` in `data/site.json`);
- icon contact links.

**Load entrance (homepage + contact).** Direct copy of evilrabbit.com’s CSS band recipe (user-directed; iterate later if it does not fit). Shared `@keyframes load-enter`: opacity `0` → `1` with `translateY(10px)` → `0`, duration **500ms**, easing **`ease-out`**, fill `forwards`, base `opacity: 0` on each band. No blur, no scale. Homepage: `.hero` at 0 delay, then `main > .section` at **100 / 200 / 300ms** (experience → writing → experiments). Contact: `.contact-intro` at 0, `.contact-section` at 100ms, `.contact-projects` at 200ms. Do not animate nav, footer, experience/writing inner pages, or individual contact bars. Under `prefers-reduced-motion: reduce`, all load entrances are disabled (opacity 1, no transform) — hafiy requirement even though Evil Rabbit does not gate its fade. CSS-only — no portfolio-page JavaScript.

Homepage `<title>`, meta description, Open Graph / Twitter tags, and footer brand text are filled by `scripts/build.py` from the same file. Do not hand-type those strings in templates, scripts, or docs; `tests/test_site_copy.py` fails CI if they appear elsewhere.

### Favicon (site tab / touch icon)

Browser and touch icons use the approved original-photo PFP crop (full composition and background retained — not a silhouette redraw). Canonical files under `assets/`:

| Path | Role |
| --- | --- |
| `favicon.ico` | Multi-size ICO (16 / 32 / 48); each frame is the matching PNG embedded byte-for-byte |
| `favicon-16.png` | 16×16 PNG |
| `favicon.png` / `favicon-32.png` | 32×32 PNG (identical bytes; HTML declares `favicon.png`) |
| `favicon-48.png` | 48×48 PNG |
| `apple-touch-icon.png` / `favicon-180.png` | 180×180 PNG (identical bytes; HTML declares `apple-touch-icon.png`) |

Public pages declare those links with cache-bust `?v=3`. Do not substitute silhouette marks for the site favicon. `assets/profile.png` is the page portrait / social image and is separate from the favicon set (do not overwrite it when refreshing icons). `tests/test_favicon.py` asserts the approved SHA-256 hashes, ICO↔PNG frame parity, and link presence on templates and built pages.

### Social sharing (identity pages)

Portfolio identity pages (`/`, `/contact/`, `/experience.html`, `/posts/`) share one Open Graph / Twitter card contract from `scripts/build.py` tokens (`@@SITE_SOCIAL_IMAGE@@`, `@@SITE_TWITTER_CARD@@`, plus title / tagline from `data/site.json`):

- `og:title` / `twitter:title`: `title` from `data/site.json`
- `og:description` / `twitter:description`: `tagline` from `data/site.json`
- image: `assets/profile.png?v=2` (absolute `https://hafiy.my/assets/profile.png?v=2`, 1024×1024 PNG), alt `Portrait of {title}`
- `twitter:card`: `summary` (square portrait; not `summary_large_image`)

Contact also uses the site title for the browser `<title>` and the tagline for meta description. Homepage keeps `home_document_title` / long meta description for the document head while social tags follow the shared contract. Experience and writing index keep page-specific browser titles and search meta descriptions. Individual article pages keep article-specific `og:title` / `og:description` and do not use this identity card.

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

### Contact microsite

`/contact/` is a mobile-first link hub rendered from `site/templates/contact/index.html`:

- no top navbar on this page only;
- centred existing portrait (`assets/profile.png`), site title, and the site tagline from `data/site.json` as the single line under the name (`.contact-bio`, same fluid one-line treatment as homepage `.hero-copy`: `container-type` on `.contact-intro`, `font-size: min(0.82rem, 3.2cqi)`, `white-space: nowrap`, `data-one-line`);
- section headings are title-case **Contact** and **Projects**;
- every action uses a `.contact-bar`: rounded rectangle (not a pill), left equal square thumbnail, title centred in the row, no kebab menus;
- contact order: WhatsApp (`https://wa.me/nazirulhafiy` username link), Call (`tel:+60135623005`, same number as vCard `TEL`), Email, LinkedIn — local monochrome PNGs under `assets/contact/` with matched optical size (Call uses the classic handset mark at `assets/contact/phone.png`; same `#111` light treatment as the other bars). No Portfolio bar on this page;
- Projects bars only: `pcds2030.com`, `sde2030.com`, `ai.sarawak.news` using monochrome local marks derived from each site’s currently declared production-browser favicon (`favicon-production-browser.png`; no coloured logos on the page). Shared solid-S silhouettes after mono are acceptable when that is what the live marks are;
- phone number is reachable via the Call `tel:` bar; WhatsApp uses the `@nazirulhafiy` username landing (`wa.me/nazirulhafiy`); `contact/nazirul-hafiy.vcf` remains published for direct URL use but is not linked from the contact bars;
- keep hafiy.my monospace/monochrome light tokens; do not copy third-party branding or invent logos.
- social sharing follows the shared identity-page card (site title + tagline + `assets/profile.png?v=2`, `twitter:card=summary`); see Social sharing above.

## Navigation

Experience and writing pages use the shared header in `styles.css`:

- wide screens show the links in a row;
- narrow screens (`max-width: 38rem`) show a menu button. Checking `#nav-toggle` opens the nav and a backdrop. Both are `<label>` elements, so the menu works without JavaScript;
- the current page sets `aria-current="page"`.

The homepage does not include this header. The contact page omits the header entirely so the hub stays scan-first. The 404 page includes the shared header but does not mark any nav item as current.

### Custom 404 (`404.html`)

GitHub Pages serves root `404.html` for missing paths on this user site (status 404, URL unchanged). The page is built from `site/templates/404.html` like other portfolio HTML:

- short heading **Page not found** and one supporting line;
- a home link;
- `<meta name="robots" content="noindex">` (and no sitemap entry);
- the shared analytics loader only — no synthetic 404 events;
- absolute paths for CSS, favicons, and in-page links (`/styles.css…`, `/`, `/experience.html`, etc.).

Do not add `/sifir`, `/kracked`, `/sifir-sprint`, `/kracked-quest`, or `/cat-pinball-game` files here; those routes are owned by other repositories (see README).

## Accessibility

Preserve:

- skip links;
- semantic headings in order;
- descriptive `aria-label` values for icon-only links;
- visible `:focus-visible` outlines;
- readable color contrast on the light palette;
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

## Other paths on the host

`/cat-pinball-game/`, `/sifir-sprint/`, and `/kracked-quest/` are published from other repositories. They are not part of this design system. Where those games send visitors, and why, is in `README.md`.

## Analytics

Portfolio pages (home, experience, writing, contact, and the custom 404) get **one** build-time analytics loader from `data/analytics.json`.

**Registry.** `data/analytics.json` (kit shape `version: 1`) holds the shared `internal_cookie` (`sn_internal`), fleet `spa` (`false`), and the `hafiy.my` host entry: GA4 `G-JTQGL6WQYW`, Cloudflare Web Analytics token `57920823ff68472c8e325232c7b86127`, aliases `www.hafiy.my` and `nazirulhafiy.github.io`. `scripts/analytics_registry.py` validates the file.

**Single loader.** `scripts/analytics_loader.py` defines the production loader; `scripts/build.py` substitutes `@@ANALYTICS_LOADER@@` in `site/templates/` with one inline `<script data-sn-analytics-loader>` per page. GA4 and the CF beacon load only on registry hostnames (not `localhost` or arbitrary preview hosts).

**Internal traffic.** `?internal=1` sets `sn_internal=1` (~1 year, `Path=/`, `SameSite=Lax`, plus `Secure` on HTTPS). `?internal=0` clears it. While that cookie is set, GA4 config includes `traffic_type: 'internal'` and the Cloudflare beacon is not loaded. Agents and automation that open the live site should use `?internal=1` (see `AGENTS.md`).

**Enhanced measurement (do not double-count).** GA4 HTTPS outbound clicks already cover WhatsApp, LinkedIn, and project links on `/contact/`. Do not add custom events for those activations. Call (`tel:`) is also left uninstrumented — do not invent a custom Call event.

**Contact custom events (`/contact/` only).** Mailto is not covered by outbound enhanced measurement, so `/contact/` includes one tiny inline `<script data-sn-contact-events>` that listens for activation clicks on the Email bar only:

| Activation | Marker | GA4 event name | Parameters |
| --- | --- | --- | --- |
| Email (`mailto:`) | `data-sn-event="email_click"` | `email_click` | `surface: "contact"` |

These count activation clicks only (not completed mail sends). The listener never calls `preventDefault`, never waits on transport/beacons, and no-ops when `gtag` is missing or throws, so mailto keeps working when analytics is absent, blocked, or off-host (for example localhost). Event parameters must stay nonpersonal: no email, phone, or full contact URLs.

**CI.** After `scripts/build.py`, `scripts/check_analytics_dist.py` fails if any generated page has zero or multiple loaders, if GA4 / CF values drift from the registry, or if cookie / `spa` values drift. `tests/test_contact_events.py` asserts the contact-only event marker and that other built pages do not ship `data-sn-contact-events`. Runtime behaviour is covered by `npm run contact-events-check` (`scripts/contact-events-check.mjs`, Chromium, local static server + injected `gtag`/`dataLayer` stub — no production GA traffic): single emission of `email_click` with `{ surface: "contact" }`, one event per repeated activation (no double registration), unmarked HTTPS / `tel:` bars emit none of these custom events, absent / nonfunction / throwing `gtag` leaves click default actions unprevented (observed via a document bubble probe registered after the page script) and does not leak uncaught errors, emitted params contain no PII, and an isolated cancel-oracle harness proves that probe would catch an intentional `preventDefault`. See [ci-layout-check.md](ci-layout-check.md).

No Content-Security-Policy is set; if one is added, allow `www.googletagmanager.com`, `*.google-analytics.com` and `static.cloudflareinsights.com`.

## Layout check

Pull requests run a Playwright layout check on `/`, `/experience.html`, `/posts/`, and `/contact/` in Chromium and WebKit. See [ci-layout-check.md](ci-layout-check.md).

`[data-box]` marks layout regions the check watches for overlap and clipping (for example the homepage hero text column, section headings, and the experience header row). `[data-one-line]` marks copy that must stay on one line at the tested viewports — notably the homepage `.hero-copy` tagline, which broke in Safari when the role line wrapped after a font-size change ([PR #21](https://github.com/nazirulhafiy/nazirulhafiy.github.io/pull/21)), and the contact `.contact-bio` tagline (same site tagline under a narrower hub measure).

Markers live in `site/templates/`; run `python3 scripts/build.py` after editing them. CI-only Node dependencies are listed in `package.json` at the repo root; production Pages deploy remains static HTML and CSS with no runtime package manager.
