---
title: "Bug: the Rundgang sometimes draws fewer than 15 frames per second in the e2e run"
priority: low
areas: [ui]
created: 2026-11-09
edited: 2026-11-09
---
# Bug: the Rundgang sometimes draws fewer than 15 frames per second in the e2e run

**Where:** web viewer, Rundgang (`web/src/tour.js`); test `web/e2e/tour.spec.js` › "the tour draws
at most ~30 frames per second (the film has 25)"

## Steps

1. `cd web && npx playwright test e2e/tour.spec.js -g "at most ~30 frames"` (headless Chromium,
   WebGL2 fallback on Metal).
2. The test starts the Rundgang and counts draws over 2 s.

## Expected

Between 15 and 32 frames per second.

## Actual

13.98 fps on 2026-11-08 (needs > 15); 8.99 fps on 2026-11-09 (full check). Flaky: it passed in two
other runs on 2026-11-09, so it depends on GPU load; a viewer tab open in the user's browser
(usual during work) competes with headless Chromium for the GPU.
Baselines count "no new failures" with this test as the known red.

## Evidence

`web/e2e/tour.spec.js:138` (the assertion `toBeGreaterThan(15)`); measured 13.98 fps in the
2026-11-08 e2e run.
