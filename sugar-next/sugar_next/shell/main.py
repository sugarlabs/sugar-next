#!/usr/bin/env python3
import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gtk

from sugar_next.api.hooks import registry as hook_registry
from sugar_next.shell.app_grid import SugarAppGrid
from sugar_next.shell.search_first import SugarSearchFirst
from sugar_next.shell.desktop_grid import SugarDesktopGrid
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
            """
            window {
                background-color: var(--sn-bg);
                color: var(--sn-text);
            }
            button {
                border-radius: 10px;
                box-shadow: 0 1px 0 rgba(255,255,255,0.12);
            }
            button:hover {
                box-shadow: 0 1px 0 rgba(255,255,255,0.18),
                            0 2px 6px rgba(0,0,0,0.12);
            }
            searchbar, entry {
                border-radius: 12px;
                border: 1px solid rgba(0,0,0,0.1);
                background: linear-gradient(180deg,
                    rgba(0,0,0,0.03) 0%,
                    rgba(0,0,0,0.01) 100%
                );
                box-shadow:
                    inset 0 1px 2px rgba(0,0,0,0.06),
                    0 1px 0 rgba(255,255,255,0.08);
            }
            .sn-dropdown {
                border: none;
                box-shadow: none;
                background: none;
                margin: 0;
                padding: 0 4px;
                min-height: 28px;
            }
            .sn-dropdown > button {
                border-radius: 8px;
                border: 1px solid rgba(0,0,0,0.12);
                background: linear-gradient(180deg,
                    rgba(255,255,255,0.08) 0%,
                    rgba(0,0,0,0.02) 100%
                );
                box-shadow: 0 1px 0 rgba(255,255,255,0.08);
                padding: 2px 10px;
            }
            .sn-dropdown > button:hover {
                border-color: rgba(0,0,0,0.20);
            }
            .sn-dropdown > popover {
                border-radius: 10px;
                border: 1px solid rgba(0,0,0,0.12);
                box-shadow: 0 3px 12px rgba(0,0,0,0.18);
                padding: 4px 0;
            }
            .sn-dropdown > popover contents > row {
                padding: 4px 12px;
            }
            .sn-dropdown > popover contents > row:hover {
                background: var(--sn-accent);
                color: white;
            }
            """
        )
        Gtk.StyleContext.add_provider_for_display(
            self.window.get_display(),
            base_css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self.frame = SugarFrame()

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

        bundled = self.app_grid._load_bundles()
        self.desktop_grid = SugarDesktopGrid(
            background_path=self.settings_store.get("background_path")
        )
        self.desktop_grid.set_on_launch(self._on_app_launched)
        self.desktop_grid.set_icon_size(icon_size)
        self.desktop_grid.populate(bundled)

        self.home_view = HomeView()
        self.home_view.add_layout(self.app_grid, set_active=True)
        self.home_view.add_layout(self.search_first)
        self.home_view.add_layout(self.desktop_grid)

        saved_layout = self.settings_store.get("home_view_layout")
        if saved_layout in self.home_view.layout_ids():
            self.home_view.set_active(saved_layout)

        self._background_picture = Gtk.Picture()
        self._background_picture.set_content_fit(Gtk.ContentFit.COVER)
        self._background_picture.set_can_shrink(True)
        bg_path = self.settings_store.get("background_path")
        if bg_path:
            self._background_picture.set_filename(bg_path)
        self._background_picture.add_css_class("home-view-bg")

        self._bg_overlay = Gtk.DrawingArea()
        self._bg_overlay.set_hexpand(True)
        self._bg_overlay.set_vexpand(True)
        self._bg_overlay.add_css_class("home-view-bg-overlay")
        self._bg_overlay.set_draw_func(self._draw_bg_overlay)

        bg_dim = self.settings_store.get("bg_dim")
        self._bg_overlay.set_opacity(bg_dim)

        home_overlay = Gtk.Overlay()
        home_overlay.set_child(self._background_picture)
        home_overlay.add_overlay(self._bg_overlay)
        home_overlay.add_overlay(self.home_view)

        shell_overlay = Gtk.Overlay()
        shell_overlay.set_child(home_overlay)
        shell_overlay.add_overlay(self.frame)
        self.window.set_child(shell_overlay)
        shell_overlay._frame = self.frame

        # Hot corner click target at top-right — click opens Frame.
        self._hot_corner = Gtk.Button()
        self._hot_corner.add_css_class("flat")
        self._hot_corner.set_opacity(0.0)
        self._hot_corner.set_size_request(80, 6)
        self._hot_corner.set_halign(Gtk.Align.END)
        self._hot_corner.set_valign(Gtk.Align.START)
        self._hot_corner.set_tooltip_text("Click or hover to reveal the Frame")
        self._hot_corner.connect("clicked", lambda _b: self.frame.reveal())
        shell_overlay.add_overlay(self._hot_corner)

        # Click outside the Frame closes it.
        close_gesture = Gtk.GestureClick()
        close_gesture.connect("pressed", self._on_background_pressed)
        home_overlay.add_controller(close_gesture)
        shell_overlay.add_overlay(self._hot_corner)

        self.settings_panel = SettingsPanel(
            home_view=self.home_view, store=self.settings_store, shell=self
        )
        self.frame.set_settings_panel(self.settings_panel)

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.window.add_controller(key_controller)

        # Motion on the hot corner itself (keeping the old behavior).
        motion = Gtk.EventControllerMotion()
        motion.connect("motion", self._on_motion)
        self._hot_corner.add_controller(motion)

        self.window.present()

    def _on_background_pressed(self, gesture, n_press, x, y):
        self.frame.set_reveal_child(False)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_F6:
            self.frame.toggle()
            return True
        if keyval in (Gdk.KEY_F1, Gdk.KEY_F10):
            if self.settings_panel.is_visible():
                self.settings_panel.popdown()
            else:
                self.frame.reveal()
                self.settings_panel.popup()
            return True
        return False

    def _on_motion(self, controller, x, y):
        if y <= 3:
            self.frame.reveal()

    def _on_shutdown(self, app):
        self.toplevel_tracker.stop()

    def _on_app_launched(self, bundle):
        self.frame.add_running(bundle)
        if self.settings_store.get("accent_color"):
            return
        color = dominant_color_hex(bundle.icon)
        theme_manager.set_accent_tint(color)

    def _draw_bg_overlay(self, area, cr, width, height):
        cr.set_source_rgba(0, 0, 0, 1.0)
        cr.paint()

    def set_background(self, path):
        if path:
            self._background_picture.set_filename(path)
        else:
            self._background_picture.set_filename(None)

    def set_bg_dim(self, value):
        self._bg_overlay.set_opacity(value)

    def _on_toplevel_open(self, wayland_app_id, title):
        pass

    def _on_toplevel_close(self, wayland_app_id, title):
        if self.toplevel_tracker.available is not True:
            return
        if not self._has_open_toplevel(wayland_app_id):
            self.frame.remove_running(wayland_app_id)

    def _has_open_toplevel(self, wayland_app_id):
        return any(
            state.get("app_id") == wayland_app_id
            for state in self.toplevel_tracker._toplevels.values()
        )

    def _on_app_process_closed(self, app_id):
        if self.toplevel_tracker.available is True:
            return
        self.frame.remove_running(app_id)


def main():
    app = SugarShell()
    return app.run(sys.argv)


if __name__ == "__main__":
    main()
