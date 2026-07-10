## 1. Settings store

- [ ] 1.1 Add `bg_saturation` (default 1.0, full color) and
      `bg_vignette` (default 0.0, off) to `settings_store.py` defaults

## 2. Background rendering (main.py)

- [ ] 2.1 Cache a greyscale `Gdk.Pixbuf` conversion of the current
      background image, regenerated only when the background path
      changes
- [ ] 2.2 Extend `_draw_bg_overlay` to cross-fade the color and
      greyscale pixbufs by the saturation slider's alpha
- [ ] 2.3 Extend `_draw_bg_overlay` to paint a `cairo.RadialGradient`
      vignette overlay scaled by the vignette slider's alpha
- [ ] 2.4 Add `set_bg_saturation`/`set_bg_vignette` methods mirroring
      `set_bg_brightness`/`set_bg_contrast`

## 3. Settings UI

- [ ] 3.1 Add Saturation slider to the Background section (Appearance
      tab, or Background tab if `color-system-and-icon-state`'s tab
      split has already landed)
- [ ] 3.2 Add Vignette slider alongside it, same section
- [ ] 3.3 Wire both sliders' `value-changed` to `SettingsStore` and the
      corresponding `set_bg_*` shell method, matching existing
      brightness/contrast wiring

## 4. Verification

- [ ] 4.1 Manual test: drag Saturation to zero, confirm background
      reaches full greyscale live
- [ ] 4.2 Manual test: increase Vignette, confirm edges darken
      progressively with a smooth radial falloff
- [ ] 4.3 Manual test: restart shell after setting non-default values,
      confirm both persist
- [ ] 4.4 Performance check: drag both sliders continuously, confirm no
      visible lag from pixbuf regeneration (should not regenerate on
      every tick, only on background-path change)
