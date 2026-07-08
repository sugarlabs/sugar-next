## Why

Resuming Sugar's GTK4 modernization requires a working, reproducible way to
build and see GTK4 Sugar code running on a modern Linux laptop. This has
never existed: [PR #1019](https://github.com/sugarlabs/sugar/pull/1019)
(the `gtk4-port` branch) stalled for months not on code review, but because
every contributor who tried to pick it up hit the same wall — there was no
documented way to actually run and test GTK4 Sugar code. The author
suggested Casilda (a GNOME Wayland-compositor-in-a-widget) as a testing
approach but never documented how, and no one since has made it work.

Research for this change (see `design.md`) found that Casilda is narrower
than assumed: it's a GTK4 widget (`CasildaCompositor`) that embeds ONE
Wayland client surface inside itself — not a general nested-session host
capable of running a whole window-managing shell like `jarabe`. Attempting
the full shell first would repeat the exact mistake that stalled PR #1019:
committing to a large, unvalidated goal before the toolchain is even known
to work.

This change scopes down deliberately: get the build toolchain
(meson + wlroots + GTK4 + `sugar-toolkit-gtk4`) working end-to-end by
running a single `sugar-toolkit-gtk4` widget embedded in a Casilda-hosted
window. That validates every moving part except shell-level window
management, which is called out explicitly as unsolved and left for a
follow-up change.

## What Changes

- Clone `sugar-toolkit-gtk4` and Casilda into `repos/` as part of this
  workspace.
- Build Casilda from source (Meson/Ninja) and confirm its example/demo
  runs on this machine (validates wlroots + GTK4 + graphics stack).
- Build `sugar-toolkit-gtk4` (`pip install -e .`) and confirm `make test`
  passes, so we know the toolkit itself is sound before integrating it
  with anything else.
- Write a minimal host application that embeds a `CasildaCompositor`
  widget in a GTK4 window and spawns a small `sugar-toolkit-gtk4`-based
  test widget/client as the embedded surface.
- Document the full working setup (dependencies, build commands, run
  commands) in `specbook/docs/gtk-porting-standards.md`, replacing the
  current "undocumented gap" note with an actual procedure.
- Explicitly document what this does NOT achieve: running `jarabe` (the
  full shell) itself — that requires window-management/layer-shell
  capabilities Casilda doesn't provide, and is out of scope here.

## Capabilities

### New Capabilities

- `gtk4-toolchain-validation`: a reproducible local build of Casilda and
  `sugar-toolkit-gtk4` from source, with passing tests, proving the
  underlying toolchain (Meson, wlroots, GTK4, Python packaging) works on a
  modern Linux laptop.
- `casilda-embedded-widget-demo`: a minimal working demo — a GTK4 host
  window using `CasildaCompositor` to display one `sugar-toolkit-gtk4`
  widget/client running as the embedded Wayland surface.

### Modified Capabilities

(none — no existing specs yet; this is the first change in this workspace)

## Impact

- **New repos cloned**: `sugar-toolkit-gtk4`, `casilda` (from
  `gitlab.gnome.org/jpu/casilda`), added under `repos/`.
- **New system dependencies**: Meson, Ninja, wlroots (+ dev headers), GTK4
  (+ dev headers) — none of these are installed yet; installation commands
  must be surfaced to the user for confirmation, not run silently, per
  `specbook/docs/base-standards.md`.
- **Docs updated**: `specbook/docs/gtk-porting-standards.md` gets a real
  "how to run GTK4 Sugar code" section once this lands.
- **No changes** to `sugar` (jarabe shell) itself in this change — the
  `gtk4-port` branch is not touched yet. That's explicitly future work,
  once this toolchain is proven.
