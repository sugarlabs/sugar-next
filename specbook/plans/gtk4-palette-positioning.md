# Plan: Fix GTK4/Wayland popup (palette) positioning and appearance

## 1. Scope

Covers `sugar-toolkit-gtk4`'s palette/popup subsystem only:
`src/sugar4/graphics/palettewindow.py`, `palette.py`, `palettemenu.py`, and
their `Invoker` hierarchy. Goal: make Sugar palettes position correctly and
look correct (border, "speech bubble" tail) under GTK4 on Wayland (including
under Casilda-hosted `jarabe`).

Out of scope: `sugar` (jarabe) call sites of `Palette`/`create_palette` —
these should need no changes if the public API (`Palette`, `PaletteWindow`,
`Invoker` subclasses, `set_content`, `popup`/`popdown`) is preserved.
Also out of scope: redesigning palette visuals/theme (separate design-system
work), X11 code paths (none exist here — this module is GTK4-only already),
and `sugar-toolkit-gtk3` (untouched, X11-only, not affected).

## 2. Confirmed root causes

**Positioning is broken by architecture, not by a missing API call.**

- `Invoker.__init__` (palettewindow.py:882-897) captures one monitor's
  `Gdk.Rectangle` via `get_monitors().get_item(0)` and treats it as a global
  "screen area" origin (0,0)-relative. `_get_position_for_alignment`,
  `_in_screen`, `_get_area_in_screen`, `get_position`, `get_alignment`
  (lines 917-1070) all compute and compare **absolute root-window
  coordinates**. Wayland gives clients no global coordinate system and no
  way to place a surface at absolute (x, y) — this model cannot work on
  Wayland regardless of which Gtk widget it's wired into.
- `WidgetInvoker.get_rect()` (1281-1305) tries to approximate "absolute"
  position via `compute_transform(native)`, which is relative to the
  widget's own native surface, not the screen — so even the input to the
  positioning math is not what the algorithm assumes it is.
- `_PaletteMenuWidget.move(x, y)` (162-164) stores `self._popup_position`
  and does nothing else — `set_pointing_to`/`set_offset` are never called
  anywhere in the codebase (confirmed via grep). All the absolute-rect math
  computed by `Invoker`/`PaletteWindow.update_position()` for the Popover
  path is discarded silently.
- `_PaletteWindowWidget` (283-402) is a plain `Gtk.Window`, and **this is
  the widget actually used for all real palettes**: `PaletteWindow.set_content()`
  (592-597) always constructs `_PaletteWindowWidget`; `Palette.get_menu()`
  in `palette.py:479-503` is the only place that builds a `_PaletteMenuWidget`,
  and only for the `PaletteMenuBox` content case (`get_menu()` — used by
  callers who explicitly want a menu-list palette body, e.g.
  `palettemenu.py`'s documented usage). Both paths end up owned by the same
  `PaletteWindow`, so a right-click/toolbar palette can be backed by either
  widget depending on how `set_content` was called for that particular
  `Palette` subclass. `_PaletteWindowWidget` has **no `move()` method at
  all** (GTK4 removed `Gtk.Window.move()` entirely — top-levels cannot be
  positioned by clients on Wayland by design). So
  `PaletteWindow.update_position()`'s `hasattr(self._widget, "move")` check
  (line 686) is `False` for `_PaletteWindowWidget` and silently no-ops —
  confirmed, not just suspected. The palette window therefore appears whatever
  the compositor's default top-level placement is (often screen center or
  cascaded), completely unrelated to the invoker.

**Visual appearance is broken for the same structural reason.**

- The "speech bubble" gap/tail (`_calculate_gap`, `WidgetInvoker.draw_rectangle`)
  depends on comparing the invoker's rect and the palette's rect in the same
  coordinate space to decide which edge to leave a gap in and draw a pointer
  notch. `draw_rectangle` (1310-1323) is explicitly a stub — comment says
  "GTK4: Would need to use snapshot API for drawing / TODO; pass" — so no
  tail/notch is drawn at all currently, independent of position bugs.
- `_PaletteWindowWidget` sets `set_decorated(False)` and a `palette` CSS
  class, so bordering depends entirely on CSS (presumably in `sugar4`'s
  stylesheet) rather than custom drawing; this part is likely fine, but
  should be visually verified once positioning is fixed, since right now
  it's untestable (window shows up in the wrong place).

## 3. Is Gtk.Popover the right foundation for all palettes?

Yes — recommend standardizing all palettes on `Gtk.Popover` (`set_parent`,
`set_pointing_to`, `set_position`), replacing `_PaletteWindowWidget`
entirely. Rationale:

