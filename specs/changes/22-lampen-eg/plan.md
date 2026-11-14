---
feature: 22-lampen-eg
title: "Plan: Lampen im EG"
status: applying
order: 4
created: 2026-11-14
edited: 2026-11-14
---
# Plan: Lampen im EG

## Steps

- [x] [python] `wandlampe(obj=, variant=)`, `WANDLAMPEN_EG` with the agreed placements, the layout objects, `FURNITURE`
  - Test first: `tests/test_core.py` › `test_wandlampen_eg_placements` — the rosettes of `EG_Wandlampen`,
    `EG_Wandlampen_Essen` (main) and `EG_Alt_Wandlampen` (alt) are exactly the agreed list (1.5 mm), at
    1.70 / 2.10; their lights tagged in `Blueprint.wall_variant`; the objects in `FURNITURE`; `default_layout()`
    drops the alt lights — fails today: no EG lamps
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k wandlampen_eg` → green; Show
- [x] [python] Ofen bed: a Wandlampe instead of the reading lamp (sub-model and house); the always-on lamp
  plumbing (`LAMP_LIGHTS`, `lamp(outside=)`, `GluehfadenAn`, `Blueprint.lamp_lights`, export, film, viewer)
  removed with its 3 tests (user's OK 2026-11-14)
  - Test first: `test_core.py` › `test_ofen_bed_wandlampe` — `Ofen_Wandlampen` on the head-end wall at
    2.10 (house: west wall x 9.056, y 5.495, facing east), no `Ofen_Lampe`, no `LAMP_LIGHTS`, its light in
    `wall_lights` — fails today: the gooseneck lamp
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "ofen"` → green
- [x] [python] Küche: the hood's spot strip
  - Test first: `test_core.py` › `test_haube_spots` — a Metall strip under the hood's back edge with 4
    Opalglas spots evenly along it, their 4 lights under them in `wall_lights` — fails today: no strip
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k haube` → green
- [x] [python] Fill lights: only the Speis keeps one; clearances
  - Test first: `ROOM_LIGHTS` == [Speis]; `test_wandlampen_clear` extended to the EG (solid wall behind
    each rosette; clear of leaves, furniture, fixtures, the shelves); `test_routes_and_spots_clear_the_wandlampen`
    over all lamps — fail today: 14 fill lights, no EG lamps checked
  - Verify: `.venv/bin/python -m pytest -q tests -k "wandlampen or room_lights"` → green
  - Done: lamps 13, 14 centred on B's boards (3.90, 4.72; the thirds fell on board joints); lamp 1 at 13.57
    (between the Windfang leaf and the front door's leaf opened by the film); off the plan sheets via
    `PLAN["skip_words"]` (not `FURNITURE`, which would also change the viewer stage)
- [x] [python] Deliberate updates of tests pinning today's numbers
  - Test first: lamp/light counts in `test_core.py`, `test_gltf.py`, `test_tour.py`; Ofen lamp tests — fail
    after the steps above for exactly these numbers
  - Verify: `bash scripts/check.sh quick` (pytest part) → green
- [x] [web] `lighting.js`: only the current layout's wall lights; `main.js` passes the layout
  - Test first: `web/src/lighting.test.js` › layout-aware sites (default: no alt lights among the sites,
    eg_alt: no main lights) + updated counts and nearest sets — fails today: all lights always
  - Verify: `cd web && npx vitest run src/lighting.test.js` → green; dusk screenshot of the Essen in both layouts
- [ ] [docs] README (components, Wandlampen count, the drawing), CLAUDE.md if needed; drawing `input/2026-11-14 input/lampen_eg_v1.svg` + generator
  - Test first: none — docs
  - Verify: `grep -c "Lampen im EG\|lampen_eg" README.md` ≥ 1; the drawing regenerates identically
- [ ] [blender] Rebuild, save, parity golden, plan sheets, film lights, clearance, still
  - Test first: `tests/test_blender_parity.py` fails on the new lamps (slow)
  - Verify: headless rebuild + save; `UPDATE_GOLDEN=1 … test_blender_parity.py`; `python3 code/export_plans.py plans/`;
    camera clearance of both routes; a dusk still of the Stube to `tmp/details/`; `bash scripts/check.sh full` → green

System docs are updated at `/spec:archive`.
