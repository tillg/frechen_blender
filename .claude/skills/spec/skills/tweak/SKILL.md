---
description: Make a small change test-first without a change directory — inline plan, red → green → verify, specs/system updated in place, one commit
disable-model-invocation: true
argument-hint: "[description of the small change]"
---

The light lane: a bug fix, a label, a renamed option, one validation rule. No
`specs/changes/<name>/`, no proposal, domain or architecture — one short inline plan, the same
red → green → verify cycle as `/spec:apply`, `specs/system/` updated in place, one commit.

A tweak lives in one session. If it turns out bigger, it stops and hands over to `/spec:propose`.

**Read first**: `.claude/skills/spec/reference/plan.md`, `principles.md`, `project.md`,
`frontmatter.md`.

**Input**: a description of the change, or a bug file `specs/bugs/<slug>.md`. Nothing given →
**AskUserQuestion** (open-ended).

**Bugs** live in `specs/bugs/`, one file per bug, with `priority` and `areas` in the frontmatter
(`frontmatter.md`). A bug found and not fixed on the spot gets a file there. Fixing one: its
`## Steps` are the failing test; the fix commit deletes the bug file.

**The tweak limits** (the one definition; `/spec:propose` points here). A tweak stays a tweak while
**all** hold:

- at most about 3 plan steps;
- no new domain term, no changed component boundary, no new model file, no authorization change —
  nothing that would need a change's `domain.md`, `architecture.md` or an ADR;
- no open design question the user has to settle;
- the harness for its step kinds exists (setting one up is a change of its own).

A judgement call, not a line count.

**Steps**

1. **Check the working tree**: `git status --porcelain`. Clean → continue. Uncommitted work while
   a change in `specs/changes/` is `applying`/`applied` → **refuse**: "Finish or commit `<change>`
   first." Other uncommitted changes → list them and ask (**AskUserQuestion**): "Continue — the
   commit takes only the tweak's files" (recommended) / "Stop"; if the tweak must touch one of
   those files, ask before staging it.

2. **Understand the request**: the code and models it touches, the relevant `specs/system/` pages,
   the live ADRs (`specs/architecture/index.md`) it must obey.

3. **Check the limits before any code**; a broken limit → **escalate** (below) without writing code.

4. **Show the inline plan** in the chat (not a file), in the `plan.md` step format — `[kind]`,
   `Test first:`, `Verify:`. More than about 3 steps → escalate. Run the relevant suite once as the
   **baseline**; red → show it and ask: "Continue — done means no *new* failures" / "Stop".

5. **Run each step test-first**: red → green → refactor → verify, showing each result; the
   per-kind rules of `/spec:apply` step 4 apply. After each step re-check the limits; outgrown →
   finish the current step green, then escalate.

6. **Update the system description in place**: every `specs/system/*.md` whose truth the tweak
   changes (a feature in `functional.md`, a component in `architecture.md`, …); `edited` = today on each. Nothing
   to update → say so.

7. **Commit**: draft a message that says what the tweak did; show it with the files to stage (code,
   tests, `specs/system/` — only the tweak's) and ask for approval (**AskUserQuestion**). Revise on
   rejection. Approved → stage exactly those files, one commit. A `reverted` decision undone by
   this tweak gets `Undone in <hash>.` appended in `DECISIONS.md`.

8. **Summary** (last output):

   ```
   ## Tweak complete

   **Steps:** N/N, each test-first · **Tests:** <suite> — <all green | no new failures>
   **System docs:** <files updated | none needed>
   **Commit:** <hash> <message>
   ```

**Escalate** (a limit broke): stop; say which limit and what you learned. Code already written →
list the files and ask (**AskUserQuestion**): "Commit what's done as a tweak" (only if every step so
far is green and complete on its own: steps 6–7, then propose the rest) / "Hand it all to
`/spec:propose`" (leave files uncommitted; pass "already done: <files, tests>" into the proposal).
Then offer `/spec:propose` with the request and what you learned, marked as an escalation.

**Unattended**: don't commit — leave changes unstaged, list files and the drafted message in the
summary; log choices (`decisions.md`).

**Guardrails**

- Tests first, always (unless `Test first: none — …`). Never weaken, skip, delete or mock a test to
  pass without the user's explicit agreement.
- Never create `specs/changes/<name>/` — a tweak that needs one is a change: escalate.
- One commit, only the approved files. No branches.
- Edit spec files with the Edit/Write tools, not sed/python in Bash.
