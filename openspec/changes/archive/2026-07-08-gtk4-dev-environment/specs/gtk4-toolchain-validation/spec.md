## ADDED Requirements

### Requirement: Casilda builds from source
The system SHALL provide a documented, reproducible procedure to build
Casilda from source using Meson/Ninja into a user-local prefix, without
requiring `sudo` or writing to system directories.

#### Scenario: Clean build succeeds
- **WHEN** a developer clones `casilda` into `repos/casilda` and runs the
  documented `meson setup` + `ninja install` commands with a user-local
  prefix
- **THEN** the build completes without errors and produces an installed
  library/demo under the user-local prefix

#### Scenario: Missing system dependency is surfaced clearly
- **WHEN** a required system dependency (wlroots dev headers, GTK4 dev
  headers, Meson, Ninja) is missing
- **THEN** the documented procedure names the exact package(s) to install
  per common distro (at least Arch/CachyOS, since that's this workspace's
  host) rather than leaving the developer to decode a raw Meson error

### Requirement: sugar-toolkit-gtk4 builds and tests pass
The system SHALL provide a documented, reproducible procedure to install
`sugar-toolkit-gtk4` in editable mode and run its test suite successfully.

#### Scenario: Editable install and test pass
- **WHEN** a developer clones `sugar-toolkit-gtk4` into
  `repos/sugar-toolkit-gtk4` and runs `pip install -e .` followed by
  `make test`
- **THEN** the install succeeds and the test suite passes (or any failures
  are pre-existing upstream issues, not caused by this environment setup)

### Requirement: Toolchain versions are recorded
The system SHALL record the exact dependency versions (Meson, wlroots,
GTK4, Python) that produced a successful build, so the setup is
reproducible on another machine.

#### Scenario: Versions written to docs
- **WHEN** the toolchain validation succeeds on this workspace's host
- **THEN** `specbook/docs/gtk-porting-standards.md` is updated with the
  working version set and the commands used
