## ADDED Requirements

### Requirement: jarabe imports successfully against sugar-toolkit-gtk4
The system SHALL allow `import jarabe.main` to complete without error
when run against `sugar-toolkit-gtk4`, with all required toolkit modules
(`activityfactory`, `i18n`, `ext`, `gtk3compat`) present.

#### Scenario: Clean import
- **WHEN** a developer runs `python3 -c "import jarabe.main"` with the
  documented environment variables and `PYTHONPATH`
- **THEN** the import completes without raising any exception

### Requirement: jarabe's Gtk.Application activates and renders a window
The system SHALL ensure the `'activate'` signal fires on `ShellModel.run(None)`
and that the resulting window displays its actual content, not a blank
compositor surface.

#### Scenario: Onboarding screen renders with visible content
- **WHEN** jarabe is launched with no existing Sugar profile, inside a
  nested Wayfire session
- **THEN** the onboarding window (name/color/gender/age entry) is visible
  with real widget content (labels, entry fields, icons) — not a blank
  gray box

### Requirement: Real gtk4-port bugs are fixed directly; genuinely missing functionality is stubbed explicitly
The system SHALL distinguish, in both code comments and documentation,
between bugs that are fixed as bugs (incorrect version strings, missing
imports, typos) versus functionality that is stubbed because a real GTK4
equivalent doesn't exist yet or requires separate design work.

#### Scenario: Stubs never silently succeed
- **WHEN** a stubbed function (e.g. `sugar4.ext.clipboard_set_with_data`)
  is called
- **THEN** it logs a warning identifying itself as a stub and does not
  claim to have performed the real operation

## Validated Implementation (2026-07-08)

Confirmed working end-to-end: jarabe (gtk4-port branch) imports, runs,
activates, and renders its onboarding screen with real visible content
inside a nested Wayfire (0.10.1) session on this host. See
`specbook/docs/gtk-porting-standards.md` "Windowed jarabe: SUCCESS" for
the full blocker chain, the ~20 files touched, and the exact working
procedure.

**Root cause of the "blank window" symptom**: `ShellModel.add_window()`
(in `jarabe/model/shell.py`) unconditionally replaced every window's
content with an empty `Casilda.Compositor()` before adding it to the
application — found by bisecting isolated tests (real `IntroWindow`
alone worked; real `ShellModel.add_window()` reproduced the bug). Fixed
to only fall back to the compositor when the window has no child
already set.

**Not verified**: Home View, Frame, Journal (no Sugar profile existed on
this host, so only the onboarding path was reached); activity-window
tracking (disabled, not redesigned, since it relied on
`Gdk.WindowTypeHint`/`get_type_hint()` which don't exist in GTK4); real
icon layout (SnowflakeLayout/ViewContainer are box-packing stubs).
