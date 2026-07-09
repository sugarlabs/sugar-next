from sugar_next.shell.settings_store import SettingsStore, icon_size_px


def test_defaults(tmp_path):
    store = SettingsStore(tmp_path / "settings.json")
    assert store.get("contrast") == "normal"
    assert store.get("icon_size") == "medium"
    assert store.get("home_view_layout") == "app-grid"
    assert store.get("accent_color") is None
    assert store.get("background_path") is None


def test_set_persists_and_reloads(tmp_path):
    path = tmp_path / "settings.json"
    store = SettingsStore(path)
    store.set("accent_color", "#ff00ff")
    store.set("icon_size", "large")

    reloaded = SettingsStore(path)
    assert reloaded.get("accent_color") == "#ff00ff"
    assert reloaded.get("icon_size") == "large"


def test_set_unknown_key_raises(tmp_path):
    store = SettingsStore(tmp_path / "settings.json")
    try:
        store.set("does-not-exist", 1)
        assert False, "expected KeyError"
    except KeyError:
        pass


def test_icon_size_px():
    assert icon_size_px("small") < icon_size_px("medium") < icon_size_px("large")
    assert icon_size_px("bogus") == icon_size_px("medium")
