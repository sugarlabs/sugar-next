import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import pytest

from sugar_next.shell.app_grid import SugarAppGrid
from sugar_next.shell.desktop_grid import SugarDesktopGrid
from sugar_next.shell.search_first import SugarSearchFirst
from sugar_next.shell.home_view import HomeView


@pytest.fixture(autouse=True)
def gtk_display():
    if not Gtk.init_check():
        pytest.skip("no display available for GTK")


def test_add_and_switch_layouts():
    home_view = HomeView()
    app_grid = SugarAppGrid()
    desktop_grid = SugarDesktopGrid()
    search_first = SugarSearchFirst()

    home_view.add_layout(app_grid, set_active=True)
    home_view.add_layout(desktop_grid)
    home_view.add_layout(search_first)

    assert home_view.active_id == "app-grid"
    assert set(home_view.layout_ids()) == {
        "app-grid",
        "desktop-grid",
        "search-first",
    }

    home_view.set_active("search-first")
    assert home_view.active_id == "search-first"

    home_view.set_active("desktop-grid")
    assert home_view.active_id == "desktop-grid"


def test_switching_resets_app_grid_search_state():
    home_view = HomeView()
    app_grid = SugarAppGrid()
    search_first = SugarSearchFirst()
    home_view.add_layout(app_grid, set_active=True)
    home_view.add_layout(search_first)

    app_grid._search_entry.set_text("firefox")
    home_view.set_active("search-first")

    assert app_grid._search_entry.get_text() == ""


def test_switching_resets_search_first_state():
    home_view = HomeView()
    app_grid = SugarAppGrid()
    search_first = SugarSearchFirst()
    home_view.add_layout(app_grid, set_active=True)
    home_view.add_layout(search_first)

    home_view.set_active("search-first")
    search_first._search_entry.set_text("something")
    home_view.set_active("app-grid")

    assert search_first._search_entry.get_text() == ""


def test_unknown_layout_raises():
    home_view = HomeView()
    app_grid = SugarAppGrid()
    home_view.add_layout(app_grid, set_active=True)
    with pytest.raises(KeyError):
        home_view.set_active("does-not-exist")
