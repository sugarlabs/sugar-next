# Sugar Next Next — Tasks

## 1. Home View layout interface

- [x] 1.1 Design `HomeViewLayout` interface (activate/deactivate/root widget)
- [x] 1.2 Adapt `shell/app-grid.py` to implement the layout interface
- [x] 1.3 Implement `shell/desktop-grid.py` (background image, floating
      icons, container folders that expand into sub-grids)
- [x] 1.4 Implement `shell/search-first.py` (blank canvas + search bar)
- [x] 1.5 Wire layout switching at runtime (no restart required)
- [x] 1.6 Smoke test: switch between all three layouts, confirm state
      (search text, scroll position) resets cleanly on switch

## 2. Settings panel

- [x] 2.1 Write `shell/settings.py` — panel shell, accessible from Frame
      or keybinding
- [x] 2.2 Add background image picker (file chooser, stretch/tile option)
- [x] 2.3 Add accent color picker (presets + custom hex)
- [x] 2.4 Add contrast slider (normal → high)
- [x] 2.5 Add icon size control (affects active Home View layout)
- [x] 2.6 Add Home View layout selector
- [x] 2.7 Add extension manager (list installed, enable/disable)
- [x] 2.8 Add keybinding viewer and About section

## 3. Color tokens and theming

- [x] 3.1 Define `--sn-bg`, `--sn-bg-alt`, `--sn-accent`, `--sn-text`,
      `--sn-text-secondary`, `--sn-surface` as a base GTK4 CSS stylesheet
- [x] 3.2 Compute tokens from `prefers-color-scheme` at startup
- [x] 3.3 Load `~/.config/sugar-next/colors.css` as a user override
      (applied after the base sheet)
- [x] 3.4 Implement active-app-palette extraction (dominant color from
      focused app's icon) with static-accent fallback
- [x] 3.5 Wire palette tint into Frame and Home View background

## 4. XDG Base Directory and FreeDesktop compliance

- [x] 4.1 Move config reads/writes to `~/.config/sugar-next/`
- [x] 4.2 Confirm all data writes use `~/.local/share/sugar-next/`
- [x] 4.3 Register `org.sugarlabs.SugarNext` D-Bus name
- [x] 4.4 Add MIME type associations for Journal entries
- [x] 4.5 Expose a StatusNotifierItem for background services (e.g.
      presence bus, when running)

## 6. Peer collaboration (exploratory)

- [x] 6.1 Add `on_peer_join`/`on_peer_leave` hooks to `api/hooks.py`
- [ ] 6.2 Research link-local transport options — **decided: XMPP**, not
      UDP broadcast or WebRTC. Real work is landing XMPP-based presence
      (possibly integrating with Gajim); still needs a proper design
      writeup (transport, library choice — e.g. slixmpp — link-local vs.
      federated).
- [ ] 6.3 Write demo P2P chat extension — a UDP-broadcast prototype
      was built to validate the on_peer_join/on_peer_leave hook shape,
      then explicitly rejected as out-of-scope. Real extension is
      XMPP-based, not started.
- [ ] 6.4 Document the collaboration design (presence bus + share
      substrate) for future phases in `specbook/docs/`
- [ ] 6.5 Smoke test: two instances on the same LAN discover each other
      and exchange presence/chat — pending the real XMPP extension.

## 7. Journal: deeper integration

- [x] 7.1 Add `on_app_close` hook to the extension API
- [x] 7.2 Update the Journal extension to record `kind='close'` entries
- [ ] 7.3 Evaluate Zeitgeist as an event source for the Journal (write up
      feasibility, API surface, effort — adopt/defer/reject recommendation)
- [ ] 7.4 Research integration with Nautilus/file managers for
      Journal-aware file browsing (write-up only, no implementation)

## 8. Community outreach

- [ ] 8.1 Post to sugar-devel with a demo and this change's proposal
- [ ] 8.2 Post to IAEP with educational framing
- [ ] 8.3 Reach out to Walter Bender for feedback

## 9. Extension contract and language backends

- [x] 9.1 Document full extension contract in
      `specs/extensions/contract.md` — all 5 hooks, signatures, lifecycle,
      enable/disable, error isolation, best practices
- [ ] 9.2 Implement gjs backend: spawn `gjs` as subprocess, pass hook
      events as JSON on stdin, collect results from stdout
- [ ] 9.3 Implement generic subprocess backend: any executable in
      `extensions/` (not just `.py`) is spawned and communicated with via
      the JSON/stdio protocol
- [ ] 9.4 Add `on_app_launch` return-value contract: if a hook returns
      `{"cancel": true}`, the launch is blocked (opt-in, backward-compatible)
- [ ] 9.5 Document the subprocess JSON/stdio protocol in `contract.md`
- [ ] 9.6 Write example JS extension (gjs) that logs launches
- [ ] 9.7 Smoke test: Python, gjs, and subprocess extensions all load and
      fire hooks correctly

## 10. Documentation

- [ ] 10.1 Document the "Groups" view (activities as temporal, sharable
      workspaces spanning multiple apps) as explicit future work in
      `sugar-next/HIG.md` or `specbook/docs/`, gated on the extension API
      proving itself first

## 11. Frame: universal window listing

- [x] 11.1 Add `wlr-foreign-toplevel-management` client via `pywayland`,
      gated behind protocol-availability detection (GNOME/Mutter does not
      implement this protocol — only wlroots compositors like Wayfire/Sway
      do). Implemented in `shell/toplevel_tracker.py`; protocol bindings
      hand-generated via `pywayland.scanner` from the upstream
      wlr-protocols XML and vendored in `sugar_next/_wayland_wlr/`.
      `pywayland` added as an optional dependency (`wayland-toplevels` extra).
- [x] 11.2 Wire toplevel create/close/title events into the Frame's
      running-apps list.
- [x] 11.3 Fallback to current behavior (session-launched apps only, via
      `on_app_close`) when the protocol is unavailable.
- [ ] 11.4 Verify against a real Wayfire session (this dev environment is
      GNOME/Mutter and cannot exercise the wlroots path).
