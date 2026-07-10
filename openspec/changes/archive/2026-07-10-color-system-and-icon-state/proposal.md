## Why

Sugar Next's HIG states "color is meaningful," but today color carries no
meaning: the accent is a flat user pick with no relationship to the rest of
the palette, and app icons render identically whether an app is closed,
open, or the one currently in focus. Learners get no at-a-glance answer to
"what's running?" or "where is my attention?" — the exact question color is
supposed to answer per HIG principle #4. This change makes the accent color
generate a coherent, adjustable palette, and makes icon saturation encode
running/focused state.

## What Changes

- Add a semantic palette generator (`colorsys`-based, no new dependencies)
  that derives a full token set — accent counterpart, tinted surfaces,
  text-on-accent — from a single user-picked accent color.
- Extend `--sn-*` tokens with `--sn-accent-counter` (contrast + secondary
  semantic role) and tint `--sn-bg-alt`/`--sn-surface` subtly toward the
  accent; `--sn-bg` and `--sn-text` stay neutral for readability.
- Allow per-token manual override on top of the generated palette, written
  to the existing `~/.config/sugar-next/colors.css` override mechanism.
- Redesign the accent picker: replace the 8-swatch + raw hex entry with an
  expanded, better-styled curated swatch grid.
- Extend `main.py`'s existing toplevel open/close tracking into a shared
  app-state registry (`open_app_ids`, `focused_app_id`) that the Frame,
  pie menu, and app grid all subscribe to, replacing the Frame's
  currently-private `_running_ids`.
- Wire icon rendering (pie menu, app grid) to that registry: greyscale
  when closed, full color when open, full-saturation highlight when
  focused. Degrades to two states (greyscale/color) when the compositor
  doesn't expose the wlroots `activated` toplevel event.

## Capabilities

### New Capabilities
- `semantic-color-system`: accent-driven palette generation, token
  derivation rules, per-token override mechanism, accent picker UI.
- `app-state-registry`: shared open/focused app tracking in `main.py`,
  consumed by Frame/pie menu/app grid; icon saturation rules tied to it.

### Modified Capabilities
- `frame-views`: the Frame's running-apps tracking (`_running_ids`,
  `add_running`/`remove_running`) is replaced by consuming the shared
  `app-state-registry` instead of maintaining private state.
- `home-view`: pie menu and app grid icon rendering gains
  state-dependent saturation (greyscale/color/focused) sourced from the
  `app-state-registry`.

## Impact

- `sugar-next/sugar_next/shell/theme.py` — palette generation, new tokens.
- `sugar-next/sugar_next/shell/settings.py` — new Color tab, redesigned
  accent picker, per-token override UI.
- `sugar-next/sugar_next/shell/main.py` — app-state registry, focus
  tracking via wlroots `activated` event (optional dependency
  `pywayland`, already optional).
- `sugar-next/sugar_next/shell/frame.py` — consumes registry instead of
  private `_running_ids`.
- `sugar-next/sugar_next/shell/pie_menu.py` — icon saturation per state.
- App grid view (home-view capability) — icon saturation per state.
- No new required dependencies; `pywayland` remains optional, feature
  degrades gracefully without it.
