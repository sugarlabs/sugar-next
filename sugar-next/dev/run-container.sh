#!/usr/bin/env bash
# Run Sugar Next from an OCI container against the host Wayland session.

set -euo pipefail

DEV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$DEV_DIR/.." && pwd)"

ENGINE="${SUGAR_NEXT_CONTAINER_ENGINE:-podman}"
IMAGE="${SUGAR_NEXT_CONTAINER_IMAGE:-sugar-next:dev}"
RUNTIME_DIR="${SUGAR_NEXT_CONTAINER_RUNTIME_DIR:-/tmp/sugar-next-runtime}"

if ! command -v "$ENGINE" >/dev/null 2>&1; then
    echo "error: container engine '$ENGINE' not found" >&2
    echo "       set SUGAR_NEXT_CONTAINER_ENGINE=docker to use Docker." >&2
    exit 1
fi

if [ -z "${WAYLAND_DISPLAY:-}" ] || [ -z "${XDG_RUNTIME_DIR:-}" ]; then
    echo "error: WAYLAND_DISPLAY and XDG_RUNTIME_DIR must be set." >&2
    echo "       run this from a graphical Wayland session." >&2
    exit 1
fi

WAYLAND_SOCKET="$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY"
if [ ! -S "$WAYLAND_SOCKET" ]; then
    echo "error: Wayland socket not found: $WAYLAND_SOCKET" >&2
    exit 1
fi

if [ "${SUGAR_NEXT_CONTAINER_BUILD:-1}" = "1" ]; then
    "$ENGINE" build -t "$IMAGE" -f "$PROJECT_DIR/Containerfile" "$PROJECT_DIR"
fi

mkdir -p "$RUNTIME_DIR"

RUN_ARGS=(run --rm -it --name sugar-next-dev)
if [ "$ENGINE" = "podman" ]; then
    RUN_ARGS+=(--userns=keep-id --group-add keep-groups --security-opt label=disable)
else
    RUN_ARGS+=(--user "$(id -u):$(id -g)")
fi

exec "$ENGINE" "${RUN_ARGS[@]}" \
    -e WAYLAND_DISPLAY="$WAYLAND_DISPLAY" \
    -e XDG_RUNTIME_DIR="$RUNTIME_DIR" \
    -e XDG_CURRENT_DESKTOP="${XDG_CURRENT_DESKTOP:-SugarNext}" \
    -e PYTHONPATH=/workspace/sugar-next \
    -v "$WAYLAND_SOCKET:$RUNTIME_DIR/$WAYLAND_DISPLAY" \
    -v "$PROJECT_DIR:/workspace/sugar-next" \
    --device /dev/dri \
    -w /workspace/sugar-next \
    "$IMAGE" \
    python3 -m sugar_next.shell.main
