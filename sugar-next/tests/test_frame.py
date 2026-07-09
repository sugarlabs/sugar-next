import json
import types

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import pytest

from sugar_next.shell.frame import SugarFrame


@pytest.fixture(autouse=True)
def gtk_display():
    if not Gtk.init_check():
        pytest.skip("no display available for GTK")


def _stub_bundle(app_id):
    return types.SimpleNamespace(
        app_id=app_id, name=app_id, icon=None, launch=lambda: True
    )


def test_toggle(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    frame = SugarFrame()
    assert not frame.get_reveal_child()
    frame.toggle()
    assert frame.get_reveal_child()
    frame.reveal()
    assert frame.get_reveal_child()


def test_pin_persists_and_reloads(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    frame = SugarFrame()
    frame.pin_favorite(_stub_bundle("fake-app.desktop"))
    frame.pin_favorite(_stub_bundle("fake-app.desktop"))  # no duplicates

    favorites_file = tmp_path / "sugar-next" / "favorites.json"
    assert json.loads(favorites_file.read_text()) == ["fake-app.desktop"]

    # A fresh frame loads them back; the uninstalled app id is
    # skipped in the UI but kept in the list.
    frame2 = SugarFrame()
    assert frame2._favorite_ids == ["fake-app.desktop"]

    frame2._unpin_favorite(_stub_bundle("fake-app.desktop"))
    assert json.loads(favorites_file.read_text()) == []


def test_add_running_deduplicates(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    frame = SugarFrame()
    frame.add_running(_stub_bundle("app.desktop"))
    frame.add_running(_stub_bundle("app.desktop"))
    children = 0
    child = frame._running_box.get_first_child()
    while child is not None:
        children += 1
        child = child.get_next_sibling()
    assert children == 1


def _running_box_count(frame):
    count = 0
    child = frame._running_box.get_first_child()
    while child is not None:
        count += 1
        child = child.get_next_sibling()
    return count


def test_remove_running_clears_the_icon(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    frame = SugarFrame()
    frame.add_running(_stub_bundle("app.desktop"))
    assert _running_box_count(frame) == 1

    frame.remove_running("app.desktop")
    assert _running_box_count(frame) == 0
    assert "app.desktop" not in frame._running_ids


def test_remove_running_only_removes_matching_app(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    frame = SugarFrame()
    frame.add_running(_stub_bundle("app-a.desktop"))
    frame.add_running(_stub_bundle("app-b.desktop"))

    frame.remove_running("app-a.desktop")
    assert _running_box_count(frame) == 1
    assert frame._running_ids == {"app-b.desktop"}


def test_remove_running_unknown_app_is_a_no_op(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    frame = SugarFrame()
    frame.add_running(_stub_bundle("app.desktop"))
    frame.remove_running("never-launched.desktop")
    assert _running_box_count(frame) == 1
