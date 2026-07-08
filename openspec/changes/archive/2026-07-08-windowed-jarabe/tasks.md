## 1. Confirm environment and install Wayfire

- [x] 1.1 Confirm `repos/sugar` (gtk4-port branch) is cloned (already done
      during investigation for this change)
- [x] 1.2 Check whether Wayfire and its runtime deps (`wlroots0.19`,
      `wf-config`) are already installed; if not, surface the exact
      `pacman` package name(s) and get user confirmation before
      installing, per `specbook/docs/base-standards.md`
      **Result**: user installed `wayfire 0.10.1-5.1` (+ `wf-config
      0.10.0-2.1`, `wlroots0.19 0.19.3-1.1`) before this apply session.
- [x] 1.3 Install confirmed dependencies (user-confirmed step)
      **Result**: done by user, confirmed via `pacman -Q`.
- [x] 1.4 Confirm Wayfire runs nested (windowed) inside the current
      Wayland session at all, with no Sugar involved yet — just an empty
      Wayfire instance in a window, as a baseline sanity check
      **Result**: `wayfire` (no args) auto-detects `$WAYLAND_DISPLAY` and
      opens as a nested wayland-backend client (log: "Creating wayland
      backend"), creates virtual output `WL-1`, starts XWayland. Process
      stayed alive under a background run, confirming it's a live
      compositor waiting for clients, not crashing. One benign warning
      ("Couldn't find matching mode 1280x720@0 for output WL-1... Trying
      custom mode") — cosmetic, doesn't block startup.

## 2. Locate and understand the exact code paths to change

- [x] 2.1 Re-confirm line numbers/exact code in `repos/sugar`'s
      `src/jarabe/main.py` (`_start_window_manager`, `main()`),
      `src/jarabe/desktop/homewindow.py` (`HomeWindow.__init__`), and
      `src/jarabe/frame/framewindow.py` (`FrameWindow`) — these were
      identified during design but re-verify against the current state
      of the branch before editing, in case it moved
      **Result**: unchanged since design — `main.py:165`
      (`_start_window_manager`), `main.py:323` (call site in `main()`),
      `homewindow.py:63` (`set_default_size`), `homewindow.py:75`
      (`DESKTOP` hint), `framewindow.py:145` (`DOCK` hint).
- [x] 2.2 Check `jarabe/config.py` for existing patterns of how
      flags/env vars are read, to decide between a CLI flag and an env
      var per design.md's Open Question
      **Result**: `config.py.in` is Autotools-substituted build paths
      only, not a runtime flag mechanism. The actual codebase convention
      (confirmed via grep across `main.py`) is `os.environ[...]` reads —
      `SUGAR_HOME`, `SUGAR_PROFILE`, `SUGAR_SCALING` etc. are all read
      this way from `bin/sugar.in`. `sys.argv` is used nowhere for jarabe's
      own flags (only passed through to `Gst.init`). **Decision: use an
      env var, `SUGAR_NO_FULLSCREEN=1`**, matching the existing pattern
      exactly rather than introducing argparse.

## 3. Implement windowed-jarabe-mode

- [x] 3.1 Add the chosen flag/env var (e.g. `SUGAR_NO_FULLSCREEN=1`) and
      thread it through to `main()`
      **Result**: added `_windowed_mode()` helper (reads
      `SUGAR_NO_FULLSCREEN=1`) locally in both `main.py` and
      `homewindow.py` — not shared via import, to avoid a circular
      import (`main.py` imports `jarabe.desktop.homewindow`). Small
      duplication, acceptable per `base-standards.md` rule 1 (avoid
      premature abstraction) for a 3-line helper.
- [x] 3.2 In `main()`, skip the `_start_window_manager()` call entirely
      when the flag is set (don't spawn Mutter, don't mutate
      `org.gnome.desktop.interface` GSettings)
      **Result**: `_start_window_manager()` now checks `_windowed_mode()`
      first and returns early (still calling `_complete_desktop_startup()`
      if needed) without touching GSettings or spawning Mutter.
      `_stop_window_manager()` symmetrically no-ops in windowed mode —
      needed because it unconditionally referenced
      `_cursor_theme_settings`/`_mutter_process`, which would otherwise
      never get set and crash with `NameError` at shutdown.
- [x] 3.3 In `HomeWindow.__init__`, when the flag is set, use a fixed or
      configurable default size instead of `screen.get_width()/get_height()`,
      and skip `set_type_hint(Gdk.WindowTypeHint.DESKTOP)`
      **Result**: added `_WINDOWED_DEFAULT_WIDTH/HEIGHT` (1024x768,
      matching the size used in the earlier `gtk4-dev-environment`
      Casilda demo for consistency). Also skipped the
      `screen.connect('size-changed', ...)` hookup and the
      `__screen_size_changed_cb(None)` initial call in windowed mode —
      that callback forces min/max/base geometry to the exact monitor
      size and repositions the window to the monitor's origin, which
      would fight a normal windowed placement just as much as the
      original `set_default_size` call did. Not caught during design;
      found while reading the full `__init__` before editing.
- [x] 3.4 Leave `FrameWindow`'s `DOCK` hint untouched for now — this is
      resolved empirically in section 4, not preemptively here
- [x] 3.5 (unplanned) Fix a `SyntaxError` introduced by 3.2: `global
      _starting_desktop` was declared twice in `_start_window_manager`
      (once in the new early-return branch, once in the original code
      path) — Python rejects redeclaring `global` after conditional use.
      Fixed by declaring it once at the top of the function. Caught via
      `python3 -m py_compile` before attempting to run jarabe at all.

## 4. Validate: run jarabe windowed inside nested Wayfire

- [x] 4.1 Launch Wayfire nested (windowed) in the current session
      **Result**: confirmed working in task 1.4 (Wayfire 0.10.1 auto-nests
      via `$WAYLAND_DISPLAY` detection).
- [x] 4.2 Launch jarabe (gtk4-port branch) with windowed-jarabe-mode
      enabled, inside that nested Wayfire instance
      **Result**: BLOCKED before reaching this point — `import
      jarabe.main` itself doesn't complete. See "Blocker found" below.
      windowed-jarabe-mode's own code (task 3) was never actually
      exercised end-to-end, since jarabe can't start at all yet,
      independent of windowed mode.
- [ ] ~~4.3 Confirm the Home View renders as a normal window~~ — not
      reached.
- [ ] ~~4.4 Observe Frame's DOCK hint behavior~~ — not reached.
- [x] 4.5 Note what breaks or is unverified — see "Blocker found" below;
      this became the main finding of this change.
- [x] 4.6 Record the exact Wayfire (and wlroots) version used
      **Result**: Wayfire 0.10.1-5.1, wf-config 0.10.0-2.1, wlroots0.19
      0.19.3-1.1 (Arch/CachyOS).

### Blocker found: jarabe (gtk4-port) cannot start independent of windowed mode

Attempting `import jarabe.main` (with `SUGAR_NO_FULLSCREEN=1`, using
`repos/sugar-toolkit-gtk4`'s venv python plus `PYTHONPATH=src`) surfaced a
chain of pre-existing integration gaps between the `gtk4-port` branch and
`sugar-toolkit-gtk4`, unrelated to Casilda/Wayfire/windowed-mode:

1. **`src/jarabe/config.py` doesn't exist** — normally Autotools-generated
   from `config.py.in` at build time; never built here. Worked around by
   hand-writing a dev-only `config.py` pointing at this checkout (see the
   file itself for the "why", flagged as dev-environment-only, not a
   real fix).
2. **`gi.require_version('SugarExt', '2.0')` — a real bug in `gtk4-port`.**
   Confirmed via `git diff origin/master origin/gtk4-port -- src/jarabe/main.py`:
   commit `b9fdeefb` ("[WIP] Port to Gtk4") changed this from the correct
   `'1.0'` to `'2.0'`. **`SugarExt-2.0` has never existed** — this looks
   like an unintentional version bump done alongside the GTK3→4 API
   migration. **Fixed in this change** (changed back to `'1.0'`) since
   it's an unambiguous bug, not a design decision.
3. **`SugarExt` (from `sugar-toolkit-gtk3`, installed via the Arch
   `sugar-toolkit-gtk3` package) is compiled against GTK3.** `jarabe`
   (gtk4-port) already loads GTK4 before importing it.
   `gi.RepositoryError: Requiring namespace 'Gtk' version '3.0', but
   '4.0' is already loaded` — **GObject Introspection cannot load two
   ABI-incompatible Gtk versions in one process.** This is a structural
   gap: SugarExt would need to be rebuilt against GTK4 for `jarabe`
   (gtk4-port) to use it at all, regardless of Casilda/Wayfire/windowed
   mode. **Worked around** for this validation only with a minimal,
   explicitly non-functional Python stub
   (`specbook/demos/sugarext_stub.py`) covering just the small subset of
   `SugarExt.*` calls still active in this branch (most call sites are
   already commented out in the code itself) — `Grid`, `CursorTracker`,
   `VolumeAlsa`, `clipboard_set_with_data`, `fat_set_hidden_attrib`.
4. **`sugar4.test.uitree` doesn't exist in `sugar-toolkit-gtk4`** (only
   used for a debug UI-tree dump). Worked around with a defensive
   try/except in `keyhandler.py` (see task 3.5-adjacent fix).
5. **`sugar4.activity.activityfactory` doesn't exist in
   `sugar-toolkit-gtk4`** (`sugar-toolkit-gtk4/src/sugar4/activity/` has
   `activity.py`, `activityhandle.py`, `activityinstance.py`,
   `bundlebuilder.py`, `widgets.py` — no `activityfactory`). This is
   needed by `jarabe/journal/journalactivity.py` to launch activities —
   **not optional/debug functionality**, unlike 1 and 4. This is where
   further workaround-stubbing stops being reasonable for this change:
   reimplementing activity-launching machinery is a substantial, separate
   effort, not a stub.

**Decision: stop here.** `windowed-jarabe-mode`'s own code (the
`SUGAR_NO_FULLSCREEN` env var, `_start_window_manager` early-return,
`HomeWindow` sizing) is implemented and believed correct by inspection,
but **could not be exercised end-to-end** because `jarabe` (gtk4-port)
doesn't start at all yet — independent of windowed mode, Wayfire, or
Casilda. The real next gap is finishing `jarabe`↔`sugar-toolkit-gtk4`
integration (activityfactory and whatever comes after it), which is
PR #1019's own unfinished-port problem, not something this change set out
to solve. See `specbook/docs/gtk-porting-standards.md` for the documented
handoff.

## 5. Documentation

- [x] 5.1 Update `specbook/docs/gtk-porting-standards.md` with: the
      Wayfire install/nested-launch procedure, the windowed-jarabe-mode
      flag/env var and how to use it, and the version numbers from 4.6
      **Result**: added "Windowed jarabe: findings (2026-07-08)" section.
- [x] 5.2 Document known limitations from 4.5 explicitly, so this reads
      as "dev aid" not "full session replacement"
      **Result**: covered — the blocker chain (config.py,
      SugarExt version bug, SugarExt/GTK3-vs-GTK4 ABI conflict, missing
      uitree, missing activityfactory) is documented in full, since it
      turned out to be the main finding rather than a footnote.
- [x] 5.3 Note the upstream angle: this change directly implements what
      sugar#929 asked for, and is a reasonable candidate to eventually
      propose upstream — not committing to that step now, just flagging it
      **Result**: noted in proposal.md's Impact section (unchanged from
      planning); the SugarExt version bug fix (2.0→1.0) is also a
      legitimate small upstream-able bugfix on its own, independent of
      windowed mode.

