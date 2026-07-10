# Desktop Pie Menu — Tasks

## 1. Pie menu widget

- [x] 1.1 Create `shell/pie_menu.py` — radial layout widget
- [x] 1.2 Wire center button → Settings panel popup
- [x] 1.3 Load favorites from `favorites.json` and populate petals
- [x] 1.4 Wire petal click → launch app
- [x] 1.5 Wire right-click on petal → unpin from favorites
- [x] 1.6 Add animation (fade-in, smooth reveal)
- [x] 1.7 Handle empty state (no favorites pinned)

## 2. Desktop view replacement

- [x] 2.1 Replace `desktop_grid.py` usage in `HomeView` with `pie_menu.py`
- [x] 2.2 Delete `shell/desktop_grid.py`
- [x] 2.3 Verify wallpaper background still renders behind pie menu —
      `SugarPieMenu.set_background` is a no-op like the old desktop_grid;
      the shell-level `_background_picture`/`_bg_overlay` still sit behind
      `home_view` in the same `Gtk.Overlay` stack

## 3. Frame simplification

- [x] 3.1 Remove `_favorites_box` and favorites code from `frame.py` —
      pin/unpin/load/save moved to `pie_menu.py` (still needed for the
      Apps view's pin action)
- [x] 3.2 Remove Settings button from Frame
- [x] 3.3 Remove `set_settings_panel()` and related wiring from `frame.py`

## 4. Settings relocation

- [x] 4.1 Remove `frame.set_settings_panel()` call from `main.py`
- [x] 4.2 Wire pie menu center → `settings_panel.popup()` —
      `SugarShell._on_settings_requested`
- [x] 4.3 Ensure F10 keybinding still opens Settings

## 5. Search view removal

- [x] 5.1 Remove `search-first` from views list in `main.py`
- [x] 5.2 Delete `shell/search_first.py`
- [x] 5.3 Update `_VIEW_KEYS` — F3 is no longer bound; document as reserved
- [x] 5.4 Update view switcher in Frame (only [Desktop] [Apps])

## 6. Cleanup

- [x] 6.1 Smoke test: navigate Desktop → Apps → Frame → Desktop — ran the
      shell headless against a real Wayland display, switched
      desktop-grid → app-grid → desktop-grid via `_activate_view`
- [x] 6.2 Smoke test: pin app in Apps view, verify it appears in pie menu —
      pinned a real installed app, verified petal count and empty-state
      visibility
- [x] 6.3 Smoke test: unpin from pie menu, verify it disappears — verified
      petal removed and empty state restored
- [x] 6.4 Smoke test: open Settings from pie menu center —
      `_on_settings_requested` opens `settings_panel`, verified visible
- [x] 6.5 Remove `home_view.py` if no longer needed — kept: `HomeView`
      still owns the crossfade transition between Desktop/Apps and backs
      `view_ids()`/`get_view()`/`active_id`, which `settings.py` (icon
      size, background) and `main.py` (F1/F2, persistence) depend on
- [x] 6.6 Update tests — removed `test_pin_persists_and_reloads` from
      `test_frame.py` (favorites moved out of Frame), added
      `tests/test_pie_menu.py` covering pin/unpin/persist/empty-state/
      settings callback; updated `test_home_view.py`,
      `test_settings_panel.py`, `test_frame.py`, `test_xdg_compliance.py`,
      `test_settings_store.py` for the `SugarSearchFirst` →
      `SugarPieMenu` swap and the `home_view_layout` default fix.
      64/64 tests pass.
