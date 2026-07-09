"""Settings window — modal dialog with tabs.

Accessible from the Frame or F1/F10. Appearance, Behavior, Extensions, About.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, GdkPixbuf, Gtk

from sugar_next.api.hooks import list_extensions, registry, set_extension_enabled
from sugar_next.shell.settings_store import SettingsStore, icon_size_px
from sugar_next.shell.theme import DEFAULT_ACCENT, manager as theme_manager

_ACCENT_PRESETS = [
    "#3584e4",
    "#33d17a",
    "#f6d32d",
    "#ff7800",
    "#e01b24",
    "#9141ac",
    "#1a5fb4",
    "#26a269",
]

_ACCENT_NAMES = [
    "Blue", "Green", "Yellow", "Orange",
    "Red", "Purple", "Navy", "Forest",
]

_KEYBINDINGS = [
    ("F1 / F10", "Open/close Settings"),
    ("F6", "Toggle the Frame"),
    ("Esc", "Close this dialog"),
]

_SETTINGS_CSS = """
    .settings-window {
        background: linear-gradient(180deg,
            rgba(255,255,255,0.97) 0%,
            rgba(0,0,0,0.02) 100%
        );
    }
    .settings-bg-thumb {
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.10);
        background-color: var(--sn-bg);
    }
    .settings-tab-page {
        padding: 16px;
    }
    .settings-swatch {
        min-width: 28px;
        min-height: 28px;
        border-radius: 50%;
        border: 2px solid transparent;
        transition: border-color 150ms;
    }
    .settings-swatch:hover {
        border-color: var(--sn-accent);
    }
    .settings-swatch-active {
        border-color: var(--sn-text);
    }
    .settings-section {
        margin-bottom: 16px;
    }
    .settings-section-title {
        font-weight: bold;
        margin-bottom: 6px;
    }
