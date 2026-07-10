# semantic-color-system Specification

## Purpose
TBD - created by archiving change color-system-and-icon-state. Update Purpose after archive.
## Requirements
### Requirement: Accent-derived palette generation
The shell SHALL derive a full `--sn-*` token set from a single
user-chosen accent color using HSL-based computation, without requiring
any color-science dependency beyond the Python standard library.

#### Scenario: Picking a new accent regenerates the palette
- **WHEN** the learner selects a new accent color in Settings
- **THEN** `--sn-accent-counter`, `--sn-bg-alt`, and `--sn-surface` are
  recomputed from the new accent and applied without restarting the
  shell

#### Scenario: Neutral tokens stay neutral
- **WHEN** any accent color is selected
- **THEN** `--sn-bg`, `--sn-text`, and `--sn-text-secondary` are not
  altered by accent derivation and retain their light/dark or
  high-contrast values

### Requirement: Accent counterpart token
The shell SHALL compute `--sn-accent-counter`, a color that is both
readable when used as text/icon color against `--sn-accent` as a
background, and visually distinguishable from `--sn-accent` as a
secondary semantic color.

#### Scenario: Counterpart contrast
- **WHEN** `--sn-accent-counter` is used as a foreground color on top of
  a `--sn-accent` background
- **THEN** the contrast is sufficient for text/icon legibility

#### Scenario: Counterpart distinguishability
- **WHEN** `--sn-accent` and `--sn-accent-counter` are shown as adjacent
  swatches
- **THEN** they are visually distinct in hue, not near-duplicates

### Requirement: Per-token manual override
The shell SHALL allow the learner to override any individual generated
token, independent of the others, and persist that override through the
existing `~/.config/sugar-next/colors.css` mechanism.

#### Scenario: Overriding one derived token
- **WHEN** the learner sets a custom value for `--sn-surface` in the
  Color tab
- **THEN** `--sn-surface` uses the custom value while
  `--sn-accent-counter` and `--sn-bg-alt` remain auto-derived

#### Scenario: Resetting an override
- **WHEN** the learner resets a previously overridden token
- **THEN** that token reverts to its accent-derived value and the
  override is removed from `colors.css`

### Requirement: Accent picker UI
The Settings Color tab SHALL provide an expanded curated swatch grid for
choosing the accent color, replacing the previous 8-swatch-plus-hex-entry
picker.

#### Scenario: Selecting from the expanded grid
- **WHEN** the learner opens the Color tab
- **THEN** they see a grid of curated accent swatches larger than the
  previous 8-color set, with the currently active accent visibly marked

