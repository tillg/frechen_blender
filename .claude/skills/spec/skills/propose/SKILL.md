---
description: Propose a new change — create specs/changes/<name>/ with proposal, domain, architecture (A12 impact, key decisions) and a test-first plan
disable-model-invocation: true
argument-hint: "[change-name or description]"
---

Propose a new change: create `specs/changes/<name>/` and its four artifacts in one step. When
ready to implement, the user runs `/spec:apply`.

**Read first** (all under `.claude/skills/spec/reference/`): `frontmatter.md`, `plan.md`,
`a12.md`, `adr.md`, `principles.md`.

**Input**: the argument is a kebab-case change name, or a description of what to build. Nothing
given → **AskUserQuestion** (open-ended): "What change do you want to work on?" Derive a kebab-case
name from the description. Do not proceed without understanding what the user wants.

**Steps**

1. **Small enough for a tweak?** If the request fits the tweak limits (`../tweak/SKILL.md`, "The
   tweak limits"), say so and offer it (**AskUserQuestion**: "Tweak it" / "Full proposal"). The
   user picks. Skip when the request came from a tweak's escalation.

2. **Check for work in progress.** Run `bash .claude/skills/spec/scripts/spec-status.sh`. For
   every other open change: `applied` → recommend archiving it first (a proposal builds on
   `specs/system/`, which is only current after archive); `applying`/`proposed` → say it is in
   progress. **AskUserQuestion**: "Archive `<x>` first (Recommended)" (only for `applied`; then
   follow `../archive/SKILL.md` and come back) / "Stop here" / "Continue anyway". Unattended:
   continue and log it (`decisions.md`).

3. **Ground it.** Read `specs/system/domain.md`, `architecture.md`, `functional.md`, `models.md`
   and `specs/architecture/index.md` (live ADRs bind the proposal). Read the code and models the
   change touches. For a change that is not obviously trivial in A12 terms (new models, engines,
   authorization, client/server split), invoke `a12-solution-architect:research-a12-solution` if
   available — else search the A12 docs (release 2026.06) — and use its recommendation in
   `architecture.md`. Say which you used.

4. **Create the directory** `specs/changes/<name>/`. If it exists, ask: continue it or pick a new
   name.

5. **Create the artifacts in order** from `specs/templates/` (copy, then fill; keep every
   section, write "none" rather than deleting a section). Track with the Task\* tools; show
   "Created proposal.md" after each.
   - `proposal.md` — what, why, scope and non-goals, expected outcome, open questions.
   - `domain.md` — the delta to the system domain: new or changed concepts, vocabulary. Mermaid
     `erDiagram` where entities change.
   - `architecture.md` — read proposal first. Approach, a Mermaid diagram, the **A12 impact**
     section filled per `a12.md`, **Key decisions** (decision · alternatives · why), integration
     points and the live ADRs it obeys. A decision meeting the three ADR criteria (`adr.md`) gets
     a `proposed` ADR now: `bash .claude/skills/spec/scripts/new-adr.sh <slug> "<title>"`, fill it,
     `bash .claude/skills/spec/scripts/gen-adr-index.sh`, link its id in the table. Most changes
     need no ADR — don't invent one.
   - `plan.md` — read proposal and architecture first. Ordered checkbox steps in the format of
     `plan.md` (reference): every step has a `[kind]`, a `Test first:` and a `Verify:` with the
     real commands from `a12.md`. Each step is one red → green cycle; `[model]` steps precede
     their consumers. If the change needs a test harness the project lacks, the first step sets it
     up. No step for `specs/system/` — that is `/spec:archive`'s job; the plan ends with the note
     "System docs are updated at `/spec:archive`."

   Every file starts with the frontmatter from `frontmatter.md`, `status: proposed`, `order` 1–4,
   `created` = `edited` = today. Keep the `# Title` heading equal to `title`.

   Unclear context → **AskUserQuestion**, then continue. Unattended → make a sensible choice, log
   it in `DECISIONS.md`, continue.

6. **Summary** (always the last output): change name and path; the four artifacts in one line
   each; ADRs created (ids) or "no ADR needed"; decisions logged (if any); then
   "Run `/spec:grill` to stress-test it, mark it up and run `/spec:iterate`, or `/spec:apply` to
   start implementing."

**Guardrails**

- Create all four artifacts; read earlier ones before writing later ones; verify each file exists
  before moving on.
- Every plan step has `[kind]`, `Test first:` and `Verify:` — without them it isn't proposed.
- Don't start a new change silently while another is open.
- Don't write code. Don't change `specs/system/`.
- Edit spec files with the Edit/Write tools, not sed/python in Bash.
- Mermaid for every diagram.
