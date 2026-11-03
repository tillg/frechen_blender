---
description: Implement a change's plan test-first, step by step — red → green → refactor → verify → tick — with the checks per step kind
disable-model-invocation: true
argument-hint: "[change-name]"
---

Implement the plan of a change, test-first: for every step the test is written and seen failing
before the code, and the step is ticked only when its `Verify:` and the full suite pass.

**Read first**: `.claude/skills/spec/reference/plan.md` (the cycle and the step kinds),
`principles.md` (surgical changes), `project.md` (commands), `frontmatter.md`.

**Input**: optionally a change name. Otherwise infer from the conversation; auto-select if exactly
one change in `specs/changes/` is `proposed`/`applying`; else **AskUserQuestion**. Unattended →
pick and log (`decisions.md`). Announce "Using change: <name>" and how to override.

**Steps**

1. **Read the artifacts**: `proposal.md`, `domain.md`, `architecture.md`, `plan.md`; the live ADRs
   the architecture cites. No `plan.md` → suggest `/spec:propose` and stop.

2. **Show progress**: `N/M` from the checkboxes (count mechanically:
   `grep -c -E '^\s*- \[x\]' plan.md` / `grep -c -E '^\s*- \[[ x]\]' plan.md`) and the remaining
   steps. All done → congratulate, suggest `/spec:adversarial-code-review`, then `/spec:archive`,
   and stop. Steps lacking `[kind]`, `Test first:` or `Verify:` → derive them from the step and
   the architecture, write them into `plan.md` first, and say so.

3. **Baseline**: run the suites the plan's kinds need (`project.md`: `python3 -m pytest -q`,
   a still render, `cd web && npm test`) once before the first step, so a red baseline
   isn't mistaken for your breakage. Red baseline → show it and ask (**AskUserQuestion**):
   "Continue — done means no *new* failures" / "Stop". No harness for a kind the plan needs → the
   first step must set it up; add it to `plan.md` if missing.

4. **Implement steps — loop until done or blocked.** Per step, the cycle from `plan.md`:
   - Show which step is being worked on.
   - **Red** — write the `Test first:` test. Run it; show that it fails for the stated reason. Passes
     already → the test doesn't test the step: fix the test, not the plan. `Test first: none — …`
     steps skip this.
   - **Green** — the minimum code that makes it pass. Surgical: only what the step names; match the
     file's style; no drive-by refactors (note them instead).
   - **Refactor** — tidy while green, within the step's files.
   - **Verify** — the step's `Verify:` and the full relevant suite. Both pass → show the output.
   - **Tick** `- [ ]` → `- [x]`, bump `plan.md`'s `edited`. After the **first** tick set
     `status: applying` on every file of the change (a status-only change doesn't bump `edited`).
     If the step undoes a `reverted` decision in `DECISIONS.md`, append `Undone in <commit or
     "working tree">.` to it.

   **Per kind** (`project.md`):
   - `[python]` — pytest under `tests/`; `python3 -m pytest -q`.
   - `[blender]` — run the scripts via the Blender MCP server in the order of `CLAUDE.md` ›
     Running; render a still from a temporary camera to `tmp/details/` and read it (then remove the
     camera and restore `scene.camera`); film route changes also need the camera clearance check.
   - `[web]` — `cd web && npm test && npx playwright test`; read the screenshots at 1×.
   - `[docs]`/`[config]` — the mechanical check named in `Verify:`.

   When every step is `[x]` and the full suite is green, set `status: applied` on every file.

   **Pause** (report, wait for guidance) when: a step is unclear; implementation reveals an
   architectural issue (suggest updating the artifacts, or an ADR); an error or blocker; the test
   can't be made to fail first or Verify keeps failing (show both outputs); the user interrupts.
   Unattended: decide and log instead of pausing; never tick a red step.

5. **Status at the end** (completion or pause): steps completed this session, `N/M`, decisions
   logged; all done → "Review it with `/spec:adversarial-code-review`, then `/spec:archive`";
   paused → why, and the options.

**Output during implementation**

```
## Implementing: <name>

Step 3/7 [python]: <step>
✗ Red: test_core › gable windows are recorded fails — list stays empty (as planned)
✓ Green: passes
✓ Verify: python3 -m pytest -q — green
✓ Step complete
```

**Guardrails**

- Tests first, always: no production code for a step before its test has been seen failing.
- Tick a step only after its Verify and the full suite pass — then immediately.
- Never make a test pass by weakening, skipping, deleting or mocking it without the user's
  explicit agreement.
- Keep changes minimal and scoped to the step; `status` identical in all files of the change.
- Pause on errors, blockers or unclear requirements — don't guess.
- Edit spec files with the Edit/Write tools, not sed/python in Bash.
- Don't commit: `/spec:archive` commits with the user's approval. Don't create branches.
