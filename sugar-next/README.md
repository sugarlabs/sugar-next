# Sugar Next — A Learning Shell for Everyday Computing

## What this is

Sugar Next is a **sibling project** to the classic Sugar desktop, not a fork
and not a replacement. It lives under the [Sugar Labs](https://www.sugarlabs.org/)
umbrella and leaves the `sugar` (jarabe) repository completely untouched.
PR #1019 (the GTK4 port of the classic shell) continues on its own track.

Sugar Next is a place to explore what a modern, low-floor learning
environment could look like — using the technologies available today
(GTK4, Wayland, Python, XDG) — while the classic stack continues to serve
the XO hardware and existing deployments.

## Rationale

Sugar's founding insight was the **low floor**: a child could look inside
their computer and change it. Twenty years on, the stack that carried that
idea has quietly raised the floor out of reach:

- **GTK3 + X11** — both deprecated upstream. The GTK4 port of the shell
  (PR #1019) stalled on environment friction, not on technical difficulty:
  nobody could easily *run* what they were porting.
- **Autotools** — a build system most of today's contributors have never
  seen.
- **The activities-only bubble** — the shell only shows XO-style bundles.
  Firefox, the terminal, GIMP: invisible. The user is isolated from their
  own computer.
- **A high barrier for creators** — writing a Sugar activity means
  learning GObject Introspection, the activity lifecycle, D-Bus, and the
  build system before printing "hello".
- **No reproducible dev environment** — the recommended setup is a 1 GB
  Live ISO tied to a specific distro version.

The community is active — the energy exists. Sugar Next is a place to
point some of it at *evolving* the environment instead of only maintaining
it.

Full design principles: [HIG.md](HIG.md).

### What Sugar Next deliberately does not do

- Touch the `sugar` repo, jarabe, or PR #1019 — the legacy shell stays
  exactly as it is.
- Migrate existing XO activities to a new API (a compat layer may come
  later, if the community wants it).
- Reimplement legacy mesh collaboration (the protocols are specific to the
  XO hardware and are not being recreated here).

## Status

This is a **rapid prototype**. Things change fast, break, and get rewritten
as we learn what works. We use [OpenSpec](https://github.com/Fission-AI/OpenSpec)
to track every change — see `openspec/changes/` for the active proposals,
designs, and task lists. If something doesn't work, **that is expected**,
and a fix is probably already in progress.

**The developer experience is a pillar of this project.** Sugar Next aims
to be as easy to hack on as it is to use. If setting up the dev
environment, running tests, or understanding the code feels harder than it
should, that is a bug — please report it.

## Quick Start

Requires GTK4 and PyGObject from your distro:

| Distro | Command |
|--------|---------|
| Fedora | `sudo dnf install python3-gobject gtk4` |
| Debian/Ubuntu | `sudo apt install python3-gi gir1.2-gtk-4.0` |
| Arch | `sudo pacman -S python-gobject gtk4` |

```sh
git clone https://github.com/sugarlabs/sugar-next.git
cd sugar-next/sugar-next
./bootstrap.sh
sugar-next
```

> Note: in this monorepo, `sugar-next/` is the actual project directory.
> Most commands below assume you are either in that directory or using the
> repository root paths shown by the VS Code tasks.

## Startup Modes

Sugar Next supports exactly two ways to run — no nested-compositor dev
indirection in between (see `HIG.md`'s "Startup modes and window
observation" and the `casilda-activity-host` change for the full design):

| Mode | How | Window data source |
| --- | --- | --- |
| **Hosted** (primary dev environment) | Run normally inside a GNOME session — `sugar-next` or `PYTHONPATH=. python -m sugar_next.shell.main` | `sugar-next-windows` GNOME Shell extension (installed by `bootstrap.sh`) |
| **Standalone** | The shell as a Wayfire session's own client — see `session/wayfire.ini` | `wlr-foreign-toplevel-management` (native to Wayfire) |

`bootstrap.sh` detects which mode applies and prepares it — installing and
enabling the GNOME Shell extension on a GNOME session, or pointing to
`session/wayfire.ini` otherwise. Neither mode requires Sugar Next to own
window placement or tiling; that stays with GNOME or Wayfire.

| VS Code task / launch config | Command | Use when |
| --- | --- | --- |
| `Run Sugar Next` / `Sugar Next (editable src)` | `PYTHONPATH=. python -m sugar_next.shell.main` | Hosted-mode local run inside GNOME |
| `Run Sugar Next (container)` | `dev/run-container.sh` | Run from an OCI image against the host Wayland socket |
| `Bootstrap Sugar Next` | `./bootstrap.sh` | Install into `~/.local/share/sugar-next/venv`, create a desktop entry, set up hosted-mode window observation |
| `Test Sugar Next` | `python -m pytest tests/` | Run the shell test suite |

Install `debugpy` once if you want the debugpy launch configs:

```sh
~/.local/share/sugar-next/venv/bin/pip install debugpy
```

## Container Run

The container runner builds `sugar-next:dev` and runs the editable source
tree against your host Wayland socket:

```sh
dev/run-container.sh
```

Requirements:

| Tool | Notes |
| --- | --- |
| Podman | Default engine. Use `SUGAR_NEXT_CONTAINER_ENGINE=docker` for Docker. |
| Wayland session | `WAYLAND_DISPLAY` and `XDG_RUNTIME_DIR` must be set. |
| GPU device access | The runner passes `--device /dev/dri`. |

Useful overrides:

```sh
SUGAR_NEXT_CONTAINER_BUILD=0 dev/run-container.sh
SUGAR_NEXT_CONTAINER_IMAGE=sugar-next:test dev/run-container.sh
SUGAR_NEXT_CONTAINER_ENGINE=docker dev/run-container.sh
```

Manual equivalent:

```sh
podman build -t sugar-next:dev -f Containerfile .
dev/run-container.sh
```

If rootless Podman networking fails after a kernel update with a `pasta` or
`/dev/net/tun` error, rebuild once with:

```sh
podman build --network=host -t sugar-next:dev -f Containerfile .
```

## Acknowledgements

- **James Cameron (Quozl)** — for the green light to bring Sugar Next under
  the Sugar Labs umbrella, and for his decades of stewardship of the Sugar
  platform.
- **Walter Bender** — for the original vision of Sugar, and for keeping the
  educational mission alive through all these years.
- **Martin Abente (tchx84)** — for the Sugarapp/Flatpak work that proved
  Sugar activities can live outside the classic shell, and for Endless OS
  inspiration.
- **Ted Hein and Repurpose-IT** — for recognising the advantages of free
  software for the benefit of indigenous communities, and for providing
  hardware support and a real deployment target.
- **The Sugar Labs community** — the GSoC students, the sugar-devel
  regulars, and everyone who has contributed to keeping this project going
  since 2006.

License: GPL-3.0-or-later, like the rest of Sugar.
