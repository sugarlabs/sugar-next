---
name: writing-skills
description: Use when the user wants to add a new skill to this workspace's SpecBook, or when a repeated task in a conversation would be better captured as a reusable skill than repeated ad hoc.
metadata:
  author: sugarlabs-specbook
  version: "1.0"
---

# Writing Skills

Meta-skill for adding new skills to this workspace, adapted from the
lidr-specboot approach: a skill earns its place by being tested against a
concrete scenario, not just written from a description.

## When to write a new skill

- A task got done manually in this conversation and will clearly recur
  (e.g. a specific repo-cloning pattern, a recurring build-debugging
  sequence).
- The user explicitly asks for one.
- Not every recurring task needs a skill — one-off scripts belong in
  `specbook/docs/` as a documented procedure if they don't need to be
  triggered by description-matching.

## Process

1. **Write the pressure scenario first.** Before writing the skill itself,
   write down the concrete situation where it should trigger (a prompt a
   user might realistically type) and what should happen without the skill
   (missing context, wrong assumptions, repeated questions).
2. **Confirm the gap.** If practical, try the scenario without the skill
   present to confirm it actually fails/underperforms — this avoids writing
   skills for problems that don't exist.
3. **Write the `SKILL.md`**, following the frontmatter convention already
   used across this workspace's skills:
   ```yaml
   ---
   name: skill-name-in-kebab-case
   description: Use when <specific triggering condition, third person, no plot summary of internal steps>
   metadata:
     author: sugarlabs-specbook
     version: "1.0"
   ---
   ```
   - `description` is what the agent uses to decide whether to load the
     skill — it must describe **triggering conditions**, not a summary of
     what the skill does internally.
   - Keep the body scoped: Overview, Steps/Process, Notes. Don't pad with
     restating the description.
4. **Re-run the pressure scenario** with the skill present and confirm it
   now succeeds.
5. **Place it** under `.claude/skills/<name>/`. This workspace targets only
   Claude Code for now (see `specbook/docs/base-standards.md`) — no
   symlink-mirroring to other tools' directories is needed unless/until
   multi-copilot support is explicitly added.

## Notes

- Prefer editing an existing skill over creating a near-duplicate — check
  `.claude/skills/` first.
- Skills that wrap risky operations (anything touching system directories,
  `sudo`, or irreversible git operations) must explicitly instruct
  confirming with the user before acting, per this workspace's general
  safety posture — see how `setup-sugar-workspace` handles `make install`.
