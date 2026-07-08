## Context

The prior change (`windowed-jarabe`) stopped at a chain of import-time
failures (missing `config.py`, a real `SugarExt` version bug, then a
structural GTK3/GTK4 ABI conflict in `SugarExt` itself, then a missing
`activityfactory` module). The user's direction at that point: "busca en
los repos de sugar si hay alguna reimplementacion o port sino haz la más
basica que puedas" — search for existing reimplementations first, then
do the most basic port/stub possible.

Research found no existing GTK4 port of `SugarExt` in any branch of
`sugar-toolkit-gtk3`, `sugar-toolkit-gtk4`, or `sugar`. Analysis of
`SugarExt`'s actual C source (`sugar-toolkit-gtk3/src/sugar3/*.c`) showed
its 5 actively-used functions split cleanly: `Grid` (pure weight-matrix
arithmetic) and `fat_set_hidden_attrib` (plain Linux ioctl) have zero
GTK3/X11 dependency and are directly portable; `CursorTracker` (raw X11
XInput2 events + XFixes) and the clipboard helper (GTK3 `GtkClipboard`
API) have no direct Wayland/GTK4 equivalent and need real design work.

## Goals / Non-Goals

**Goals:**
- Get `jarabe` (gtk4-port) importing and running against
  `sugar-toolkit-gtk4` without any `sudo`-installed system-wide `sugar`
  package.
- Fix every bug that blocks import/startup, distinguishing real
  `gtk4-port` bugs (fix directly) from missing functionality that
  legitimately can't be ported mechanically (stub explicitly, log on
  use, never fake success).
- Get at least one real screen (whatever `jarabe` shows first) rendering
  with visible content, not a blank window.

**Non-Goals:**
- A complete, pixel-correct GTK4 port of `jarabe`. This is triage to get
  something running, following the same "small changes, don't guess at
  unclear intent" discipline as the prior change.
- Designing the real replacements for stubbed functionality (Wayland
  cursor/clipboard APIs, `Gtk.LayoutManager`-based icon layout,
  activity-window role tracking). Each is flagged as its own future
  change.
- Validating the Home View, Frame, or Journal — only whatever startup
  path is reached (which turned out to be the onboarding/intro screen,
  since no Sugar profile exists on this host) is validated.
- A Sugar-specific GTK4 visual theme. The existing `sugar-72`/`sugar-100`
  GTK3 themes don't apply to GTK4's theming model at all; jarabe renders
  with the host's default GTK4 theme.

## Decisions

**D1 — Port what's mechanically portable; stub the rest explicitly,
never silently.**
Directly from the user's instruction. Applied consistently: `Grid` and
`fat_set_hidden_attrib` in `sugar4/ext.py` are real, tested-by-running
ports. `CursorTracker`, `VolumeAlsa`, `clipboard_set_with_data`,
`SwipeController` are stubs that log a warning on use and are documented
with a `NOT_IMPLEMENTED` docstring explaining exactly what real
implementation would require (Wayland pointer-constraints protocols,
`Gdk.Clipboard`/`Gdk.ContentProvider`, PipeWire, `Gtk.GestureSwipe`
respectively).

**D2 — Centralize repeated GTK3-API-removed shims in one module
(`sugar4.gtk3compat`) rather than editing every call site.**
Several removed APIs (`Gtk.Alignment`, `pack_start`/`pack_end`,
`get_children`, `Gdk.Screen`) each appear dozens of times across the
`jarabe` codebase (up to 157 occurrences in 24 files for
`pack_start`/`pack_end`). Editing each site individually would be a much
larger, more error-prone diff than installing a monkey-patched
compatibility shim once at startup. This mirrors the same "small,
centralized fix over many scattered edits" reasoning as `SugarExt`
itself. Rejected alternative: editing every call site to native GTK4
idioms (`append()`, `halign`/`valign`, etc.) — correct long-term, but a
much larger and riskier change than this triage pass intends.

**D3 — Fix classes with a small, easily-verified surface directly;
reserve shims for widely-repeated patterns.**
`Gtk.EventBox`/`Gtk.Bin` base-class swaps (~10 classes) and one-off API
renames (`Gdk.ModifierType.MOD1_MASK` → `.ALT_MASK`,
`Gdk.Seat.get_slaves` → `.get_devices`, etc.) were fixed directly in
each file rather than shimmed, since each occurs only once or twice and
a shim would add more indirection than it saves.

