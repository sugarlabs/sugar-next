## ADDED Requirements

### Requirement: Shared open-app tracking
The shell SHALL maintain a single, shared registry of currently-open
application ids in `main.py`, replacing per-view private tracking such
as the Frame's `_running_ids`.

#### Scenario: Frame, pie menu, and app grid see the same open set
- **WHEN** an application opens a toplevel window
- **THEN** the Frame, the Desktop pie menu, and the Apps grid all
  observe that app id as open, sourced from the same registry

#### Scenario: App closes
- **WHEN** an application's last toplevel window closes (or its process
  exits, on compositors without toplevel tracking)
- **THEN** the registry removes that app id and all subscribed views
  update

### Requirement: Focused-app tracking where available
On compositors exposing the wlroots `zwlr_foreign_toplevel_manager_v1`
`activated` state (with the optional `pywayland` dependency installed),
the shell SHALL track which single app id currently holds focus.

#### Scenario: Focus changes between two open apps
- **WHEN** the learner switches focus from App A to App B, both already
  open
- **THEN** the registry's focused app id updates from A to B without
  either app leaving the open set

#### Scenario: No focus protocol available
- **WHEN** the compositor does not support the wlroots toplevel
  management protocol, or `pywayland` is not installed
- **THEN** the registry's focused app id remains `None` at all times,
  and the shell does not guess focus from the open set

### Requirement: Icon saturation reflects app state
Application icons in the Desktop pie menu and the Apps grid SHALL render
in greyscale when the app is not open, in normal color when the app is
open, and with a full-saturation highlight when the app is focused.

#### Scenario: Closed app icon
- **WHEN** an app has no entry in the registry's open set
- **THEN** its icon renders desaturated (greyscale)

#### Scenario: Open, unfocused app icon
- **WHEN** an app is in the open set and is not the focused app id
- **THEN** its icon renders in normal color

#### Scenario: Focused app icon
- **WHEN** an app id matches the registry's focused app id
- **THEN** its icon renders with a full-saturation highlight
  distinguishing it from other open apps

#### Scenario: Two-state fallback without focus data
- **WHEN** the registry's focused app id is always `None` (no focus
  protocol available)
- **THEN** icons only ever render greyscale (closed) or normal color
  (open); no icon receives the full-saturation focused treatment
