## ADDED Requirements

### Requirement: sugar4.ext provides a GTK4-usable replacement for SugarExt/SugarGestures
The system SHALL provide a `sugar4.ext` module usable in place of
`gi.repository.SugarExt`/`SugarGestures` (GTK3-compiled GObject
Introspection libraries incompatible with a GTK4 process), covering the
subset of that API jarabe's gtk4-port branch actively calls.

#### Scenario: Grid and fat_set_hidden_attrib are real, functional ports
- **WHEN** `sugar4.ext.Grid` or `sugar4.ext.fat_set_hidden_attrib` is used
- **THEN** it behaves equivalently to the original C implementation
  (verified: neither depends on X11 or GTK3-specific APIs, so no
  behavior is approximated)

#### Scenario: Non-portable functionality is an explicit, logged stub
- **WHEN** `sugar4.ext.CursorTracker`, `VolumeAlsa`, `clipboard_set_with_data`,
  or `SwipeController`/`SwipeDirectionFlags` is used
- **THEN** it logs a warning describing itself as a stub and what a real
  implementation would require (Wayland pointer protocols, PipeWire,
  `Gdk.Clipboard`/`Gdk.ContentProvider`, `Gtk.GestureSwipe` respectively)

## Validated Implementation (2026-07-08)

`repos/sugar-toolkit-gtk4/src/sugar4/ext.py` created. `Grid` (icon-grid
weight matrix) and `fat_set_hidden_attrib` (FAT filesystem hidden
attribute via Linux ioctl) are direct, real ports from
`sugar-toolkit-gtk3`'s C source — confirmed no GTK3/X11 dependency.
`CursorTracker`, `VolumeAlsa`, `clipboard_set_with_data`,
`SwipeController`/`SwipeDirectionFlags` are explicit stubs, each with a
`NOT_IMPLEMENTED` docstring naming the real GTK4/Wayland equivalent that
would need to be built. All jarabe call sites
(`jarabe/frame/clipboardicon.py`, `jarabe/journal/model.py`,
`jarabe/model/sound.py`, `jarabe/desktop/grid.py`,
`jarabe/view/launcher.py`, `jarabe/view/cursortracker.py`,
`jarabe/view/gesturehandler.py`) updated to import from `sugar4.ext`
instead of `gi.repository.SugarExt`/`SugarGestures`.
