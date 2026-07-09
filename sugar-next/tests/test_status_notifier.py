import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio

import pytest

from sugar_next.shell.status_notifier import StatusNotifierItem


@pytest.fixture(autouse=True)
def session_bus():
    try:
        Gio.bus_get_sync(Gio.BusType.SESSION, None)
    except Exception:
        pytest.skip("no session D-Bus available")


def test_publish_and_withdraw_do_not_raise():
    item = StatusNotifierItem("test-service", title="Test Service")
    item.publish()
    item.withdraw()


def test_properties_exposed():
    item = StatusNotifierItem("test-service-2", icon_name="dialog-information")
    assert item._handle_get_property(None, None, None, None, "Id") is not None
    assert item._handle_get_property(None, None, None, None, "IconName") is not None
    assert item._handle_get_property(None, None, None, None, "unknown") is None
