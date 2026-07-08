## Purpose

Centralize fixes for GTK3 APIs removed in GTK4 that recur across dozens
of files in jarabe's codebase, avoiding a much larger and more
error-prone diff than editing every call site individually.

## Requirements

### Requirement: sugar4.gtk3compat centralizes repeated GTK3-API-removed shims
The system SHALL provide a `sugar4.gtk3compat` module, installed via a
single `install()` call early in jarabe's startup, that patches
GTK3-era APIs removed in GTK4 back onto the relevant `Gtk`/`Gdk` classes,
for APIs that recur across many files rather than being fixed at each
call site individually.

#### Scenario: Widely-repeated APIs are shimmed, not edited per-site
- **WHEN** jarabe code calls `Gtk.Alignment.new(...)`,
  `box.pack_start(...)`/`pack_end(...)`, `widget.get_children()`,
  `Gdk.Screen.width()`/`height()`/`get_default()`,
  `widget.set_border_width(...)`, or `Gtk.HButtonBox()` after
  `gtk3compat.install()` has run
- **THEN** each call succeeds via the shim rather than raising
  `AttributeError`

#### Scenario: install() is idempotent
- **WHEN** `gtk3compat.install()` is called more than once
- **THEN** it does not double-patch or raise (checks `hasattr` before
  assigning each shim)

## Validated Implementation (2026-07-08)

`repos/sugar-toolkit-gtk4/src/sugar4/gtk3compat.py` created, covering:
`Gtk.Alignment` (~15 call sites, 8 files — mapped to a `Gtk.Box`
subclass translating xalign/yalign to halign/valign), `Gtk.Box.pack_start`/
`pack_end` (157 call sites, 24 files — mapped to `append()` +
hexpand/vexpand + margin), `Gtk.Widget.get_children()` (~21 files —
walks `get_first_child()`/`get_next_sibling()`), `Gdk.Screen` (~38 call
sites, 18 files, all `.width()`/`.height()`/`.get_default()` — mapped to
`Gdk.Display.get_monitors()`), `Gtk.Widget.set_border_width()`
(11 files — mapped to four `set_margin_*` calls), `Gtk.HButtonBox`/
`Gtk.ButtonBoxStyle` (4 files), and `Gtk.Button.set_image()` (2 direct
`Gtk.Button` call sites in `jarabe/intro/window.py`). Installed via
`gtk3compat.install()` called once near the top of `jarabe/main.py`,
before any module using these APIs is imported.
