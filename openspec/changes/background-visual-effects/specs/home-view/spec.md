## MODIFIED Requirements

### Requirement: Settings panel
The shell SHALL provide a Settings panel accessible from the Frame or a
keybinding, exposing background image, background brightness, contrast,
saturation, and vignette, accent color, icon size, and extension
management controls.

#### Scenario: Changing accent color
- **WHEN** the learner picks a new accent color in Settings
- **THEN** the shell chrome updates to use that color without restarting

#### Scenario: Adjusting background saturation
- **WHEN** the learner moves the Saturation slider toward zero
- **THEN** the Desktop background image desaturates toward greyscale
  live, without restarting the shell

#### Scenario: Adjusting background vignette
- **WHEN** the learner increases the Vignette slider
- **THEN** the Desktop background darkens progressively toward the
  screen edges, live, without restarting the shell

#### Scenario: Effects persist across restart
- **WHEN** the learner sets a non-default saturation or vignette value
  and restarts the shell
- **THEN** the same values are restored and applied to the background
