# Sugar Next Next — Tasks

## 1. Home View layout interface

- [x] 1.1 Design `HomeViewLayout` interface (activate/deactivate/root widget)
- [x] 1.2 Adapt `shell/app-grid.py` to implement the layout interface
- [x] 1.3 Implement `shell/desktop-grid.py` (background image, floating
      icons, container folders that expand into sub-grids) — implemented
      and tested, but **parked out of the active Home View** in `main.py`
      (confusing UX as shipped); code stays for later rework, not deleted.
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
- [ ] 6.3 ~~Write demo P2P chat extension~~ — a UDP-broadcast prototype
      was built to validate the on_peer_join/on_peer_leave hook shape,
      then explicitly rejected as out-of-scope (see
      `examples/extensions/peer-chat.py`, kept only as a reference
      example, not installed). Real extension is XMPP-based, not started.
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

## 9. Documentation

- [ ] 9.1 Document the "Groups" view (activities as temporal, sharable
      workspaces spanning multiple apps) as explicit future work in
      `sugar-next/HIG.md` or `specbook/docs/`, gated on the extension API
      proving itself first

## 10. Frame: only show apps with real windows (not out of scope originally —
       added mid-implementation per user feedback: "el shell debería hacer
       como GNOME y mostrar solo lo activo")

- [ ] 10.1 Add `wlr-foreign-toplevel-management` client via `pywayland`,
      gated behind protocol-availability detection (GNOME/Mutter does not
      implement this protocol at all — only wlroots-based compositors
      like Wayfire/Sway do; confirmed via `wayland-info` in this dev
      environment, which shows zero `zwlr_*` interfaces)
- [ ] 10.2 Wire toplevel create/close/title events into the Frame's
      running-apps list, replacing the current "apps launched this
      session" heuristic where the protocol is available
- [ ] 10.3 Fallback to current behavior (session-launched apps only, via
      `on_app_close`) when the protocol is unavailable — never crash or
      show nothing
- [ ] 10.4 Verify against a real Wayfire session (this repo's dev
      environment is GNOME/Mutter and cannot exercise the wlroots path;
      see `wayland-compositor-dev` skill for setting up nested Wayfire)
