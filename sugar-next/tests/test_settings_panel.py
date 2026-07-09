import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import pytest

from sugar_next.shell.home_view import HomeView
from sugar_next.shell.app_grid import SugarAppGrid
from sugar_next.shell.search_first import SugarSearchFirst
from sugar_next.shell.settings import SettingsPanel
from sugar_next.shell.settings_store import SettingsStore


@pytest.fixture(autouse=True)
def gtk_display():
    if not Gtk.init_check():
        pytest.skip("no display available for GTK")


def test_builds_without_home_view(tmp_path):
    store = SettingsStore(tmp_path / "settings.json")
    panel = SettingsPanel(store=store)
    assert panel.get_child() is not None


def test_layout_row_present_with_home_view(tmp_path):
    store = SettingsStore(tmp_path / "settings.json")
    home_view = HomeView()
    home_view.add_layout(SugarAppGrid(), set_active=True)
    home_view.add_layout(SugarSearchFirst())
    panel = SettingsPanel(home_view=home_view, store=store)
    assert panel.get_child() is not None


def test_layout_change_updates_store_and_home_view(tmp_path):
    store = SettingsStore(tmp_path / "settings.json")
    home_view = HomeView()
    home_view.add_layout(SugarAppGrid(), set_active=True)
    home_view.add_layout(SugarSearchFirst())
    panel = SettingsPanel(home_view=home_view, store=store)

    panel._on_layout_changed(
        type("Dropdown", (), {"get_selected": lambda self: 1})(),
        None,
        home_view.layout_ids(),
    )
    assert home_view.active_id == home_view.layout_ids()[1]
    assert store.get("home_view_layout") == home_view.layout_ids()[1]


def test_accent_choice_updates_store(tmp_path):
    store = SettingsStore(tmp_path / "settings.json")
    panel = SettingsPanel(store=store)
    panel._on_accent_chosen(None, "#123456")
    assert store.get("accent_color") == "#123456"


def test_extensions_list_shows_installed_extensions(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    extensions = tmp_path / "sugar-next" / "extensions"
    extensions.mkdir(parents=True)
    (extensions / "logger.py").write_text("")
    (extensions / "journal.py.disabled").write_text("")

    store = SettingsStore(tmp_path / "settings.json")
    panel = SettingsPanel(store=store)

    from sugar_next.api.hooks import list_extensions

    assert list_extensions(extensions) == [("journal", False), ("logger", True)]
    # Panel built without crashing and shows the extensions box.
    assert panel._extensions_box is not None


def test_toggling_extension_switch_persists_and_reloads(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    extensions = tmp_path / "sugar-next" / "extensions"
    extensions.mkdir(parents=True)
    (extensions / "logger.py").write_text("def on_shell_start(): pass\n")

    store = SettingsStore(tmp_path / "settings.json")
    panel = SettingsPanel(store=store)

    panel._on_extension_toggled(None, False, "logger")

    from sugar_next.api.hooks import list_extensions

    assert list_extensions(extensions) == [("logger", False)]
    assert (extensions / "logger.py").exists() is False
    assert (extensions / "logger.py.disabled").exists() is True

    panel._on_extension_toggled(None, True, "logger")
    assert list_extensions(extensions) == [("logger", True)]
