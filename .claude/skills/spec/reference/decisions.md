# Decisions log (`DECISIONS.md`)

When a skill runs **unattended** (nobody to answer — e.g. under `/goal`, `/loop` or an autonomous
run) and has to make a choice it would normally ask about, it records the choice in `DECISIONS.md`
at the project root. One file per project; the user reviews every choice made without them in one
place. Interactive runs don't write here: the user answered, and the answer lands in the artifacts.

**What goes in:** a choice the user would have been asked about — an unclear plan step and how it
was read, one option picked where the architecture names several, a change selected by inference,
a check skipped, an open change left in place. Not routine work the plan spells out.

## Format

```markdown
---
title: "Decisions"
created: 2026-10-02
edited: 2026-10-02
---

# 2026-10-02 14:30 — Implement login for add-auth {#run-2026-10-02-1430}

- **Started by:** `/spec:apply add-auth` (unattended)
- **Task, as given:** > Implement the login part of add-auth while I'm in meetings.

## 14:42 — Store sessions in Postgres {#run-2026-10-02-1430-1}

- **Status:** open
- **Context:** plan step 3 of `add-auth`; `architecture.md` names no session store.
- **Question:** Redis or Postgres for sessions?
- **Decision:** Postgres.
- **Why:** already a dependency; one less service to run and back up.
- **Alternatives:** Redis (faster expiry, but a new service).
- **Consequences:** adds a `sessions` table migration; revisit if session load grows.
```

- One `#` **run** per unattended invocation (written with its first decision), one `##` **decision**
  per choice, chronological, appended at the end. Old entries are never rewritten except `Status`
  and lines appended to `Consequences` (`Undone in <commit>.`, `Promoted to <path>.`).
- A decision that bends a guardrail (a rule from a skill, `CLAUDE.md` or the user) adds
  `- **Overrides:** <rule and where it lives>` right after `Status`.
- `Status` is `open` when written; the user sets `confirmed` or `reverted`. A `reverted` decision is
  undone test-first (`/spec:tweak` or `/spec:apply`); until `Undone in …` is appended it is a
  **pending revert**.
- Counting, never by eye: open = `grep -c '^- \*\*Status:\*\* open' DECISIONS.md`.

## Review and promotion

- `/spec:archive` reviews the change's `open` decisions with the user (AskUserQuestion, ≤ 4 per
  call: Confirm / Revert / Stop) and **does not archive** while any is `open` or a pending revert.
- `/spec:overview` shows `Decisions: N open, P pending reverts` and offers the same review.
- At archive, a `confirmed` decision that meets the three ADR criteria (`adr.md`) is promoted to an
  ADR; otherwise to a `## Key decisions` row in `specs/system/architecture.md`. Append
  `Promoted to <path>.` to its Consequences.
- A change's decisions are those whose run or `Context` names the change as a whole token
  (`` `add-auth` `` or `specs/changes/add-auth/`), never a substring.

The skill's final summary names the run and how many decisions it logged.
