# Changelog

All notable changes to DevDeck are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] — 2026-09-27

A UI correctness and visual-design release. The previous stylesheet was
partially invalid, which left large parts of the interface unstyled and made
dark mode non-functional; this release rebuilds the theme system and corrects
several behavioural bugs found while testing it.

### Fixed

- **Stylesheet parsing failures.** The theme contained malformed declarations
  (missing semicolons) and unterminated rule blocks. Qt drops the remainder of
  a rule on the first bad declaration, so many widgets rendered unstyled.
- **Dark mode was effectively broken.** It relied on `[theme="dark"]` property
  selectors layered over the broken rules, and produced a near-identical
  result to light mode. The two themes are now distinct, complete stylesheets.
- **Theme choice was not persisted.** `ConfigManager` force-overwrote the
  stored theme to dark on every launch, so the setting could never stick.
- **ANSI colour was silently discarded in the console.** `ansi_to_html` built
  the `style` attribute without quotes, producing invalid HTML that Qt ignored.
  Spans left open at a chunk boundary also leaked a stray `</span>`.
- **The "Individual Projects" section header disappeared** whenever projects
  were viewed on their own. The two section headers are now independent.
- **The sidebar "Favorites" count was always zero** for stacks.
- **Projects were double-counted** in the total and port statistics when the
  same project also appeared inside a stack.
- **Stat colours ignored the active theme**, using hard-coded light-mode hex
  values and leaving the "active" number unreadable on the dark background.
- **Disabled Start/Stop buttons still rendered in full colour**, because
  `objectName` rules outrank the generic `:disabled` rule. The muted state is
  now restated per button.
- **Cards were clipped at narrow widths.** The two-column grid imposed a hard
  ~694px minimum, wider than the viewport, forcing the container wider and
  cutting off cards. The grid now drops to one column and re-flows on resize.
- **Full-screen console button rendered as a tofu box**, because the geometric
  arrow glyph is absent from common Linux UI fonts.

### Added

- **Light theme.** Previously light was nominally available but unusable; it is
  now a complete, first-class theme. The selection persists across launches.
- **`Ctrl + N`** to add a project, **`Esc`** to clear search.
- **Clear buttons** on both the project and console search fields.
- **Responsive layout.** Service rows drop their command snippet and secondary
  shortcuts when narrow; the project grid re-flows between one and two columns.
- **Informed port termination.** Killing a port now shows the process name,
  PID, and working directory before acting, and defaults to *No*.
- **Stack status accuracy.** Each stack reports how many of its services are
  genuinely running, and the whole card is visually marked when fully up.
- **`version.py`** as the single source of truth for the version string,
  previously hardcoded inside a widget and unreadable by build scripts.

### Changed

- **Design tokens.** `theme.py` now generates both stylesheets from token
  dictionaries, so light and dark cannot drift apart. Adjust the palette in
  one place.
- **Density pass.** Borders removed from service rows, icon boxes, badges, and
  nested surfaces; spacing and background tint now do the separating, so cards
  stand out instead of everything competing equally.
- **Monochrome icon set** (`ui/icons.py`) replacing mixed emoji and symbols,
  which rendered inconsistently across platforms. Port labels are now plain
  monospace numbers rather than an unrelated pictogram.
- **Accessibility.** All fifteen text/background pairs in both themes now meet
  WCAG AA (≥ 4.5:1). The dark "starting" amber and the favourite star were the
  same hue and have been separated.
- `devdeck.desktop` no longer hardcodes a developer's absolute home path.

---

## [1.0.3]

- Prior release. Multi-project stacks, ANSI console drawer, and system tray
  integration.

[1.1.0]: https://github.com/nagachaitanyaappana/DevDeck/releases/tag/v1.1.0
