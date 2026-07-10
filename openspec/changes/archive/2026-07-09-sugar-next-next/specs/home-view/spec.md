## ADDED Requirements

### Requirement: Pluggable Home View layouts
The shell SHALL provide three built-in Home View layouts — desktop grid,
app grid, and search-first — implementing a common layout interface, and
SHALL allow additional layouts to be provided by extensions.

#### Scenario: Switching layout at runtime
- **WHEN** the learner selects a different Home View layout from Settings
- **THEN** the shell swaps the active layout without restarting

#### Scenario: Extension-provided layout
- **WHEN** an installed extension registers a layout implementing the
  Home View layout interface
- **THEN** it appears as a selectable option in Settings

### Requirement: Desktop grid layout
The desktop grid layout SHALL display app icons floating on a
user-selectable background image and SHALL support container folders
that expand into sub-grids.

#### Scenario: Opening a container folder
- **WHEN** the learner clicks a container folder icon
- **THEN** the layout expands into a sub-grid showing that folder's apps

### Requirement: App grid layout
The app grid layout SHALL display apps in a `Gtk.FlowBox` with a search
bar and no visible background image, matching the existing Fase 1
prototype behavior.

#### Scenario: Filtering apps by search
- **WHEN** the learner types in the search bar
- **THEN** the grid filters to matching apps in real time

### Requirement: Search-first layout
The search-first layout SHALL show no app icons until the learner types
in the search bar.

#### Scenario: Empty state
- **WHEN** the search-first layout is active and the search bar is empty
- **THEN** no app icons are visible

### Requirement: Settings panel
The shell SHALL provide a Settings panel accessible from the Frame or a
keybinding, exposing background image, accent color, contrast, icon size,
Home View layout, and extension management controls.

#### Scenario: Changing accent color
- **WHEN** the learner picks a new accent color in Settings
- **THEN** the shell chrome updates to use that color without restarting

### Requirement: Color token system
The shell SHALL define its chrome colors as `--sn-*` CSS custom
properties set from the system `prefers-color-scheme`, and SHALL allow
user overrides via `~/.config/sugar-next/colors.css` or the Settings
panel.

#### Scenario: User override file present
- **WHEN** `~/.config/sugar-next/colors.css` exists and defines `--sn-accent`
- **THEN** the shell uses that value instead of the computed default

### Requirement: Active-app palette tint
The shell chrome SHALL subtly tint toward the focused application's icon
palette, falling back to the static accent color when a dominant color
cannot be determined.

#### Scenario: Focus changes
- **WHEN** the learner focuses a different application window
- **THEN** the Frame and Home View background tint shift toward that
  app's icon color within a short, unobtrusive transition

### Requirement: XDG Base Directory compliance
The shell SHALL store configuration under `~/.config/sugar-next/` and
data under `~/.local/share/sugar-next/`, per the XDG Base Directory
specification.

#### Scenario: Fresh install
- **WHEN** the shell starts with no existing config or data directories
- **THEN** it creates them under the XDG-specified paths, not elsewhere

### Requirement: FreeDesktop desktop citizenship
The shell SHALL register the `org.sugarlabs.SugarNext` D-Bus name,
associate MIME types with Journal entries, and expose a
StatusNotifierItem for background services.

#### Scenario: Background service running
- **WHEN** a background service (e.g. presence bus) is active
- **THEN** a StatusNotifierItem icon is visible in the system tray
