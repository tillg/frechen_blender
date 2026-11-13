---
feature: 19-wandlampen-og
title: "Plan: Wandlampen im 1. Stock"
status: applying
order: 4
created: 2026-11-13
edited: 2026-11-13
---
# Plan: Wandlampen im 1. Stock

Existing tests that pin the old numbers get the new values in the step that changes them, as
that step's Red. Approving this plan is the permission for exactly these edits:
- the `ROOM_LIGHTS` count 23 → 14 in `test_core.py`, `test_gltf.py` and `blueprint.test.js`
- the two mirrors 95 → 85 in `test_og_flur_waschbecken_between_the_two_doors`,
  `test_waschbecken_og_baeder` and `test_gaestebad_submodel`
- the nearest-site indices in `lighting.test.js`
- the Blender golden

## Steps

- [x] [python] The lamp: `wandlampe()` with materials `Messing` and `Opalglas`, recording its light in `WALL_LIGHTS`
  - Test first: `tests/test_core.py` › `test_wandlampe_after_the_photo`. It builds one lamp into
    a scratch collection at a wall point and asserts:
    - shade Ø 0.16 ± 2 mm and 0.11 ± 5 mm high;
    - reach from the wall 0.21 ± 5 mm;
    - total height ≤ 0.21, of which ≤ 0.085 above the rosette centre;
    - materials `Messing` (rosette, arm, gallery) and `Opalglas` (shade);
    - every part is closed (each edge used twice);
    - its light, recorded in `WALL_LIGHTS`, lies 50 cm out from the wall at the bulb's height, in the
      shade's vertical plane (at the bulb itself, 13 cm from the plaster, it burnt a bright spot
      into the wall: request 2026-11-13);
    - `Opalglas` has `night=True`;
    - no draw from the global random stream (its state is unchanged).

    Fails today: no `wandlampe`.
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k wandlampe` → green
- [x] [python] Mirrors 85 high, and the four + one lamps in the Gästebad and the two over the Flur basin
  - Test first:
    - `test_waschbecken_og_baeder`: the Gästebad frame top becomes zo + 2.02.
    - `test_og_flur_waschbecken_between_the_two_doors`: frame 1.10 × 0.85, glass 0.90 × 0.65.
    - `test_gaestebad_submodel`: the label becomes "Spiegel 140 × 85", and the sub's Wandlampen
      solids are among the house's.
    - New `test_wandlampen_over_the_og_mirrors`:
      - 4 lamps over the Gästebad mirror, rosettes at x 1.44 ± 0.175 and ± 0.525 on y 8.57;
      - 2 over the Flur mirror at 6.01 ± 0.275 on y 6.35;
      - 1 on the Gästebad west wall at y 6.545;
      - all with the rosette centre at zo + `WANDLAMPE_SPIEGEL_H`, and the rosette clear above
        the mirror's frame.

    Fails today: mirrors 0.95, no lamps.
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "waschbecken or gaestebad or wandlampen"` → green
- [x] [python] The other 22 OG lamps: the 21 of `WANDLAMPEN_OG` at `WANDLAMPE_H` (`build_wandlampen()`) and the one over the WC mirror (`build_sanitary()`)
  - Test first: `test_wandlampen_og_placements` asserts the rosette centre of every lamp listed
    in the proposal's table, to the cm and per room, 29 in all. `test_wandlampen_clear` asserts:
    - no lamp's box intersects a door leaf from `BP.doors` (2.0 high), an `OG_Moebel` part, the
      box of a wall opening in `OPENINGS` or of an interior door opening;
    - every lamp sits on a wall face (the rosette touches a `_Waende` part);
    - every lamp stays ≥ 1 cm under the ceiling (Z_OG_TOP).

    Fails today: 7 lamps, not 29.
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k wandlampen` → green
- [x] [python] Lights: `ROOM_LIGHTS` without the OG fill lights except Bad S; `Blueprint.wall_lights`; glTF `extras.wall_lights`
  - Test first:
    - `test_paint_and_room_lights_live_in_the_core`: 14 entries, `(7.0, 1.5, Z_OG)` the only OG
      one, and `BP.wall_lights == WALL_LIGHTS` with 29 entries.
    - `test_gltf.py`: `room_lights` 14, `wall_lights` 29, equal to the Blueprint's.
    - `test_gaestebad_submodel`: its Blueprint has 5 `wall_lights`, and `build()` afterwards has 29
      (registries cleared).

    Fails today: 23 room lights, no `wall_lights`.
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py tests/test_gltf.py -k "light or gaestebad"` → green
- [x] [python] The film camera clears the lamps: every route frame in the OG keeps ≥ 0.25 m from every lamp's box
  - Test first: `tests/test_tour.py` › `test_routes_and_spots_clear_the_wandlampen`, over every
    route and every Standpunkt. It failed in the Schlafzimmer (route on x 14.0: 14 cm; on y 0.75:
    24 cm) and at the Standpunkte Waschküche (10 cm) and Yoga (18 cm). Agreed 2026-11-13: the route
    moves to x 13.85 and y 0.90, the Standpunkte to (8.25, 3.30) and (5.60, 9.40);
    `tests/golden/tour.json` regenerated.
  - Verify: `.venv/bin/python -m pytest -q tests/test_tour.py -k wandlampen` → green
