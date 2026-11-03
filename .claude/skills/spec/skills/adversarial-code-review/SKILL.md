---
description: Use when reviewing implemented code for bugs, regressions, edge cases, plan drift and drive-bys. Reviews the diff since a fixed point along three axes — Defects, Standards (project conventions, surgical-change rule, smell baseline) and Spec — in parallel sub-agents, findings first, and writes review.md into the change. Use after /spec:apply and before /spec:archive, or for "review since X".
argument-hint: "[fixed-point] [change-name]"
---

# Adversarial code review

Review code with a hostile mindset: assume something is wrong and try to find it. Three axes, each
in its own sub-agent so they don't pollute each other's context:

- **Defects** — bugs, regressions, edge cases, state, security.
- **Standards** — this repo's documented conventions (`CLAUDE.md`, `principles.md`), the
  surgical-change rule, and a code-smell baseline.
- **Spec** — does the diff faithfully implement the change, test-first, and nothing more?

**Read first**: `.claude/skills/spec/reference/principles.md`, `plan.md`, `project.md`,
`frontmatter.md`.

## 1. Pin the scope

**Input**: optionally a fixed point (SHA, branch, tag, `main`, `HEAD~5`) and a change name.

- With a fixed point: `git diff <fixed-point>...HEAD` and `git log <fixed-point>..HEAD --oneline`.
- Without: the working-tree diff, the staged diff, and the branch diff against `main` when relevant
  (a change implemented by `/spec:apply` is usually uncommitted).

Confirm the ref resolves and the diff is non-empty before spawning anything.

## 2. Find the spec and the standards

**Spec**: the change named, else the single `applying`/`applied` change in `specs/changes/`
(`bash .claude/skills/spec/scripts/spec-status.sh`), else ask. Its `proposal.md`, `domain.md`,
`architecture.md` (impact, key decisions, ADRs), `plan.md` with `Test first:`/`Verify:`, and
its entries in `DECISIONS.md`. No spec → skip the Spec axis and say "no spec available".

**Standards**: `CLAUDE.md`, `.claude/skills/spec/reference/principles.md`, the live ADRs in
`specs/architecture/index.md`, the vocabulary in `specs/system/domain.md` and the change's
`domain.md` (names in code use those terms), the pitfalls in `CLAUDE.md`. Plus the **smell baseline**
(Fowler), always labelled judgement calls: Mysterious Name, Duplicated Code, Feature Envy, Data
Clumps, Primitive Obsession, Repeated Switches, Shotgun Surgery, Divergent Change, Speculative
Generality, Message Chains, Middle Man, Refused Bequest. A documented repo standard overrides the
baseline; skip anything tooling enforces.

## 3. Spawn the three sub-agents in parallel

Give each the diff command and commit list (or the working-tree diff).

**Defects**: "Find defects in this diff and the code paths it touches. Report each as
`[CRITICAL/HIGH/MEDIUM/LOW] Short description / File: path:line / Risk / Fix`, by severity.
Checklist: behavioural regressions (changed semantics behind existing APIs or UI flows, callers not
updated after a model/DTO change); edge cases (empty/null, deleted related documents, duplicate
submissions, stale data, partial updates); state and consistency (invalid transitions, duplicated
constants, schema or model assumptions not reflected in code, config/docs not updated — don't flag
`specs/system/`, archive updates it); **this project**: coplanar faces that z-fight, overlapping
parts without a shared `rnd` value, exterior openings missing from `OPENINGS`/`GABLE_WIN`, a door
leaf clashing with walls, the film camera passing through geometry, a builder that breaks
idempotent re-runs; tests that can't fail (assert nothing, mock the
thing under test), suite not green. Add `Security Concerns` if relevant."

**Standards**: the standards sources, the smell baseline pasted in full, and: "Report per file/hunk
(a) every breach of a documented standard, citing it; (b) **drive-bys**: hunks that don't trace to
a plan step or the request — reformatting, refactors of untouched code, orphaned or newly unused
code (`principles.md` §3); (c) baseline smells, named and quoted. Hard violations vs judgement
calls. Under 400 words."

**Spec** (skip if none): the spec paths, and: "Report (a) plan steps or requirements missing or
partial; (b) behaviour not asked for (scope creep); (c) requirements that look implemented but
wrong; (d) shortcuts weakening correctness or coverage vs the plan; (e) test-first gaps: a ticked
step whose `Test first:` test is missing, doesn't assert the step, or doesn't pass; a `Verify:` that
fails when you run it; (f) a live or proposed ADR the code contradicts. Quote the spec or plan line.
Under 400 words."

## 4. Report and record

Present `## Defects`, `## Standards`, `## Spec` verbatim or lightly cleaned; never merge or rerank
across axes (one axis must not mask another). Defects stay ordered by severity. End with one line:
findings per axis and the worst within each. No findings anywhere → "No findings — adversarial
code review passed."

Then, when the review belongs to a change, write `specs/changes/<name>/review.md` from
`specs/templates/review.md` (`order: 5`, the change's current `status`, today's dates): scope, the
three sections, verdict. Overwrite an earlier `review.md`. This file is what marks the review step
done for `/spec:overview`, the status pane and `/spec:archive`.

Offer the fixes: **AskUserQuestion** "Fix the CRITICAL/HIGH findings now (test-first, via
`/spec:apply` steps added to plan.md)" / "Accept as is — note it in review.md" / "Later".

## Rules

- Defects: concrete failure paths, not style nits. Standards: style, smells and drive-bys, labelled.
- Call out missing tests when they hide real behavioural risk.
- The review itself is read-only: report, don't fix. Fixes go through the plan.
- Unattended: skip the questions, write `review.md`, log skipped axes (`decisions.md`).
