---
name: setup-sugar-workspace
description: Use when the user wants to clone Sugar Labs repos into this workspace's repos/ directory to start hands-on work (porting, building, testing) — not for reading about the stack, which lives in specbook/docs/sugar-stack.md.
metadata:
  author: sugarlabs-specbook
  version: "1.0"
---

# Setup Sugar Workspace

Clones the Sugar Labs repos needed for a given task as siblings under
`repos/`, following the native-build path documented in
`specbook/docs/sugar-stack.md` (itself sourced from
`sugar-docs/docs/development-environment.md`).

## Before running anything

1. Read `specbook/docs/sugar-stack.md` for the current repo map and the
   three setup options (Sugar Live Build / packaged / native).
2. Ask the user which path they want if it's not already clear from context:
   - **Sugar Live Build** — recommended if touching `sugar` core or either
     toolkit; this skill does not automate that (it's a separate VM/ISO
     workflow, config lives in the `sugar-live-build` repo) — point the user
     there instead of improvising a partial native setup.
   - **Native build** — this skill automates the cloning step of this path.
   - **Packaged (`sucrose`)** — only relevant for activity-only work, no
     cloning of Sugar core needed; this skill isn't needed.

## Steps (native build path)

1. Confirm `repos/` exists at the workspace root (sibling to `openspec/`
   and `specbook/`).
2. Ask which repos are actually needed for the task at hand — don't clone
   the whole org speculatively. Common combinations:
   - GTK4 porting work: `sugar`, `sugar-toolkit-gtk4`, `sugar-ext`.
   - Toolkit (GTK3) activity work: `sugar-toolkit-gtk3`.
   - Journal/datastore work: `sugar-datastore`.
3. Clone each needed repo into `repos/<name>` from
   `https://github.com/sugarlabs/<name>`. Use full clones
   (`git clone`, not `--depth`) — shallow clones caused push friction for
   contributors per the PR #1019 discussion in
   `specbook/docs/gtk-porting-standards.md`.
4. For each cloned repo with an `autogen.sh`, do not run
   `make install` automatically — building/installing System-wide files
   requires `sudo` and affects the host system. Surface the exact commands
   to the user and let them run the install step themselves.
5. For `sugar-toolkit-gtk4`, `pip install -e .` is safe to suggest directly
   since it's a user-space editable install — confirm with the user before
   running it if a virtualenv isn't already active.

## Notes

- This skill only sets up source trees. It does not attempt to configure a
  running Sugar session (X11/GDM session picker, or the Casilda/Wayland
  setup needed for GTK4 shell testing) — that's tracked as an open gap in
  `specbook/docs/gtk-porting-standards.md`, not yet solved.
- If the user asks to fully automate the native build including
  `make install`, confirm explicitly first — it writes outside the
  workspace (system dirs, PolicyKit symlinks) and isn't easily reversible.
