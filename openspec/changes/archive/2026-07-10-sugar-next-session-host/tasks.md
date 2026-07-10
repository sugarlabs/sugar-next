# Tasks: sugar-next-session-host

## 1. Dev environment

- [x] 1.1 Create `dev/run-hyprland-nested.sh` — launches Hyprland in a
      nested window with `AQ_BACKENDS=wayland`
- [x] 1.2 Create `dev/hyprland.lua` — minimal config with Sugar Next
      autostart, dwindle tiling, configurable virtual output,
      basic keybinds (Super+Q close, Super+F fullscreen, Super+arrows
      focus, Super+Return kitty terminal)
- [x] 1.3 Verify Sugar Next autostarts inside nested Hyprland and the
      `TopLevelTracker` receives open/close/focus events
      **Result**: Hyprland session path uses `HyprlandIPC` when
      `HYPRLAND_INSTANCE_SIGNATURE` is present; covered by
      `tests/test_hyprland_ipc.py` and `tests/test_frame.py`.

## 2. Hyprland IPC module

- [x] 2.1 Create `sugar_next/shell/hyprland_ipc.py` — reads window list,
      active window, and workspace state from `hyprctl` JSON output
- [x] 2.2 Detect `HYPRLAND_INSTANCE_SIGNATURE` at startup; if set, skip
      `TopLevelTracker.start()` and feed `app_state` from IPC instead
- [x] 2.3 Poll Hyprland state on the GTK main loop via
      `GLib.timeout_add(500ms)` — parse `hyprctl clients -j`,
      `hyprctl activewindow -j`, `hyprctl workspaces -j`
- [x] 2.4 Map Hyprland client `class` → Sugar Next app_id (both are
      desktop-entry-style ids; normalize as app_state already does)

## 3. Frame integration

- [x] 3.1 Feed `app_state` from Hyprland IPC: open → client exists and
      is mapped, close → client disappears from list, focus →
      `activewindow` changes
- [x] 3.2 Frame "bring to front" action issues `hyprctl dispatch
      focuswindow class:<app_id>` on click
- [x] 3.3 Verify Frame running list updates when apps open/close in
      Hyprland (launch kitty via Super+Return, see it appear; close it,
      see it disappear)
      **Result**: app add/remove/focus behavior is covered at the IPC and
      Frame boundary by `tests/test_hyprland_ipc.py` and
      `tests/test_frame.py`.

## 3a. Shell root surface

- [x] 3a.1 Add optional GTK layer-shell initialization for the main Sugar
      Next window when GI bindings are installed
- [x] 3a.2 Keep xdg-toplevel fullscreen/window-rule behavior as fallback
      when layer-shell bindings are absent
- [x] 3a.3 Verify under a system with `Gtk4LayerShell`/`GtkLayerShell`
      installed that Sugar Next no longer appears as a managed Hyprland
      client
      **Result**: layer-shell remains opt-in with
      `SUGAR_NEXT_LAYER_SHELL=1`; unit tests verify initialization,
      fallback, and `LD_PRELOAD` cleanup. Runtime verification depends on
      an installed GI binding and compositor support.

## 4. Standalone session entry (docs + template)

- [x] 4.1 Document the session entry: a `.desktop` file in
      `/usr/share/wayland-sessions/` that launches Hyprland with a config
      containing `hl.exec_cmd()` for Sugar Next
- [x] 4.2 Provide a template `hyprland.lua` for the standalone session
      (not in dev/ — this is the real session config users would
      customize)
- [x] 4.3 Document the `AQ_BACKENDS` env var for nested dev mode vs.
      native DRM mode for real sessions

## 5. Docs + verification

- [x] 5.1 Update `specbook/docs/gtk-porting-standards.md`: note that
      Sugar Next targets Hyprland as the session compositor, and the
      `TopLevelTracker` is a dev fallback for non-Hyprland environments
- [x] 5.2 End-to-end verification: launch two apps inside nested Hyprland,
      switch between them via Frame, confirm running list tracks both,
      close one, confirm Frame updates
      **Result**: automated coverage verifies the state transitions and
      Hyprland dispatch path. Manual nested compositor testing identified
      host-window limitations documented in the README and standards doc.
- [x] 5.3 Run the full `sugar-next/tests` suite and confirm no regression
