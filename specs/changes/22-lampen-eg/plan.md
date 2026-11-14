---
feature: 22-lampen-eg
title: "Plan: Lampen im EG"
status: applied
order: 4
created: 2026-11-14
edited: 2026-11-14
---
# Plan: Lampen im EG

## Steps

- [x] [python] `wandlampe(obj=, variant=)`, `WANDLAMPEN_EG` with the agreed placements, the layout objects, off the plans
  - Test first: `tests/test_core.py` › `test_wandlampen_eg_placements` — the rosettes of `EG_Wandlampen`,
    `EG_Wandlampen_Essen` (main) and `EG_Alt_Wandlampen` (alt) are exactly the agreed list (1.5 mm), at
    1.70 / 2.10; their lights tagged in `Blueprint.wall_variant`; "Wandlampen" in `PLAN["skip_words"]`; `default_layout()`
    drops the alt lights — fails today: no EG lamps
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k wandlampen_eg` → green; Show
- [x] [python] Ofen bed: a Wandlampe instead of the reading lamp (sub-model and house); the always-on lamp
  plumbing (`LAMP_LIGHTS`, `lamp(outside=)`, `GluehfadenAn`, `Blueprint.lamp_lights`, export, film, viewer)
  removed with its 3 tests: `test_ofen_lamp_is_switched_on`, the viewer's switched-on lamp test in
  `lighting.test.js`, the filament test in `materials.test.js` (user's OK 2026-11-14)
  - Test first: `test_core.py` › `test_ofen_bed_wandlampe` — `Ofen_Wandlampen` on the head-end wall at
    2.10 (house: west wall x 9.056, y 5.495, facing east), no `Ofen_Lampe`, no `LAMP_LIGHTS`, its light in
    `wall_lights` — fails today: the gooseneck lamp
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "ofen"` → green
- [x] [python] Küche: the hood's spot strip
  - Test first: `test_core.py` › `test_haube_spots` — a Metall strip under the hood's back edge with 4
    Opalglas spots evenly along it, their 4 lights under them in `wall_lights` — fails today: no strip
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k haube` → green
- [x] [python] Fill lights: only the Speis keeps one; clearances
  - Test first: `test_room_lights_only_the_speis`; new `test_eg_lamps_clear` (the OG's `test_wandlampen_clear` stays) for the EG (solid wall behind
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
  - Done: e2e `stages.spec.js` updated (hires count 1 + 71; the Stube's own lights instead of its fill light;
    the check after `lookFrom` dropped: the controls lift that camera to 3.3 m, it passed only by coincidence,
    the URL Stube view right after checks the same properly); dusk shots `tmp/web/i22_*.png` read
- [x] [docs] README (components, Wandlampen count, the drawing), CLAUDE.md if needed; drawing `input/2026-11-14 input/lampen_eg_v1.svg` + generator
  - Test first: none — docs
  - Verify: `grep -c "Lampen im EG\|lampen_eg" README.md` ≥ 1; the drawing regenerates identically
- [x] [blender] Rebuild, save, parity golden, plan sheets, film lights, clearance, still
  - Test first: `tests/test_blender_parity.py` fails on the new lamps (slow)
  - Verify: headless rebuild + save; `UPDATE_GOLDEN=1 … test_blender_parity.py`; `python3 code/export_plans.py plans/`;
    camera clearance of both routes; a dusk still of the Stube to `tmp/details/`; `bash scripts/check.sh full` → green

  - Done: headless rebuild (MCP down) + save, parity golden (rnd shift after the removed lamp's draws; later
    only `_room_lights` for the moved hood light), plan sheets, drawing regenerated; clearance of both routes
    0 frames under 0.25 m, 0 crossings; stills `tmp/details/eg_lamps_stube.png`, `eg_lamps_kueche.png` read;
    `check.sh full` green but the tour frame-rate test (machine load, red in the baseline too)

System docs are updated at `/spec:archive` (also #19's Wandlampe, folded in on the user's choice).
