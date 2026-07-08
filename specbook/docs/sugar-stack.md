# Sugar Stack — Repo Map

Snapshot of the Sugar Labs repo landscape, as researched 2026-07-08. This is
a map for orientation, not a live status page — verify current state
(`git log`, issue trackers) before relying on specifics here for decisions.

## Core repos

| Repo | Role | Build system | Notes |
|---|---|---|---|
| [`sugar`](https://github.com/sugarlabs/sugar) | The GTK shell itself (`jarabe`): desktop/home view, frame, journal UI, control panel, activity launching | Autotools (`autogen.sh` → `configure` → `make install`) | 90 open issues. Home of the stalled GTK4 port, [PR #1019](https://github.com/sugarlabs/sugar/pull/1019) — see [[gtk-porting-standards]]. |
| [`sugar-toolkit-gtk3`](https://github.com/sugarlabs/sugar-toolkit-gtk3) | Activity Toolkit (`sugar3`) — the API activities are built against, current stable | Autotools, Python 3 | Legacy toolkit; activities still target this. |
| [`sugar-toolkit-gtk4`](https://github.com/sugarlabs/sugar-toolkit-gtk4) | Ground-up reimplementation of the toolkit using GTK4 and modern Python practices | `pip install -e .` + Makefile (`make install`, `make test`, `make test-coverage`, `make format`, `make build`) | **Most active repo in the org** — pushed same week as this research. This is where GTK4 momentum actually lives, even though the shell-level port (`sugar` PR #1019) stalled. |
| [`sugar-datastore`](https://github.com/sugarlabs/sugar-datastore) | Journal's storage backend/service | Autotools | |
| [`sugar-artwork`](https://github.com/sugarlabs/sugar-artwork) | Icons and themes | Autotools | Relevant input for [[design-system]] work — decide reuse vs. redesign per-icon, not wholesale. |
| [`sugar-docs`](https://github.com/sugarlabs/sugar-docs) | Contributor/developer documentation | — | Includes `docs/development-environment.md`, the canonical setup guide. |

## Supporting / adjacent

- **`sugar-toolkit`** — Python 2 toolkit, legacy, not a target for new work.
- **`sugar-live-build`** — builds the ~1GB bootable Sugar Live ISO/VM used as
  the recommended dev environment for anyone touching Sugar core or the
  toolkits. Config in `src/config/hooks/normal/0900-sugar.hook.chroot`.
- **`sugar-ext`** — helper repo needed to fully test the GTK4 shell port.
- **Activity repos** (`browse-activity`, `terminal-activity`,
  `musicblocks`/`musicblocks-v4`, `turtleart-activity`, `Pippy`,
  `jukebox-activity`, `log-activity`, `sugar-ai`, dozens more) — wildly
  uneven activity, from "pushed this week" to years dormant. Not in scope
  for this workspace's first cycle.

## Three ways to get a dev environment running

(from `sugar-docs/docs/development-environment.md`)

1. **Sugar Live Build** — pre-built ISO/VM with source trees under
   `/usr/src` and binaries already installed. Recommended for anyone
   changing Sugar core or the toolkits.
2. **Packaged Sugar** (`sucrose` via apt/dnf) — for activity development
   only, doesn't touch Sugar core.
3. **Native build** ("for experts") — clone each module as a sibling, install
   build deps per module (`apt build-dep` / `dnf builddep`, plus
   `python3-six`, `python3-empy`), then per module:
   `./autogen.sh --with-python3` → `make` → `sudo make install`. Finish by
   symlinking PolicyKit files and cloning Browse/Terminal activities into
   `~/Activities/`.

See the `setup-sugar-workspace` skill for automating option 3 in this
workspace's `repos/` directory.

## Relationship to this workspace

`repos/` (sibling to `specbook/` and `openspec/`) is where the actual Sugar
repos get cloned when work starts on them.

**Currently cloned** (as of the `gtk4-dev-environment` and
`windowed-jarabe` changes, 2026-07-08): `repos/casilda` (GNOME's
compositor widget, not a Sugar repo but needed for GTK4 dev environment
work), `repos/sugar-toolkit-gtk4` (with a `.venv` using
`--system-site-packages`), `repos/sugar` (gtk4-port branch), and
`repos/sugar-toolkit-gtk3` (cloned read-only, to reference its C source
for `SugarExt`/`SugarGestures` while writing `sugar4/ext.py` and
`sugar4/activity/activityfactory.py`/`i18n.py` ports — not built from
this checkout, the compiled binding comes from the Arch package instead).
See [[gtk-porting-standards]] for the working build/run procedure — as
of `windowed-jarabe`, jarabe's onboarding screen renders successfully in
a nested Wayfire session.

**System packages installed** for this work: `wlroots0.20`, `gtk4-demos`,
`wayfire` (+ `wf-config`, `wlroots0.19` — note the *different* wlroots
version than Casilda's, since Wayfire and Casilda each pin their own),
`sugar-toolkit-gtk3` (for its compiled `SugarExt-1.0` GObject
Introspection binding — installed standalone, without the full `sugar`
package/session), `python-gwebsockets` (for `jarabe/apisocket.py`).
