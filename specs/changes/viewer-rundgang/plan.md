---
feature: viewer-rundgang
title: "Plan: Rundgang in the web viewer"
status: applied
order: 4
created: 2026-11-04
edited: 2026-11-04
---
# Plan: Rundgang in the web viewer

## Steps

- [x] [python] Move `ROUTE` and the frame baking from `film.py` to `code/tour.py` (`build_tour()` returns the smoothed keys)
  - Test first: headless Blender dump of the current `film.py` keys → `tests/golden/tour.json` (count, sha1 of rounded keys, first/last); `tests/test_tour.py` › "build_tour reproduces the film keys" — fails today: no `tour` module
  - Verify: `python3 -m pytest -q tests/test_tour.py` → green, full suite no new failures
- [x] [python] Export the keys to `scene.extras.tour` (house only)
  - Test first: `tests/test_gltf.py` › "tour keys in scene extras" — fails today: no `tour` key
  - Verify: `python3 -m pytest -q tests/test_gltf.py tests/test_tour.py` → green
- [x] [blender] `film.py` writes the keys from `tour.build_tour()`
  - Test first: headless Blender: exec the new `film.py` on the saved `.blend`, compare the camera's evaluated location/rotation/lens at every frame with the golden — fails today: n/a (refactor; the dump from step 1 is the before-state)
  - Verify: same headless check → identical; `python3 -m pytest -q` no new failures; `.blend` not saved
- [x] [web] `tour.js` math: `poseAt(keys, fps, t)` (lerp, yaw unwrap) and `fovFor(lens, aspect)`
  - Test first: `web/src/tour.test.js` › pose interpolation, clamping, fov at 16:9 and portrait — fails today: no module
  - Verify: `cd web && npm test` → green
- [x] [web] Rundgang UI and playback in the viewer (button, play/pause, scrubber, Beenden, door, stage)
  - Test first: `web/e2e/tour.spec.js` › start puts the camera at key 0 and stage furnished; playing advances; Beenden restores the camera — fails today: no button
  - Verify: `cd web && npm test && npx playwright test` → green; interior screenshot `tmp/web/tour_*.png` read at 1×
- [x] [docs] README script table / viewer section and CLAUDE.md mention `tour.py` and the viewer Rundgang
  - Test first: none — docs
  - Verify: `grep -n "tour.py" README.md CLAUDE.md` matches

- [x] [python] Close the route: return leg + closing orbit in `ROUTE`, cyclic smoothing in `build_tour()` when the route ends at its start; own golden switch `UPDATE_TOUR_GOLDEN`
  - Test first: `tests/test_tour.py` › "route ends where it starts" (last key = first key, yaw mod 2π; seam step ≈ normal step) — fails today: route ends in the OG
  - Verify: `python3 -m pytest -q` → green; one-off: new keys up to the end of the old route match `tmp/tour_before/camera.json` (≤ 1e-4) except the frames the smoothing window touches at both ends
- [x] [blender] Camera clearance of the return leg
  - Test first: headless BVH check (find_nearest ≥ 0.25 m, ray_cast between frames) over all keys on the saved `.blend` (no save) — old route as baseline
  - Verify: no new violations on the return leg
- [x] [web] Playback 0.75×, "Endlos" toggle, review fixes (fov on resize, fixed sun target, cutaway disabled during tour, damping reset, dt clamp)
  - Test first: `web/src/tour.test.js` › `step(t, dt, T, loop)` wraps/clamps, fov known numbers; `web/e2e/tour.spec.js` › 1 s plays ≈ 0.75 s of route; Endlos wraps past the end; resize while paused updates fov; cutaway disabled while touring — fail today: no speed/loop
  - Verify: `cd web && npm test && npx playwright test` → green
- [x] [docs] README Rundgang paragraph and `tour.py` row: closed route, 0.75×, Endlos; CLAUDE.md frame count and golden switch
  - Test first: none — docs
  - Verify: `grep -n "Endlos" README.md` and `grep -n "UPDATE_TOUR_GOLDEN" CLAUDE.md` match

System docs are updated at `/spec:archive`.
