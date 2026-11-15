---
feature: 33-zwei-duschen
title: "Review: two showers in the Bad Nadine & Till"
status: applied
order: 5
created: 2026-11-15
edited: 2026-11-15
---
# Review: two showers in the Bad Nadine & Till

**Scope:** working-tree diff on `issue/33-zwei-duschen` against `issue/31-fotos-anzeigen` · **Reviewed:** 2026-11-15

## Defects

- [HIGH] The Blender `.blend` and parity golden were not rebuilt. Not applicable: the Blender backend has been dormant since #35, and no parity test exists any more.
- [MEDIUM] `web/src/lighting.test.js` hard-codes the pool indices (66, 64, 34, 65). This matches the file's existing style. The indices were taken from a probe of the new glb (default camera: the six nearest sites are 35, 22, 23, 66, 64, 34, and the 7th is 65). Accepted.
- [LOW] The Rundgang stop at y 1.15 looks through the south pane, not through the passage. The test docstring and decision -14 were corrected to say so.
- [LOW] The north pane's end and its rail reach into the north wall above 1.20, by 4 mm (glass) and 12 mm (rail). This is how a pane is fixed, not a fixture on the wall. Decision -12 notes it for #30. Accepted.
- [LOW] About 11 mm of plaster between the north limestone (to 6.485) and the tiles (from 6.496) sits behind the glass edge. Accepted.
- [LOW] The tour clearance test covers the east-wall lamps: their parts lie at x < 8.6, so they are inside the filter. The toilet/basin clearance compares x only, which is correct because both stand on the north/east walls. No change.

## Standards

- The lighting cut-off assertion now targets the Stube lamp (34). It is the 6th-nearest site under the same rule; the Elternbad lamps moved out of that rank. Accepted.
- The plan named the tour test `test_routes_clear_the_elternbad`; the test is `test_routes_and_spots_clear_the_elternbad`. Fixed in the plan.
- A one-element loop remains in `test_waschbecken_og_baeder`. Smells (judgement calls): terse constants (`XG`, `PA`, `PB`), matching the file's style; two near-identical `shower()` calls. Accepted.

## Spec

- The architecture said "≥ 40 free each side", while the test asserts ≥ 20, the issue-level requirement. The architecture was corrected (as built: 44 / 69).
- The heads hang 30 cm from each side wall: "in the corner", with room for the 12 cm head disc. Documented in decision -12.
- Red runs were seen: `test_elternbad_layout` and the tour tests failed before the code changed.

## Verdict

Defects: 1 HIGH (not applicable, Blender dormant), 1 MEDIUM and 4 LOW, all accepted or fixed (wording). Standards: 1 drift, fixed; the rest are judgement calls. Spec: 1 mismatch, fixed in the architecture.
