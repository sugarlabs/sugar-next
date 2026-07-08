## Purpose

Let jarabe (gtk4-port branch) run as an ordinary windowed client under a
host compositor, instead of assuming it owns the full session/display —
implementing what [sugar#929](https://github.com/sugarlabs/sugar/issues/929)
asked for, as a prerequisite for local dev/testing on a modern Linux
laptop.

## Requirements

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

#### Scenario: Windowed mode is verified end-to-end
- **WHEN** jarabe runs in windowed mode inside nested Wayfire
- **THEN** its onboarding window renders as an ordinary, visible window
  with real content — confirmed by running it, not just by code
  inspection

### Requirement: HomeWindow does not assume it owns the full screen in windowed mode
The system SHALL size `HomeWindow` to a fixed or configurable size instead
of the host output's full width/height, and SHALL NOT set
`Gdk.WindowTypeHint.DESKTOP`, when windowed mode is enabled.

#### Scenario: HomeWindow renders as an ordinary window
- **WHEN** jarabe runs in windowed mode inside a host compositor
- **THEN** `HomeWindow` appears as a normal, movable/resizable window
  rather than a full-screen desktop-hinted surface
- **STATUS**: implemented and believed correct by inspection, but not yet
  exercised end-to-end — reaching `HomeWindow` requires an existing Sugar
  profile or completing the onboarding flow, which wasn't done in this
  change (only the onboarding screen itself was validated)

### Requirement: FrameWindow behavior in windowed mode is resolved empirically
The system SHALL document whatever behavior `FrameWindow`'s
`Gdk.WindowTypeHint.DOCK` hint produces when run nested inside Wayfire,
and adjust it only if it prevents Frame from being usable.

#### Scenario: Frame is usable in the nested session
- **WHEN** jarabe runs in windowed mode inside Wayfire
- **THEN** the Frame (edges UI) is visible and interactive, even if its
  exact visual placement differs from a full-session deployment

## Validated Implementation (2026-07-08, updated)

The env var and `HomeWindow` code are unchanged from the prior change.
What changed: **the reason `HomeWindow`/`FrameWindow` couldn't be
exercised end-to-end is now resolved** — `jarabe.main` imports and runs
successfully (see `jarabe-gtk4-integration` and `sugar4-ext-module`
specs for how). The onboarding screen (reached before `HomeWindow` in
jarabe's startup path, since no profile exists) is confirmed rendering
correctly in windowed mode inside nested Wayfire.

`HomeWindow`/`FrameWindow` specifically remain unverified — not because
of an import blocker anymore, but because reaching them requires
completing the onboarding flow or having an existing profile, which this
change didn't do. The `FrameWindow` `DOCK`-hint question from the prior
change remains open for the same reason.
