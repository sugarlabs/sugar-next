"""Real window tracking via wlr-foreign-toplevel-management.

Sugar Next's Frame originally only tracked "apps launched this session"
(see frame.py's v0 scope note) because a normal Wayland client cannot
enumerate other clients' windows without a dedicated protocol. This
module implements a client for that protocol so the Frame can show only
apps that actually have an open window — closing a window removes it
immediately, same as GNOME/KDE's taskbars.

Protocol availability is compositor-specific: only wlroots-based
compositors (Wayfire, Sway, Hyprland — Sugar Next's target, see
specbook/docs/gtk-porting-standards.md) implement
zwlr_foreign_toplevel_manager_v1. GNOME/Mutter implements neither this
nor the newer ext_foreign_toplevel_list_v1 standard, by deliberate
design (confirmed via `wayland-info` during development — this repo's
dev environment cannot exercise this code path at all). When the
protocol is unavailable, TopLevelTracker silently reports nothing and
the shell's existing on_app_close-based tracking in main.py remains the
only source of truth.

Runs the Wayland event dispatch loop on a background thread (GLib's main
loop is busy running GTK) and marshals updates back to the GTK thread via
GLib.idle_add, since GTK widgets must only be touched from the main
thread.
"""

import logging
import threading

import gi

gi.require_version("GLib", "2.0")
from gi.repository import GLib

log = logging.getLogger("sugar-next.toplevel-tracker")

try:
    from pywayland.client import Display

    _HAS_PYWAYLAND = True
except ImportError:
    _HAS_PYWAYLAND = False

if _HAS_PYWAYLAND:
    from sugar_next._wayland_wlr.wlr_foreign_toplevel_management_unstable_v1.zwlr_foreign_toplevel_manager_v1 import (
        ZwlrForeignToplevelManagerV1,
    )

_PROTOCOL_NAME = "zwlr_foreign_toplevel_manager_v1"


class TopLevelTracker:
    """Tracks open windows via zwlr_foreign_toplevel_manager_v1, if present.

    Callbacks (*on_open*, *on_close*) are invoked on the GTK main thread
    via GLib.idle_add — safe to touch widgets from them directly.
    """

    def __init__(self, on_open=None, on_close=None):
        self._on_open = on_open
        self._on_close = on_close
        self._thread = None
        self._display = None
        self._running = False
        self._available = None
        #: handle id (Wayland object id) -> {"app_id": str, "title": str}
        self._toplevels = {}

    @property
    def available(self) -> bool:
        """Whether the protocol was found on this compositor.

        Only meaningful after start() has run its initial roundtrip —
        None before that (unknown), True/False after.
        """
        return self._available

    def start(self):
        if not _HAS_PYWAYLAND:
            log.info("pywayland not installed; toplevel tracking disabled")
            self._available = False
            return
        self._available = None
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._display is not None:
            try:
                self._display.disconnect()
            except Exception:
                pass

    def _run(self):
        try:
            self._display = Display()
            self._display.connect()
            registry = self._display.get_registry()

            manager_proxy = {}

            def on_global(_registry, name, interface, version):
                if interface == _PROTOCOL_NAME:
                    manager_proxy["proxy"] = registry.bind(
                        name, ZwlrForeignToplevelManagerV1, min(version, 3)
                    )

            registry.dispatcher["global"] = on_global
            self._display.roundtrip()

            manager = manager_proxy.get("proxy")
            if manager is None:
                self._available = False
                log.info(
                    "%s not offered by this compositor; toplevel tracking disabled",
                    _PROTOCOL_NAME,
                )
                return

            self._available = True
            manager.dispatcher["toplevel"] = self._on_toplevel_created

            while self._running:
                self._display.dispatch(block=True)
        except Exception:
            self._available = False
            log.exception("Toplevel tracker stopped due to an error")
        finally:
            if self._display is not None:
                try:
                    self._display.disconnect()
                except Exception:
                    pass

    def _on_toplevel_created(self, _manager, handle):
        state = {"app_id": None, "title": None}
        self._toplevels[handle.id] = state

        def on_app_id(_handle, app_id):
            state["app_id"] = app_id

        def on_title(_handle, title):
            state["title"] = title

        def on_closed(_handle):
            self._toplevels.pop(handle.id, None)
            if self._on_close is not None:
                GLib.idle_add(self._on_close, state.get("app_id"), state.get("title"))

        def on_done(_handle):
            if self._on_open is not None:
                GLib.idle_add(self._on_open, state.get("app_id"), state.get("title"))

        handle.dispatcher["app_id"] = on_app_id
        handle.dispatcher["title"] = on_title
        handle.dispatcher["closed"] = on_closed
        handle.dispatcher["done"] = on_done
