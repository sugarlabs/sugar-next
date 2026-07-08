## ADDED Requirements

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

## Validated Implementation (2026-07-08)

Wayfire (0.10.1-5.1, wlroots0.19 0.19.3-1.1) confirmed running nested on
this host via auto-detection of `$WAYLAND_DISPLAY`.

**jarabe (gtk4-port) could not be validated running inside it**, because
`jarabe.main` fails to import at all, independent of windowed
mode/Wayfire/Casilda. Blocker chain, in order:

1. `src/jarabe/config.py` missing (Autotools-generated, never built) —
   worked around with a hand-written dev-only version.
2. `SugarExt` version `'2.0'` required, which never existed — **a real
   bug in `gtk4-port`**, traced via `git diff` to commit `b9fdeefb`, fixed
   directly (changed to `'1.0'`).
3. `SugarExt` (from `sugar-toolkit-gtk3`) is compiled against GTK3;
   `jarabe` (gtk4-port) already loads GTK4 — GObject Introspection refuses
   to load both ABIs in one process. **Structural gap**, not fixed;
   worked around only for this investigation with an explicitly
   non-functional stub (`specbook/demos/sugarext_stub.py`).
4. `sugar4.test.uitree` missing from `sugar-toolkit-gtk4` (debug-only) —
   worked around with a defensive `try/except`.
5. `sugar4.activity.activityfactory` missing from `sugar-toolkit-gtk4` —
   needed for real activity-launching functionality, not stubbable
   reasonably. **Investigation stopped here.**

See `specbook/docs/gtk-porting-standards.md` "Windowed jarabe: findings"
for full detail. The `windowed-jarabe-mode` code itself (separate
capability/spec) is implemented and believed correct by inspection, but
was never exercised end-to-end as a result.