- `Popover` positioning is relative to its parent widget and mediated by
  the compositor's positioner protocol (`xdg_popup` under Wayland) — this
  is the only mechanism in GTK4 that has real supported Wayland placement.
  A plain `Gtk.Window` fundamentally cannot be positioned by a client on
  Wayland; there is no workaround for that within GTK4's public API short
  of a layer-shell protocol extension (out of scope — that's for
  panel/shell-level surfaces, not per-widget popups, and
  `gtk-porting-standards.md` already flags layer-shell as unavailable/
  undocumented in the current Casilda setup).
  This is a **structural constraint**, so keeping any top-level-window
  palette path is a dead end on Wayland, not an alternative worth
  preserving.
- `Popover` supports `set_has_arrow(True)` (default) which draws GTK's own
  themed pointer/tail natively — this can replace `_calculate_gap`/
  `draw_rectangle` entirely rather than needing a custom-drawn notch, which
  is likely less work than porting the old gap-drawing code to the GTK4
  snapshot API.
- Popovers auto-constrain to the monitor and reposition/flip automatically
  when they'd overflow — this subsumes most of `Invoker._get_alignments`/
  `get_alignment`'s "try each corner, pick best-fitting" logic, which can
  be significantly simplified or dropped.

Caveat requiring a design decision from the human: `Gtk.Popover` is
*modal-ish* relative to its parent — it grabs and requires a widget
(`set_parent`) as anchor, and a Popover cannot outlive/detach from its
parent the way a free-floating top-level can. Two invoker patterns in the
current code assume no fixed parent-widget anchor:

- `CursorInvoker`/`AT_CURSOR` position hint (used for e.g. canvas
  right-click-at-pointer palettes, `TreeViewInvoker` cell palettes) — these
  invokers currently compute a synthetic rect around the *cursor position*,
  not a real anchor widget. Popover needs `set_parent()` on a real widget
  and `set_pointing_to()` with a rect *in that parent's coordinate space*.
  This is doable (attach popover to the underlying `TreeView`/canvas widget,
  point at a rect derived from local (not root) cursor coords captured at
  click time) but is a behavior change worth the human confirming, since
  cursor-anchored popovers over a TreeView with many rows/cells is the
  trickiest case to get right.
- Palettes invoked from one widget but logically describing another (rare
  in this codebase, worth a grep sweep in `sugar`'s jarabe call sites during
  implementation, not just toolkit) may need re-checking that `set_parent`
  target and `get_rect()`/anchor target agree.

## 4. Required changes to Invoker's positioning math

Replace absolute-screen-rect math with parent-relative math:

