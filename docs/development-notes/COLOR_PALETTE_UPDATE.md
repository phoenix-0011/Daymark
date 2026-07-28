# Daymark Color Palette System

Daymark now supports three complete palettes from Settings:

- Warm sage
- Sky blue
- Aristocratic green

Each palette has an independently tuned light and dark variant. The selected palette is stored in `QSettings` under `colorPalette` and is restored on the next launch.

## Semantic color coverage

Every palette defines shared roles for:

- app background and sidebar
- cards and elevated surfaces
- alternate and pressed surfaces
- primary, muted, and faint text
- borders and focus rings
- accent, hover, pressed, and soft-accent states
- readable foreground text on accent surfaces
- danger and soft-danger states
- overlays and toast surfaces
- six palette-coherent category swatches

These roles are consumed by the global stylesheet and custom-painted Qt widgets, including navigation highlights, launcher-style marks, task actions, calendar selections, planner cells, heatmaps, donuts, bar charts, settings controls, and dialogs.

## Settings behavior

Open **Settings → Appearance → Color palette** and select a palette. The update is applied immediately to every live widget and persists after closing the app.

Changing light/dark appearance keeps the selected color family and switches to its corresponding light or dark variant.

## Accessibility checks

Automated tests verify:

- all three palettes contain complete light/dark role sets
- every color is a valid six-digit hex value
- primary text has at least 7:1 contrast against the window background
- muted text has at least 4.5:1 contrast against the window background
- foreground text on accent and danger surfaces has at least 4.5:1 contrast
- Settings and QSettings persistence hooks are present
