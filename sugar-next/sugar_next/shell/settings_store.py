"""Persistence for Settings-panel preferences.

A flat JSON file under XDG config, written whenever a Settings control
changes. Kept intentionally simple — no schema migration machinery, since
the preference set is small and additive.
"""

import json
import os
from pathlib import Path

_DEFAULTS = {
    "background_path": None,
    "accent_color": None,
    "contrast": "normal",  # "normal" | "high"
    "icon_size": "medium",  # "small" | "medium" | "large"
    "home_view_layout": "desktop-grid",
    # Background wash applied over the wallpaper, under every Home View
    # layout. brightness: -1.0 (black) .. 0 .. +1.0 (white).
    # contrast: 0.0 (none) .. 1.0 (flat mid-grey veil).
    "bg_brightness": -0.25,
    "bg_contrast": 0.0,
    # saturation: 0.0 (greyscale) .. 1.0 (full color).
    # vignette: 0.0 (off) .. 1.0 (fully black edges).
    "bg_saturation": 1.0,
    "bg_vignette": 0.0,
}

_ICON_SIZES = {"small": 32, "medium": 48, "large": 64}


def config_dir() -> Path:
    config_home = os.environ.get(
        "XDG_CONFIG_HOME", os.path.expanduser("~/.config")
    )
    return Path(config_home) / "sugar-next"


def settings_file() -> Path:
    return config_dir() / "settings.json"


def icon_size_px(size_name: str) -> int:
    return _ICON_SIZES.get(size_name, _ICON_SIZES["medium"])


class SettingsStore:
    def __init__(self, path=None):
        self._path = path or settings_file()
        self._values = dict(_DEFAULTS)
        self._load()

    def _load(self):
        if not self._path.is_file():
            return
        try:
            data = json.loads(self._path.read_text())
        except ValueError:
            return
        for key in _DEFAULTS:
            if key in data:
                self._values[key] = data[key]
        # Migrate the old single "bg_dim" (0..1 dark overlay) to the new
        # signed brightness control, if the new key was never written.
        if "bg_dim" in data and "bg_brightness" not in data:
            try:
                self._values["bg_brightness"] = -float(data["bg_dim"])
            except (TypeError, ValueError):
                pass

    def save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._values, indent=2))

    def get(self, key):
        return self._values.get(key, _DEFAULTS.get(key))

    def set(self, key, value):
        if key not in _DEFAULTS:
            raise KeyError(f"unknown setting {key!r}")
        self._values[key] = value
        self.save()
