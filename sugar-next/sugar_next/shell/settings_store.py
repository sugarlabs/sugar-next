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
    "home_view_layout": "app-grid",
    "bg_dim": 0.25,  # 0.0–1.0 — dark overlay over background for label contrast
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
