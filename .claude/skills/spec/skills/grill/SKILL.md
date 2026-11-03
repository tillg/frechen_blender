---
description: Grill the user relentlessly on a spec change — design-tree interview in rounds, project questions included — and fold every answer into proposal, domain, architecture, plan and ADRs
disable-model-invocation: true
argument-hint: "[change-name]"
---

Stress-test a change before implementing it. The interview method is in
`.claude/skills/spec/reference/grilling.md` (read it now, and follow it); this skill chooses the
subject and where the answers go. Use it between `/spec:propose` and `/spec:apply`, as often as
you like.

**Read first**: `grilling.md`, `project.md`, `adr.md`, `plan.md`, `frontmatter.md` (all in
`.claude/skills/spec/reference/`).

**Input**: optionally a change name. Otherwise the single open change; several → **AskUserQuestion**.
Announce: "Grilling change: <name>".

**Steps**

1. **Read the change and its context**: every `.md` in `specs/changes/<name>/`, the system pages
   `specs/system/domain.md`, `architecture.md`, `functional.md`, and `specs/architecture/index.md`
   (live ADRs). A proposal that contradicts a live ADR is the first question of round 1.

2. **Run the interview** as `grilling.md` says: build the design tree, ask the whole frontier per
   round with a recommended answer each, wait for the user, recompute. Seed the first round with
   what the artifacts leave open, hedge on or contradict, plus the grill seeds in `project.md` for
   anything touching models, engines, authorization or data. Facts (what the code or a model does
   today, what the plans in `input/` show) you look up; decisions you ask.

   **Capture as you go, not at the end**: a resolved term → the change's `domain.md`; a resolved
   decision → the `## Key decisions` row in `architecture.md`; a decision meeting the three ADR
   criteria → `bash .claude/skills/spec/scripts/new-adr.sh <slug> "<title>"`, fill it as
   `proposed`, link the id in the table, `bash .claude/skills/spec/scripts/gen-adr-index.sh`.

3. **Fold the answers in** when the frontier is empty or the user stops:
   - `proposal.md`: scope, non-goals, outcomes the user settled; open questions removed.
   - `domain.md`, `architecture.md`: already updated; reread for consistency; Impact complete.
   - `plan.md`: add, remove or reorder steps the decisions imply; every new decision has a step
     that implements or verifies it, in the `plan.md` format.
   - Bump `edited` on changed files; leave `status` as it is.

4. **Summary** (last output):

   ```
   ## Grilling complete: <name>

   Rounds: N · Decisions settled: N · Terms defined/changed: N · ADRs proposed: <ids or none>

   ### Changed
   - proposal.md: … · domain.md: … · architecture.md: … · plan.md: …

   ### Still open
   - <questions the user deferred>

   Run /spec:apply to start implementing (or /spec:grill again).
   ```

**Guardrails**

- Follow the interview rules: rounds, recommended answers, wait for the user.
- Never write `GLOSSARY.md` or `docs/adr/`; the spec files and `specs/architecture/` are the record.
- Don't implement anything. Unattended (nobody to answer) → say grilling needs a user and stop.
- Edit with the Edit/Write tools, not sed/python in Bash.
