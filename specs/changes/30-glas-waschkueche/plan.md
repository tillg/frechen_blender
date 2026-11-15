---
feature: 30-glas-waschkueche
title: "Plan: glazed top metre in the Bad / Waschküche partition"
status: applying
order: 4
created: 2026-11-16
edited: 2026-11-16
---
# Plan: glazed top metre in the Bad / Waschküche partition

## Steps

- [x] [python] Lower the four Waschküche lamps over the table under the glazing's sill
  - Test first: `tests/test_core.py` › `test_wandlampen_og_placements` (Waschküche entries at `LAMPE_H` 1.10) and
    a new `test_oberlicht_bad_waschkueche` sweep (nothing of either room in the glazing box) — fail today: lamps at 1.70
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "wandlampen_og or oberlicht"` → the lamp test green
- [x] [python] The Oberlicht: opening, lining, mullions, beads, Milchglas in house and sub-model
  - Test first: `tests/test_core.py` › `test_oberlicht_bad_waschkueche` — fails today: no glass in the partition,
    plaster up to the ceiling; `tests/test_tour.py` › `test_routes_and_spots_clear_the_oberlicht`
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py tests/test_tour.py` → green; Show from both rooms + top
- [x] [docs] Plans, README, CLAUDE.md, module docstrings
  - Test first: none — documentation; plans by `tests/test_plans.py` (slow)
  - Verify: `python3 code/export_plans.py plans/` and `grep -q Oberlicht README.md`

System docs are updated at `/spec:archive`.
