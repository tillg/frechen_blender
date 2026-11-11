---
feature: 2d-plan-export
title: "Plan: 2D plan export"
status: applying
order: 4
created: 2026-11-11
edited: 2026-11-11
---
# Plan: 2D plan export

Every step is `[python]` (the viewer and the Blender output are untouched). A step with a visible result is checked by a **Look** instead of a Show:

- `rsvg-convert -w 2400 -b white plans/<s>.svg -o tmp/plans/<s>.png`, then read the PNG at 1× and zoom into the changed spot with `magick … -crop`;
- for floor plans, also an overlay on `input/2026-11-03 input/grundriss_<eg|og>.png`, using the page transform of `build_references()`.

The per-step check is the step's test plus `bash scripts/check.sh quick`.

## Steps

- [x] [python] `DOORS` registry: every hinged leaf records storey, hinge point, width, wall axis, swing side and opened angle
  - **Scope:** `panel_door`, `entrance_door` and `back_door` append to `DOORS`; `build()`/`build_*()` clear it; the Blueprint gets `doors`. No `random` draws, no `GEO` change.
  - **Test first:** `tests/test_plans.py` › "every opened leaf has a door record". Assert the number of `DOORS` per storey equals the number of hinged leaves (`LEAVES` without the three sliding leaves, plus Haustür and Hintertür), and that the Küche door's hinge is at x = 6.125 (west jamb 6.10 plus its 2.5 cm lining) on the Küche face y = 5.849. Fails today: there is no `DOORS`.
  - **Verify:** `.venv/bin/python -m pytest -q tests/test_plans.py tests/test_tour.py tests/test_gltf.py` → green. The parity golden is unchanged; the full tier runs at the end.

- [x] [python] `PLAN_ROOMS`: the architect's room names with storey and anchor, for every room of EG and OG
  - **Scope:** the table in `house_core.py`, with names as in the PDFs (EG: Großeltern, Bad Großeltern, WC Großeltern, Flur (2×), WC, Garderobe, Bibliothek, Neuer Windfang, Küche, Speis, Stube, Elektroraum, Heizung; OG: Schlafen bzw. Yoga, Schlafen (4×), Bad (2×), WC (2×), Flur, Hauswirtschaftsraum). Where the model changed a room, the model's room wins (Gäste-WC + Garderobe; Musikraum + Büro are one open region, "Bibliothek", user 2026-11-11).
  - **Test first:** `tests/test_plans.py` › "plan room anchors lie inside the footprint and outside every wall". Fails today: there is no table.
  - **Verify:** `.venv/bin/python -m pytest -q tests/test_plans.py` → green

- [x] [python] Sheet writer: A3 at 1:100, title block with model state, scale bar, deterministic output
  - **Scope:** `code/export_plans.py`, with `sheet()`, number formatting, `model_state(bp)`, and the CLI `python3 code/export_plans.py <outdir>` writing six (empty-drawing) sheets.
  - **Test first:** `tests/test_plans.py` covers:
    - "sheets are A3 in mm with a 1 m = 10 mm scale bar": parse with `xml.etree`; `width="420mm"`, `height="297mm"`, `viewBox="0 0 420 297"`; the 5 m scale bar is 50 units long;
    - "export is byte-identical across processes": two subprocess runs with `PYTHONHASHSEED=1` and `2` give identical bytes.

    Both fail today: there is no module.
  - **Verify:** `.venv/bin/python -m pytest -q tests/test_plans.py` → green

- [x] [python] Grundriss section: walls hatched inside one union outline, other cut parts thin, at the cut height per storey
  - **Scope:**
    - `section(bp, storey)` slices the closed Parts into loops;
    - wall loops are filled with the hatch, and the union outline is stroked with seams removed;
    - cut heights are EG 1.80 and OG 1.55 above the floor.
  - **Test first:** `tests/test_plans.py` covers:
    - "every opening spans its storey's cut height" (`OPENINGS` and `DOORS`);
    - "the EG wall outline spans the footprint": the stroked outline's bbox equals 0…`W_OUT` × 0…`D_OUT` plus the annex `ANNEX`;
    - "no stroked wall edge lies inside the wall union": the midpoint of every stroked edge has wall on one side only;
    - "each exterior opening of the storey is a gap in the outline".

    All fail today: there is no `section`.
  - **Verify:**
    - `.venv/bin/python -m pytest -q tests/test_plans.py` → green;
    - Look at `eg.png`/`og.png` and the overlays: the walls line up with the architect's plans; no seams in the hatch.

