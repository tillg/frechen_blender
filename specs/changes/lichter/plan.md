---
feature: lichter
title: "Plan: lights off by day, only the nearest at dusk"
status: applied
order: 4
created: 2026-11-05
edited: 2026-11-06
---
# Plan: lights off by day, only the nearest at dusk

Baseline first: `cd web && npm test && npx playwright test` once before step 1.

Tests this change rewrites, because they encode the behaviour it replaces (agreed in grilling, not
a weakening; nothing else in the suite is touched):

- `web/src/lighting.test.js`: "one room light per ROOM_LIGHTS entry…", "dusk turns the room lights
  on…", "dusk switches the outside lamps on…" — they become the `hires` cases (step 1) and the
  pool cases (steps 2–3).
- `web/e2e/stages.spec.js` › "no grass while the camera is indoors, except in the Rundgang" — the
  Rundgang now hides the grass too; only `hires=on` keeps it (step 5).

## Steps

- [x] [web] Guard the `hires` path: today's per-site lights become `createLighting(…, { hires: true })`
  - Test first: existing tests pass before and after — the three per-site cases in `web/src/lighting.test.js` now call `createLighting(…, { hires: true })` and also assert every light `visible` by day and at dusk (23 point lights at floor + `ROOM_LIGHT_H`, 8 spots at the bulbs, intensity 0 by day / > 0 at dusk). They pass today (the option is ignored) and must stay green through steps 2–3, which change only the default path
  - Verify: `cd web && npm test` → green
- [x] [web] Fast mode: a pool of 6 room / 2 outside lights, out of the render list by day
  - Test first: `web/src/lighting.test.js` › "fast mode: a fixed pool of ROOM_N room and OUTSIDE_N outside lights" (`roomLights.length === 6`, `outsideLights.length === 2`, point/spot types) and › "by day the pool is off, at dusk on" (`setDusk(0)` → every pooled light and spot target `visible === false`; `setDusk(1)` → all `visible`; sun lower as before) — fails today: 23/8 lights, always visible
  - Verify: `cd web && npm test` → green
- [x] [web] `update(cameraPos, inside)` moves the pool to the nearest sites (storey-aware indoors), same objects, faded at the cut-off
  - Test first: `web/src/lighting.test.js` › "update() moves the pool to the nearest sites": from `(33,-24,13)`, outside → room pool at sites {15, 3, 18, 0, 5, 17} + `ROOM_LIGHT_H`, outside pool at bulbs 2 and 3 (y-up); from the Stube `(11.7,3.2,1.6)`, inside → the same instances (`toBe`) at sites {3, 2, 0, 4, 5, 6} (all EG); from the OG Galerie `(11.1,6.3,4.3)`, inside → {14, 15, 21, 17, 20, 13} (all OG, no EG site); spot targets 1 m below their light. › "the light at the cut-off fades": pooled intensity = `base · v · clamp((d_cut − d) / 1.0, 0, 1)` (default camera: site 15 at full `9 · v`, site 17 at ≈ 0.16 · 9 · v) — fails today: no `update()`
  - Verify: `cd web && npm test` → green
- [x] [web] `main.js`: `hires` from the URL (kept by `saveView()`), lights in fast/hires mode, `lights.update(camera.position, indoors(…))` before `renderer.render`; dev hooks `__fl.lights`, `__fl.hires`
  - Test first: `web/e2e/stages.spec.js` › "lights: none by day, the nearest few at dusk" (fast: p = 2 → 0 visible room/outside lights in `__fl.lights`; p = 3 → 6 + 2 visible; `lookFrom(11.7,3.2,1.6)` → site 3 (11.7, 3.2, 2.1) among the room-pool positions; log the time of the first dusk frame; screenshot `tmp/web/lights_dusk.png`) and › "hires=on keeps every light" (`?hires=on&p=3` → 23 + 8 lights visible; `hires=on` still in `location.search` after a `lookFrom`) — fails today: no `__fl.lights`, no `hires`
  - Verify: `cd web && npm test && npx playwright test` → green, incl. "Gebaut is darker outside, with warm windows"; read `tmp/web/gebaut.png` and `tmp/web/lights_dusk.png` at 1× (SE windows and the two SE lamps warm, Stube lit from inside); note the logged first-dusk time
