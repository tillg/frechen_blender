---
description: Archive a completed change — run the tests, review open decisions, fold the change into specs/system and the ADRs, commit, delete the change directory
disable-model-invocation: true
argument-hint: "[change-name]"
---

Archive a completed change: update the truth pages and ADRs, commit the work, then clean up.

**Read first**: `.claude/skills/spec/reference/frontmatter.md`, `adr.md`, `decisions.md`, `project.md`.

**Input**: optionally a change name. Otherwise list `specs/changes/` and **AskUserQuestion** — never
auto-select here.

**Steps**

1. **Check readiness** — inform and confirm, don't block (except 1d):
   a. Artifacts present (`proposal.md`, `architecture.md`, `plan.md`; `domain.md` optional)?
      Missing → warn, ask to continue.
   b. `plan.md`: unticked steps? → warn with the count, ask to continue.
   c. `review.md` present? Missing → recommend `/spec:adversarial-code-review` first; continue only
      on explicit confirmation. CRITICAL/HIGH findings in it not marked fixed or accepted → same.
   d. **Run the tests**: the final check (`project.md`) and every `Verify:` in `plan.md`; model
      validation if models changed. Show the result. Red → recommend fixing via
      `/spec:apply`; continue only on an explicit "archive anyway".
   e. **Decisions gate** (blocks): if `DECISIONS.md` exists, run the review flow of `decisions.md`
      over the change's `open` decisions. Any still `open` or a pending revert → stop, name what to
      undo and how (`/spec:tweak` or `/spec:apply`), say to run `/spec:archive` again. Other open
      decisions: report the count only.

2. **Update the system description.** Read the change's artifacts and every `specs/system/*.md`;
   update **every** page whose truth changed — `domain.md` (concepts, vocabulary), `architecture.md`
   (components, interactions, Key decisions rows), `functional.md` (features, scripts, film). Present tense, in place,
   replace rather than append, no history, no change name in the prose. Mermaid diagrams updated.
   Never copy `feature`, `status`, `order` into system files; `edited` = today on each touched file.
   The goal: afterwards `specs/system/` fully reflects the system; nothing stays only in the change.

3. **Settle the decisions.** The change's `proposed` ADRs → `status: accepted` (`## History` untouched);
   a superseded ADR gets `status: superseded`, `superseded_by`, and moves to
   `specs/architecture/archive/`. `confirmed` decisions from `DECISIONS.md` that meet the three ADR
   criteria → a new ADR (`bash .claude/skills/spec/scripts/new-adr.sh`, `accepted`); the rest → Key
   decisions rows in `specs/system/architecture.md`; append `Promoted to <path>.` to each. Then
   `bash .claude/skills/spec/scripts/gen-adr-index.sh` and `--check`.

4. **Commit — with approval.** Draft a concise message that says what the change accomplished
   ("Add role-based access control with JWT", not "archive x"). Show it and the file list (code,
   tests, models, `specs/changes/<name>/`, `specs/system/`, `specs/architecture/`, `DECISIONS.md`)
   and **AskUserQuestion** to approve. Never commit without approval. Approved → stage those files
   and commit. `README.md` changes a user-visible feature needs go into the same commit
   (`principles.md` §3).

5. **Delete the change.** Confirm `specs/changes/<name>/` is in git history
   (`git log --oneline -1 -- specs/changes/<name>/` shows a commit and
   `git status --porcelain specs/changes/<name>/` is empty) — else stop. Then `rm -rf` the
   directory, stage only that deletion, commit with the same message + ` - cleaned from change`.

6. **Summary**:

   ```
   ## Archive complete: <name>

   ### Commits
   1. <message> — implementation + system description
   2. <message> - cleaned from change

   ### Updated
   - specs/system/… — <what>
   - ADRs: <ids accepted / created>, or none
   ```

**Guardrails**

- Always let the user pick the change; always ask before committing.
- Update the system description before committing — don't strand knowledge in change artifacts.
- The first commit carries the work and the docs; the second only removes the change directory.
- No new branches. Push and merge only as `CLAUDE.md` › GitHub issues says (issue branch, after the
  human's approval). Unattended: don't archive at all — report what is ready and stop.
- Edit spec files with the Edit/Write tools, not sed/python in Bash. Mermaid for diagrams.