## 6. Verification

- [x] 6.1 From a clean shell, re-run the full documented procedure
      top to bottom to confirm reproducibility, per this workspace's
      established practice (same as `gtk4-dev-environment` task 6.1)
      **Result**: adjusted in scope — since jarabe doesn't start yet
      (blocker chain in section 4), there's no successful end-to-end
      procedure to reproduce. Instead, verified reproducibility of what
      *does* work: re-ran `python3 -m py_compile` on both edited files
      (`main.py`, `homewindow.py`) and confirmed the exact blocker
      sequence (config.py → SugarExt 2.0 → SugarExt GTK3/GTK4 ABI
      conflict → uitree → activityfactory) reproduces identically from a
      fresh `rm` of the shell.log and a clean env-var-only invocation —
      confirming the documentation in `gtk-porting-standards.md`
      accurately reflects a reproducible (if currently blocked) state,
      not a one-off session artifact.
- [x] 6.2 Run `openspec sync` (or the manual equivalent) to merge delta
      specs into `openspec/specs/`
      **Result**: created `openspec/specs/windowed-jarabe-mode/spec.md`
      and `openspec/specs/nested-wayfire-dev-session/spec.md`. Both
      updated during sync to honestly reflect that end-to-end rendering
      was not achieved — the original delta specs assumed success: see
      each spec's "Validated Implementation" section for what changed
      between the planned scenarios and the actual outcome. Both
      validated clean (`openspec validate --specs`).
- [x] 6.3 Run `openspec archive` once 6.1 passes
