#!/usr/bin/python3
"""
Minimal proof: a sugar-toolkit-gtk4 activity rendering inside a
Casilda-embedded Wayland surface, hosted in a GTK4 window.

This is the deliverable for openspec change `gtk4-dev-environment`,
capability `casilda-embedded-widget-demo`. It validates the build/embed
toolchain only — it does not attempt to run the full jarabe shell (see
specbook/docs/gtk-porting-standards.md for why that's a separate,
unsolved problem).

Run with:
    LD_LIBRARY_PATH=$HOME/.local/lib \\
    GI_TYPELIB_PATH=$HOME/.local/lib/girepository-1.0 \\
    python3 specbook/demos/casilda_sugar_demo.py
"""

import os
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Casilda", "1.0")
from gi.repository import GLib, Gtk, Casilda

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLKIT_VENV = os.path.join(REPO_ROOT, "repos", "sugar-toolkit-gtk4", ".venv")
ACTIVITY_SCRIPT = os.path.join(
    REPO_ROOT, "repos", "sugar-toolkit-gtk4", "examples", "basic_activity.py"
)


class CasildaSugarDemo(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.sugarlabs.specbook.CasildaSugarDemo")

    def do_activate(self):
        compositor = Casilda.Compositor()

        window = Gtk.ApplicationWindow(
            application=self,
            title="Sugar GTK4 activity, embedded via Casilda",
            default_width=900,
            default_height=700,
            child=compositor,
        )

        venv_python = os.path.join(TOOLKIT_VENV, "bin", "python3")

        # SimpleActivity expects to be launched as a Sugar bundle; these
        # three vars are what examples/activity/activity.info declares.
        child_env = os.environ.copy()
        child_env["SUGAR_BUNDLE_PATH"] = os.path.dirname(ACTIVITY_SCRIPT)
        child_env["SUGAR_BUNDLE_NAME"] = "Sugar Examples"
        child_env["SUGAR_BUNDLE_ID"] = "org.sugarlabs.SugarExamples"
        envp = [f"{k}={v}" for k, v in child_env.items()]

        ok = compositor.spawn_async(
            os.path.dirname(ACTIVITY_SCRIPT),
            [venv_python, ACTIVITY_SCRIPT],
            envp,
            GLib.SpawnFlags.DEFAULT,
        )
        if not ok:
            print("spawn_async returned False — see stderr for details", file=sys.stderr)

        window.present()


if __name__ == "__main__":
    app = CasildaSugarDemo()
    sys.exit(app.run(sys.argv))
