# Base Standards — Sugar Labs Workspace

Single source of truth for how work happens in this workspace. `CLAUDE.md` at
the root points here. If a rule below conflicts with something an agent or
skill assumes, this document wins.

## Why this exists

Sugar's codebase is split across many repos with uneven activity, a mix of
Python 2/3 legacy patterns and modern practices, and a GTK4 port
([sugar#1019](https://github.com/sugarlabs/sugar/pull/1019)) that stalled on
process friction rather than technical difficulty. These rules exist to keep
new work legible and reversible so it doesn't stall the same way.

## Core rules

1. **Small changes, one at a time.** A change (OpenSpec `openspec/changes/<name>/`)
   should cover one coherent unit of work. Prefer several small archived
   changes over one large one — large diffs are exactly what made PR #1019
   hard to review and pick back up.

2. **Tests before implementation, where the repo has a test story.**
   `sugar-toolkit-gtk4` has `make test` / `make test-coverage` — use it.
   Legacy Autotools repos (`sugar`, `sugar-toolkit-gtk3`) have thinner test
   infrastructure (`tests/`, `testrunner.py`); when touching them, add or
   extend tests where feasible rather than skipping the step entirely.

3. **English for all technical artifacts.** Code, commit messages, specs,
   docstrings, and OpenSpec proposals are written in English — Sugar is an
   international project and upstream contribution requires it. Conversation
   with Sebastián in this workspace can stay in Spanish; anything destined
   for a repo or an upstream PR must be English.

4. **Match the build system already in place.** Don't introduce a new build
   tool into a repo that doesn't have it yet:
   - `sugar`, `sugar-toolkit-gtk3`, `sugar-datastore`, `sugar-artwork`:
     Autotools (`./autogen.sh` → `configure` → `make` → `make install`).
   - `sugar-toolkit-gtk4`: modern Python packaging (`pip install -e .`,
     `Makefile` with `make install`/`make test`/`make format`/`make build`).
   Modernizing a repo's build system is its own change, proposed and
   reviewed explicitly — not a side effect of an unrelated fix.

5. **Documentation is the source of truth once a change is proposed.** If a
   fix or scope adjustment is needed after `/opsx:propose` but before
   `/opsx:archive`, update the change's spec/proposal files first, then the
   code. Don't let code and spec drift silently.

6. **Environment friction is a first-class bug.** PR #1019 stalled because
   there was no reproducible way to run and test the GTK4 shell (Casilda
   compositor setup was undocumented). Treat "can a new contributor get this
   running in under an hour" as part of the definition of done for any
   environment-touching change.

## Workflow

This workspace uses [OpenSpec](https://github.com/Fission-AI/OpenSpec) as the
spec/change engine:

```
/opsx:explore              # optional, no artifacts — scope out an idea
/opsx:propose <name>       # creates openspec/changes/<name>/{proposal,specs,design,tasks}.md
/opsx:apply                # implement tasks.md one item at a time
/opsx:sync                 # merge delta specs into openspec/specs/
/opsx:archive <name>       # validate + move to openspec/changes/archive/YYYY-MM-DD-<name>/
```

Use the `sugar-developer` agent (`.claude/agents/sugar-developer.md`) to draft
implementation plans for anything touching PyGObject/GTK/D-Bus code — it
proposes, it does not implement directly.

## Scope of this document

This covers workspace-wide process. Stack-specific reference material lives
in sibling docs:

- [[sugar-stack]] — the repo map: what each repo is, its current state, how
  they relate.
- [[gtk-porting-standards]] — GTK3→GTK4/PyGObject migration conventions and
  the real status of PR #1019.
- [[design-system]] — visual design system (placeholder, not yet defined).
