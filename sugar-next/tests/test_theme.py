import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import pytest

from sugar_next.shell.theme import ThemeManager, colors_override_file


@pytest.fixture(autouse=True)
def gtk_display():
    if not Gtk.init_check():
        pytest.skip("no display available for GTK")


def test_apply_does_not_raise_without_override_file(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    manager = ThemeManager()
    manager.apply()


def test_apply_loads_override_file(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    override = colors_override_file()
    override.parent.mkdir(parents=True, exist_ok=True)
    override.write_text("window { --sn-accent: #ff00ff; }")
    manager = ThemeManager()
    manager.apply()


def test_set_accent_tint_and_clear():
    manager = ThemeManager()
    manager.apply()
    manager.set_accent_tint("#00ff00")
    manager.set_accent_tint(None)


def test_set_contrast_high_and_normal():
    manager = ThemeManager()
    manager.apply()
    manager.set_contrast("high")
    manager.set_contrast("normal")
