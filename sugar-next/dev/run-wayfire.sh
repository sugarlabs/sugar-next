#!/usr/bin/env bash
# Run Sugar Next inside a nested Wayfire compositor.
#
# Why: GNOME/Mutter (the usual dev session) does not implement
# zwlr_foreign_toplevel_manager_v1, so Sugar Next can only see two icon
# states there (closed/open). Wayfire is wlroots-based and DOES offer that
# protocol including window focus, so running the shell nested inside it
# exercises the full three-state rendering: greyscale -> color -> focused.
#
# This opens a single Wayfire window inside your current Wayland session;
# Sugar Next autostarts inside it. Close that window to end the session.

set -euo pipefail

DEV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$DEV_DIR/.." && pwd)"

export WLR_WL_OUTPUTS="${WLR_WL_OUTPUTS:-1}"
export WLR_HEADLESS_OUTPUTS="${WLR_HEADLESS_OUTPUTS:-0}"

VENV_PY="${SUGAR_NEXT_PYTHON:-$HOME/.local/share/sugar-next/venv/bin/python3}"
if [ ! -x "$VENV_PY" ]; then
    echo "error: venv python not found at $VENV_PY" >&2
    echo "       set SUGAR_NEXT_PYTHON to override." >&2
    exit 1
fi

if [ -z "${WAYLAND_DISPLAY:-}" ]; then
    echo "error: no WAYLAND_DISPLAY — run this from inside a Wayland session." >&2
    exit 1
fi

# Command Wayfire's autostart will run for the shell. PYTHONPATH points at
# the in-place source so edits take effect without reinstalling.
export SUGAR_NEXT_CMD="cd '$PROJECT_DIR' && GDK_BACKEND=wayland PYTHONPATH='$PROJECT_DIR' '$VENV_PY' -m sugar_next.shell.main"

# With WAYLAND_DISPLAY set, wlroots auto-selects the nested Wayland backend
# (a window in the host session). Avoid adding an output mode here: on wlroots
# 0.19 fixed-mode nested outputs can reject custom modes and disable WL-1.

echo "Starting nested Wayfire; Sugar Next will autostart inside it."
echo "Nested backend outputs: WLR_WL_OUTPUTS=${WLR_WL_OUTPUTS}, WLR_HEADLESS_OUTPUTS=${WLR_HEADLESS_OUTPUTS}"
echo "Close the Wayfire window to exit."
wayfire -c "$DEV_DIR/wayfire.ini"
