## ADDED Requirements

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
  approach was actually made to work, per the design's D1/fallback risk

### Requirement: Shell-level scope is explicitly disclaimed
The system SHALL make clear, in the delivered documentation, that this
demo validates only the build/embedding toolchain — not the feasibility
of running the full `jarabe` shell inside Casilda.

#### Scenario: Docs state the boundary
- **WHEN** `specbook/docs/gtk-porting-standards.md` is updated with this
  change's results
- **THEN** it explicitly states that running the full shell (with its own
  window management) inside Casilda remains unproven and is out of scope
  for this change
