---
feature: 10-hoehenverstellbarer-schreibtisch
title: "Review: Höhenverstellbarer Schreibtisch"
status: applying
order: 5
created: 2026-11-12
edited: 2026-11-12
---
# Review: Höhenverstellbarer Schreibtisch

**Scope:** working tree vs `main` (uncommitted at review time) · **Reviewed:** 2026-11-12

## Defects

- [LOW] Test comment "2.5 turns" wrong (2.5π = 1.25 turns) · `web/src/slides.test.js` · misleading ·
  fixed.
- [LOW] `Kirschbaum` MAT_DEF entry not indented · `code/house_core.py` · style · fixed.
- [LOW] Clearance test skipped lifted parts below 0.70 m (spindles) · `tests/test_core.py` · a
  spindle collision would go unnoticed · fixed: all lifted parts swept, spindles exempt only inside
  the frame's footprint; a probe box in the lift path is caught.
- [LOW] `house_core.build()` at the end of the random-stream test called dead · not a defect: it
  restores the registries after the scratch build · kept.
- [LOW] `liftBoxes` without `updateMatrixWorld` · `web/src/main.js` · correct only by accident ·
  fixed.
- [LOW] Hand wheel aliasing: 8 turns in 3 s peak ≈ 48°/frame at 30 fps, five spokes (72°) ·
  `code/desk.py` · looks like spinning backwards · fixed: 4 turns per stroke.
- [LOW] Blender/film show the desk at 75 cm only · intended (proposal non-goal), README says so.

## Standards

- No documented standard broken. Pre-existing tests edited, all because the desk changed size,
  place and objects (none weakened): `test_bibliothek_piano_desk_and_werkstattofen`,
  `test_desk_submodel`, `test_desk_built_into_the_bibliothek` (`tests/test_core.py`),
  `test_desk_export` (`tests/test_gltf.py`, assertions only added), `web/e2e/desk.spec.js`
  ("Tisch 190").
- Judgement calls, accepted: `liftingNodes` / `lifters` / `liftBoxes` follow the existing
  `swingingNodes` / `swingers` / `swingBoxes` pattern rather than abstracting it; frame sizes are
  literal numbers read off the photo (marked assumed in the proposal and the dimensions);
  `desk.js` repeats the desk centre and wall line like before.

## Spec

- Proposal now says the spindles run inside the housings by design (was "every lifted part stays
  clear").
- Step 3 test now asserts the crank's full angle at the top.
- Photo details simplified (round spindle bells as square housings, no gear teeth, no lettering):
  within the proposal's non-goals.
- No ADR contradicted.

## Verdict

Defects 7 LOW (6 fixed, 1 kept as not a defect); Standards 0 breaches, a few judgement calls
accepted; Spec 2 gaps, both fixed. The user checked the desk in the viewer and approved it
(2026-11-12).