- [x] [python] Projection: one hidden-line routine for plan (below the cut) and elevation (one facade)
  - **Scope:** `project(bp, view, clip)`:
    - `mesh_ops.orient` per Part, back-face and edge-on culling;
    - far-to-near order with white fills, a 2 cm occupancy raster cull;
    - no stroke on edges between coplanar faces of the same material;
    - garden excluded from elevations; loose furniture (`bp.furniture`) excluded from elevations and plans, the built-ins below the cut stay in plans;
    - glass opaque.
  - **Test first:** `tests/test_plans.py` covers:
    - "Ansicht Süd outline": the silhouette spans the roof width `W_OUT + 2·GABLE_OH` and reaches `RIDGE_Z`;
    - "no loose furniture on any sheet": no polygon in an elevation or a plan comes from an object in `bp.furniture`;
    - "plans show the stairs and the kitchen below the cut": polygons from `EG_Treppe` and `EG_Kueche` are present in `eg.svg`, none from `OG_*` objects;
    - "size and time budget": six sheets in ≤ 30 s, each ≤ 2 MB.

    All fail today: there is no `project`.
  - **Verify:**
    - `.venv/bin/python -m pytest -q tests/test_plans.py` → green;
    - Look at all four elevations against `Ansichten neuer Entwurf.pdf`: no interior through the windows, no wall seams in the plaster, shutters, cladding and roof boards as in the architect's sheet.

- [x] [python] Door swings in the floor plans: leaf line and quarter arc per `DOORS` entry
  - **Test first:** `tests/test_plans.py` › "one arc per door of the storey, centred on its hinge, radius = leaf width". Fails today: no arcs are drawn.
  - **Verify:**
    - `.venv/bin/python -m pytest -q tests/test_plans.py` → green;
    - Look: zoom on Küche door, Windfang double door and the back hall's three doors.

- [x] [python] Room labels: architect name and computed net area
  - **Scope:** a region fill of the near-ceiling section (EG 2.19, OG +2.15; exterior openings closed on the inner face; walls and ceiling-high built-ins divide); the label "Name / 12,34 m²" at the anchor.
  - **Test first:** `tests/test_plans.py` covers:
    - "each plan room is its own region": no region holds two anchors, and no named region is open to the outside;
    - "Bad Großeltern area = `bad.W · (bad.D − bad.NICHE)` minus the shaft" within ± 0.01 m² (the niche is apart, user 2026-11-11);
    - "the area label uses a decimal comma and two decimals".

    All fail today: there are no labels.
  - **Verify:**
    - `.venv/bin/python -m pytest -q tests/test_plans.py` → green;
    - Look: every room is labelled once and no label overlaps a wall.

- [x] [python] Dimension chains on the floor plans: openings, walls, overall, on all four sides
  - **Scope:** `fmt_dim()` in the architect's notation; chains scanned from the section; cumulative rounding; tick marks; text above the line, rotated on the vertical sides.
  - **Test first:** `tests/test_plans.py` covers:
    - "notation": 0.31 → "31", 0.415 → "41⁵", 2.05 → "2.05", 4.015 → "4.01⁵", 14.885 → "14.88⁵";
    - "every chain sums to its overall dimension";
    - "the EG overall chains are `W_OUT` and `D_OUT`";
    - "the north opening chain has the edges of the north `OPENINGS`";
    - "the walls chain runs inside the rooms, not inside the facade wall" (added in apply: the east wall's south part is 53.5 cm thick, so the scan line lies 5 cm beyond the facade wall's thickness, probed along the side).

    All fail today: there are no chains.
  - **Verify:**
    - `.venv/bin/python -m pytest -q tests/test_plans.py` → green;
    - Look: compare the EG north side with the architect's chain (31 | 2.05 | 30 | 3.37 …). Differences only where the model differs.

- [x] [python] Elevation annotation: level marks (±0,00, OK FFB OG, Traufe, First) and the overall width chain
  - **Test first:** `tests/test_plans.py` › "Ansicht Süd marks ±0,00, +2,70 and +7,67 and the width chain spans the facade". The values come from `Z_OG` and `RIDGE_Z`. Fails today: no marks.
  - **Verify:**
    - `.venv/bin/python -m pytest -q tests/test_plans.py` → green;
    - Look at all four elevations.

- [x] [python] Commit `plans/` and keep it current
  - **Scope:** run `python3 code/export_plans.py plans/` and commit the six SVGs.
  - **Test first:** `tests/test_plans.py` › "plans/ equals a fresh export", marked `slow`. Fails today: `plans/` does not exist.
  - **Verify:** `.venv/bin/python -m pytest -q -m slow tests/test_plans.py` → green

- [x] [docs] README (German): the Pläne section (what, how to export, `plans/`), the component list and the script table. `CLAUDE.md`: `export_plans.py` under "Other scripts", plus the rule "after a core change, re-run `export_plans.py`" under Running.
  - **Test first:** none, no runtime surface
  - **Verify:** `grep -q "export_plans.py" README.md && grep -q "export_plans.py" CLAUDE.md`

