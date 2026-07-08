## Why

The previous change (`windowed-jarabe`, archived) implemented an opt-in
windowed mode for jarabe but stopped because `jarabe` (gtk4-port branch)
didn't start at all — a chain of missing modules and a GTK3/GTK4 ABI
conflict in `SugarExt` blocked even `import jarabe.main`.

This change completes that integration: ports the missing pieces into
`sugar-toolkit-gtk4`, fixes roughly a dozen distinct categories of
GTK3-API-removed-in-GTK4 bugs across the `sugar` (gtk4-port) codebase,
and — critically — finds and fixes the actual root cause of why every
shell window rendered as a blank gray box once the code did start
running: `ShellModel.add_window()` unconditionally replaced every
window's content with an empty Casilda compositor before adding it.

With that fixed, jarabe's onboarding/intro screen (name/color/gender/age
entry) now renders with real, visible content inside a nested Wayfire
session — confirmed visually. This is the first time in this
workspace's investigation (and likely the first time since PR #1019 was
opened) that the GTK4 port has been observed actually running.

## What Changes

- **`sugar-toolkit-gtk4`**: add `sugar4/ext.py` (pure-Python replacement
  for `SugarExt`/`SugarGestures` — real ports of what's portable, explicit
  non-functional stubs for what isn't), `sugar4/gtk3compat.py` (shims for
  ~7 categories of removed GTK3 API, installed via `gtk3compat.install()`),
  `sugar4/activity/activityfactory.py` and `sugar4/activity/i18n.py`
  (direct namespace ports, no GTK3/X11 dependency). Add a `set_image()`
  method to `sugar4/graphics/menuitem.py`'s `MenuItem` for GTK3-style
  post-construction icon setting.
- **`sugar` (gtk4-port branch)**: fix the `SugarExt` version bug
  (`'2.0'` → `'1.0'`), the missing `from gi.repository import Casilda`
  import, the `window.__name__`/`get__type_hint` typos, and — the actual
  blocker — `ShellModel.add_window()`'s unconditional
  `window.set_child(self.compositor)`. Fix ~10 classes inheriting from
  removed GTK3 widgets (`Gtk.EventBox`, `Gtk.Bin`, `Gtk.Toolbar`) to use
  `Gtk.Box` instead. Fix positional-argument GTK3 constructor calls,
  removed enum members, renamed methods, and GTK3-only signals
  (`'button-press-event'`, `'key-press-event'`) across ~20 files.
  Disable (not redesign) `get_type_hint()`-based activity-window tracking
  in `_window_added_cb`/`_window_removed_cb`, since GTK4 has no
  equivalent and a real replacement needs its own design.
- **Docs**: `specbook/docs/gtk-porting-standards.md` gets a full account
  of the blocker chain, the working procedure, and explicit known
  limitations (Home View/Frame/Journal unverified; activity-window
  tracking disabled; icon layout is a plain-box-packing stub, not the
  real circular/delegated layout; no Sugar-specific GTK4 theme exists
  yet).

**BREAKING**: none — all changes are either opt-in (`SUGAR_NO_FULLSCREEN`,
from the prior change) or fix code that didn't work at all before.

## Capabilities

### New Capabilities

- `jarabe-gtk4-integration`: jarabe (gtk4-port branch) successfully
  imports, initializes, and renders its onboarding UI when run against
  `sugar-toolkit-gtk4` in a nested Wayfire session — the toolkit
  integration and the ~20-file GTK3-API-removal fixes that make this
  possible.
- `sugar4-ext-module`: a pure-Python `sugar4.ext` module replacing
  `SugarExt`/`SugarGestures` for GTK4 consumers, with real ports where
  portable and explicit stubs where not.
- `sugar4-gtk3compat-module`: a centralized compatibility-shim module
  (`sugar4.gtk3compat`) covering GTK3 APIs removed in GTK4
  (`Gtk.Alignment`, `pack_start`/`pack_end`, `get_children`, `Gdk.Screen`,
  `set_border_width`, `Gtk.HButtonBox`) that would otherwise require
  editing dozens of call sites individually.

### Modified Capabilities

- `windowed-jarabe-mode`: no requirement changes, but its "not verified
  end-to-end" caveat from the prior change is now resolved — the
  windowed-mode code IS exercised end-to-end successfully.
- `nested-wayfire-dev-session`: the "jarabe cannot be validated running
  inside it" finding from the prior change is superseded — it now runs
  and renders successfully.

## Impact

- **Code changed**: `repos/sugar` (gtk4-port branch, ~20 files) and
  `repos/sugar-toolkit-gtk4` (5 new/modified files).
- **No new system dependencies** beyond what `gtk4-dev-environment` and
  the prior `windowed-jarabe` change already required (Wayfire,
  `sugar-toolkit-gtk3` for the compiled `SugarExt`, `python-gwebsockets`
  for `apisocket.py`, plus a compiled `org.sugarlabs` GSettings schema in
  `~/.local/share/glib-2.0/schemas`).
- **Docs updated**: `specbook/docs/gtk-porting-standards.md` (major
  rewrite of the "Windowed jarabe" section), `specbook/docs/sugar-stack.md`
  (repo/package inventory).
- **Explicitly not done**: Home View/Frame/Journal validation, real
  activity-window tracking, real icon layout (SnowflakeLayout/
  ViewContainer), Sugar GTK4 theme — all flagged as follow-up work.
