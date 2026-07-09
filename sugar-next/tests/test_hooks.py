from sugar_next.api.hooks import HookRegistry, list_extensions, set_extension_enabled


def _write(directory, name, body):
    path = directory / name
    path.write_text(body)
    return path


def _tracer(directory, filename, out_name):
    """Extension body that appends hook calls to a trace file."""
    trace = directory / out_name
    body = (
        f"TRACE = {str(trace)!r}\n"
        "def _log(what):\n"
        "    with open(TRACE, 'a') as f:\n"
        "        f.write(what + '\\n')\n"
        "def on_shell_start():\n"
        "    _log('start')\n"
        "def on_app_launch(app_id, app_info):\n"
        "    _log('launch:' + app_id)\n"
    )
    _write(directory, filename, body)
    return trace


def _trace_lines(trace):
    return trace.read_text().splitlines() if trace.exists() else []


def test_load_and_call(tmp_path):
    trace = _tracer(tmp_path, "good.py", "good.trace")
    registry = HookRegistry()
    registry.load(tmp_path)
    registry.call("on_shell_start")
    registry.call("on_app_launch", "foo.desktop", None)
    assert _trace_lines(trace) == ["start", "launch:foo.desktop"]


def test_broken_extension_is_isolated(tmp_path):
    _write(tmp_path, "broken.py", "raise RuntimeError('boom')\n")
    trace = _tracer(tmp_path, "works.py", "works.trace")
    registry = HookRegistry()
    registry.load(tmp_path)
    registry.call("on_shell_start")
    assert _trace_lines(trace) == ["start"]


def test_failing_hook_does_not_break_others(tmp_path):
    _write(
        tmp_path,
        "a_fails.py",
        "def on_shell_start():\n"
        "    raise ValueError('hook error')\n",
    )
    trace = _tracer(tmp_path, "b_works.py", "b.trace")
    registry = HookRegistry()
    registry.load(tmp_path)
    registry.call("on_shell_start")
    assert _trace_lines(trace) == ["start"]


def test_missing_directory_is_fine(tmp_path):
    registry = HookRegistry()
    registry.load(tmp_path / "does-not-exist")
    registry.call("on_shell_start")


def test_dashed_filenames(tmp_path):
    trace = _tracer(tmp_path, "my-ext.py", "my-ext.trace")
    registry = HookRegistry()
    registry.load(tmp_path)
    registry.call("on_shell_start")
    assert _trace_lines(trace) == ["start"]


def test_peer_and_app_close_hooks(tmp_path):
    trace = tmp_path / "peer.trace"
    body = (
        f"TRACE = {str(trace)!r}\n"
        "def _log(what):\n"
        "    with open(TRACE, 'a') as f:\n"
        "        f.write(what + '\\n')\n"
        "def on_peer_join(peer_id, peer_name):\n"
        "    _log('join:' + peer_id + ':' + peer_name)\n"
        "def on_peer_leave(peer_id):\n"
        "    _log('leave:' + peer_id)\n"
        "def on_app_close(app_id, app_info):\n"
        "    _log('close:' + app_id)\n"
    )
    _write(tmp_path, "peer-ext.py", body)
    registry = HookRegistry()
    registry.load(tmp_path)
    registry.call("on_peer_join", "peer1", "Ada")
    registry.call("on_peer_leave", "peer1")
    registry.call("on_app_close", "foo.desktop", None)
    assert _trace_lines(trace) == [
        "join:peer1:Ada",
        "leave:peer1",
        "close:foo.desktop",
    ]


def test_internal_listener_fires_alongside_extensions(tmp_path):
    trace = _tracer(tmp_path, "ext.py", "ext.trace")
    registry = HookRegistry()
    registry.load(tmp_path)

    internal_calls = []
    registry.subscribe("on_shell_start", lambda: internal_calls.append("internal"))
    registry.call("on_shell_start")

    assert internal_calls == ["internal"]
    assert _trace_lines(trace) == ["start"]


def test_internal_listener_survives_reload(tmp_path):
    registry = HookRegistry()
    registry.load(tmp_path)

    calls = []
    registry.subscribe("on_app_close", lambda app_id, app_info: calls.append(app_id))

    # Reloading extensions (e.g. after installing a new one) must not
    # drop internal shell listeners.
    registry.load(tmp_path)
    registry.call("on_app_close", "foo.desktop", None)

    assert calls == ["foo.desktop"]


def test_failing_internal_listener_does_not_block_others(tmp_path):
    registry = HookRegistry()
    registry.load(tmp_path)

    calls = []
    registry.subscribe("on_shell_start", lambda: (_ for _ in ()).throw(RuntimeError))
    registry.subscribe("on_shell_start", lambda: calls.append("second"))
    registry.call("on_shell_start")

    assert calls == ["second"]


def test_list_extensions_empty_directory(tmp_path):
    assert list_extensions(tmp_path / "does-not-exist") == []
    tmp_path.mkdir(exist_ok=True)
    assert list_extensions(tmp_path) == []


def test_list_extensions_mixed_enabled_disabled(tmp_path):
    _write(tmp_path, "logger.py", "")
    _write(tmp_path, "journal.py.disabled", "")
    assert list_extensions(tmp_path) == [
        ("journal", False),
        ("logger", True),
    ]


def test_set_extension_enabled_disables_and_reenables(tmp_path):
    _write(tmp_path, "logger.py", "def on_shell_start(): pass\n")

    set_extension_enabled("logger", False, tmp_path)
    assert list_extensions(tmp_path) == [("logger", False)]
    assert (tmp_path / "logger.py").exists() is False
    assert (tmp_path / "logger.py.disabled").exists() is True

    set_extension_enabled("logger", True, tmp_path)
    assert list_extensions(tmp_path) == [("logger", True)]
    assert (tmp_path / "logger.py").exists() is True


def test_set_extension_enabled_is_idempotent(tmp_path):
    _write(tmp_path, "logger.py", "")
    # Already enabled — enabling again should not raise or lose the file.
    set_extension_enabled("logger", True, tmp_path)
    assert list_extensions(tmp_path) == [("logger", True)]

    set_extension_enabled("logger", False, tmp_path)
    # Already disabled — disabling again should not raise.
    set_extension_enabled("logger", False, tmp_path)
    assert list_extensions(tmp_path) == [("logger", False)]


def test_disabled_extension_is_not_loaded(tmp_path):
    trace = _tracer(tmp_path, "works.py", "works.trace")
    set_extension_enabled("works", False, tmp_path)

    registry = HookRegistry()
    registry.load(tmp_path)
    registry.call("on_shell_start")

    assert _trace_lines(trace) == []

    set_extension_enabled("works", True, tmp_path)
    registry.load(tmp_path)
    registry.call("on_shell_start")

    assert _trace_lines(trace) == ["start"]