- [x] Final check: `bash scripts/check.sh full` → green. There is no Blender rebuild because the Blender output is unchanged; the parity test confirms it.
  - **Test first:** none, final check
  - **Verify:** `bash scripts/check.sh full` exits 0

Notes from apply (2026-11-11):

- The determinism test and the currency test are marked `slow` (each runs the export again); the `slow` marker in `pytest.ini` says so. The time budget is measured as CPU time of the export process, so a busy machine does not fail it.
- Room regions are cut at 2.19 m in the EG (below the annex ceiling), and ceiling-high built-ins divide rooms (the Speis cabinet).
- Known gap, not in this change: the OG Grundriss shows the stairwell's railing but not the stair (it belongs to `EG_Treppe`). (Leaves opened flat no longer show twice: review fixes.)

## Review fixes (2026-11-11)

From `review.md`, the user chose "fix now". The user's choices: the door symbol is the conventional 90° symbol, and the elevation text is amended to match the code.

- [x] [python] Plan classification in the core (ADR-001-XEWL)
  - **Scope:**
    - `PLAN` lives next to `FURNITURE` / `NO_GRASS` / `BEDS` and holds names only:
      - the masonry objects and their wall material;
      - the window/door frame objects;
      - the floor and ceiling objects;
      - the ground objects left off the sheets;
      - the extra collections and objects each Grundriss draws besides its storey (`Balkone`).
    - The Blueprint gets a `plan` field.
    - `export_plans.py` reads it (`is_wall`, `plan_objects`, `GARDEN`, the `_Fenster_Tueren` filter) instead of naming model objects.
    - `GEO` and the random sequence are untouched, so the parity golden stays.
  - **Test first:** `tests/test_plans.py` covers:
    - "every object named in the plan table exists in the model";
    - "export_plans names no model object": the source contains none of `_Waende`, `EG_Anbau`, `Balkone`, `Gelaende`, `Kiesel`, `Kiesstreifen`, `_Fenster_Tueren`, `"Boden"`, `"Decke"`.

    Both fail today: there is no table.
  - **Verify:**
    - `.venv/bin/python -m pytest -q tests/test_plans.py tests/test_gltf.py tests/test_tour.py` → green;
    - `python3 code/export_plans.py tmp/plans-r1 && diff -r tmp/plans-r1 plans` → identical, because this is a pure move.

- [x] [python] The west larch cladding is drawn cut in both Grundrisse
  - **Scope:** `PLAN` lists `Verschalung_West` as an extra object of EG and OG. It lies in collection `Dach` and spans z 0.25–7.55, so both cut planes pass through it. `Verschalung_Ost` starts at z 4.90, above the OG cut (4.25), so it stays off both plans.
  - **Test first:** `tests/test_plans.py` › "the west cladding is cut in EG and OG, the east cladding in neither". `section()` has `Verschalung_West` loops at x −0.08…0 for both storeys and no `Verschalung_Ost` loop. Fails today: `plan_objects` keeps only the storey and `Balkone`.
  - **Verify:**
    - `.venv/bin/python -m pytest -q tests/test_plans.py` → green, the area and chain tests unchanged;
    - Look at the west side of `eg.png`/`og.png` at 1×: the cladding strip is outside the wall hatch, and the dimension chains and plan extent are not shifted by it (`dim_chains` scans `sec["walls"]` or also `sec["cut"]`: check which).

- [x] [python] Conventional door symbol: the cut leaves of hinged doors leave the section; `DOORS` loses `angle`
  - **Scope:**
    - The Parts of the hinged leaves (matched by the `LEAVES` boxes of the `DOORS` entries) are not drawn as cut.
    - Every door keeps the 90° leaf line and quarter arc.
    - `angle` is removed from `DOORS`, because nothing reads it.
  - **Test first:** `tests/test_plans.py` › "no hinged leaf is drawn in the section": no `sec["cut"]` loop lies inside the `LEAVES` box of a hinged leaf. Fails today for the 8 flat-opened leaves (EG hinges 4.431/8.876, 7.358/8.876, 11.778/5.849, −0.365/2.590; OG 4.125/8.860, 7.175/6.060, 2.570/7.685, 8.590/1.675).
  - **Verify:**
    - `.venv/bin/python -m pytest -q tests/test_plans.py` → green;
    - Look: zoom on the Küche door and the Bibliothek doors. One symbol each, no slab against the wall.