**D4 — When a widget implements a whole removed protocol
(`Gtk.Container`'s `do_realize`/`do_size_allocate`/etc.), stub the
public interface, don't attempt the protocol port.**
`SnowflakeLayout` and `ViewContainer` implement custom icon-layout logic
via the full GTK3 container-implementation protocol, which GTK4 replaces
with an entirely different API (`Gtk.LayoutManager`). Porting the actual
circular/delegated-layout math to that new API is real layout-design
work. Instead, both were reduced to plain `Gtk.Box` subclasses that keep
the same public methods (`add_icon()`, `remove()`, `set_layout()`) their
callers use, with insertion-order box packing instead of the original
positioning — visually wrong, but keeps the calling code (and the
overall import/render path) working.

**D5 — Root-cause the "blank window" symptom by bisection, not by
guessing.**
When `jarabe` first ran without crashing but rendered as a blank gray
box, the investigation didn't guess at CSS/theming causes — it
progressively isolated: real `IntroWindow` class alone (worked), real
`_IntroBox` alone (worked), `Casilda.Compositor()` alongside a plain
`Gtk.Application` (worked), and finally the real `ShellModel.add_window()`
(reproduced the bug). This found the actual root cause
(`window.set_child(self.compositor)` unconditionally overwriting real
window content) in a few isolated tests rather than an open-ended
CSS/theme investigation that might never have found it.

## Risks / Trade-offs

- **[Risk] The `ShellModel.add_window()` fix (`if window.get_child() is
  None`) is a heuristic, not a real design.** If a future activity window
  is created *without* setting its own child first (relying on
  `add_window()` to supply the compositor, as the original code seems to
  have intended), this fix would silently do nothing instead of hosting
  the compositor. → Mitigation: documented explicitly in
  `gtk-porting-standards.md` and in the fix's own comment; flagged as
  needing a real window-role-based design, not left as if it were
  correct.

- **[Risk] Disabling `_window_added_cb`/`_window_removed_cb`'s
  `get_type_hint()`-based logic (`if False:`) means activity-window
  registration is untested and likely broken.** Any future work
  exercising the Home View/Journal will hit this immediately.
  → Mitigation: explicitly called out as a known limitation, not
  discovered fresh by whoever picks this up next.

- **[Risk] The `gtk3compat` shims are approximations, not exact GTK3
  semantics** (e.g. `pack_start`'s `fill` parameter is dropped entirely;
  `Gtk.Alignment`'s xscale/yscale are ignored). Visual layout produced
  by these shims will differ from what GTK3 rendered, in ways not fully
  characterized. → Mitigation: each shim's docstring states exactly what
  it does and doesn't preserve; acceptable for the "get it running"
  triage goal of this change, not appropriate to treat as a finished
  port.

- **[Trade-off] Time spent stubbing `SnowflakeLayout`/`ViewContainer`
  rather than attempting a real `Gtk.LayoutManager` port.** Accepted:
  those are substantial, separable pieces of work, and getting jarabe to
  render *something* first is more valuable than blocking on a correct
  icon-layout implementation before any visual validation was possible.

## Migration Plan

Not applicable in the deploy/rollback sense — this is local development
code in an unreleased branch (`gtk4-port`), not shipped functionality.
"Rollback" is simply reverting the specific commits in `repos/sugar` and
`repos/sugar-toolkit-gtk4` if a future contributor prefers a different
approach to any of the stubbed pieces.

## Open Questions

- Should `sugar4.ext`'s stubs (`CursorTracker`, clipboard, `VolumeAlsa`,
  `SwipeController`) eventually move into `sugar-toolkit-gtk4` proper as
  first-class (if still-stubbed) API surface, or stay workspace-local?
  Leaning toward upstreaming once real implementations exist for at
  least one of them, to avoid diverging further from what
  `sugar-toolkit-gtk4` itself should eventually provide.
- Is `gtk3compat`'s monkey-patching approach (mutating `Gtk`/`Gdk`
  module namespaces at runtime) acceptable for eventual upstream
  contribution, or would maintainers prefer explicit call-site fixes
  despite the larger diff? Worth raising if/when this work is proposed
  upstream.
