---
feature: 26-haube-induktion
title: "Review: the hood over the cooktop, the Wamsler's pipe higher into the wall"
status: applied
order: 5
created: 2026-11-15
edited: 2026-11-15
---
# Review: the hood over the cooktop, the Wamsler's pipe higher into the wall

**Scope:** `git diff fix/waschkueche-zwei-maschinen...HEAD` (2 commits) · **Reviewed:** 2026-11-15

## Defects

- [MEDIUM] Riser of the Wamsler pipe ended at `zc + 0.06`, 1 mm above the elbow's top: two near-coplanar tops with different `rnd`. · `code/ofen.py` · z-fight / lip · **Fixed:** the riser ends at `zc` inside the elbow; the test asserts it ends between the elbow's bottom and top.
- [LOW] Rosette ended 2 mm short of the east wall face (8.555 vs 8.557). · `code/ofen.py` · visible gap · **Fixed:** rosette x 8.547–8.557; test tolerance tightened to 1e-6.
- [LOW] The Rundgang guard covered only hood and pipe, not the Küche cabinets next to the moved Standpunkt. · `tests/test_tour.py` · coverage gap · **Fixed:** all `EG_Haube`, `EG_Herd` and `EG_Kueche` parts.

## Standards

- Comments in `wamsler()` split mid-phrase over several lines; docstring wrap ragged. **Fixed.**
- Judgement: `test_routes_and_spots_clear_the_kueche_hood` repeats the box/gap pattern of the Waschküche and Elternbad guards (Duplicated Code) — accepted, the file's established pattern.
- Judgement: magic numbers in the hood geometry (`zl + 0.14`, …) — accepted, the module's style (the old hood had the same).
- The new rosette draws one more `rnd` from the Küche's own stream: only Küche parts after it shift shading; the rest of the house is untouched (the docstring's claim holds).

## Spec

- Küche Standpunkt moved (`code/tour.py`) and `web/src/lighting.test.js` site index 2 → 31: beyond the plan's letter, both logged in decisions 31/32 with the reason (hood filled the Standpunkt's view; the pinned lit set changed).
- The rewritten hood test lost the old width lower bound: **fixed** (x 0.8–1.0, y 0.5–0.7). Material set stays asserted in `test_kueche_hood_sink_tap_and_wamsler_in_steel`.
- Show done: `tmp/web/26-kueche-sub.png`, `26-eye-hob-wamsler.png`, `26-spot-60.png`, `26-spot-c2-60.png`, `26-pipe-close.png`.

## Verdict

Defects 3 (worst MEDIUM), Standards 4 (worst: comment style), Spec 3 (worst: Standpunkt moved beyond the plan). All defects fixed before archive; the duplicated guard pattern and magic numbers accepted as the files' existing style.
