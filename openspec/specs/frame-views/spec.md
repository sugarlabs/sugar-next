## Purpose

Define Frame-based view switching between Desktop and Apps — the
top-level ways of seeing the system, navigated via the Frame (not via a
Settings layout selector). Layouts are a low-level widget concern;
choosing between fundamentally different ways of seeing your system is a
navigation concern, as in Sugar classic's four views (Neighborhood,
Groups, Home, Activity). F3 is reserved for a future Groups/Neighborhood
view; the earlier Search view was retired in favor of putting favorites
directly on the Desktop (see the `desktop-pie-menu` change).
## Requirements
### Requirement: Views accessible from the Frame

The shell SHALL provide two views — Desktop, Apps — accessible from the
Frame (overlay bar at screen bottom / F6), NOT from Settings. The Frame
SHALL show a view switcher alongside running windows. The Frame's
running-windows list SHALL be sourced from the shared app-state registry
(see `app-state-registry` capability) rather than private per-Frame
tracking.

#### Scenario: Switching from Desktop to Apps view
- **WHEN** the learner presses F6 (Frame) and selects the "Apps" button
- **THEN** the shell switches to the App Grid view. The Frame closes.
  The same view is active next time the Frame is opened.

#### Scenario: Frame shows running windows AND view switcher
- **WHEN** the Frame opens (F6 or hot corner)
- **THEN** it shows: [Desktop] [Apps] buttons on the left, running
  windows on the right. Favorites and Settings live in the Desktop pie
  menu, not the Frame.

#### Scenario: Running list reflects the shared registry
- **WHEN** an app opens or closes and the app-state registry updates
- **THEN** the Frame's running-windows list updates to match, without
  maintaining its own separate open/closed bookkeeping

### Requirement: Settings loses layout selector

The Settings panel SHALL NOT include a Home View layout selector. The
learner changes views through the Frame, never through a configuration
panel.

#### Scenario: Settings no longer shows layout option
- **WHEN** the learner opens Settings
- **THEN** the Background, Accent color, Contrast, Extensions, and About
  sections are present, but there is no layout selector

### Requirement: Each view remembers its state

Each view SHALL preserve its scroll position, search text, and filter
state when the learner switches away and back.

#### Scenario: Switching views preserves scroll
- **WHEN** the learner scrolls down in Apps view, switches to Desktop,
  then switches back to Apps
- **THEN** the Apps view shows the same scroll position as before

### Requirement: Desktop view is the pie menu

The Desktop view (F1 as direct keybinding) SHALL display the learner's
pinned favorites as a radial pie menu, floating on the user's chosen
background image. The pie menu's center button SHALL open Settings.

#### Scenario: Desktop background
- **WHEN** the learner has set a background image in Settings
- **THEN** the Desktop view shows the pie menu over that image

#### Scenario: Empty Desktop with no favorites
- **WHEN** no apps have been pinned yet
- **THEN** the Desktop view shows a message pointing the learner to the
  Apps view to pin apps, and the Settings center button

#### Scenario: Settings opens from the pie menu center
- **WHEN** the learner clicks the pie menu's center button
- **THEN** the Settings panel opens

### Requirement: Apps view is the grid

The Apps view (F2 direct keybinding) SHALL display the App Grid
(Gtk.FlowBox with search bar, no background image). Pinning an app from
this view SHALL add it to the Desktop pie menu.

#### Scenario: Apps filtered by search
- **WHEN** the learner types in the search bar in Apps view
- **THEN** the grid filters in real time

#### Scenario: Pinning sends a favorite to the pie menu
- **WHEN** the learner pins an app from the Apps view
- **THEN** it appears as a petal in the Desktop pie menu

### Requirement: Default view on first start

The shell SHALL start in Desktop view on first launch. Returning learners
see the last active view (persisted in config).

#### Scenario: First launch
- **WHEN** the shell starts for the first time
- **THEN** Desktop view is shown

#### Scenario: Subsequent launch
- **WHEN** the shell starts and a view was previously selected
- **THEN** that same view is shown

