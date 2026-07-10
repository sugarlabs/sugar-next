## MODIFIED Requirements

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
