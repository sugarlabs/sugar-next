## Why

The Settings panel already offers brightness and contrast controls for
the Desktop background, painted as simple Cairo overlays in
`main.py:_draw_bg_overlay`. Learners customizing their background have
no way to mute a busy photo's colors (saturation) or draw the eye toward
the center of the screen (vignette) — both are standard wallpaper
treatments the current two-slider set doesn't cover, and both fit the
existing overlay-painting mechanism without new dependencies.

## What Changes

- Add a Saturation slider (background effects group) that desaturates
  the background image toward greyscale, painted via the same
  `Gtk.DrawingArea` overlay mechanism as brightness/contrast.
- Add a Vignette slider that darkens the background toward the edges via
  a radial gradient overlay.
- Both effects are persisted through `SettingsStore` alongside the
  existing `bg_brightness`/`bg_contrast` values and applied live without
  restart, matching current slider behavior.

## Capabilities

### New Capabilities
(none — this extends the existing Settings/background behavior defined
under `home-view`)

### Modified Capabilities
- `home-view`: the Settings panel requirement gains Saturation and
  Vignette controls alongside the existing Background/Accent/Contrast
  controls.

## Impact

- `sugar-next/sugar_next/shell/main.py` — `_draw_bg_overlay` gains
  saturation and vignette painting; new `set_bg_saturation`/
  `set_bg_vignette` methods mirroring `set_bg_brightness`/
  `set_bg_contrast`.
- `sugar-next/sugar_next/shell/settings.py` — two new sliders in the
  Background section (or the "Color" tab introduced by the
  `color-system-and-icon-state` change, if sequenced after it).
- `sugar-next/sugar_next/shell/settings_store.py` — new
  `bg_saturation`/`bg_vignette` defaults.
- No new dependencies.