- [x] [web] Viewer: bulb sites join the room-light ranking with their own base; the Gästebad page colours its lamps
  - Test first: `web/src/lighting.test.js`:
    - hires: one light per room site and per bulb, bulbs at their absolute (x, y, z), intensity
      `LAMP_BASE · v`;
    - fast mode: the pool of 6 from an OG room camera (Waschküche) lands on its five bulbs and one
      more;
    - the nearest-site indices of the existing cases recomputed for the 14 + 29 sites;
    - `blueprint.test.js` 23 → 14.

    Fails today: `wall_lights` ignored.
  - Verify: `cd web && npx vitest run src/lighting.test.js src/blueprint.test.js` → green. Then
    dusk screenshots (`Abend`) from inside the Gästebad, Waschküche and Flur, in fast mode and
    with `?hires=on`, read at 1×: lamps lit, shades glowing, no blow-out. Then a day close-up of
    one lamp against the photo.
- [x] [python] The mirrors are furnishings (request 2026-11-13): `bad_mirror()`, `wc_mirror()` and `wood_mirror()` build into `<coll>_Spiegel`, and `EG_Spiegel` / `OG_Spiegel` are in `FURNITURE`, so the plan sheets leave them out and the viewer shows them in Eingerichtet
  - Test first: the mirror checks of `test_og_flur_waschbecken_between_the_two_doors`,
    `test_wc_fixtures_after_the_photo`, `test_waschbecken_og_baeder`,
    `test_wandlampen_over_the_og_mirrors`, `test_gaeste_wc_submodel` and `test_gaeste_wc_export`
    look in `_Spiegel`; red until the helpers move.
  - Verify: `.venv/bin/python -m pytest -q -m "not slow" tests/` → green
- [ ] [blender] `film.py`: one `Wandlampe_NN` point light per bulb in `Innenlicht` (deferred by request: after the next changes)
  - Test first: an MCP check after rebuilding: `Innenlicht` holds 14 `Innenlicht_*` + 29
    `Wandlampe_*` + 1 `Lampe_*`, each lamp light at a `WALL_LIGHTS` site. Fails today: 23 + 0 + 1.
  - Verify: rebuild in the `CLAUDE.md` order and save. Render stills of the Gästebad (mirror wall)
    and the Waschküche (table wall) to `tmp/details/` and read them. Run the camera clearance
    check (BVH ≥ 0.25 m) over the film route. Regenerate the golden (`UPDATE_GOLDEN=1`), read its
    diff, save the `.blend`.
- [ ] [python] Plan sheets regenerated (deferred by request: after the next changes)
  - Test first: existing `tests/test_plans.py` (room areas unchanged, sheets current). Fails
    today: the sheets are out of date.
  - Verify: `python3 code/export_plans.py plans/ && .venv/bin/python -m pytest -q tests/test_plans.py` →
    green. The diff shows only the model hash and the two mirrors.
- [x] [docs] README: Wandlampen in the component list; `wandlampe.png` committed as input
  - Test first: none, docs only
  - Verify: `grep -n "Wandlampe" README.md` matches; `git ls-files "input/2026-11-13 input/wandlampe.png"` lists it

System docs are updated at `/spec:archive`.
