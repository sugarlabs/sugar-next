"""Home View layout interface.

A Home View layout is any widget implementing ``HomeViewLayout``:
``on_activate``/``on_deactivate`` are called when the layout becomes the
visible Home View, and ``root`` is the ``Gtk.Widget`` to display. Built-in
layouts are app-grid, desktop-grid, and search-first; extensions may
provide additional layouts implementing the same interface.
"""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class HomeViewLayout:
    """Mixin every Home View layout widget implements.

    Subclasses are expected to also subclass a ``Gtk.Widget`` so ``root``
    can simply return ``self``.
    """

    #: Stable identifier used in Settings and the school-lock policy file.
    layout_id = None

    #: Human-readable name shown in the Settings layout selector.
    layout_name = None

    @property
    def root(self) -> Gtk.Widget:
        """The widget to place in the Home View container."""
        return self

    def on_activate(self):
        """Called when this layout becomes the visible Home View."""

    def on_deactivate(self):
        """Called when switching away from this layout."""


class HomeView(Gtk.Stack):
    """Container that swaps between registered Home View layouts."""

    __gtype_name__ = "SugarNextHomeView"

    def __init__(self):
        super().__init__()
        self.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self._layouts = {}
        self._active_id = None

    def add_layout(self, layout: HomeViewLayout, set_active=False):
        if layout.layout_id is None:
            raise ValueError("layout_id must be set on the layout instance")
        self._layouts[layout.layout_id] = layout
        self.add_named(layout.root, layout.layout_id)
        if set_active or self._active_id is None:
            self.set_active(layout.layout_id)

    def set_active(self, layout_id):
        if layout_id not in self._layouts:
            raise KeyError(f"unknown layout {layout_id!r}")
        if layout_id == self._active_id:
            return
        previous = self._layouts.get(self._active_id)
        if previous is not None:
            previous.on_deactivate()
        self._active_id = layout_id
        self.set_visible_child_name(layout_id)
        self._layouts[layout_id].on_activate()

    @property
    def active_id(self):
        return self._active_id

    def layout_ids(self):
        return list(self._layouts.keys())
