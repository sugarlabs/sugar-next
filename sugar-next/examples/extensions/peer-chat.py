"""OUT OF SCOPE reference extension — not the planned collaboration path.

This was a throwaway UDP-broadcast prototype written to prove the
on_peer_join/on_peer_leave hook shape (see api/hooks.py) before real
presence work started. The actual plan is XMPP-based presence (possibly
integrating with Gajim), not this ad-hoc protocol — do not install this
in ~/.local/share/sugar-next/extensions/ as a real collaboration feature.

Kept here only as a worked example of consuming on_peer_join/
on_peer_leave from an extension. Delete once a real XMPP presence
extension exists to demonstrate the same hooks.

Transport notes from this prototype (for context, not a recommendation):
plain UDP broadcast on the local subnet, since no Avahi/DNS-SD Python
bindings were reliably available. Each instance broadcasts a "hello"
beacon periodically and listens for others; a peer that stops beaconing
is considered gone. Chat is a second UDP message type — never wired to
any UI.
"""

import json
import os
import socket
import threading
import time
import uuid

_PORT = 21212
_BEACON_INTERVAL = 3.0
_PEER_TIMEOUT = 9.0

_peer_id = uuid.uuid4().hex[:8]
_peer_name = os.environ.get("USER", "learner") + "-" + _peer_id
_known_peers = {}  # peer_id -> (address, last_seen)
_hook_registry = None  # set in on_shell_start via lazy import
_running = False
_sock = None


def _get_hook_registry():
    global _hook_registry
    if _hook_registry is None:
        from sugar_next.api.hooks import registry

        _hook_registry = registry
    return _hook_registry


def _make_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # SO_REUSEADDR alone does not let two sockets on the same host both
    # receive the same broadcast datagram on Linux; SO_REUSEPORT does.
    # This mainly matters for testing two "instances" on one machine —
    # real deployments are one instance per device.
    if hasattr(socket, "SO_REUSEPORT"):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", _PORT))
    sock.settimeout(1.0)
    return sock


def _beacon_loop():
    beacon = json.dumps({"type": "hello", "id": _peer_id, "name": _peer_name})
    while _running:
        try:
            _sock.sendto(beacon.encode(), ("255.255.255.255", _PORT))
        except OSError:
            pass
        time.sleep(_BEACON_INTERVAL)


def _receive_loop():
    registry = _get_hook_registry()
    while _running:
        try:
            data, addr = _sock.recvfrom(4096)
        except socket.timeout:
            _expire_peers(registry)
            continue
        except OSError:
            break
        try:
            message = json.loads(data.decode())
        except ValueError:
            continue
        _handle_message(message, addr, registry)


def _handle_message(message, addr, registry):
    peer_id = message.get("id")
    if peer_id is None or peer_id == _peer_id:
        return
    if message.get("type") == "hello":
        is_new = peer_id not in _known_peers
        _known_peers[peer_id] = (addr, time.monotonic())
        if is_new:
            registry.call("on_peer_join", peer_id, message.get("name", peer_id))
    elif message.get("type") == "chat":
        print(f"[peer-chat] {message.get('name', peer_id)}: {message.get('text', '')}")


def _expire_peers(registry):
    now = time.monotonic()
    expired = [
        peer_id
        for peer_id, (_, last_seen) in _known_peers.items()
        if now - last_seen > _PEER_TIMEOUT
    ]
    for peer_id in expired:
        del _known_peers[peer_id]
        registry.call("on_peer_leave", peer_id)


def send_chat(text):
    """Send *text* to every currently known peer. Callable from a UI."""
    message = json.dumps(
        {"type": "chat", "id": _peer_id, "name": _peer_name, "text": text}
    )
    for addr, _ in _known_peers.values():
        try:
            _sock.sendto(message.encode(), addr)
        except OSError:
            pass


def on_shell_start():
    global _running, _sock
    if _running:
        return
    _sock = _make_socket()
    _running = True
    threading.Thread(target=_beacon_loop, daemon=True).start()
    threading.Thread(target=_receive_loop, daemon=True).start()
    print(f"[peer-chat] started as {_peer_name} (id={_peer_id})")
