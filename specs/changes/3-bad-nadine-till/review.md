---
feature: 3-bad-nadine-till
title: "Review: Bad Nadine & Till"
status: applied
order: 5
created: 2026-11-13
edited: 2026-11-13
---
# Review: Bad Nadine & Till

**Scope:** `git diff 7c01f38...HEAD` (2 commits: 2a7f5bc, e31cb7a) · **Reviewed:** 2026-11-13

## Defects

- [HIGH] Suite red: `test_elternbad_submodel` asserted a sub-model floor not yet built · tests/test_core.py · it was
  the test-first red of the user's floor request, written while the review ran · **fixed**: the page lays the floor.
- [MEDIUM] Sub-model window without shutters (house `win()` passes sh=1) · code/elternbad.py `waende()` · page
  differs from the house · **fixed** (`"W", 1`; test asserts `Elternbad_Laeden`).
- [MEDIUM] Window span duplicated between `elternbad.FENSTER` and `build_og()` · code/house_core.py · silent drift
  · **fixed**: `build_og()` uses `win(*elternbad.FENSTER)` (house geometry identical). Sill/head 3.62/4.60 and the
  wall extents in `waende()` stay literal, as in `gaestebad.waende()` (the sub-model's wall pieces).
- [LOW] Stale comments (elternbad.py entrance wording) · **fixed**. "from y 1.24" in `elternbad.js` is correct in
  sub-model coordinates (1.64 − 0.40) · no change.
- [LOW] Test alias `tray = drain` · **fixed**.
- [LOW] Hairline gaps of 1–2 mm between glass, north slabs and north tiles at x 7.72 · cosmetic, accepted
  (deliberate clearance against coplanar faces).
- Verified clean: `bad.stone()` refactor (Bad geometry identical), `shower(tray=False)` default keeps other callers,
  house geometry changed only in the Bad's objects, plans current, no leaf clash, camera ≥ 0.36 m in the Bad.

## Standards

- Hard: ADR-001-XEWL repeated window span — fixed (above). Room facts in the `elternbad.js` header comment, as in
  `gaestebad.js` · accepted (existing pattern, comment only).
- Docstring "tiles and basin from their own generator" flagged as wrong · it is right: `wainscot` and
  `waschbecken` seed their own `random.Random` · no change.
- Judgement calls, accepted: `cm()` and the dimension-line lambda copied per sub-model module (existing
  pattern, out of scope); `CLAD`/slab thickness repeated in bad.py and elternbad.py; terse constant names
  (`SS`, `SE`, `GA`, `TX`, …, each commented, as in gaestebad.py); `STOREYS` labels repeat the house entries'.
- Drive-bys: none (`bad_mirror()` removed as orphaned; `limestone()` extracted to share, Bad unchanged).

## Spec

- Stale text against the final code (no-tray shower missing from proposal, plan step 1/6/5 wording, architecture
  mermaid "peek", resume note) · **fixed**.
- Toilet faces the window diagonally (axis 8.14, window 6.84..7.72) · now stated as the trade-off in the proposal.
- No scope creep (cladding, floor, route, drop-down are user requests), no test-first gaps, no ADR contradicted.

## Verdict

Defects 6 (worst HIGH, an in-progress red, fixed); Standards 1 hard (fixed) + judgement calls (accepted);
Spec 2 (stale text, fixed; toilet trade-off documented). Fixed before archive: shutters, shared window, floor,
comments, alias, spec text. Accepted: existing sub-model patterns (`cm()`, wall literals in `waende()`), hairline gaps.
