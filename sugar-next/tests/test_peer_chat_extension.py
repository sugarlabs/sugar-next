"""Smoke test for the demo peer-chat extension (task 6.5).

Loads two independent copies of the extension's module code (each patched
onto its own UDP port to simulate "two Sugar Next instances"), starts
both, and confirms they discover each other and fire on_peer_join.

Broadcast to 255.255.255.255 does not reliably work in every sandboxed
environment, so this test patches the extension's broadcast destination
to the loopback interface's own broadcast address (127.255.255.255,
which — unlike a plain unicast 127.0.0.1 send — actually fans out to
every socket bound to the port on lo) — it still exercises the real
beacon/receive/join-detection logic, only the destination differs from a
production LAN broadcast.

The extension calls the shared ``sugar_next.api.hooks.registry`` singleton
directly (as it does in the real shell), so both simulated instances
report through the same registry; we distinguish them by peer id instead
of by registry identity.
"""

import importlib.util
import time
from pathlib import Path

from sugar_next.api.hooks import registry as hook_registry

EXAMPLES = Path(__file__).parent.parent / "examples" / "extensions"


def _load_module(tmp_path, name, port):
    source = (EXAMPLES / "peer-chat.py").read_text()
    source = source.replace("_PORT = 21212", f"_PORT = {port}")
    source = source.replace('"255.255.255.255"', '"127.255.255.255"')
    path = tmp_path / f"{name}.py"
    path.write_text(source)

    spec = importlib.util.spec_from_file_location(f"peer_chat_test_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_two_instances_discover_each_other(tmp_path, monkeypatch, capsys):
    port = 21299
    events = []
    monkeypatch.setattr(
        hook_registry,
        "call",
        lambda name, *args, **kw: events.append((name, args)),
    )

    module_a = _load_module(tmp_path, "peer_a", port)
    module_b = _load_module(tmp_path, "peer_b", port)

    try:
        module_a.on_shell_start()
        module_b.on_shell_start()

        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            join_ids = {args[0] for name, args in events if name == "on_peer_join"}
            if module_a._peer_id in join_ids and module_b._peer_id in join_ids:
                break
            time.sleep(0.2)

        join_ids = {args[0] for name, args in events if name == "on_peer_join"}
        assert module_a._peer_id in join_ids, "instance A never saw instance B join"
        assert module_b._peer_id in join_ids, "instance B never saw instance A join"

        capsys.readouterr()  # drain startup/join output before the chat check
        module_a.send_chat("hello from A")

        deadline = time.monotonic() + 5
        received = False
        while time.monotonic() < deadline:
            if "hello from A" in capsys.readouterr().out:
                received = True
                break
            time.sleep(0.1)
        assert received, "instance B never printed instance A's chat message"
    finally:
        module_a._running = False
        module_b._running = False
        module_a._sock.close()
        module_b._sock.close()
