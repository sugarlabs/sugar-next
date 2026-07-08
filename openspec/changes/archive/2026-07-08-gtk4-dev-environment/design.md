## Context

PR #1019 (`sugar` repo, `gtk4-port` branch) is a mechanical GTK3→GTK4 port
of the entire `jarabe` shell (133 files). It stalled because no one could
reliably build and run GTK4 Sugar code to test it — the author suggested
Casilda but never documented a working setup, and later contributors
(vyagh, D-I-R-M) hit the same wall.

Research into Casilda (`gitlab.gnome.org/jpu/casilda`, LGPL-2.1, C,
built on wlroots + GTK4) found it is **narrower** than the PR discussion
implied:

- It's a `GtkWidget` subclass (`CasildaCompositor`) you embed in your own
  GTK4 app — not a standalone binary or a general nested-session host.
- It hosts exactly one embedded Wayland client surface per compositor
  instance (its one documented real-world use is Cambalache's live
  workspace preview pane).
- It has **no layer-shell support, no window-manager/session protocols,
  no multi-surface management**. `jarabe` expects to *be* the
  window-managing shell — launching activities, arranging their windows.
  Casilda has no API surface for that today.
- Build is Meson/Ninja; no PyGObject/GI typelib is documented, so
  Python-side (PyGObject) usage is unverified — all documented usage is C.

Meanwhile `sugar-toolkit-gtk4` (separate repo) is a from-scratch GTK4
toolkit reimplementation with modern Python tooling (`pip install -e .`,
`make test`), and is the most actively maintained repo in the Sugar org.
It doesn't depend on Casilda or on `jarabe` — it's just PyGObject/GTK4
widgets.

## Goals / Non-Goals

**Goals:**
- Get a real, working build of Casilda from source on this machine,
  proving the wlroots + GTK4 + Meson toolchain functions here.
- Get a real, working build of `sugar-toolkit-gtk4`, with `make test`
  passing, proving the toolkit itself is sound in isolation.
- Produce one minimal integration: a GTK4 host window with an embedded
  `CasildaCompositor`, displaying a small `sugar-toolkit-gtk4`-based test
  widget as the embedded client. This is the smallest possible proof that
  these two pieces can be wired together at all.
- Document the whole thing so it's reproducible by someone else — closing
  the exact gap that stalled PR #1019.

**Non-Goals:**
- Running `jarabe` (the full shell) inside Casilda. That needs
  window-management capabilities Casilda doesn't have. Explicitly deferred
  to a future change, once (a) this toolchain is proven and (b) either
  Casilda gains that capability, or a different approach is chosen for the
  shell specifically (e.g. a full nested compositor like `cage` run
  full-screen instead of embedded, or continuing to test via a dedicated
  X11/Wayland session as today).
- Touching the `gtk4-port` branch of `sugar` itself. Not part of this
  change.
- Making PyGObject bindings for Casilda if none exist — if the C-only API
  turns out to block even the minimal demo, the fallback (see Risks) is to
  spawn the `sugar-toolkit-gtk4` test widget as a separate process
  connected via `WAYLAND_DISPLAY` pointed at Casilda's socket, rather than
  in-process GObject Introspection calls.

## Decisions

**D1 — Scope to a single embedded widget, not the shell.**
Rationale: matches what Casilda actually supports today (see Context).
Attempting the full shell first would repeat PR #1019's failure mode —
committing to a large integration before validating the toolchain works
at all. Alternative considered: skip Casilda entirely and use a classic
nested X11 approach (Xephyr) with the GTK3 `master` branch as a safer
baseline. Rejected for *this* change because the user's explicit goal is
the GTK4 track; the Xephyr/GTK3 path remains available as a fallback if
Casilda integration turns out to be a dead end (see Risks).

**D2 — Build everything from source into `repos/`, no system-wide
installs without confirmation.**
Rationale: consistent with `specbook/docs/base-standards.md` and the
`setup-sugar-workspace` skill's existing posture — this workspace doesn't
silently write to system directories. Casilda's `ninja -C _build install`
defaults to a system prefix; this change uses a user-local prefix
(`--prefix=~/.local` or equivalent) instead, avoiding `sudo` entirely for
this experiment.

**D3 — Validate Casilda and sugar-toolkit-gtk4 independently before
integrating.**
Rationale: isolates failure. If the combined demo doesn't work, we need
to already know whether Casilda alone works, and whether the toolkit
alone works, to know which side to debug. This directly follows from the
`base-standards.md` "small changes" rule applied to a spike/experiment
rather than a feature.

## Risks / Trade-offs

- **[Risk] Casilda has no documented PyGObject bindings — the embedded
  client demo may not be buildable in Python at all.**
  → Mitigation: fall back to a two-process approach — run
  `sugar-toolkit-gtk4`'s test widget as a normal Wayland client process
  with `WAYLAND_DISPLAY` pointed at Casilda's socket (Casilda exposes a
  socket path via its constructor), rather than requiring in-process C/
  Python interop. Document whichever approach actually works.

- **[Risk] wlroots version/ABI mismatches with the installed GTK4 /
  distro packages** (common failure mode for wlroots-based projects on
  rolling-release distros). → Mitigation: record exact dependency
  versions that work in `specbook/docs/gtk-porting-standards.md` once
  found; treat a clean build as the acceptance bar, not a specific
  version pin.

- **[Risk] The "minimal embedded widget" demo succeeds but tells us
  nothing about whether `jarabe`-the-shell can ever run this way**,
  giving false confidence. → Mitigation: the design and proposal
  explicitly scope this as toolchain validation, not shell-readiness: the
  written docs must say plainly that shell-level integration is unproven
  and separately scoped.

- **[Trade-off] Time spent on Casilda specifically vs. just documenting
  the Xephyr/X11 fallback for the GTK3 master branch.** Accepted per the
  user's explicit choice to pursue the GTK4/Casilda track first; the
  Xephyr fallback is noted as available, not pursued now.

## Migration Plan

Not applicable in the deploy/rollback sense — this is a new local dev
environment setup, not a change to shipped code. "Rollback" is simply: the
demo app and cloned repos live under `repos/` and can be deleted without
affecting anything else in the workspace.

## Open Questions (resolved during implementation)

- ~~Does Casilda's socket-based embedding actually work with a Python/
  PyGObject client process, or only C clients?~~ **Resolved: yes.**
  Casilda ships full GObject Introspection bindings and its own
  `examples/compositor.py` demo is pure Python. The in-process embedding
  path (`compositor.spawn_async(...)` called directly from Python) works
  without needing the two-process/`WAYLAND_DISPLAY` fallback anticipated
  in the Risks section above.
- ~~What's the minimal `sugar-toolkit-gtk4` widget worth using as the test
  client?~~ **Resolved:** reused `examples/basic_activity.py`
  (a `SimpleActivity` subclass) rather than writing a new one.
