## Purpose

Prove that a `sugar-toolkit-gtk4` activity can render embedded inside a
Casilda-hosted GTK4 window, as the smallest possible validation step
before ever attempting to run the full `jarabe` shell this way.

## Requirements

### Requirement: A sugar-toolkit-gtk4 widget renders inside a Casilda-hosted window
The system SHALL provide a minimal demo application in which a GTK4 host
window embeds a `CasildaCompositor` widget, and a small
`sugar-toolkit-gtk4`-based client renders as the embedded Wayland surface
inside that window.

#### Scenario: Demo runs and displays the embedded widget
- **WHEN** a developer runs the documented demo launch command
- **THEN** a GTK4 window opens showing the `sugar-toolkit-gtk4` test
  widget rendered inside the Casilda-hosted area, with no manual
  intervention beyond the documented steps

#### Scenario: Client connection method is documented, whichever works
- **WHEN** the demo is implemented
- **THEN** the docs state explicitly whether the embedded client connects
  via in-process GObject Introspection calls or as a separate process
  pointed at Casilda's Wayland socket (`WAYLAND_DISPLAY`) — whichever
  approach was actually made to work

### Requirement: Shell-level scope is explicitly disclaimed
The system SHALL make clear, in the delivered documentation, that this
demo validates only the build/embedding toolchain — not the feasibility
of running the full `jarabe` shell inside Casilda.

#### Scenario: Docs state the boundary
- **WHEN** `specbook/docs/gtk-porting-standards.md` is updated with this
  change's results
- **THEN** it explicitly states that running the full shell (with its own
  window management) inside Casilda remains unproven and is out of scope

## Validated Implementation (2026-07-08)

`specbook/demos/casilda_sugar_demo.py` embeds
`repos/sugar-toolkit-gtk4/examples/basic_activity.py` (a `SimpleActivity`
subclass) inside a `Casilda.Compositor()` widget. **In-process GObject
Introspection embedding worked directly** — Casilda ships a full GI
typelib and its own upstream example (`compositor.py`) is pure Python, so
no two-process/`WAYLAND_DISPLAY` fallback was needed (this corrects an
assumption in the original design that only a C API was documented).

`SimpleActivity`-based clients require `SUGAR_BUNDLE_PATH`,
`SUGAR_BUNDLE_NAME`, `SUGAR_BUNDLE_ID` env vars (passed via
`spawn_async`'s `envp` parameter) since they expect to be launched as a
Sugar bundle, not as a bare script.

Shell-level (`jarabe`) integration remains explicitly unproven — Casilda
has no layer-shell or window-manager protocol support, and `jarabe`
expects to be the window-managing compositor itself. See
`specbook/docs/gtk-porting-standards.md` "Out of scope for now".
