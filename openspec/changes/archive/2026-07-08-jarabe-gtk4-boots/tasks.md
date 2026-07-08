## 1. Port missing sugar-toolkit-gtk4 modules

- [x] 1.1 Write `sugar4/ext.py`: real ports of `Grid` and
      `fat_set_hidden_attrib`; explicit stubs for `CursorTracker`,
      `VolumeAlsa`, `clipboard_set_with_data`,
      `SwipeController`/`SwipeDirectionFlags`
- [x] 1.2 Write `sugar4/activity/activityfactory.py` (direct namespace
      port from `sugar-toolkit-gtk3`)
- [x] 1.3 Write `sugar4/activity/i18n.py` (direct namespace port)
- [x] 1.4 Add `set_image()` to `sugar4/graphics/menuitem.py`'s
      `MenuItem` for GTK3-style post-construction icon setting

## 2. Write the centralized GTK3-compat shim module

- [x] 2.1 Write `sugar4/gtk3compat.py`: `Gtk.Alignment`,
      `Gtk.Box.pack_start`/`pack_end`, `Gtk.Widget.get_children()`,
      `Gdk.Screen`, `Gtk.Widget.set_border_width()`,
      `Gtk.HButtonBox`/`Gtk.ButtonBoxStyle`, `Gtk.Button.set_image()`
- [x] 2.2 Call `gtk3compat.install()` early in `jarabe/main.py`, before
      any module using these APIs is imported

## 3. Fix real bugs and update imports in repos/sugar (gtk4-port)

- [x] 3.1 Fix `SugarExt` version string bug (`'2.0'` → `'1.0'`) in
      `main.py`
- [x] 3.2 Update `SugarExt`/`SugarGestures` imports to `sugar4.ext` in
      `clipboardicon.py`, `journal/model.py`, `model/sound.py`,
      `desktop/grid.py`, `view/launcher.py`, `view/cursortracker.py`,
      `view/gesturehandler.py`
- [x] 3.3 Fix `Gtk.EventBox`/`Gtk.Bin` base classes (→ `Gtk.Box`) across
      ~10 classes: `expandedentry.py`, `detailview.py`, `colorpicker.py`,
      `activitieslist.py`, `projectview.py`, `notification.py`,
      `viewsource.py`, `gui.py`, `listview.py`, `iconview.py`,
      `framewindow.py`
- [x] 3.4 Fix `Gtk.Toolbar` base class (→ `Gtk.Box`) across 9 classes:
      `viewtoolbar.py`, `activitychooser.py` (×2), `volumestoolbar.py`,
      `zoomtoolbar.py`, `viewsource.py`, `viewhelp.py`, `toolbar.py` (×2)
- [x] 3.5 Stub `SnowflakeLayout`/`ViewContainer` (`Gtk.Container`
      protocol → plain `Gtk.Box` packing, per design.md D4)
- [x] 3.6 Fix `GtkSource` version (`'4'` → `'5'`) in `viewsource.py`
- [x] 3.7 Fix `WebKit2` → `WebKit` namespace/version in
      `viewhelp_webkit2.py`
- [x] 3.8 Fix positional `Gtk.Label`/`Gtk.Button` constructor calls
      (`agepicker.py`, `keydialog.py`, `window.py`, `launcher.py`)
- [x] 3.9 Fix `Gtk.STOCK_STOP` (removed stock items) in `launcher.py`
- [x] 3.10 Fix `Gtk.Adjustment` `step_incr`/`page_incr` →
      `step_increment`/`page_increment` in `agepicker.py`
- [x] 3.11 Fix `Gtk.HScale` → `Gtk.Scale(orientation=...)` in
      `agepicker.py`
- [x] 3.12 Fix `'button-press-event'` → `Gtk.GestureClick` in
      `colorpicker.py`
- [x] 3.13 Fix `'key-press-event'` → `Gtk.EventControllerKey` in
      `intro/window.py`
