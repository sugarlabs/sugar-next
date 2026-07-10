## Why

`TopLevelTracker` failed to receive any `toplevel` events on wlroots
compositors, causing the app-state registry's open/focused tracking to
silently do nothing. The shell remained stuck in its two-state (closed/
open) fallback even on compositors that fully support
`zwlr_foreign_toplevel_manager_v1`.

Two root causes were identified and fixed through live instrumentation of
the shell inside nested Wayfire:

1. `_on_toplevel_created` crashed on the first `toplevel` event with
   `AttributeError: 'ZwlrForeignToplevelHandleV1Proxy' object has no
   attribute 'id'`. This prevented any handle from being registered,
   making the tracker a no-op regardless of event-loop mechanism.
   Fixed by keying `_toplevels` on `id(handle)` (Python object identity)
   instead of the nonexistent `.id`.

2. The `_on_app_process_closed` callback in `main.py` had an early return
   when the tracker was available (`if self.toplevel_tracker.available is
   True: return`). When an app process exited without the tracker having
   seen a window for it, the app was never removed from the running list
   and its icon remained stuck in the Frame forever. Fixed by always
   removing on process close; the tracker's own close path handles
   window-level closes, so the two paths do not conflict.

The `dispatch(block=True)` → `roundtrip()` loop change originally
suspected was kept — it is defensible hardening (roundtrip flushes, which
dispatch does not) and was verified not to cause regressions — but it was
not the blocking defect; the loop would have worked with `dispatch()` once
the `handle.id` crash was fixed (verified empirically).

## What Changes

- `toplevel_tracker.py`: key `_toplevels` by `id(handle)` not `handle.id`.
- `main.py`: remove the early return in `_on_app_process_closed` so that
  process exit always removes the app from the running list, regardless of
  tracker availability.
- `toplevel_tracker.py`: keep the `roundtrip()` event loop (flushes
  requests; empirically safe and correct).
- `dev/wayfire.ini`: remove the obsolete KNOWN ISSUE comment claiming
  Wayfire 0.10.1 does not emit toplevel events (verified: it does).

## Capabilities

### New Capabilities
- `wayland-toplevel-tracking`: the guarantee that, on a compositor
  advertising `zwlr_foreign_toplevel_manager_v1`, the tracker delivers
  open/close/focus events to its callbacks (not merely reports the
  protocol available).

### Modified Capabilities
(none)

## Impact

- `sugar-next/sugar_next/shell/toplevel_tracker.py` — `_on_toplevel_created`
  key fix + loop hardening.
- `sugar-next/sugar_next/shell/main.py` — `_on_app_process_closed` fix.
- `sugar-next/dev/wayfire.ini` — comment cleanup.
- No API change: `TopLevelTracker`'s constructor, callbacks, and
  `available` property are unchanged.
- Tests: 86/86 pass.
