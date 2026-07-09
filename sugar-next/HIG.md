# Sugar Next HIG — Human Interface Guidelines

*A Learning Shell for Everyday Computing*

## Principles

### 1. The Home View is yours

The Home View is the learner's personal space. It can be:
- A **desktop grid** like Endless OS or Android — icons on a background
- A **full-screen app grid** like the current prototype
- A **folder container** layout where apps group into category folders
- A **simple search bar** with results (minimalist, no icons visible until you search)

The layout is always the learner's choice — no deployer or institution
overrides it. The Home View supports **custom background images**,
**accent colors**, and **icon size** preferences.

### 2. The four views

Sugar Next reimagines Sugar's classic four-view model (Neighborhood,
Groups, Home, Activity) as a spatial metaphor the learner navigates:

| View | Sugar classic | Sugar Next |
|------|---------------|------------|
| **Focus** | Fullscreen activity window | Any app window, fullscreen or tiled |
| **Home** | Activity grid (the "mesh" view) | The configurable Home View — app grid, desktop, or search |
| **Groups** | Shared activities with friends | Named, sharable contexts — an activity as a *temporal workspace* that can span multiple apps and people |
| **Neighborhood** | Peer discovery on LAN | Presence bus — link-local + federated peer list |

Transitions between views are smooth and keyboard-navigable (e.g. F6 for
Frame, F7 for Groups, F8 for Neighborhood).

### 3. Collaboration is central

Computing is social, not solitary. The shell makes peers discoverable and
communication effortless — link-local (zero-config, no server, no account)
for the classroom and the home; federated (XMPP) for schools with
infrastructure. Collaboration is not a "feature" of an activity; it is a
property of the environment. Every app can be shared because the shell
provides the substrate.

**Near-term scope**: presence hooks in the extension API
(`on_peer_join`, `on_peer_leave`) and a demo chat extension. Full XMPP
infrastructure is a future phase, pending research on what is pragmatic
to deliver.

### 4. Color is meaningful

Color communicates state, not decoration. The shell respects the system
light/dark preference and adds high-contrast control. The active
application's palette may influence the shell's chrome — the Frame, the
Home View background — so the learner always knows where their attention
is. Profile colors (XO-style) are a future possibility for multi-user
sessions.

End-user color customization: accent color, background image, and
contrast level are available from a Settings panel.

### 5. Flow is protected

The shell never interrupts. No prompts, no dialogs, no "did you know"
popups. Reflection is *facilitated*, not forced — the Journal exists to be
consulted, not to notify. The learner decides when to look back.

### 6. Tasks are multi-application

Modern work flows across apps. The Frame shows everything running, not
just "the current activity". The Journal crosses app boundaries: "what was
I working on?" is a question about *state of the system*, not about which
app was in focus.

### 7. Low floor, wide walls, high ceiling

- **Low floor:** an extension is a `.py` file in a folder. No build system,
  no registration, no GObject.
- **Wide walls:** the same hook system powers logging, counting, a SQLite
  journal, and eventually collaborative sharing.
- **High ceiling:** the extension API exposes enough to build real
  tooling. The Journal itself is an extension. There is no privileged
  internal API.

### 8. The environment is malleable

Every part of the shell that can be an extension, should be. Learners who
want to look inside find plain Python files, not compiled binaries. The
shell's behavior is discoverable and changeable by its users.

### 9. Opt-in, never opt-out

Every layer beyond the Home View is a choice: Journal, collaboration,
favorites sync, activity model. Installing an extension *is* the act of
opting in. The base shell is complete on its own.

## Color system

| Token | Usage |
|-------|-------|
| `--sn-bg` | Shell background (adapts to light/dark) |
| `--sn-bg-alt` | Frame bar, search bar background |
| `--sn-accent` | Active highlight, selection |
| `--sn-text` | Primary text |
| `--sn-text-secondary` | Labels, metadata |
| `--sn-surface` | Card backgrounds (grid cells) |

The shell reads the system `prefers-color-scheme` and sets these tokens
accordingly. Users may override via `~/.config/sugar-next/colors.css` or
the Settings panel.

## Home View layouts

Three built-in layouts, with the ability to write custom layouts as
extensions:

1. **Desktop grid** (Endless-inspired) — icons float on a background
   image. Supports container folders that expand into sub-grids. Default
   for full-shell mode.

2. **App Grid** (current prototype) — a `Gtk.FlowBox` with search bar,
   no background image visible behind icons. Default for windowed mode.

3. **Search-first** — no icons visible until you type. Clean slate,
   minimal distraction.

Layouts are selected from Settings, always by the learner.

## Settings panel

The shell provides a minimal Settings panel (accessible from the Frame or
a keybinding):

- **Background**: choose an image file or solid color
- **Accent color**: pick from presets or custom
- **Contrast**: slider from normal to high
- **Home View layout**: Desktop grid / App Grid / Search-first
- **Extensions**: list installed extensions, enable/disable
- **About**: version, license

## XDG FreeDesktop compliance

Sugar Next aims to be a good citizen in the FreeDesktop ecosystem:

- `.desktop` file installed by `bootstrap.sh` (done)
- XDG Desktop Menu spec for app scanning (done)
- XDG Base Directory spec (`~/.local/share/sugar-next/`, `~/.config/sugar-next/`)
- `org.sugarlabs.SugarNext` D-Bus name (future)
- `wlr-foreign-toplevel-management` protocol for window listing (future)
- MIME type associations for Journal entries (future)
- StatusNotifierItem (system tray) for background services (future)

## Activity model (reimagined)

An "Activity" in Sugar Next is not a bundle type. It is a *temporal
context*: a named, sharable workspace that can span multiple apps.

Example: a learner is researching birds. They have a browser tab open, a
terminal with a Python script, and a drawing app. They name this context
"Birds". Sugar Next tracks which apps belong to it, can share the whole
context with a peer, and records it in the Journal as a single episode.

This is future work — the extension API must first prove itself before we
design the context layer. But the principle is set: activities are not
apps, they are *agglomerations of apps in time*.

## Collaboration model (exploratory)

The collaboration model is a design direction, not a committed feature.
It is documented here to guide future research on what is pragmatic:

```
Presence bus (XMPP)
├── link-local: zero-config LAN discovery (Avahi/DNS-SD), no account
├── federated: standard XMPP server for cross-network presence
└── Share substrate exposed via extension API:
    ├── cursor/share
    ├── clipboard exchange
    └── app-level data channels (extensions opt in)
```

The presence bus would be a shell service — it needs to be running for any
app to discover peers. The share substrate is an API that apps call through
extensions, never coupling them to XMPP directly.

First concrete step: an extension hook `on_peer_join`/`on_peer_leave` and
a demo P2P chat extension. Everything beyond that needs real-world
validation.

## Inspirations

- **Endless OS** — desktop-grid launcher, knowledge apps as first-class
  citizens, search-unified UX, offline-first content, container folders,
  immutable base.
- **Sugar (classic)** — four-view model, journal, collaboration as
  default, XO colors, low floor for creators.
- **GNOME** — Wayland-native, GTK4, XDG compliance, accessibility
  infrastructure.
- **elementary OS** — design consistency, HIG-driven development,
  settings simplicity.
