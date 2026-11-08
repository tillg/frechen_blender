---
feature: desk
title: "Review: Desk sub-model with monitors, MacBook, keyboard and trackpad"
status: applied
order: 5
created: 2026-11-08
edited: 2026-11-08
---
# Review: Desk sub-model with monitors, MacBook, keyboard and trackpad

**Scope:** `git diff c1e43bf 432a702` (1 commit) · **Reviewed:** 2026-11-08

## Defects

- [MEDIUM] Rundgang camera clearance not re-checked after the new Bibliothek furniture · File:
  `code/house_core.py` (`desk.desk_neu`/`desk.stuhl` in EG), `code/tour.py` · Risk: the monitors
  reach ~1.28 m; if the route passes the desk the film and the viewer's Rundgang could clip
  through them · Fix: run the per-frame BVH clearance (≥ 0.25 m) plus ray_cast check; record the
  result.
- [LOW] Missing texture gives no signal · File: `web/src/materials.js` (`TextureLoader.load`
  without error callback) · Risk: a 404 leaves the screen grey; the e2e `textures() === 2` wait
  times out without a clear reason · Fix: error callback / failure count.
- Checked and consistent: turn maths in `local()`, Blender and glTF; Blueprint argument order;
  house table and chair at their old coordinates, devices on their own `random.Random(3)`; shared
  `rnd` per device, pane 0.5 mm proud; guarded fire extras; test hooks. `pytest tests/test_core.py
  tests/test_gltf.py`: 58 passed.

## Standards

- Hard violations: none (CLAUDE.md, principles.md, ADR-001-XEWL, ADR-002-MLQS, ADR-003-SKGB).
- Drive-by: `web/src/materials.js:68` `userData.image = d.image` is set but never read (orphaned).
- Judgement: `desk_neu(..., z=0.0)` — `z` never varied by a caller (Speculative Generality).
- Judgement: `keyboard()`/`trackpad()`/`wedge()` repeat the same slope lambda; `monitor()`'s
  `fbox` near-duplicates `obox` (Duplicated Code). `(c, o, m, …, rnd)` threaded through every
  device (Data Clumps). Single-letter names follow house style.

## Spec

- Partial: plan step 3's "camera clearance check ≥ 0.25 m" has no record (same as the MEDIUM
  defect).
- ADR drift: ADR-001-XEWL's summary names `house_core.py` plus `ofen.py`; `desk.py` now also
  describes part of the house (CLAUDE.md and README already say so).
- Test-first: every ticked step's named test exists and matches; the pytest ones pass. Weak spot:
  `test_back_door_has_lever_handles_inside_and_outside` uses `any()`/`all()` and does not pin the
  handle count.
- Scope creep: none (back door handles were requested in the session).

## Verdict

Defects: 2 (worst MEDIUM: clearance check unrecorded). Standards: 1 drive-by + judgement calls
(worst: orphaned `userData.image`). Spec: 2 (worst: clearance step partial, ADR-001-XEWL summary
stale).

Fixed before archive (2026-11-08):
- Clearance check run headless on the saved `.blend` (7157 frames, `Ref_*` reference planes
  excluded): minimum 0.252 m, 0 ray hits; nearest approach to the desk devices 1.251 m.
- Orphaned `userData.image` removed; `TextureLoader.load` logs `texture missing: <url>` on error.
- ADR-001-XEWL: description, decision and consequences name the sub-model modules; History line
  added.
- `npm test` 42 passed; `npx playwright test e2e/desk.spec.js --project=dev` 3 passed.

Accepted as is: the smell judgement calls (house style; `z` mirrors the other builders) and the
loose back-door handle test.
