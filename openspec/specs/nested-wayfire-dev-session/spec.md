## Purpose

Provide a working nested Wayfire compositor to eventually host jarabe in
windowed mode, and document precisely what currently blocks jarabe
(gtk4-port) from starting there at all.

## Requirements

### Requirement: Wayfire runs nested on this workspace's host
The system SHALL provide a documented, reproducible procedure to run
Wayfire nested (windowed) inside the existing Wayland session, as the
target host compositor for jarabe's windowed mode.

#### Scenario: Nested Wayfire starts successfully
- **WHEN** a developer runs `wayfire` from an existing Wayland session
- **THEN** it auto-detects `$WAYLAND_DISPLAY` and runs as a windowed
  Wayland client (confirmed: Wayfire 0.10.1, creates virtual output,
  stays alive without crashing)

#### Scenario: Working Wayfire version is recorded
- **WHEN** the nested session is validated on this host
- **THEN** the exact Wayfire (and wlroots) version used is recorded in
  `specbook/docs/gtk-porting-standards.md`

### Requirement: jarabe startup blockers are documented precisely
The system SHALL document, precisely and in order, every blocker
encountered attempting to start jarabe (gtk4-port branch) in a
`sugar-toolkit-gtk4` environment — whether caused by this change's own
code or by pre-existing gaps in the GTK4 port — so the next attempt
doesn't rediscover them.

#### Scenario: Blocker chain is documented
- **WHEN** `jarabe.main` fails to import
- **THEN** `specbook/docs/gtk-porting-standards.md` lists each blocker
  encountered in order, which were fixed vs. worked around vs. left
  unresolved, and why

#### Scenario: Real bugs found are distinguished from environment gaps
- **WHEN** a blocker is a genuine bug in the `gtk4-port` branch itself
  (as opposed to a missing dev-environment setup step)
- **THEN** it is fixed directly in the checkout and called out explicitly
  as a bug fix, not folded into general environment documentation

#### Scenario: jarabe successfully runs to completion inside nested Wayfire
- **WHEN** all blockers documented in this spec's history have been
  resolved (ported or stubbed)
- **THEN** jarabe imports, activates, and renders a real window with
  visible content inside the nested Wayfire session

## Validated Implementation (2026-07-08, updated)

**jarabe (gtk4-port) now runs successfully inside nested Wayfire**,
superseding the prior "could not be validated" finding. Wayfire
(0.10.1-5.1, wlroots0.19 0.19.3-1.1) unchanged from before.

Full blocker chain, extending the prior 5 items to completion:

1-5. (unchanged from prior validation: `config.py`, `SugarExt` version
   bug, `SugarExt`/GTK3-GTK4 ABI conflict, missing `uitree`, missing
   `activityfactory` — all resolved, see items below)

6. `activityfactory` **ported for real** (not stubbed) —
   `sugar4/activity/activityfactory.py`, direct namespace port from
   `sugar-toolkit-gtk3` (pure Python/D-Bus/subprocess, no GTK3
   dependency).
7. `sugar4/ext.py` written as the real `SugarExt`/`SugarGestures`
   replacement (see `sugar4-ext-module` spec) — resolves item 3's ABI
   conflict properly instead of via a throwaway demo stub.
8. `sugar4/activity/i18n.py` missing — direct port (pure Python,
   `pgettext` + MO-file parsing).
9. ~20 files across `sugar` (gtk4-port) needed fixes for GTK3 APIs
   removed in GTK4: `Gtk.EventBox`/`Gtk.Bin` base classes,
   `Gtk.Toolbar`, positional `Gtk.Label`/`Gtk.Button` constructor args,
   `Gtk.STOCK_STOP`, `Gtk.Adjustment` property names, `Gtk.HScale`,
   `'button-press-event'`/`'key-press-event'` signals,
   `Gdk.ModifierType.MOD1_MASK`, `Gdk.Seat.get_slaves()`. Centralized
   via `sugar4.gtk3compat` where the pattern repeated dozens of times
   (see that spec); fixed directly where it didn't.
10. `Gio.ApplicationFlags.IS_SERVICE` prevented `'activate'` from firing
    on `Gtk.Application.run(None)` in GTK4 (confirmed via isolated
    reproduction — different behavior than GTK3). Removed; documented as
    a lifecycle-semantics change needing a real
    `hold()`/`release()`-based fix later.
11. `Gtk.main()` (called after `_start_window_manager()` returns) doesn't
    exist in GTK4 and was redundant anyway (`shell.run(None)` already
    runs the main loop) — removed.
12. **Root cause of the "renders as blank gray box" symptom**:
    `ShellModel.add_window()` unconditionally did
    `window.set_child(self.compositor)` before adding any window,
    clobbering real content already set by `IntroWindow`. Found by
    bisection (see `jarabe-gtk4-integration` spec). Fixed: only fall
    back to the compositor if the window has no child already.

**Confirmed working**: jarabe's onboarding screen renders with real,
visible content (name/color/gender/age entry) inside the nested Wayfire
window — visually confirmed, not just inferred from lack of errors.

See `specbook/docs/gtk-porting-standards.md` "Windowed jarabe: SUCCESS"
for the complete account, working procedure, and known limitations
(Home View/Frame/Journal unverified; activity-window tracking disabled;
icon layout is a box-packing stub; no Sugar GTK4 theme exists).
