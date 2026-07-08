## Context

Confirmed by reading `repos/sugar` (gtk4-port branch) source directly:

- `jarabe/main.py::main()` calls `_start_window_manager()` unconditionally,
  which spawns `mutter --wayland` as a subprocess and mutates the
  session-wide `org.gnome.desktop.interface` GSettings schema (cursor
  theme; `setup_fonts()`/`setup_theme()` also touch `gtk-theme` and
  `icon-theme` globally).
- `jarabe/desktop/homewindow.py::HomeWindow.__init__` sizes itself via
  `screen.get_width()/get_height()` and sets
  `Gdk.WindowTypeHint.DESKTOP`.
- `jarabe/frame/framewindow.py::FrameWindow` sets
  `Gdk.WindowTypeHint.DOCK`.

This matches the maintainer's diagnosis in
[sugar#929](https://github.com/sugarlabs/sugar/issues/929) exactly:
jarabe assumes it owns the entire session and display. Nesting it inside
any compositor — however capable — doesn't fix this on its own.

Nested-compositor research (this workspace, 2026-07-08) ranked Wayfire as
the best host: actively maintained (wlroots0.19, packaged in Arch
`extra`), full multi-window management (unlike Cage's kiosk-only model),
wlr-layer-shell support (Cage lacks this; relevant if `FrameWindow`'s DOCK
hint ends up needing layer-shell semantics to render correctly), and
documented nested/windowed operation.

## Goals / Non-Goals

**Goals:**
- jarabe (gtk4-port branch) gains an opt-in windowed mode: no self-spawned
  Mutter, no global GSettings mutation, no assumption of owning the full
  screen.
- jarabe in this mode runs successfully nested inside Wayfire, on this
  workspace's host, as a normal windowed Wayland client.
- The Home View and Frame are both visible and usable (even if visually
  imperfect) inside that nested window — this is a dev/testing capability,
  not a polished end-user feature yet.
- Document the working procedure.

**Non-Goals:**
- Upstreaming the patch to `sugarlabs/sugar` as part of this change (noted
  as a reasonable follow-up, not committed to here).
- Making windowed mode the default — the existing full-session behavior
  (own Mutter, fullscreen, DESKTOP hint) must remain the default and
  unaffected.
- Visual/UX polish of jarabe running windowed — first pass is "does it
  run and is it usable enough to develop against", not a finished
  experience.
- Touching `sugar-toolkit-gtk4` or Casilda — this change is scoped to
  `jarabe` (the `sugar` repo) and the Wayfire hosting setup only.
- Activity launching/Telepathy/datastore integration correctness inside
  the nested session — if those subsystems misbehave without a full
  session (D-Bus services, etc.), that's noted as a risk, not solved here.

## Decisions

**D1 — Gate the new behavior behind an explicit flag/env var, not a
runtime environment auto-detection.**
Rationale: auto-detecting "am I nested" is fragile (many false
positives/negatives across compositors) and the maintainer's own
suggestion in #929 was an explicit flag. Concretely: add a
`--no-fullscreen` CLI argument to `bin/sugar.in`'s exec line (or a
`SUGAR_NO_FULLSCREEN=1` env var, whichever is more consistent with
jarabe's existing config patterns — check `jarabe/config.py` during
implementation) that `main.py` checks before calling
`_start_window_manager()`.

**D2 — Skip window-manager startup entirely in windowed mode, don't try
to make jarabe spawn a *different* nested-aware WM itself.**
Rationale: the host (Wayfire) is already the window manager in this
scenario; having jarabe spawn Mutter *inside* Wayfire would be a
compositor-inside-a-compositor situation that adds complexity for no
benefit. Alternative considered: keep spawning Mutter but tell it to
nest inside Wayfire too — rejected, since the goal is exactly to stop
jarabe from needing its own WM process at all, per #929's guidance.

**D3 — Use Wayfire's nested mode as the target environment, documented
as a `specbook/docs` procedure, not automated end-to-end in this change.**
Rationale: consistent with how `gtk4-dev-environment` handled Casilda —
validate manually first, write down what worked, automate later if it
becomes a repeated need. Installing Wayfire requires user confirmation
per `base-standards.md` (new system dependency).

**D4 — Fix `HomeWindow`'s sizing and `DESKTOP` hint; treat
`FrameWindow`'s `DOCK` hint as an open question to resolve empirically.**
Rationale: `HomeWindow`'s screen-size assumption is unambiguously wrong
for windowed mode and easy to fix (use a fixed/configurable size instead).
`FrameWindow`'s `DOCK` hint is less clear-cut — under Wayfire (layer-shell
aware), a DOCK-hinted window might render fine, oddly, or not at all;
decide based on what's actually observed running it, rather than
preemptively rewriting frame window semantics.

## Risks / Trade-offs

- **[Risk] D-Bus/session services (Telepathy/mission-control, the
  notification service, `apisocket`) may misbehave without a full Sugar
  session/logind session backing them.** → Mitigation: run with
  `dbus-run-session` (already used for Mutter in the existing code, so
  the pattern is already in the codebase) wrapping the whole jarabe
  process if needed; treat any resulting errors as expected/documented
  limitations of dev-mode, not bugs to chase down in this change.

- **[Risk] `FrameWindow`'s `DOCK` hint may not render sensibly inside a
  nested Wayfire instance**, since DOCK semantics are compositor-specific.
  → Mitigation: this is explicitly an Open Question (see below), resolved
  empirically during `tasks.md` execution rather than guessed at here.

- **[Risk] Wayfire's own nested-mode maturity** — the research found
  changelog entries about *fixing* nested-mode crashes as recently as
  2026, implying it's a real but not bulletproof code path. → Mitigation:
  pin/note the exact Wayfire version that works, same as was done for
  wlroots/Casilda in the prior change.

- **[Trade-off] Not pursuing Xephyr/X11 for the GTK3 `master` branch as an
  easier baseline.** Accepted per the user's continued preference for the
  GTK4 track; noted as available if this path stalls.

## Migration Plan

Not applicable in the deploy sense. Rollback is simply: the
`--no-fullscreen`/env-var-gated code path is unused unless explicitly
invoked, so default (full-session) Sugar behavior is unaffected by this
change existing.

## Open Questions (resolved/superseded during implementation)

- ~~Is a CLI flag or an env var more consistent with jarabe's existing
  config conventions?~~ **Resolved**: env var (`SUGAR_NO_FULLSCREEN=1`) —
  confirmed by grepping the whole codebase, `os.environ` reads are the
  only config-passing convention in use; no argparse/CLI-flag pattern
  exists anywhere in jarabe.
- ~~Does `FrameWindow`'s `DOCK` hint need adjustment under Wayfire?~~
  **Superseded, not reached**: jarabe doesn't start at all yet
  (independent of windowed mode) — see
  `specbook/docs/gtk-porting-standards.md` "Windowed jarabe: findings"
  for the full blocker chain (a real `SugarExt` version bug found and
  fixed, plus a structural GTK3-vs-GTK4 ABI conflict in `SugarExt` itself
  that's out of scope for this change). This question is deferred to
  whichever future change gets jarabe importable again.
- ~~Do activity-launching and Journal/datastore integration work in this
  nested mode?~~ **Superseded, not reached** for the same reason —
  `jarabe/journal/journalactivity.py` itself fails to import
  (`sugar4.activity.activityfactory` missing from `sugar-toolkit-gtk4`)
  before windowed mode's own behavior could be exercised at all.