"""


class SettingsWindow(Gtk.Window):
    __gtype_name__ = "SugarNextSettingsWindow"

    def __init__(self, home_view=None, store=None, shell=None):
        super().__init__()
        self.set_title("Settings")
        self.set_modal(True)
        self.set_default_size(480, 520)
        self.set_resizable(False)
        self.set_hide_on_close(True)

        provider = Gtk.CssProvider()
        provider.load_from_string(_SETTINGS_CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self._home_view = home_view
        self._store = store or SettingsStore()
        self._shell = shell

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.add_css_class("settings-window")

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_margin_start(4)
        stack.set_margin_end(4)
        stack.set_margin_bottom(4)
        stack.set_vexpand(True)
        stack.set_hexpand(True)

        stack.add_titled(
            self._build_appearance(), "appearance", "Appearance"
        )
        stack.add_titled(
            self._build_behavior(), "behavior", "Behavior"
        )
        stack.add_titled(
            self._build_extensions_tab(), "extensions", "Extensions"
        )
        stack.add_titled(
            self._build_about_tab(), "about", "About"
        )

        switcher = Gtk.StackSwitcher()
        switcher.set_stack(stack)
        switcher.set_halign(Gtk.Align.CENTER)
        switcher.set_margin_top(10)
        switcher.set_margin_bottom(4)
        vbox.append(switcher)
        vbox.append(stack)
        self.set_child(vbox)

        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self._on_key)
        self.add_controller(key_ctrl)

    def _on_key(self, _ctrl, keyval, _keycode, _state):
        if keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    # -- Tab: Appearance --------------------------------------------------

    def _build_appearance(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        scrolled.set_child(box)
        scrolled.add_css_class("settings-tab-page")

        # -- Background section --
        section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section.add_css_class("settings-section")
        title = Gtk.Label(label="Background image", xalign=0)
        title.add_css_class("settings-section-title")
        section.append(title)

        self._bg_thumb = Gtk.Picture()
        self._bg_thumb.set_size_request(-1, 120)
        self._bg_thumb.set_content_fit(Gtk.ContentFit.COVER)
        self._bg_thumb.set_can_shrink(True)
        self._bg_thumb.add_css_class("settings-bg-thumb")
        self._refresh_bg_thumb()
        section.append(self._bg_thumb)

        bgbtns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        choose_btn = Gtk.Button(label="Choose image\u2026")
        choose_btn.connect("clicked", self._on_choose_background)
        bgbtns.append(choose_btn)
        clear_btn = Gtk.Button(label="Clear")
        clear_btn.add_css_class("flat")
        clear_btn.connect("clicked", self._on_clear_background)
        bgbtns.append(clear_btn)
        section.append(bgbtns)

        self._bg_name_label = Gtk.Label(
            label=self._bg_display_name(), xalign=0
        )
        section.append(self._bg_name_label)

        opacity_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        opacity_row.append(
            Gtk.Label(label="Background dim", xalign=0)
        )
        opacity_row.append(
            Gtk.Label(
                label="Darken the background to keep labels readable",
                xalign=0,
            )
        )
        opacity_row.get_last_child().add_css_class("dim-label")
        adj = Gtk.Adjustment(
            value=self._store.get("bg_dim"),
            lower=0.0, upper=0.8, step_increment=0.05,
        )
        opacity_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
        opacity_scale.set_hexpand(True)
        opacity_scale.set_draw_value(False)
        opacity_scale.connect("value-changed", self._on_bg_opacity_changed)
        opacity_row.append(opacity_scale)
        self._opacity_pct = Gtk.Label(
            label=f"{int(adj.get_value() * 100)}%", xalign=1
        )
        opacity_row.append(self._opacity_pct)
        section.append(opacity_row)

        box.append(section)

        # -- Accent color section --
        section2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section2.add_css_class("settings-section")
        title2 = Gtk.Label(label="Accent color", xalign=0)
        title2.add_css_class("settings-section-title")
        section2.append(title2)

        current_color = self._store.get("accent_color")
        self._accent_label = Gtk.Label(
            label=current_color or DEFAULT_ACCENT, xalign=0
        )
        section2.append(self._accent_label)

        swatches = Gtk.FlowBox()
        swatches.set_max_children_per_line(8)
        swatches.set_selection_mode(Gtk.SelectionMode.NONE)
        swatches.set_homogeneous(True)
        swatches.set_row_spacing(4)
        swatches.set_column_spacing(4)

        css_rules = []
        self._swatch_buttons = []
        for idx, hex_color in enumerate(_ACCENT_PRESETS):
            btn = Gtk.Button()
            btn.add_css_class("settings-swatch")
            btn.add_css_class(f"sw-{idx}")
            btn.set_tooltip_text(f"{_ACCENT_NAMES[idx]}: {hex_color}")
            css_rules.append(
                f".sw-{idx} {{ background: {hex_color};"
                " min-width: 28px; min-height: 28px; border-radius: 50%; }"
            )
            btn.connect("clicked", self._on_accent_chosen, hex_color)
            swatches.append(btn)
            self._swatch_buttons.append((hex_color, btn))
        self._update_active_swatch(current_color)

        prov = Gtk.CssProvider()
        prov.load_from_string("\n".join(css_rules))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            prov,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        section2.append(swatches)

        custom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self._custom_entry = Gtk.Entry()
        self._custom_entry.set_placeholder_text("#rrggbb")
        self._custom_entry.set_max_length(7)
        self._custom_entry.set_hexpand(True)
        custom_row.append(self._custom_entry)
        apply_btn = Gtk.Button(label="Apply")
        apply_btn.connect("clicked", self._on_custom_accent)
        custom_row.append(apply_btn)
        section2.append(custom_row)

        box.append(section2)

        return scrolled

    def _refresh_bg_thumb(self):
        path = self._store.get("background_path")
        if path:
            self._bg_thumb.set_filename(path)
        else:
            self._bg_thumb.set_filename(None)

    def _bg_display_name(self):
        path = self._store.get("background_path")
        if not path:
            return "No image selected"
        from pathlib import Path
        return Path(path).name

    def _on_choose_background(self, _btn):
        dialog = Gtk.FileChooserNative.new(
            "Choose a background image",
            self,
            Gtk.FileChooserAction.OPEN,
            "Select",
            "Cancel",
        )
        dialog.connect("response", self._on_background_chosen)
        dialog.show()
        self._bg_dialog = dialog

    def _on_background_chosen(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            if file is not None:
                path = file.get_path()
                self._store.set("background_path", path)
                self._bg_name_label.set_label(file.get_basename() or "")
                self._refresh_bg_thumb()
                self._apply_background(path)
        dialog.destroy()

    def _on_clear_background(self, _btn):
        self._store.set("background_path", None)
        self._bg_name_label.set_label("No image selected")
        self._refresh_bg_thumb()
        self._apply_background(None)

    def _apply_background(self, path):
        if self._shell is not None and hasattr(self._shell, "set_background"):
            self._shell.set_background(path)
        if self._home_view is not None:
            dg = self._home_view._layouts.get("desktop-grid")
            if dg is not None and hasattr(dg, "set_background"):
                dg.set_background(path)

    def _on_bg_opacity_changed(self, scale):
        val = scale.get_value()
        self._store.set("bg_dim", val)
        self._opacity_pct.set_label(f"{int(val * 100)}%")
        if self._shell is not None and hasattr(self._shell, "set_bg_dim"):
            self._shell.set_bg_dim(val)

    def _update_active_swatch(self, hex_color):
        for color, btn in self._swatch_buttons:
            if color == hex_color:
                btn.add_css_class("settings-swatch-active")
            else:
                btn.remove_css_class("settings-swatch-active")

    def _on_accent_chosen(self, _btn, hex_color):
        self._store.set("accent_color", hex_color)
        self._accent_label.set_label(hex_color)
        theme_manager.set_accent_tint(hex_color)
        self._update_active_swatch(hex_color)

    def _on_custom_accent(self, _btn):
        text = self._custom_entry.get_text().strip()
        if len(text) == 7 and text.startswith("#"):
            self._on_accent_chosen(None, text)

    # -- Tab: Behavior ----------------------------------------------------

    def _build_behavior(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        scrolled.set_child(box)
        scrolled.add_css_class("settings-tab-page")

        # Home View layout
        if self._home_view is not None:
            section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            section.add_css_class("settings-section")
            title = Gtk.Label(label="Home View layout", xalign=0)
            title.add_css_class("settings-section-title")
            section.append(title)

            layout_ids = self._home_view.layout_ids()
            dropdown = Gtk.DropDown.new_from_strings(layout_ids)
            dropdown.add_css_class("sn-dropdown")
            if self._home_view.active_id in layout_ids:
                dropdown.set_selected(layout_ids.index(self._home_view.active_id))
            dropdown.connect(
                "notify::selected", self._on_layout_changed, layout_ids
            )
            section.append(dropdown)
            box.append(section)

        # Icon size
        section2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        section2.add_css_class("settings-section")
        title2 = Gtk.Label(label="Icon size", xalign=0)
        title2.add_css_class("settings-section-title")
        section2.append(title2)
        sizes = ["small", "medium", "large"]
        dropdown2 = Gtk.DropDown.new_from_strings(sizes)
        dropdown2.add_css_class("sn-dropdown")
        current = self._store.get("icon_size")
        if current in sizes:
            dropdown2.set_selected(sizes.index(current))
        dropdown2.connect("notify::selected", self._on_icon_size_changed, sizes)
        section2.append(dropdown2)
        box.append(section2)

        # Contrast
        section3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        section3.add_css_class("settings-section")
        title3 = Gtk.Label(label="Accessibility", xalign=0)
        title3.add_css_class("settings-section-title")
        section3.append(title3)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.append(Gtk.Label(label="High contrast", xalign=0, hexpand=True))
        switch = Gtk.Switch()
        switch.set_active(self._store.get("contrast") == "high")
        switch.connect("state-set", self._on_contrast_toggled)
        row.append(switch)
        section3.append(row)
        box.append(section3)

        # Keybindings
        section4 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        section4.add_css_class("settings-section")
        title4 = Gtk.Label(label="Keybindings", xalign=0)
        title4.add_css_class("settings-section-title")
        section4.append(title4)
        for key, desc in _KEYBINDINGS:
            section4.append(
                Gtk.Label(label=f"{key} \u2014 {desc}", xalign=0)
            )
        box.append(section4)

        return scrolled

    def _on_layout_changed(self, dropdown, _pspec, layout_ids):
        lid = layout_ids[dropdown.get_selected()]
        self._store.set("home_view_layout", lid)
        if self._home_view is not None:
            self._home_view.set_active(lid)

    def _on_icon_size_changed(self, dropdown, _pspec, sizes):
        size_name = sizes[dropdown.get_selected()]
        self._store.set("icon_size", size_name)
        if self._home_view is not None:
            px = icon_size_px(size_name)
            for lid in self._home_view.layout_ids():
                layout = self._home_view._layouts.get(lid)
                if layout is not None and hasattr(layout, "set_icon_size"):
                    layout.set_icon_size(px)

    def _on_contrast_toggled(self, _switch, state):
        level = "high" if state else "normal"
        self._store.set("contrast", level)
        theme_manager.set_contrast(level)
        return False

    # -- Tab: Extensions --------------------------------------------------

    def _build_extensions_tab(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._ext_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._extensions_box = self._ext_box  # test compat
        self._ext_box.set_margin_start(16)
        self._ext_box.set_margin_end(16)
        self._ext_box.set_margin_top(16)
        self._ext_box.set_margin_bottom(16)
        scrolled.set_child(self._ext_box)
        scrolled.add_css_class("settings-tab-page")

        title = Gtk.Label(label="Installed extensions", xalign=0)
        title.add_css_class("settings-section-title")
        self._ext_box.append(title)
        self._rebuild_ext_list()
        return scrolled

    def _rebuild_ext_list(self):
        while child := self._ext_box.get_last_child():
            if child is self._ext_box.get_first_child():
                break
            self._ext_box.remove(child)

        extensions = list_extensions()
        if not extensions:
            self._ext_box.append(
                Gtk.Label(label="(none installed)", xalign=0)
            )
            return
        for name, enabled in extensions:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            row.append(Gtk.Label(label=name, xalign=0, hexpand=True))
            switch = Gtk.Switch()
            switch.set_active(enabled)
            switch.connect("state-set", self._on_extension_toggled, name)
            row.append(switch)
            self._ext_box.append(row)

    def _on_extension_toggled(self, _switch, state, name):
        set_extension_enabled(name, state)
        registry.load()
        return False

    # -- Tab: About -------------------------------------------------------

    def _build_about_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.add_css_class("settings-tab-page")

        box.append(Gtk.Label(label="Sugar Next", xalign=0))
        box.append(
            Gtk.Label(
                label="A Learning Shell for Everyday Computing",
                xalign=0,
            )
        )
        box.append(Gtk.Label(label="GPL-3.0-or-later", xalign=0))
        return box


# Compatibility alias so frame.py can call set_settings_panel.
class SettingsPanel(SettingsWindow):
    def __init__(self, home_view=None, store=None, shell=None):
        super().__init__(home_view=home_view, store=store, shell=shell)
        self.connect("close-request", self._on_close_request)

    def popup(self):
        self.present()

    def popdown(self):
        self.set_visible(False)

    def is_visible(self):
        return self.get_visible()

    def _on_close_request(self):
        return False
