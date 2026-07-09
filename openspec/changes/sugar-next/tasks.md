# Sugar Next — Tasks

## Fase 1: Shell mínimo + App Grid

- [x] **1.1** Create `sugar-next/` directory structure under monorepo root
- [x] **1.2** Write `shell/main.py` — minimal GTK4 app that opens a window
- [x] **1.3** Write `bundles/desktop-bundle.py` — wrapper for `.desktop` files
- [x] **1.4** Write `shell/app-grid.py` — `Gtk.FlowBox` listing apps from XDG
- [x] **1.5** Wire launch: click icon → `Gio.AppInfo.launch()`
- [x] **1.6** Add search bar filtering
- [x] **1.7** Add `pyproject.toml` for `sugar-next/` as installable Python package
- [x] **1.8** Smoke test: shell starts, shows apps, clicking launches Firefox

## Fase 2: API de extensiones

- [x] **2.1** Design hook interface (start with `on_app_launch`)
- [x] **2.2** Write `api/hooks.py` — scanner + caller for extension `.py` files
- [x] **2.3** Write 2 example extensions (logger, launcher-counter)
- [x] **2.4** Wire hooks into the app launch pipeline
- [x] **2.5** Document the extension API in `specbook/docs/`

## Fase 3: Frame universal

- [x] **3.1** Design Frame widget (icons, hot-corner, keybinding)
- [x] **3.2** Write `shell/frame.py` — basic window switcher
- [x] **3.3** Integrate with app grid: "Pin to Frame favorites"
- [x] **3.4** Per-window palette (placeholder actions)

## Fase 4: Journal opt-in + packaging

- [x] **4.1** Design Journal extension API
- [x] **4.2** Write Journal extension (SQLite backend)
- [x] **4.3** Create OCI image for `podman run`
- [x] **4.4** Write minimal `bootstrap.sh` — `pip install` + `.desktop` entry
- [x] **4.5** Write documentation + demo video (README + extension API doc + `sugar-next/docs/demo.mp4`)

## Fase 5: Home View, Settings, and customization

- [ ] **5.1** Design pluggable Home View interface (desktop grid, app grid, search-first)
- [ ] **5.2** Implement desktop-grid layout (Endless-inspired: background, floating icons, container folders)
- [ ] **5.3** Implement app-grid layout (port from current prototype)
- [ ] **5.4** Implement search-first layout (blank + search bar)
- [ ] **5.5** Write Settings panel (background, accent, contrast, layout selector, extensions)
- [ ] **5.6** Add background image support and accent color picker
- [ ] **5.7** Add XDG Base Directory compliance (`~/.config/sugar-next/`, `~/.local/share/sugar-next/`)
- [ ] **5.8** Write layout switcher UI in Settings
- [ ] **5.9** Allow layouts as extensions
- [ ] **5.10** Support school-locked layouts via config file

## Fase 6: Colaboración (exploratoria)

- [ ] **6.1** Add `on_peer_join`/`on_peer_leave` hooks to extension API
- [ ] **6.2** Write demo P2P chat extension (link-local, no account needed)
- [ ] **6.3** Research XMPP link-local vs. WebRTC vs. custom UDP for pragmatic approach
- [ ] **6.4** Document collaboration design for future phases

## Fase 7: Journal profundo + integración

- [ ] **7.1** Evaluate Zeitgeist as event source for Journal
- [ ] **7.2** Add `on_app_close` hook to extension API
- [ ] **7.3** Research integration with Nautilus/file managers
- [ ] **7.4** Add explicit publish UI (user chooses what goes into Journal)

## Community

- [ ] **C.1** Post to sugar-devel with demo and proposal
- [ ] **C.2** Post to IAEP with educational framing
- [ ] **C.3** Reach out to Walter Bender for feedback