- [x] [web] Fast mode prewarms the dusk variant at load (`lights.prewarm()` + `renderer.compileAsync`), so the Rundgang start does not stall (added at apply, 2026-11-06)
  - Test first: the existing `web/e2e/tour.spec.js` › "playing advances the camera along the route" and › "plays at 0.75× the film speed" — red after step 4: the first dusk at Rundgang start stalls ~0.8 s (`tour.time` 0.29 instead of > 0.8); `tmp/lichter_probe.mjs` shows 2.9 fps in the first tour second (fast) vs 14 (`hires=on`)
  - Verify: `cd web && npm test && npx playwright test` → green; `node tmp/lichter_probe.mjs` → first-second rate in fast mode close to `hires=on`
- [x] [web] `hires` also lifts the pixel-ratio cap and keeps the grass indoors; the Rundgang no longer keeps it in fast mode
  - Test first: `web/e2e/stages.spec.js` › "no grass while the camera is indoors, except with hires=on" (rewritten: fast mode → no grass in the Küche and at an indoor Rundgang frame; `?hires=on` → grass at both) and › "hires=on: full pixel ratio" (`__fl.pixelRatio` = `devicePixelRatio` with `hires=on`, `min(dpr, 1.5)` without; run with `deviceScaleFactor: 2`) — fails today: grass kept in the tour regardless, no `hires`
  - Verify: `cd web && npm test && npx playwright test` → green
- [x] [docs] README (Gebaut line: by day all lights off, at dusk only the rooms and outside lamps nearest the camera; URL list: `hires=on` = full quality for the film capture), `film-render` skill (capture URL with `&hires=on`), capture memory (`film-capture-full-quality`: shortcuts apply in the Rundgang; the capture uses `hires=on`)
  - Test first: none — docs only
  - Verify: `grep -n "am nächsten" README.md && grep -n "hires=on" README.md .claude/skills/film-render/SKILL.md` → each matches
- [x] [web] Capture check: one Rundgang frame captured with `hires=on` looks as before
  - Test first: none — visual only
  - Verify: `node tmp/threejs_film.mjs "http://localhost:5377/?hires=on" 1800 1800` → `tmp/film_web/frame_1801.png` is 1280×720 with all room lights and grass as before; read it at 1×

Review fixes (`review.md`, 2026-11-06):

- [x] [web] A failing prewarm doesn't block the viewer: `prewarm()` catches a rejected compile, restores the pool's day/dusk visibility and warns
  - Test first: `web/src/lighting.test.js` › "a failing prewarm restores the pool and resolves" (`compile` rejects → `prewarm()` resolves, pool `visible === false` at `setDusk(0)`) — fails today: the rejection propagates, and in `main.js` the animation loop never starts
  - Verify: `cd web && npm test` → green
- [x] [web] The resize listener is registered before `await renderer.init()` / the prewarm, so a resize while compiling isn't lost
  - Test first: none — the window (init + prewarm, a few hundred ms) can't be hit deterministically from Playwright; the listener only moves up, its body is unchanged
  - Verify: `cd web && npm test && npx playwright test` → green (viewer and tour resize tests included)
- [x] [config] The capture script `tmp/threejs_film.mjs` (gitignored) forces `hires=on` and stops if the page doesn't report `__fl.hires === true`
  - Test first: none — scratch tool outside the suite
  - Verify: `node tmp/threejs_film.mjs http://localhost:5377/ 1800 1800` → prints `hires: true`, writes `tmp/film_web/frame_1801.png`

System docs are updated at `/spec:archive`.
