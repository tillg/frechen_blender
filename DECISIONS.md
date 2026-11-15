---
title: "Decisions"
created: 2026-11-08
edited: 2026-11-15
---

Choices made while nobody was there to ask are logged here
(`.claude/skills/spec/reference/decisions.md`); confirmed ones are removed after review.

**Contents**

- [2026-11-15 16:33 — Implement issues #35 … #30](#run-2026-11-15-1633)
  - [16:40 — Stack the issue branches; open one PR per issue, leave merging to the user](#run-2026-11-15-1633-1)
  - [16:40 — Work the issues strictly one after another, one agent per issue](#run-2026-11-15-1633-2)
  - [16:51 — #35 as a `/spec:tweak` that commits, no change directory](#run-2026-11-15-1633-3)
  - [16:51 — Replace the Blender parity tests by a compile-only guard of the Blender scripts](#run-2026-11-15-1633-4)

# 2026-11-15 16:33 — Implement issues #35 … #30 {#run-2026-11-15-1633}

- **Started by:** `/autonomous`
- **Task, as given:**

  > implement gh issues
  > Implement github issues. Don't wait fopr my, takes decisions as u think best. 
  > Do the issues in this order: #35, #34, #31, #33, #32, #29, #28, #27, #26, #30
  > Make sure to always commit & push in between. Use agents to save space in your context

  Added during the run:

  > Und ganz am Ende: Den Film neu genieren und publishen

## 16:40 — Stack the issue branches; open one PR per issue, leave merging to the user {#run-2026-11-15-1633-1}

- **Status:** open
- **Overrides:** `CLAUDE.md` › GitHub issues — work on an issue starts from current `main` (here: from the previous issue's branch); `/spec:archive` — archive only after the human's approval and with no `open` decisions (here: archived on the branch after self-review, decisions stay `open`).
- **Context:** ten issues in a fixed order, almost all of them change `code/house_core.py`, the committed `plans/*.svg` and the goldens; the user is away and asked to commit & push in between, not to merge.
- **Question:** how can later issues build on earlier ones while nothing is merged without the user?
- **Decision:** each issue gets its branch `issue/<n>-<slug>` from the previous issue's branch (#35 from `main`); per issue: final check green → `/spec:adversarial-code-review` → archive on the branch → push → PR with base = the previous issue's branch (`Closes #n`), label `[under review]`. No merge.
- **Why:** later issues build on earlier ones (#34's layout under #27/#26, #33/#29 next to #30's wall); merging to `main` (which deploys Pages) is the user's call.
- **Alternatives:** merge each PR after self-review (simpler history, but bypasses the human gate and deploys unreviewed); independent branches from `main` (conflicts on plans and goldens).
- **Consequences:** merge the PRs in order (#35 first); with "delete branch on merge" GitHub retargets the next PR to `main`. A change requested in an early PR has to be carried up the stack (rebase/merge the later branches).

## 16:40 — Work the issues strictly one after another, one agent per issue {#run-2026-11-15-1633-2}

- **Status:** open
- **Context:** the user asked to use agents to save context; the repo allows exactly one dev server (5377), which serves one working tree.
- **Question:** parallel worktrees per issue, or sequential?
- **Decision:** sequential, one `worker` agent per issue (on the issue branch in the main checkout); extra agents only inside an issue (exploration, review axes).
- **Why:** shared core, plan sheets and goldens would conflict; worktree work can't be shown on the one dev server.
- **Alternatives:** parallel worktrees (faster wall clock, but conflicts and no Show).
- **Consequences:** slower; each issue starts from the merged result of the one before.

## 16:51 — #35 as a `/spec:tweak` that commits, no change directory {#run-2026-11-15-1633-3}

- **Status:** open
- **Overrides:** `/spec:tweak` — unattended: don't commit, leave changes unstaged (here: committed and pushed on the issue branch, as the run's brief asks).
- **Context:** issue #35 "Nur noch threejs": drop the Blender tests and the rebuild/save steps from the workflow, keep the Blender scripts.
- **Question:** tweak or propose + apply?
- **Decision:** tweak: three steps (guard test, remove the Blender tests, docs); no code in `code/`, no new domain term, no ADR change (ADR-001-XEWL still holds: the Blender backend stays, it is only no longer checked). Review and archive run against the branch diff; with no change directory the review's Spec axis checks against the issue text.
- **Why:** mechanical change; a change directory would only repeat the issue.
- **Alternatives:** propose + apply (a proposal/plan for a deletion and doc edits).
- **Consequences:** no `specs/changes/35-*`; `specs/system/` updated in place.

## 16:51 — Replace the Blender parity tests by a compile-only guard of the Blender scripts {#run-2026-11-15-1633-4}

- **Status:** open
- **Context:** #35; `tests/test_blender_parity.py` (2 `slow` tests, start Blender), `tests/blender/snapshot.py` and `tests/golden/blender_snapshot.json` are the only tests that launch Blender. Last full check with parity green: `main` at 7805879 (pytest 195 passed in 67 s, Vitest 60, Playwright 106).
- **Question:** what stays to keep re-enabling Blender cheap?
- **Decision:** delete those three; add `tests/test_blender_scripts.py`, which compiles the six Blender scripts (`build_house`, `fire`, `paint`, `windrose`, `garden`, `film`) with the standard Python (no `bpy` needed). Keep `tests/fixtures/garden_blender.json` (read by `test_core.py`, no Blender), `test_film_release.py`, `test_tour.py` and `tests/golden/tour.json` (the three.js Rundgang uses the keys). `frechenlehen.blend` stays, frozen at 7805879.
- **Why:** faster dev cycles (the issue's motivation); a syntax check costs milliseconds and catches the cheapest kind of rot.
- **Alternatives:** keep parity as an opt-in marker (still drifts, golden goes stale); no guard at all.
- **Consequences:** the guard checks syntax only: the scripts can drift from the core's API unnoticed. The Blender BVH camera-clearance check of the route is dormant too; only the pure-Python route tests (`test_tour.py`: Wandlampen, Alternativ furniture) remain — a gap against all other geometry. To re-enable: restore `git show 7805879:tests/test_blender_parity.py`, `tests/blender/snapshot.py`, `tests/golden/blender_snapshot.json`, rebuild (CLAUDE.md › Blender backend), regenerate the golden, save the `.blend`.
