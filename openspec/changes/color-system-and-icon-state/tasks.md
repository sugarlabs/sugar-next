## 1. Palette generation (theme.py)

- [ ] 1.1 Implement HSL-based derivation functions using `colorsys`:
      accent → `--sn-accent-counter` (hue-shifted 150-210°, contrast-
      adjusted lightness), accent → tinted `--sn-bg-alt`/`--sn-surface`
      (hue/saturation shift only, lightness preserved)
- [ ] 1.2 Extend `ThemeManager` to regenerate the derived tokens whenever
      `set_accent_tint` is called, instead of only setting `--sn-accent`
- [ ] 1.3 Add per-token override support: a token set manually via
      Settings is excluded from regeneration and written to
      `colors.css`; clearing the override re-enables derivation
- [ ] 1.4 Verify contrast: derived `--sn-accent-counter` against
      `--sn-accent`, and derived `--sn-bg-alt`/`--sn-surface` against
      `--sn-text`, stay within the same contrast bounds as the existing
      fixed light/dark tokens

## 2. Settings: Color tab

- [ ] 2.1 Split the current "Appearance" tab into "Background" and a new
      "Color" tab
- [ ] 2.2 Replace the 8-swatch + hex-entry accent picker with an
      expanded curated swatch grid (12-20 tones), restyled
- [ ] 2.3 Add per-token override controls to the Color tab: token name,
      current swatch (generated or overridden), reset-to-generated
      button
- [ ] 2.4 Convert `Gtk.StackSwitcher` tab labels to icon-only (Background,
      Color, Behavior, Extensions, About), each with a tooltip carrying
      the text label for accessibility

## 3. App-state registry (main.py)

- [ ] 3.1 Extract the existing toplevel open/close tracking
      (`_on_toplevel_open`, `_on_toplevel_close`, `_has_open_toplevel`)
      into a registry object exposing `open_app_ids` and a
      subscribe/callback mechanism
- [ ] 3.2 Add focused-app tracking: subscribe to the wlroots `activated`
      toplevel state when `pywayland` is available; leave
      `focused_app_id` permanently `None` otherwise
- [ ] 3.3 Update `frame.add_running`/`remove_running` call sites to be
      driven by registry callbacks instead of direct calls from
      `_on_app_process_closed` etc., without changing the Frame's public
      method signatures
- [ ] 3.4 Remove `Frame._running_ids` private tracking once the registry
      is wired in as the source of truth

## 4. Icon saturation (pie menu + app grid)

- [ ] 4.1 Add a CSS/paintable-based greyscale rendering path for
      `Gtk.Image`/icon widgets in `pie_menu.py`
- [ ] 4.2 Subscribe pie menu petal icons to the app-state registry;
      apply greyscale/color/full-saturation per the three-state (or
      two-state fallback) rule
- [ ] 4.3 Locate the app grid's icon rendering code (home-view
      capability) and apply the same subscription and rendering rule
- [ ] 4.4 Confirm two-state fallback: with `focused_app_id` always
      `None`, verify no icon ever renders in the full-saturation
      focused state

## 5. Verification

- [ ] 5.1 Manual test: change accent color, confirm
      `--sn-accent-counter`/`--sn-bg-alt`/`--sn-surface` update live
      without restart
- [ ] 5.2 Manual test: override a single token, confirm it persists
      across restart and survives subsequent accent changes until reset
- [ ] 5.3 Manual test (Wayfire/wlroots session): open two apps, switch
      focus between them, confirm pie menu and app grid icon saturation
      tracks correctly
- [ ] 5.4 Manual test (no `pywayland` installed): confirm icons only
      ever show greyscale/color, never the focused highlight
- [ ] 5.5 Run existing test suite (`sugar-next/tests`) and fix any
      breakage from the `Frame._running_ids` removal
