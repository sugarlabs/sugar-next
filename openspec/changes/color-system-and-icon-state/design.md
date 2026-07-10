## Context

`theme.py` currently defines two fixed token dicts (`_LIGHT_TOKENS`,
`_DARK_TOKENS`) plus a high-contrast override and a single-token accent
tint (`set_accent_tint`). There is no derivation logic — the accent is
just written into `--sn-accent` and everything else stays fixed. The
workspace has zero color-math dependencies (`pyproject.toml` only lists
`pygobject`), and `base-standards.md` biases toward matching existing
build systems and minimizing environment friction over dependency-heavy
approaches.

Separately, `main.py` already tracks open toplevels well enough to
drive `frame.add_running`/`remove_running`, via `_on_toplevel_open`,
`_on_toplevel_close`, and `_has_open_toplevel`. It does not track focus.
The optional `wayland-toplevels` extra (`pywayland`) wraps
`zwlr_foreign_toplevel_manager_v1`, which does expose an `activated`
state per toplevel handle — this is the natural source for focus, but
only on wlroots compositors (Wayfire, Sway, Hyprland); it is unavailable
on GNOME/Mutter, where the shell currently falls back to
`on_app_close`-based tracking with no per-window granularity at all.

## Goals / Non-Goals

**Goals:**
- Derive a full, legible `--sn-*` token set from one accent color using
  only `colorsys` (stdlib).
- Let users override any individual generated token, persisted through
  the existing `colors.css` override file.
- Establish one shared, observable source of truth for "which apps are
  open" and "which app is focused," replacing the Frame's private
  `_running_ids`.
- Drive icon greyscale/color/full-saturation state from that registry
  in both the pie menu and the app grid.
- Degrade gracefully (two states instead of three) when focus data is
  unavailable.

**Non-Goals:**
- Perceptually-uniform color science (HCT/CAM16). HSL is good enough
  for a shell UI and keeps the dependency footprint at zero.
- Per-user/profile color (XO-style multi-user palettes) — HIG marks
  this a future possibility, not in scope here.
- Any GNOME/Mutter-side focus protocol work. If a compositor doesn't
  emit `activated`, the shell does not attempt to compensate with
  heuristics (e.g. "only one window open = focused") — two-state
  fallback only, since a guess that's wrong is worse than no highlight.

## Decisions

**HSL-based generation over `materialyoucolor` dependency.**
`colorsys` ships with Python; using it keeps `pyproject.toml` dependency-free
and matches the "match each repo's existing build system, don't add
friction" rule in `base-standards.md`. HCT/CAM16 is more perceptually
correct but is overkill for a handful of shell chrome tokens, and pulling
in an external package for the first time in this codebase is a cost that
needs stronger justification than "closer to Android's algorithm."

Derivation sketch (implemented in `theme.py`):
- `--sn-accent`: the user-picked color, unchanged.
- `--sn-accent-counter`: hue rotated ~150-210° in HSL from the accent
  (adjustable band, not a fixed 180° complement, so it stays legible
  across the hue circle), lightness adjusted for contrast against
  `--sn-accent`. Serves both roles agreed in exploration: guaranteed
  contrast *and* a distinguishable secondary semantic color (e.g. peer
  presence vs. local focus, future work).
- `--sn-bg-alt` / `--sn-surface`: base light/dark value, hue-shifted
  toward the accent's hue by a small fixed blend (~6-10% lightness-
  preserving mix), not overriding lightness — keeps contrast ratios
  from the existing light/dark tokens intact.
- `--sn-bg`, `--sn-text`, `--sn-text-secondary`: stay neutral, untouched
  by accent derivation. These carry the readability contract and
  high-contrast mode already depends on them being predictable.
- All derived tokens remain individually overridable: Settings' Color
  tab writes single-token overrides into `colors.css` (same mechanism
  already used for user overrides today), so the cascade order doesn't
  change, only what populates the "generated" layer beneath it.

**`main.py` as the single app-state registry over per-view tracking.**
`main.py` already owns the wayland toplevel lifecycle events; extending
it avoids three parallel, driftable copies of "is X open" (Frame already
has one privately). The registry exposes:
- `open_app_ids: set[str]`
- `focused_app_id: str | None`
- a simple callback/signal mechanism (reuse whatever pattern
  `on_app_close` already uses — likely a plain callback list, no new
  pub/sub framework) that Frame, pie menu, and app grid each register
  against.

Frame's `add_running`/`remove_running` become thin methods driven by
registry callbacks rather than being called ad hoc from `main.py`; this
is a refactor of existing wiring, not new behavior for the Frame itself.

**Two-state fallback, not heuristic guessing, when focus is unavailable.**
Confirmed in exploration: a wrong guess (e.g. assuming the sole open app
is focused, which breaks the moment a second app opens) is worse than
an honestly simpler two-state system. `focused_app_id` simply stays
`None` forever on non-wlroots compositors or without `pywayland`
installed, and icon rendering treats "no known focus" as "open apps all
render at normal color, none get the full-saturation highlight."

**Accent picker: expanded curated swatch grid, not a custom HSL wheel.**
GTK4 has no built-in color-wheel widget; hand-rolling one means custom
`Gtk.DrawingArea` + pointer math for a shell-chrome picker, which is a
lot of new surface area for a settings dialog. A larger, better-styled
`Gtk.FlowBox` grid (12-20 curated tones instead of 8, restyled swatches)
is a direct extension of the existing `_ACCENT_PRESETS` mechanism in
`settings.py` and ships with much less implementation risk.

## Risks / Trade-offs

- [Hue-shift blending on `--sn-surface`/`--sn-bg-alt` could reduce
  contrast in edge-case accent hues (e.g. very light yellow accent in
  light mode)] → Clamp the blend so lightness of the base token is
  preserved within existing contrast-tested bounds; only hue/saturation
  shift, never lightness, on these two tokens.
- [Refactoring Frame's `_running_ids` into registry-driven callbacks
  touches wiring in `main.py` that several event paths depend on
  (`_on_toplevel_open`, `_on_app_process_closed`, etc.)] → Keep Frame's
  public methods (`add_running`/`remove_running`) as-is so callers
  outside this change aren't affected; only their *trigger* moves from
  direct calls to registry callbacks.
- [No focus signal on GNOME/Mutter means the "activity model" HIG
  language about knowing "where your attention is" only partially
  ships there] → Documented as an accepted platform gap, not silently
  faked.
- [Per-token override UI adds a new interaction surface in Settings
  beyond the accent swatch grid] → Scope the Color tab's override
  controls to a simple list (token name + swatch + reset-to-generated
  button), no new widget types beyond what the swatch grid redesign
  already introduces.

## Open Questions

- Exact hue-shift degree band for `--sn-accent-counter` (150-210°
  suggested) may need tuning once real swatches are tested against
  both light and dark base tokens — left as an implementation-time
  calibration, not a blocking decision.
- Whether app grid icons currently have any per-item render hook to
  attach saturation to, or whether that hook needs to be added as part
  of this change — needs confirmation against the `home-view` capability
  code during implementation (not yet inspected in exploration).
