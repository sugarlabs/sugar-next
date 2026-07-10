## MODIFIED Requirements

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
