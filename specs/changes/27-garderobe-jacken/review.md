---
feature: 27-garderobe-jacken
title: "Review: Garderobe für viele Jacken"
status: applied
order: 5
created: 2026-11-15
edited: 2026-11-15
---
# Review: Garderobe für viele Jacken

**Scope:** `git diff issue/28-waschkueche-fliesenboden...HEAD` (2 commits, plans excluded) · **Reviewed:** 2026-11-15

## Defects

- [MEDIUM] Coat hems vs the boots under them not tested (Kamel hem 0.704, boot top 0.67). Fixed: the test asserts each coat's hem ≥ 2 cm above the shoes under it.
- [MEDIUM] Hook count only `>= 20`. Fixed: rows 12 + 11 asserted.
- [LOW] Bench-absence check weak (exact z 0.45 / filter excluded y near the wall). Fixed: no Garderobe part between 0.55 and 1.30.
- [LOW] Hanger hook ran through the collar. Fixed: it starts at the collar top.

## Standards

- Stale docstring of `test_gaeste_wc_submodel` (bench) — fixed. Three blank lines before a test — fixed.
- Label "Stange" vs domain term "Kleiderstange" — fixed (label "Kleiderstange 94 auf 178").
- Golden/.blend not regenerated — not applicable: the Blender backend is dormant (issue #35, `project.md`).
- Judgement calls accepted: short local lambdas (`X`, `Bx`, `T`) as elsewhere in the sub-model modules; the tour-clearance test copies the pattern of its neighbours.

## Spec

- Hash check "other objects unchanged" was run as a script (only `*_Garderobe` changed, `*_Kleidung` new), not as a test — accepted.
- Tour clearance asserted at 0.25 m (the project's rule), measured 1.35 m.
- `test_garderobe_kleidung` is a separate function instead of "extended" — naming only.
- Hat shelf raised to 1.95: needed for the upper hook row, logged in decision run-2026-11-15-1633-27.
- Step 3's red side was the core label assertion (noted in plan.md); the viewer colour has no test (presentation only).

## Verdict

Defects 4 (worst MEDIUM), Standards 3 + judgement calls (worst LOW), Spec 5 (worst LOW). All MEDIUM/LOW defects and the standards breaches fixed before archive; the rest accepted as noted.
