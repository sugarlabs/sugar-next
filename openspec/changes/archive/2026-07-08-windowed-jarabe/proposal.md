## Why

The previous change (`gtk4-dev-environment`, archived) proved the GTK4
build toolchain works, but explicitly stopped short of running the full
`jarabe` shell — Casilda can't host it, since Casilda has no
window-management/layer-shell support and `jarabe` expects to manage
multiple activity windows itself.

Research into nested-compositor alternatives (Cage, Wayfire, sway
`--nested`, GNOME Shell `--nested`, Xephyr) found that **the missing piece
isn't primarily a compositor capability gap — it's that `jarabe` itself
was never built to run windowed.** This is confirmed by
[sugar#929](https://github.com/sugarlabs/sugar/issues/929) ("Launch sugar
in a window"), open since 2020, where a maintainer already specified
exactly what's needed: jarabe should skip fullscreen, not start its own
window manager/session, accept a `--no-fullscreen`/`--resolution`-style
flag, and let whatever compositor is already running manage focus and
window switching. No such changes have ever been implemented, and PR
#1019 (the GTK4 port) doesn't touch this either.

Reading `jarabe`'s actual startup code (`gtk4-port` branch) confirms and
sharpens this:
- `jarabe/main.py`'s `_start_window_manager()` unconditionally spawns its
  **own** `mutter --wayland` subprocess and mutates global
  `org.gnome.desktop.interface` GSettings (cursor theme, later also font/
  theme settings) — it assumes it owns the whole session, not just an
  app-level compositor.
- `jarabe/desktop/homewindow.py`'s `HomeWindow` sizes itself to
  `screen.get_width()/get_height()` (the full output) and sets
  `Gdk.WindowTypeHint.DESKTOP`.
- `jarabe/frame/framewindow.py`'s `FrameWindow` sets
  `Gdk.WindowTypeHint.DOCK`.

All three assume jarabe owns the display. None of this is exotic to fix —
it's config/startup-path changes, not a rewrite — but it hasn't been done.

Wayfire is the concrete target compositor: it's the only actively
maintained wlroots compositor that combines full multi-surface/window
management, wlr-layer-shell support, and documented nested/windowed
operation (unlike Cage, which is kiosk-only and lacks layer-shell; unlike
GNOME Shell `--nested`, which is Mutter-specific and reportedly broken in
recent GNOME; unlike sway, which is a valid alternative but a stricter
tiling model than jarabe's own floating/desktop-style window placement).

## What Changes

- Add a `--no-fullscreen` (or equivalent env var) startup mode to jarabe
  that:
  - Skips `_start_window_manager()`'s Mutter subprocess spawn entirely —
    assumes a compositor is already running (Wayfire, in our target
    setup) and jarabe is just another Wayland client under it.
  - Skips the global `org.gnome.desktop.interface` GSettings mutation
    (cursor theme et al.) in this mode, since it's not appropriate to
    change the host compositor's settings for a nested dev session.
  - Sizes `HomeWindow` to a fixed configurable size (or the nested
    compositor's own output size) instead of assuming it owns a screen,
    and drops `Gdk.WindowTypeHint.DESKTOP`.
  - Similarly adjusts `FrameWindow`'s `DOCK` hint if it interferes with
    normal windowed placement inside Wayfire (to be confirmed empirically
    during implementation).
- Document a working procedure to run jarabe nested inside Wayfire on
  this workspace's host, building on `repos/sugar` (gtk4-port branch)
  already cloned during this investigation.
- Update `specbook/docs/gtk-porting-standards.md` with the result,
  replacing its current "out of scope for now" framing for this specific
  problem.

**BREAKING**: none for existing full-session Sugar deployments — the new
mode is opt-in via flag/env var; default behavior (own Mutter, fullscreen,
DESKTOP hint) is unchanged.

## Capabilities

### New Capabilities

- `windowed-jarabe-mode`: jarabe gains an opt-in mode where it does not
  start its own window manager/session and does not assume it owns a
  full screen, making it embeddable as an ordinary window inside a host
  compositor.
- `nested-wayfire-dev-session`: a documented, reproducible way to run
  jarabe (in `windowed-jarabe-mode`) inside Wayfire, nested inside this
  workspace's existing Wayland session, for local development/testing.

### Modified Capabilities

(none — `gtk4-toolchain-validation` and `casilda-embedded-widget-demo`
from the prior change are unaffected; this change targets `jarabe`
directly, which those specs didn't cover)

## Impact

- **Code changed**: `repos/sugar` (gtk4-port branch) —
  `src/jarabe/main.py`, `src/jarabe/desktop/homewindow.py`, possibly
  `src/jarabe/frame/framewindow.py`. Small, targeted changes per
  `specbook/docs/base-standards.md` rule 1 — not a rewrite.
- **New system dependency**: `wayfire` (Arch/CachyOS package, depends on
  `wlroots0.19`/`wf-config`) — not yet installed on this host, needs
  confirmation before installing (per `base-standards.md`).
- **Docs updated**: `specbook/docs/gtk-porting-standards.md` gets a
  concrete "run jarabe windowed under Wayfire" section, and the current
  "unsolved" framing for shell-level nesting is resolved (for this
  specific approach; it doesn't retroactively make Casilda capable of
  this).
- **Upstream angle**: since this directly implements what a Sugar
  maintainer already asked for in sugar#929, the resulting patch to
  `jarabe` is a reasonable candidate to eventually upstream — noted here,
  not committed to as part of this change's scope.
