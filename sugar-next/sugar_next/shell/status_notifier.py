"""Minimal StatusNotifierItem (system tray) support.

Exposes ``org.kde.StatusNotifierItem`` directly over D-Bus — there is no
GTK4-native binding for it, and pulling in libappindicator would add a
dependency most distros don't ship by default. Intended for background
services (e.g. a future presence bus, see Fase 6) to signal they're
running; the shell itself does not require a tray icon to function.
"""

import logging

import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib

log = logging.getLogger("sugar-next.status-notifier")

_SNI_XML = """
<node>
  <interface name="org.kde.StatusNotifierItem">
    <property name="Category" type="s" access="read"/>
    <property name="Id" type="s" access="read"/>
    <property name="Title" type="s" access="read"/>
    <property name="Status" type="s" access="read"/>
    <property name="IconName" type="s" access="read"/>
    <method name="Activate">
      <arg type="i" direction="in" name="x"/>
      <arg type="i" direction="in" name="y"/>
    </method>
  </interface>
</node>
"""

_WATCHER_BUS_NAME = "org.kde.StatusNotifierWatcher"
_WATCHER_OBJECT_PATH = "/StatusNotifierWatcher"


class StatusNotifierItem:
    """Registers a single background service with the StatusNotifierWatcher.

    Usage::

        item = StatusNotifierItem("presence-bus", icon_name="network-wireless")
        item.publish()
        ...
        item.withdraw()
    """

    def __init__(self, service_id, title=None, icon_name="application-x-executable"):
        self.service_id = service_id
        self.title = title or service_id
        self.icon_name = icon_name
        self.status = "Active"
        self._connection = None
        self._registration_id = None
        self._object_path = f"/StatusNotifierItem/{service_id.replace('-', '_')}"

    def publish(self, connection=None):
        self._connection = connection or Gio.bus_get_sync(Gio.BusType.SESSION, None)
        node_info = Gio.DBusNodeInfo.new_for_xml(_SNI_XML)
        interface_info = node_info.interfaces[0]
        self._registration_id = self._connection.register_object(
            self._object_path,
            interface_info,
            self._handle_method_call,
            self._handle_get_property,
            None,
        )
        self._announce_to_watcher()

    def withdraw(self):
        if self._connection is not None and self._registration_id is not None:
            self._connection.unregister_object(self._registration_id)
            self._registration_id = None

    def _announce_to_watcher(self):
        try:
            self._connection.call_sync(
                _WATCHER_BUS_NAME,
                _WATCHER_OBJECT_PATH,
                _WATCHER_BUS_NAME,
                "RegisterStatusNotifierItem",
                GLib.Variant("(s)", (self._object_path,)),
                None,
                Gio.DBusCallFlags.NONE,
                -1,
                None,
            )
        except GLib.Error:
            # No StatusNotifierWatcher running (no tray host, e.g. headless
            # or a desktop environment without one) — non-fatal.
            log.info(
                "No StatusNotifierWatcher available; %s tray icon not shown",
                self.service_id,
            )

    def _handle_method_call(
        self, connection, sender, path, interface, method, params, invocation
    ):
        if method == "Activate":
            invocation.return_value(None)
        else:
            invocation.return_value(None)

    def _handle_get_property(self, connection, sender, path, interface, name):
        values = {
            "Category": "ApplicationStatus",
            "Id": self.service_id,
            "Title": self.title,
            "Status": self.status,
            "IconName": self.icon_name,
        }
        if name in values:
            return GLib.Variant("s", values[name])
        return None
