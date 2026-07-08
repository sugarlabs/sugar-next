## ADDED Requirements

### Requirement: jarabe supports an opt-in windowed startup mode
The system SHALL provide a way to start jarabe (gtk4-port branch) without
it spawning its own window manager subprocess or mutating session-wide
desktop GSettings, gated behind an explicit flag or environment variable
that defaults to off.

#### Scenario: Default behavior is unchanged
- **WHEN** jarabe is started without the new flag/env var set
- **THEN** it behaves exactly as before — spawns its own `mutter --wayland`,
  sets cursor/theme GSettings, assumes it owns the full screen

#### Scenario: Windowed mode skips window manager startup
- **WHEN** jarabe is started with the new flag/env var enabled
- **THEN** `_start_window_manager()`'s Mutter subprocess spawn and the
  `org.gnome.desktop.interface` GSettings mutation are both skipped

### Requirement: HomeWindow does not assume it owns the full screen in windowed mode
The system SHALL size `HomeWindow` to a fixed or configurable size instead
of the host output's full width/height, and SHALL NOT set
`Gdk.WindowTypeHint.DESKTOP`, when windowed mode is enabled.

#### Scenario: HomeWindow renders as an ordinary window
- **WHEN** jarabe runs in windowed mode inside a host compositor
- **THEN** `HomeWindow` appears as a normal, movable/resizable window
  rather than a full-screen desktop-hinted surface

### Requirement: FrameWindow behavior in windowed mode is resolved empirically
The system SHALL document whatever behavior `FrameWindow`'s
`Gdk.WindowTypeHint.DOCK` hint produces when run nested inside Wayfire,
and adjust it only if it prevents Frame from being usable.

#### Scenario: Frame is usable in the nested session
- **WHEN** jarabe runs in windowed mode inside Wayfire
- **THEN** the Frame (edges UI) is visible and interactive, even if its
  exact visual placement differs from a full-session deployment

## Validated Implementation (2026-07-08)

The `SUGAR_NO_FULLSCREEN=1` env var, `_start_window_manager()`'s
early-return path, and `HomeWindow`'s fixed-size/no-DESKTOP-hint path are
all implemented in `repos/sugar` (gtk4-port branch) — `src/jarabe/main.py`
and `src/jarabe/desktop/homewindow.py`. Verified by code inspection and
`python3 -m py_compile` (which also caught and fixed an unrelated
`SyntaxError` this change introduced — a duplicated `global` declaration).

**Not verified end-to-end**: whether `HomeWindow` and `FrameWindow`
actually render correctly inside nested Wayfire. `jarabe.main` fails to
import for reasons unrelated to this capability — see the
`nested-wayfire-dev-session` spec's "Validated Implementation" section
for the full blocker chain (a real `SugarExt` version bug, plus a
structural GTK3/GTK4 ABI conflict in `SugarExt` that blocks jarabe from
starting at all). The `FrameWindow` DOCK-hint requirement above remains
unresolved — deferred to whichever future change gets jarabe importable.
