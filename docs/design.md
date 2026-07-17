# Design guide

## Design intent

The site should feel like a precise, quiet professional notebook: minimal, readable, deliberate, and confident. It should not feel like a generic startup landing page or a dense resume template.

The current public design is closer to editorial documentation than marketing collateral.

## Visual language

- Monochrome palette with soft surfaces and subtle borders.
- System monospace typography for a technical, operational feel.
- Narrow content measure for readability.
- Generous vertical spacing.
- Dashed underlines and light hover movement as the main interaction language.
- Automatic dark mode through `prefers-color-scheme`, not a visible theme control.

## Layout system

- Shared page width is controlled by `--page` in `styles.css`.
- Horizontal padding is controlled by `--gutter`.
- The homepage hero uses a two-column layout on wider screens and stacks on small screens.
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

Current font stack:

```css
ui-monospace, "SFMono-Regular", "Cascadia Code", "Roboto Mono", Consolas, "Liberation Mono", Menlo, monospace
```

Guidance:

- Keep headings compact with slight negative letter spacing.
- Keep body text readable and calm; avoid very small paragraph text.
- Use uppercase micro-labels sparingly for dates and section context.
- Prefer short paragraphs and concrete verbs.

## Color and theming

The site defines light and dark variables in `:root` and a `prefers-color-scheme: dark` media query.

Use the existing tokens:

- `--background`
- `--surface`
- `--foreground`
- `--muted`
- `--border`
- `--accent`
- `--accent-soft`

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