- [x] 3.14 Fix `Gdk.ModifierType.MOD1_MASK` → `.ALT_MASK` in
      `keyhandler.py`
- [x] 3.15 Fix `Gdk.Seat.get_slaves()` → `.get_devices()` in
      `cursortracker.py`
- [x] 3.16 Fix `IntroWindow.add()`/`Gtk.Window` child API
      (`self.add()` → `self.set_child()`) in `intro/window.py`
- [x] 3.17 Fix `window.__name__` (invalid — instances don't have
      `__name__`) → `type(window).__name__` in `shell.py`
- [x] 3.18 Fix `Gio.ApplicationFlags.IS_SERVICE` blocking `'activate'`
      in GTK4 — removed from `ShellModel.__init__`
- [x] 3.19 Remove `Gtk.main()` call (doesn't exist in GTK4, redundant)
      from `main.py`
- [x] 3.20 Disable `get_type_hint()`-based activity-window tracking
      (`if False:`) in `_window_added_cb`/`_window_removed_cb`,
      including a pre-existing `get__type_hint` typo
- [x] 3.21 **Root-cause fix**: `ShellModel.add_window()` — only replace
      window child with `self.compositor` if `window.get_child() is None`

## 4. Fix a bug found in sugar-toolkit-gtk4 itself

- [x] 4.1 Fix `tray.py`'s `_apply_tray_css()` calling
      `style.apply_css_to_widget(None, css)` (invalid — `None` has no
      `get_style_context()`) — rewritten to use
      `Gtk.StyleContext.add_provider_for_display()`, the real GTK4 API
      for global CSS

## 5. Set up remaining runtime environment pieces

- [x] 5.1 Install `python-gwebsockets` (Arch package) for
      `jarabe/apisocket.py`
- [x] 5.2 Compile `org.sugarlabs` GSettings schema into
      `~/.local/share/glib-2.0/schemas/` (from `repos/sugar/data/`)
- [x] 5.3 Identify and export required env vars not covered by
      `bin/sugar.in`'s wrapper when running `jarabe.main` directly:
      `SUGAR_GROUP_LABELS`, `SUGAR_MIME_DEFAULTS`,
      `SUGAR_ACTIVITIES_HIDDEN`

## 6. Validate end-to-end

- [x] 6.1 Confirm `import jarabe.main` completes without error
- [x] 6.2 Confirm `'activate'` fires and `main()` runs (log:
      "Running main")
- [x] 6.3 Confirm a window is created and added (log: "adding window:
      IntroWindow")
- [x] 6.4 Launch nested Wayfire, point jarabe at it via
      `WAYLAND_DISPLAY`
- [x] 6.5 Visually confirm the onboarding screen renders with real
      content (not a blank window) — user-confirmed
- [x] 6.6 Remove temporary diagnostic instrumentation added during
      debugging (a `GLib.timeout_add` logging widget sizes in
      `IntroWindow.__init__`)
- [x] 6.7 Clean up test processes (nested Wayfire, jarabe)

## 7. Documentation

- [x] 7.1 Rewrite `specbook/docs/gtk-porting-standards.md`'s "Windowed
      jarabe" section with the full success account, blocker chain,
      working procedure, and known limitations
- [x] 7.2 Update `specbook/docs/sugar-stack.md` with
      `repos/sugar-toolkit-gtk3` (reference clone) and
      `python-gwebsockets` package

## 8. Verification

- [x] 8.1 Re-run the documented procedure from a clean state (killed
      all processes, cleared `shell.log`) to confirm reproducibility
- [x] 8.2 Run `openspec sync` (or the manual equivalent) to merge delta
      specs into `openspec/specs/`
      **Result**: created `jarabe-gtk4-integration`, `sugar4-ext-module`,
      `sugar4-gtk3compat-module` specs; updated `windowed-jarabe-mode`
      and `nested-wayfire-dev-session` with the resolved outcome. All 7
      specs in the workspace validate clean.
- [x] 8.3 Run `openspec archive` once 8.1 passes
