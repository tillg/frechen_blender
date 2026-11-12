---
feature: 5-kueche-variante-schrank
title: "Plan: Küche – Variante mit Schrank an der hinteren Wand"
status: applied
order: 4
created: 2026-11-12
edited: 2026-11-12
---
# Plan: Küche – Variante mit Schrank an der hinteren Wand

## Steps

- [x] [python] Core: split the default-only parts into the `main` objects (`EG_Speis_C`,
  `EG_Speis_Schiebetuer`, `EG_Speis_Waende`: suffix `_Waende` keeps it a wall for the plan sheets); the shared Speis/Küche wall runs only
  y 3.73–5.849. Add the `VARIANT` registry and `Blueprint.variant`.
  - Test first: `tests/test_core.py` › `test_variant_main_objects`. Fails today: no
    `Blueprint.variant`. It checks the three objects are `main`, together give C (y 3.13–3.728),
    the leaf and the rail and the wall stub, and the shared wall `EG_Waende` has no part in
    x 5.24–5.49 × y 3.13–3.73.
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k variant` + `bash scripts/check.sh quick` → green
- [x] [python] Core: `speis_alt()` builds the `alt` objects:
  - `EG_Alt_Schrank`: C on the Essen west wall, x 2.774–3.372, y 0.417–3.712, six columns of
    Mallnitz fronts facing east, to the ceiling;
  - `EG_Alt_Speis`: B's back panel, vertical boards at y 3.715–3.731 (1 mm off B, 3 mm off C: no
    coplanar faces);
  - `EG_Alt_Pendeltuer_S` / `_N`: two closed saloon leaves in the opening y 4.33–5.249, half
    height, `PIVOT` on the jambs, `SWING` ±90° into the Speis.
  - Test first: `test_core.py` › `test_variant_alt_objects`. Fails today: no such objects. It
    checks:
    - extents and flags;
    - the cabinet is clear of the south window, the table chairs and the walls;
    - the leaves together fill the opening (gaps ≤ 1 cm) and turn into the Speis (x < 5.24),
      clear of shelf A/B when swung.
  - Verify: as above → green; Show (`show.py EG_Alt_Schrank EG_Alt_Pendeltuer_S --print`, cut
    `eg_alt` after the web step; until then read the parts' boxes in the test).
- [x] [python] Backends: `export_gltf.py` writes `extras.variant`; `build_house.py` and
  `export_plans.py` skip `alt` objects.
  - Test first:
    - `tests/test_gltf.py` › `test_variant_extras`. Fails today: no extra. Every `alt`/`main`
      object's node carries it; shared nodes don't.
    - `tests/test_plans.py`-style fast check that `export_plans` draws no `alt` object.
  - Verify: `check.sh quick` → green; `python3 code/export_plans.py plans/`: the elevations differ
    only in the hash line; the EG sheet also only in drawing order and the stub's own hatch
    rectangle (the sorted contents: outline and hatch the same lines, split at y 3.73).
- [x] [web] Viewer entry "Erdgeschoss - Alternativ" (`cut=eg_alt`): `HOUSE`, `HIDE`, `ENTRY`,
  variant visibility in `applyVisibility`, EG spots reused.
  - Test first:
    - `web/e2e/variant.spec.js` › `Erdgeschoss - Alternativ shows the variant`. Fails today: no
      entry. Choosing the entry:
      - sets `cutaway` = `eg_alt`;
      - hides `EG_Speis_C`, `EG_Speis_Schiebetuer` and `EG_Speis_Waende`;
      - shows `EG_Alt_*` (in Eingerichtet and Gebaut);
      - after a reload with the URL, still shows it.
      Erdgeschoss shows the reverse. The OG stays hidden.
    - `web/e2e/nav.spec.js` drop-down list extended by the entry.
  - Verify: `cd web && npx playwright test e2e/variant.spec.js e2e/nav.spec.js` + `check.sh quick`
    → green. Show both entries (`?cut=eg` and `?cut=eg_alt`, view from above onto Essen/Speis)
    via `shot.js`, read at 1×.
- [x] [blender] Rebuild + save the `.blend`; regenerate the parity golden (only the split
  objects differ); regenerate plans; check the camera clearance of the Rundgang.
  - Test first: `tests/test_blender_parity.py`. It fails today on the new object set.
  - Verify: `UPDATE_GOLDEN=1 …` diff shows only `EG_Speis*`/`EG_Innentueren`/`EG_Waende` changes,
    no `EG_Alt_*`; still from the Essen looking north to `tmp/details/variant_main.png`: same as
    before; then `bash scripts/check.sh full` → green.

System docs are updated at `/spec:archive`.
