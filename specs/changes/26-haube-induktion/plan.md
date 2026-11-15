---
feature: 26-haube-induktion
title: "Plan: the hood over the cooktop, the Wamsler's pipe higher into the wall"
status: proposed
order: 4
created: 2026-11-15
edited: 2026-11-15
---
# Plan: the hood over the cooktop, the Wamsler's pipe higher into the wall

## Steps

- [ ] [python] Wamsler: pipe up to 1.80, 90° into the east wall, rosette on the wall face
  - Test first: `tests/test_core.py` › `test_wamsler_pipe_into_the_wall_higher_up` — fails today: the bend is at 1.30, no rosette
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k wamsler_pipe` + `bash scripts/check.sh quick` → no new failures
- [ ] [python] Hood over the cooktop: island hood centred on `KOCHFELD`, lip 65 above it, stack into the ceiling, spot strip + light under it; nothing above the Wamsler but its pipe; no clash with the Küche's parts
  - Test first: `tests/test_core.py` › `test_kueche_hood_over_the_cooktop` (replaces `test_kueche_old_steel_hood_above_the_herd`), `test_haube_spots` rewritten, `test_nothing_above_the_wamsler_but_its_pipe` — fail today: the hood is over the Wamsler
  - Verify: `.venv/bin/python -m pytest -q tests/test_core.py -k "hood or haube or wamsler"` + `bash scripts/check.sh quick` → no new failures; Show `EG_Haube` (house, eye height) and `--page kueche`
- [ ] [python] Rundgang and Standpunkte clear the hood and the pipe
  - Test first: `tests/test_tour.py` › `test_routes_and_spots_clear_the_kueche_hood` — new guard (green once the hood moved; seen red with the hood at y 3.0)
  - Verify: `.venv/bin/python -m pytest -q tests/test_tour.py` → green
- [ ] [docs] Plan sheets, README, CLAUDE.md, docstrings
  - Test first: none — `tests/test_plans.py` (slow) fails until regenerated
  - Verify: `python3 code/export_plans.py plans/` then `.venv/bin/python -m pytest -q tests/test_plans.py` → green

System docs are updated at `/spec:archive`.
