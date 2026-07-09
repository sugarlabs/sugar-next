#!/usr/bin/env python3
import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gtk, Gio

from sugar_next.api.hooks import registry as hook_registry
from sugar_next.shell.app_grid import SugarAppGrid
from sugar_next.shell.search_first import SugarSearchFirst
from sugar_next.shell.frame import SugarFrame
from sugar_next.shell.home_view import HomeView
from sugar_next.shell.theme import manager as theme_manager
from sugar_next.shell.palette import dominant_color_hex
from sugar_next.shell.settings import SettingsPanel
from sugar_next.shell.settings_store import SettingsStore, icon_size_px
from sugar_next.shell.toplevel_tracker import TopLevelTracker


class SugarShell(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.sugarlabs.SugarNext")
        self.connect("activate", self._on_activate)
        self.connect("shutdown", self._on_shutdown)

    def _on_activate(self, app):
        hook_registry.load()
        hook_registry.call("on_shell_start")
        self.window = Gtk.ApplicationWindow(
            application=app,
            title="Sugar Next — A Learning Shell for Everyday Computing",
            default_width=1024,
            default_height=768,
        )

        self.settings_store = SettingsStore()
        theme_manager.apply(self.window.get_display())
        if self.settings_store.get("accent_color"):
            theme_manager.set_accent_tint(self.settings_store.get("accent_color"))
        theme_manager.set_contrast(self.settings_store.get("contrast"))

        base_css = Gtk.CssProvider()
        base_css.load_from_string(
            "window { background-color: var(--sn-bg); color: var(--sn-text); }"
        )
        Gtk.StyleContext.add_provider_for_display(
            self.window.get_display(),
            base_css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self.frame = SugarFrame()

        # Real window tracking (only shows apps with an actual open
        # window, like GNOME's taskbar) when the compositor offers
        # zwlr_foreign_toplevel_manager_v1 — wlroots-based compositors
        # only (Wayfire, Sway; not GNOME/Mutter). Falls back to the
        # existing on_app_close-based "apps launched this session"
        # tracking when the protocol is unavailable.
        self.toplevel_tracker = TopLevelTracker(
            on_open=self._on_toplevel_open,
            on_close=self._on_toplevel_close,
        )
        self.toplevel_tracker.start()
        hook_registry.subscribe(
            "on_app_close", lambda app_id, app_info: self._on_app_process_closed(app_id)
        )

        icon_size = icon_size_px(self.settings_store.get("icon_size"))
        self.app_grid = SugarAppGrid(
            on_launched=self._on_app_launched,
            on_pin=self.frame.pin_favorite,
            icon_size=icon_size,
        )
        self.search_first = SugarSearchFirst(
            on_launched=self._on_app_launched, icon_size=icon_size
        )
        self.search_first.set_bundles(self.app_grid._load_bundles())

        self.home_view = HomeView()
        self.home_view.add_layout(self.app_grid, set_active=True)
        self.home_view.add_layout(self.search_first)
        # Desktop grid layout exists (shell/desktop_grid.py) but is left
        # out of the active Home View for now — parked, not deleted.

        saved_layout = self.settings_store.get("home_view_layout")
        if saved_layout in self.home_view.layout_ids():
            self.home_view.set_active(saved_layout)

        self.settings_panel = SettingsPanel(
            home_view=self.home_view, store=self.settings_store
        )
        self.frame.set_settings_panel(self.settings_panel)

        overlay = Gtk.Overlay()
        overlay.set_child(self.home_view)
        overlay.add_overlay(self.frame)
        self.window.set_child(overlay)

        # F6 toggles the Frame (Sugar's classic frame key).
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.window.add_controller(key_controller)

        # Top-right hot corner reveals the Frame.
        motion = Gtk.EventControllerMotion()
        motion.connect("motion", self._on_motion)
        self.window.add_controller(motion)

        self.window.present()

    def _on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_F6:
            self.frame.toggle()
            return True
        return False

    def _on_motion(self, controller, x, y):
        if y <= 2 and x >= self.window.get_width() - 2:
            self.frame.reveal()

    def _on_shutdown(self, app):
        self.toplevel_tracker.stop()

    def _on_app_launched(self, bundle):
        self.frame.add_running(bundle)
        if self.settings_store.get("accent_color"):
            # The learner picked an accent color explicitly in Settings —
            # don't let active-app-palette tinting override that choice.
            return
        color = dominant_color_hex(bundle.icon)
        theme_manager.set_accent_tint(color)

    def _on_toplevel_open(self, wayland_app_id, title):
        # No-op: apps already appear in the Frame at launch time via
        # add_running(). Real-window tracking here is only used to
        # *remove* apps once their last window closes — see
        # _on_toplevel_close. (Wiring toplevel-open to add_running too
        # would need building a DesktopBundle from a bare Wayland app-id,
        # which isn't always a 1:1 match with a .desktop id — future work
        # if the Frame needs to show windows opened outside the shell.)
        pass

    def _on_toplevel_close(self, wayland_app_id, title):
        if self.toplevel_tracker.available is not True:
            return
        # Only remove if no other open window still has this app_id —
        # e.g. two Nautilus windows: closing one shouldn't drop it from
        # the Frame while the other is still open.
        if not self._has_open_toplevel(wayland_app_id):
            self.frame.remove_running(wayland_app_id)

    def _has_open_toplevel(self, wayland_app_id):
        return any(
            state.get("app_id") == wayland_app_id
            for state in self.toplevel_tracker._toplevels.values()
        )

    def _on_app_process_closed(self, app_id):
        # Fallback path (see toplevel_tracker.py): only takes over when
        # the compositor doesn't offer zwlr_foreign_toplevel_manager_v1
        # (e.g. GNOME/Mutter). On a wlroots compositor, real window
        # tracking (_on_toplevel_close) is authoritative and this would
        # be redundant — but harmless, since remove_running() on an
        # already-removed app_id is a no-op.
        if self.toplevel_tracker.available is True:
            return
        self.frame.remove_running(app_id)


def main():
    app = SugarShell()
    return app.run(sys.argv)


if __name__ == "__main__":
    main()
