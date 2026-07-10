## Context

`_draw_bg_overlay` in `main.py` currently paints two flat-color Cairo
overlays on top of the background picture: a mid-grey veil for contrast,
and a white/black veil for brightness. Both work because they're
uniform-color paints with alpha — Cairo doesn't need to touch the
underlying image's pixels. Saturation is different: desaturating an
image means blending each pixel toward its own luminance, which a flat
overlay paint cannot do. Vignette is another flat-ish overlay (radial
gradient, still no per-pixel image sampling), so it fits the existing
mechanism directly.

## Goals / Non-Goals

**Goals:**
- Add Saturation and Vignette as sliders alongside Brightness/Contrast,
  same persistence and live-update behavior.
- Keep the implementation inside Cairo/GTK4's existing drawing surface,
  no new imaging library.

**Non-Goals:**
- General image-processing pipeline (blur, hue rotation, arbitrary
  filters) — only the two effects requested.
- GPU-shader-based effects. This is a desktop background behind icons,
  not a performance-critical path; CPU-side Cairo is sufficient.

## Decisions

**Saturation via `Gtk.Picture` + a greyscale sibling, cross-faded by
alpha — not per-pixel Cairo blending.**
Cairo's `paint_with_alpha` can composite a second, pre-desaturated copy
of the same image over the color original: render the background image
twice (once normal, once through a `Gdk.Pixbuf` greyscale conversion —
GdkPixbuf has a `saturate_and_pixelate` call that does exactly this),
then cross-fade between them with the slider's alpha. This reuses
`GdkPixbuf`, already a transitive dependency via PyGObject/GTK, so no
new package. Simpler alternative (per-pixel loop in Python) would be far
too slow for a live-updating slider on a full-screen image.

**Vignette via `cairo.RadialGradient` overlay.**
A radial gradient from transparent (center) to black at some alpha
(edges), painted the same way contrast's flat veil is today — just a
gradient source instead of a flat color. Directly extends the existing
`_draw_bg_overlay` pattern, no new technique needed.

**Slider placement: Background section, wherever it ends up living.**
If `color-system-and-icon-state` lands first and splits Appearance into
Background/Color tabs, these sliders join Brightness/Contrast in
Background. If this change lands first, they're added to today's single
Appearance tab and the later change's tab split carries them over
unchanged. Either ordering works since both changes touch different
slider *groups* in the same file without overlapping edits.

## Risks / Trade-offs

- [Rendering the background twice per frame (color + greyscale) for the
  saturation cross-fade could cost more than a flat overlay paint] →
  Cache the greyscale `Gdk.Pixbuf` conversion, regenerate only when the
  background image path changes, not on every slider tick.
- [Order-of-landing with `color-system-and-icon-state`'s tab split could
  conflict if both changes touch `settings.py`'s Appearance-tab-building
  method in the same session] → Confirmed non-blocking (see Decisions),
  but implementers should rebase against whichever change merges first.
