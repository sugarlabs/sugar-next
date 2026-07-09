"""Regression test: every config/data path helper must respect
XDG_CONFIG_HOME / XDG_DATA_HOME rather than a hardcoded home path.
"""

from sugar_next.api.hooks import extensions_dir
from sugar_next.shell.frame import _favorites_file
from sugar_next.shell.settings_store import config_dir as settings_config_dir
from sugar_next.shell.theme import config_dir as theme_config_dir


def test_data_paths_respect_xdg_data_home(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    assert str(extensions_dir()).startswith(str(tmp_path))
    assert str(_favorites_file()).startswith(str(tmp_path))


def test_config_paths_respect_xdg_config_home(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert str(settings_config_dir()).startswith(str(tmp_path))
    assert str(theme_config_dir()).startswith(str(tmp_path))
