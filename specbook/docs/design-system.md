# Design System — Placeholder

Not defined yet. This is a skeleton for the next SpecBook cycle, once the
methodology/scaffolding cycle (this one) is done. Do not fill this in as a
side effect of other work — it deserves its own OpenSpec change(s).

## Sections to fill in later

- **Visual language goals** — what "modernized for current Linux laptops"
  means concretely (target screen densities/DPI, HiDPI behavior, window
  scaling under GTK4).
- **Color palette** — light/dark, accessibility contrast targets.
- **Typography** — font choices, scale, legibility for the age range Sugar
  targets.
- **Iconography** — what to keep from `sugar-artwork` vs. what to redesign;
  decide per-icon, not wholesale.
- **Layout density** — Sugar's original UI assumed small, low-res XO laptop
  screens; modern laptops need different density/spacing defaults.
- **Component inventory** — Frame, Home View, Journal, Control Panel,
  palettes/launcher — what GTK4 widgets/patterns each maps to.
- **Motion/interaction conventions** — if any are introduced going from
  GTK3 to GTK4.

## Relationship to GTK4 porting

Design system decisions and [[gtk-porting-standards]] work are related but
separate: the port can proceed with the existing visual language unchanged,
then the design system change layers on top. Don't block one on the other
unless a specific decision requires it.
