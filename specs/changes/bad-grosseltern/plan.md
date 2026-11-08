---
feature: bad-grosseltern
title: "Plan: Bad Großeltern as a sub-model"
status: applied
order: 4
created: 2026-11-08
edited: 2026-11-08
---
# Plan: Bad Großeltern as a sub-model

Baseline before step 1: `python3 -m pytest -q`, `cd web && npm test` (green today).

## Steps

- [x] [python] `code/bad.py`: `BAD_AT`, `bad_neu(c, x0, y0)` (niche wall, lintel, two interlocking
  sliding leaves + rail, toilet + green tiles in the WC half, back cabinet and hanging wardrobe,
  walk-in shower with limestone cladding, drain and rain head, glass panel, low wall with glass,
  Waschtrog; own `random.Random`; `LEAVES` entries; returns dims); `house_core.build_bad()`
  - Test first: `tests/test_core.py` › `test_bad_submodel` — parts at the agreed sub-model
    coordinates with their materials (niche wall 0.964–1.084 × 0–1.20 Putz; WC/Schrank halves
    0.964 wide; leaves on two tracks 5 cm apart, the WC leaf open behind the Schrank leaf (both
    over the Schrank half, the WC half free); shower 0.80 with Kalkstein cladding to 2.0; glass
    0.35 from the north wall to 2.40; low wall 1.20 × 0.12 × 1.00 with glass to 2.40; Waschtrog
    1.00 centred on the low wall, one bowl, two mixers, no Spiegel part; lintel 2.05–2.40;
    cabinet 0.60 deep full width; wardrobe 0.60 × 0.60 with rail against the niche wall), no part
    outside the room, no leaf clashing with the walls,
    `dims` labels 80, 35, 120, 100, 96.4, 12, 120, 60 — fails today: no `bad` module
  - Verify: `python3 -m pytest -q tests/test_core.py` → green
- [x] [python] Place the Bad in the house: `build_eg()` drops the WC/Bad wall and
  `sliding_door()` (removed), opening `(9.856, 12.33)` in the bedroom wall, `bad_neu("EG",
  *BAD_AT)`; `build_sanitary()` drops today's Bad/WC fixtures and the `WCS` entry; limestone floor
  `BATH_EG`
  - Test first: `tests/test_core.py` › `test_bad_built_into_the_grosseltern` — the house has the
    sub-model's parts translated by `BAD_AT`; no wall part at y 10.10–10.25; wall x 2.358–2.657
    has no part between y 9.9 and 12.3 below 2.0 m; limestone at (1.2, 11.0), oak at (0.8, 9.3)
    and (1.6, 9.3) — fails today: old layout. Changed with the user's agreement (they pin the old
    layout): `WCS` table (WC Großeltern → niche WC half, north side open),
    `test_bathrooms_have_limestone_like_the_eg_corridor` ((1.2, 11.0) → Kalkstein),
    `test_wc_fixtures_after_the_photo` (EG Großeltern toilet at the niche's middle, hand basin
    case removed)
  - Verify: `python3 -m pytest -q` (parity excluded until the next step: it fails by design) →
    green
- [x] [python] `export_gltf.py --bad` → `web/public/bad.glb`
  - Test first: `tests/test_gltf.py` › `test_bad_export` — nodes `Bad_*` (Waende, Innentueren,
    Sanitaer, Fliesen, Schrank), `scene.extras.dims` present, no tour — fails today: no `--bad`
  - Verify: `python3 -m pytest -q tests/test_gltf.py tests/test_core.py` → green
- [x] [blender] `reload(bad)` in `build_house.py`, `garden.py`, `fire.py`, `film.py`; rebuild all
  six, save; regenerate the golden
  - Test first: parity test fails after the core change (golden differs) — seen red first
  - Verify: `UPDATE_GOLDEN=1 python3 -m pytest -q tests/test_blender_parity.py`, review the golden
    diff (only EG objects and `rnd` hashes after the Bad change), rebuild and save, then
    `python3 -m pytest -q` → green; stills `tmp/details/bad_from_bedroom.png` (eye height 1.6 m
    from the bedroom: glass, low wall with glass, Waschtrog, open WC with the toilet, closed
    Schrank door, no old wall) and
    `tmp/details/bad_top.png` (from above, no ceiling: shower, niche, cabinets), read them; north
    french door leaves clear the basin; Rundgang camera clearance ≥ 0.25 m, 0 ray hits
- [x] [web] `bad.html` + `bad.js` (views Schräg / Von oben / In die Nische; context walls west,
  south, north; grid), `vite.config.js` input, `ui.js` link "Bad Oma & Opa", `package.json`
  blueprint `--bad`, `.gitignore` `web/public/bad.glb`
  - Test first: `web/e2e/bad.spec.js` (page draws, dimension labels 80/35/120/100/96.4/60 present,
    no console errors, house links to the page and back) and preview spec "bad page is part of the
    build" — fail today: no page
  - Verify: `cd web && npm test && npx playwright test` → green; screenshots of all three views
    read at 1×
- [x] [docs] README component list + script table (`bad.py`, `bad.html`), CLAUDE.md mentions of
  the sub-models (`bad.py` beside `ofen.py`/`desk.py`, `reload(bad)`), ADR-001-XEWL's list of
  sub-model modules
  - Test first: none — docs
  - Verify: `grep -n "bad.py" README.md CLAUDE.md specs/architecture/adr-001-xewl-shared-python-core.md`
    matches in all three

System docs are updated at `/spec:archive`.
