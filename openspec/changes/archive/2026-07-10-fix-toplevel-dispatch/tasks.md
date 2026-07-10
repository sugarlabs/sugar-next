## 1. Fix handle identity crash

- [x] 1.1 Replace `handle.id` with `id(handle)` as the `_toplevels` dict
      key in `_on_toplevel_created` — `ZwlrForeignToplevelHandleV1Proxy`
      does not have a public `.id` attribute
- [x] 1.2 Update docstring on `_toplevels` to document the key scheme

## 2. Fix process-close early return

- [x] 2.1 Remove the `if self.toplevel_tracker.available is True: return`
      guard in `_on_app_process_closed` so process exit always removes the
      app from the running list
- [x] 2.2 Verify the tracker's own close path and the process-close path
      do not conflict (both paths call `app_state.remove_open`, which uses
      `discard` and is idempotent)

## 3. Event loop hardening

- [x] 3.1 Keep the `roundtrip()`-based loop (verified empirically);
      `dispatch(block=True)` does not flush requests
- [x] 3.2 `_POLL_INTERVAL` of 0.1s between roundtrips avoids busy-spin
- [x] 3.3 Confirm `stop()` still breaks the loop promptly

## 4. Regression guard (unchanged)

- [x] 4.1 Source-inspection test asserts `roundtrip()` in the loop and
      absence of `dispatch(block=True)`
- [x] 4.2 Existing no-protocol-path tests still pass

## 5. Documentation cleanup

- [x] 5.1 Remove obsolete KNOWN ISSUE from `dev/wayfire.ini` that claimed
      Wayfire 0.10.1 does not emit toplevel events
- [x] 5.2 Update `proposal.md` and `tasks.md` to reflect actual root
      causes found

## 6. Verification

- [x] 6.1 Under nested Wayfire via autostart, confirmed `toplevel`,
      `app_id`, `title`, `state` events delivered and callbacks fired
- [x] 6.2 Confirmed close callback fires and app_state.remove_open is
      called on window close
- [x] 6.3 Full `sugar-next/tests` suite: 86/86 pass