- Drop `self._screen_area` / monitor geometry capture in `Invoker.__init__`
  and all of `_in_screen`, `_get_area_in_screen` (no longer meaningful —
  Popover's positioner handles screen-edge flipping).
- Replace `get_rect()` implementations (currently mixing "root window
  coords" attempts via `compute_transform(native)`, and `TreeViewInvoker`'s
  similar pattern) with **rects relative to the anchor widget itself**
  (i.e. `Gdk.Rectangle(0, 0, widget.get_width(), widget.get_height())`,
  since that's what `Popover.set_pointing_to()` expects when
  `set_parent(anchor_widget)` has been called on that same widget).
- Replace `_get_position_for_alignment`'s 4-float-tuple alignment model
  (palette_halign/valign, invoker_halign/valign) with a direct mapping to
  `Gtk.PositionType` (`TOP`/`BOTTOM`/`LEFT`/`RIGHT`) passed to
  `Popover.set_position()`. The existing `BOTTOM`/`RIGHT`/`TOP`/`LEFT`
  alignment-tuple constants on `Invoker` map naturally 1:1 to
  `Gtk.PositionType` members — this collapses `get_alignment()`'s
  "try each direction, score by visible area" search into "prefer
  BOTTOM, else pick per `ToolInvoker._get_alignments()`'s orientation
  logic (still valid — it decides toolbar-perpendicular direction, which
  is orthogonal to the absolute-coords problem and should be kept)."
- `PaletteWindow.update_position()` becomes: compute a `Gtk.PositionType`
  + optional `Gdk.Rectangle` (relative), call
  `self._widget.set_pointing_to(rect)` and `self._widget.set_position(pos)`
  instead of `self._widget.move(x, y)`. `AT_CURSOR` hint needs the pointing
  rect built from parent-local pointer coords (via
  `widget.compute_point()`/existing `_get_pointer_position` adapted to
  return parent-local, not root, coords).
- `_calculate_gap`/`WidgetInvoker.draw_rectangle`/`has_rectangle_gap`
  likely become dead code once `Popover.set_has_arrow(True)` is adopted —
  candidates for deletion rather than porting, pending the human confirming
  the native Popover arrow is visually acceptable versus Sugar's original
  custom tail (worth a quick side-by-side screenshot check before deciding).

## 5. Rough scope / file list for implementation change

- `repos/sugar-toolkit-gtk4/src/sugar4/graphics/palettewindow.py` — largest
  diff: delete `_PaletteWindowWidget`, extend `_PaletteMenuWidget` (or
  rename, since it'd no longer be menu-specific) to be the one palette
  widget class; rewrite `Invoker` positioning methods as above;
  `PaletteWindow.update_position()`/`popup()`/`get_rect()`.
- `repos/sugar-toolkit-gtk4/src/sugar4/graphics/palette.py` — `Palette.get_menu()`'s
  `_PaletteMenuWidget`-vs-other-widget branch likely collapses since there's
  only one widget class now; check `set_content()` (line ~397) for the
  same `_PaletteWindowWidget` assumption.
- `repos/sugar-toolkit-gtk4/src/sugar4/graphics/palettemenu.py` — check for
  any assumptions about the widget being a `Gtk.Window` vs `Gtk.Popover`
  (e.g. size negotiation calls).
- `repos/sugar-toolkit-gtk4/tests/` — existing palette tests (if any; check
  `make test` coverage) will need rewriting for the new positioning API;
  per base-standards rule 2, add tests for `Invoker.get_position`/
  `get_alignment` replacements as part of this change, not after.
- No changes expected in `repos/sugar` (jarabe) call sites if the public
  `Palette`/`Invoker` surface is preserved — but a grep sweep of
  `create_palette`/`ToolInvoker`/`CursorInvoker`/`TreeViewInvoker` usages
  under `repos/sugar/src/jarabe` (12 files already identified: e.g.
  `desktop/favoritesview.py`, `frame/activitiestray.py`,
  `journal/listview.py`, `view/palettes.py`, etc.) should be a verification
  task in the implementation change, to confirm none of them poke at
  `_widget`, `.move()`, or rect internals directly.

## 6. Risks / unknowns

- **Visual verification is blocked on Casilda/GTK4-shell-testing setup**,
  which `gtk-porting-standards.md` flags as undocumented/environment-blocked
  — actually seeing a Popover render correctly in the target compositor
  needs that environment fixed or worked around first; this plan's author
  could not run the shell to visually confirm current broken appearance
  beyond static code reading.
- **Popover-grabs-parent-focus semantics** may interact with Sugar's
  existing `MouseSpeedDetector`/hover-driven auto-popup behavior
  (`on_invoker_enter`/`on_invoker_leave`, `_mouse_slow_cb`) in ways that
  need runtime testing, not just code reading — Popover's default grab
  behavior may steal focus/dismiss differently than the old Window did.
- **`TreeViewInvoker`/cursor-anchored popovers** (journal listview cell
  palettes) are the case most likely to need actual redesign rather than
  mechanical port — flagged above as needing your confirmation on the
  intended anchor/coordinate approach before implementation starts.
- Confirm whether `Gtk.Popover.set_has_arrow` visually satisfies "looks
  right" from the bug report, or if Sugar wants to keep a custom-drawn tail
  (design decision, not mechanical).

## 7. Suggested OpenSpec change breakdown

Given the size (rewrite of `Invoker` positioning math + widget class
replacement + potential jarabe call-site verification), split into at least
two changes per base-standards rule 1:

1. `gtk4-palette-popover-widget` — replace `_PaletteWindowWidget` with a
   single Popover-backed widget class in `palettewindow.py`/`palette.py`;
   keep old absolute-position `Invoker` math temporarily wired to
   `set_pointing_to`/`set_position` with a naive/best-effort translation,
   just to get *something* rendering in the right general area with the
   correct look (arrow, border). Add/update toolkit tests.
2. `gtk4-invoker-relative-positioning` — the real fix: rewrite
   `Invoker.get_rect()`/`get_position_for_alignment`/`get_alignment` to be
   parent-relative throughout, remove `_screen_area`/`_in_screen`/
   `_get_area_in_screen`, handle `AT_CURSOR` and `TreeViewInvoker` properly.
3. (optional, only if step 1/2 surface call-site breakage) 
   `jarabe-palette-invoker-verification` — sweep and fix any `repos/sugar`
   call sites found to poke at removed internals.

Recommend running `/opsx:propose gtk4-palette-popover-widget` first.