- [x] [python] Every door record checked; `back_door` derives its directions from `P`
  - **Scope:** `back_door` records `closed`/`open` from its wall frame `P` instead of the literals `(0,-1)`/`(1,0)`. The record values are unchanged.
  - **Test first:** `tests/test_plans.py` › "every door opens to its leaf's side and its arc sweeps from closed to open", for all 22 records:
    - the projection of the leaf's `LEAVES` box on `open` is ≥ −0.02 m;
    - the sign of the arc's sweep flag equals the sign of cross(closed, open) on the sheet.

    This is coverage for a refactor: green before and after.
  - **Verify:** `.venv/bin/python -m pytest -q tests/test_plans.py` → green before and after the `back_door` change

- [x] [python] The "Modellstand" hash covers every plan input
  - **Scope:** `model_state` hashes `bp.geo` plus `repr` of `bp.doors`, `bp.plan_rooms`, `bp.plan` and `CUT` / `ROOM_CUT` / `FLOOR` / `CEIL`. These are lists, dicts and tuples, no sets, so the hash does not depend on `PYTHONHASHSEED`.
  - **Test first:** `tests/test_plans.py` › "the model state changes with a room name and a door". Renaming one `plan_rooms` entry, or moving one `doors` hinge, changes `model_state`. Fails today: only `geo` is hashed.
  - **Verify:** `.venv/bin/python -m pytest -q tests/test_plans.py` → green, the determinism test included (`-m slow`)

- [x] [python] Robustness: a misplaced room anchor names the room; SVG text is escaped; every sub-model build clears `DOORS`
  - **Test first:** `tests/test_plans.py` covers:
    - "an anchor inside a wall raises ValueError naming the room". Fails today: `KeyError: None`.
    - "text escapes &, < and >". Fails today: written raw.
    - "a sub-model build leaves no door records behind": after `build()`, `build_ofen()` and `build_desk()` each leave `DOORS` empty. Fails today: both keep the house's 22.
  - **Verify:** `.venv/bin/python -m pytest -q tests/test_plans.py` → green

- [x] [python] No room label overlaps a wall (closes the unasserted Look of the room-label step)
  - **Test first:** `tests/test_plans.py` › "no room label overlaps a wall". The approximate text box of every label (name lines and area; width = characters × 0.55 × size) touches no wall loop of `section()`. This adds coverage and is expected green today; if it fails, it has found a real overlap, which is fixed in the same step.
  - **Verify:** `.venv/bin/python -m pytest -q tests/test_plans.py` → green

- [x] [docs] Texts follow the fixes
  - **Scope:**
    - README and `domain.md`: the door symbol is the conventional 90° swing ("the opened angle" goes);
    - `architecture.md`: an elevation fits the house without garden and loose furniture (the user's choice, replacing "clipped to the house plus a margin");
    - the "Known gaps" note below drops the doubled leaves.
  - **Test first:** none, no runtime surface
  - **Verify:** `! grep -q "opened angle" README.md specs/changes/2d-plan-export/domain.md && ! grep -q "clipped to the house plus a margin" specs/changes/2d-plan-export/architecture.md`

- [x] [python] Re-export `plans/` once after all fixes
  - **Test first:** the existing "plans/ equals a fresh export" (`slow`) fails after the fixes above, until `plans/` is regenerated.
  - **Verify:**
    - `python3 code/export_plans.py plans/ && .venv/bin/python -m pytest -q -m slow tests/test_plans.py` → green;
    - Look at all six sheets at 1×.

- [ ] Final check after the review fixes: `bash scripts/check.sh full` → green
  - **Deferred (user, 2026-11-11):** not run after the fixes. The fixes are small and more changes come first; the full check runs once at the end of the whole procedure. Until then this step stays open, and so does `status: applying`.
  - **Note:** if port 5377 is served from another clone, the Playwright half tests that clone's viewer. This change touches no `web/`, so the report then says so, and the pytest half (including `slow`) is the evidence.
  - **Test first:** none, final check
  - **Verify:** `bash scripts/check.sh full` exits 0

Notes from applying the review fixes (2026-11-11):

- The leaf box in `DOORS` (`leaf`):
  - It includes the lever handles (4.5 cm off the leaf's centre line), so no handle is left in the plan projection.
  - For the two leaves built closed (Haustür, Hintertür) it spans the leaf's own boards and handles.
  - It also removes the leaf's faces from the plan projection below the cut, not only from the section.
- The cladding test asserts that the boards lie outside the wall hatch, not a fixed x range: the west cladding also has boards in the window reveals and, in the OG, on the faces above the annex.
- The baseline (`check.sh full`, before step 13) had 2 Playwright reds unrelated to this change (`nav.spec.js:99`, `tour.spec.js:132`); the user chose to continue, with "done = no new failures".

System docs are updated at `/spec:archive`.
