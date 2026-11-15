---
feature: 29-waschkueche-becken-dusche
title: "Plan: basin and shower in the Waschküche"
status: proposed
order: 4
created: 2026-11-15
edited: 2026-11-15
---
# Plan: basin and shower in the Waschküche

## Steps

- [ ] [python] Shower cabin 1.10 × 1.10 on the west wall north of the table; basket cupboard shortened to two baskets per shelf
  - Test first: `tests/test_core.py` › `test_waschkueche_shower_cabin` (glass S/N/E to 2.0, door 60 with hinges and handle, limestone floor only inside, Eiche around, limestone wall, head, drain, door arc and 60 in front free, clear of table and cupboard, nothing new on the south wall above 1.20); `test_waschkueche_open_cupboard…` rewritten for two baskets per shelf — fail today: no cabin, three baskets
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k waschkueche` → green; `bash scripts/check.sh quick`; Show top-down
- [ ] [python] Basin 60 on the east wall with Taubenblau tiles, mirror and the tower lamp over it
  - Test first: `tests/test_core.py` › `test_waschkueche_basin` (`_waschbecken`, tiles behind, mirror 80 × 85, ≥ 5 cm outside the leaf's sweep, 60 in front free, clear of the machines); `test_wandlampen_og_placements` updated (the lamp over the mirror at 2.10) — fail today: no basin
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "waschkueche or wandlampen"` → green; `bash scripts/check.sh quick`; Show from the door at 1.6 m
- [ ] [python] Rundgang clearance
  - Test first: `tests/test_tour.py` › `test_routes_and_spots_clear_the_waschkueche` — fails today: no Waschküche fixtures (the box count assertion)
  - Verify: `.venv/bin/python -m pytest -q tests/test_tour.py` → green
- [ ] [docs] Plan sheets, README, CLAUDE.md, reload lists
  - Test first: none — `tests/test_plans.py` (slow) pins the sheets; `tests/test_blender_scripts.py` compiles the scripts
  - Verify: `python3 code/export_plans.py plans/` then `bash scripts/check.sh full` → green

System docs are updated at `/spec:archive`.
