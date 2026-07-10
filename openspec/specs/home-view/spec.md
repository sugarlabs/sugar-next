## Purpose

Define the Sugar Next Home View — its Settings panel, color/theming model,
and desktop-environment citizenship (XDG paths and FreeDesktop
integration) — so the shell's presentation layer is configurable,
themeable, and a well-behaved Linux desktop citizen. View selection
(Desktop, Apps, Search) is defined in the `frame-views` capability, not
here.
## Requirements
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

### Requirement: Color token system
The shell SHALL define its chrome colors as `--sn-*` CSS custom
properties set from the system `prefers-color-scheme`, plus tokens
derived from the user's accent color via HSL-based generation (see the
`semantic-color-system` capability), and SHALL allow user overrides —
per-token or wholesale — via `~/.config/sugar-next/colors.css` or the
Settings Color tab.

#### Scenario: User override file present
- **WHEN** `~/.config/sugar-next/colors.css` exists and defines `--sn-accent`
- **THEN** the shell uses that value instead of the computed default

#### Scenario: Accent-derived tokens follow accent changes
- **WHEN** the learner changes the accent color without any per-token
  overrides set
- **THEN** `--sn-accent-counter`, `--sn-bg-alt`, and `--sn-surface`
  update to values derived from the new accent

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

