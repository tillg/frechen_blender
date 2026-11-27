---
feature: 61-umbauten
title: "Plan: Umbauten EG/OG"
status: applied
order: 4
created: 2026-11-27
edited: 2026-11-27
---
# Plan: Umbauten EG/OG

Tests that pin a removed feature are rewritten for the new state in the same step (the change the user asked for).

## Steps

- [x] [python] Speis: drywall on the Essen side of shelf B, lamps 13/14 on its face
  - Test first: `tests/test_core.py` › `test_speis_trockenwand` — fails today: no wall part at y 3.64..3.714
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k trockenwand` → green; Show
- [x] [python] Küche: hood gone, Muldenlüfter in the cooktop
  - Test first: `test_core.py` › `test_kueche_muldenluefter` — fails today: `EG_Haube` exists, no vent
  - Verify: `pytest -k "muldenluefter or kueche"` → green; Show
- [x] [python] Bad Oma & Opa: one room, one sliding leaf, Einbauschrank
  - Test first: `test_core.py` › `test_bad_submodel`, `test_bad_built_into_the_grosseltern` rewritten — fail today: niche wall and two leaves
  - Verify: `pytest -k bad` → green; Show `--page bad`
- [x] [python] Oberlicht half as high (sill 1.70)
  - Test first: `test_core.py` › `test_oberlicht_bad_waschkueche` (sill 1.70) — fails today: sill 1.20
  - Verify: `pytest -k oberlicht` → green; Show
- [x] [python] Waschküche: shower gone, cupboard back to 5.95 × 3 baskets
  - Test first: `test_core.py` › `test_waschkueche_ohne_dusche` — fails today: shower glass present
  - Verify: `pytest -k waschkueche` → green; Show
- [x] [python] Hintereingang: Duschbad (variant B) + Schuhregal; Garderobe there gone
  - Test first: `test_core.py` › `test_gaeste_wc_submodel` rewritten, `test_schuhregal` — fail today: partition, old north wall
  - Verify: `pytest -k "gaeste_wc or duschbad or schuh"` → green; Show `--page gaeste_wc`
- [x] [python] Flur-Garderobe G1 (`code/garderobe.py`), lamps 18/19 up
  - Test first: `test_core.py` › `test_flur_garderobe` — fails today: nothing on the Flur south wall
  - Verify: `pytest -k garderobe` → green; Show
- [x] [python] Ofen narrow (1.20 × 0.50), straight bed 70 × 190, old corner stove's draws burnt
  - Test first: `test_core.py` › `test_ofen_submodel_after_the_sketches` rewritten, `test_ofen_built_into_the_stube` — fail today: corner stove 1.20 × 1.20
  - Verify: `pytest -k ofen` → green; Show
- [x] [python] Essen Bauernschrank (`bauernschrank(ax="y")`), Speis panel door, drywall from the west wall
  - Test first: `test_core.py` › `test_speis_essen` rewritten, `test_speis_v6`, `test_one_eg_layout` — fail today: cabinet C, saloon leaves
  - Verify: `pytest -k "speis or essen or eg_layout"` → green; Show
- [x] [python] Schuhregal 2 m, Einbauschrank turned 90°, bench under the Flur Garderobe
  - Test first: `test_schuhregal`, `test_bad_submodel`, `test_flur_garderobe` extended — fail today: 0.50 high rack, cabinet on the south wall, no bench
  - Verify: `pytest -k "schuhregal or bad or garderobe"` → green; Show
- [x] [python] OG Bauernschränke (Saschi, Schlafzimmer, Bichlach; `bauernschrank(face=-1)`), the wardrobes' draws burnt
  - Test first: `test_core.py` › `test_og_bauernschraenke_in_place_of_the_wardrobes` — fails today: built-in wardrobes
  - Verify: `pytest -k bauernschr` → green; Show
- [x] [web] Viewer and e2e follow the renamed objects (Bad leaf, Gäste-WC labels, Vorlagen anchor)
  - Test first: `web/e2e/bad.spec.js`, `gaeste_wc.spec.js` updated — fail today on the old names
  - Verify: `npx playwright test e2e/bad.spec.js e2e/gaeste_wc.spec.js e2e/vorlagen.spec.js e2e/shot.spec.js` → green
- [x] [docs] README, CLAUDE.md, module docstrings; plan sheets regenerated
  - Test first: none — docs; plan currency is `tests/test_plans.py`
  - Verify: `python3 code/export_plans.py plans/` then `bash scripts/check.sh full` → green

System docs are updated at `/spec:archive`.
