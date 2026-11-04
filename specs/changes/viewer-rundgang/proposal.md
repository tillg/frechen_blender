---
feature: viewer-rundgang
title: "Proposal: Rundgang in the web viewer"
status: applied
order: 1
created: 2026-11-04
edited: 2026-11-04
---
# Proposal: Rundgang in the web viewer

## What

The walkthrough route of the film moves out of `film.py` into its own pure-Python module
`code/tour.py`. Blender (`film.py`) and the glTF export both read it; the viewer gets a
"Rundgang" button that plays the same camera path live, with pause, scrubbing and looking around
when paused.

## Why

Today the walkthrough exists only as a rendered MP4 that is stale after every model change and
takes about an hour to re-render. The viewer is always current. A separate route file lets another
agent or developer edit the route without touching the film script or the house core.

## Scope

- In: `code/tour.py` (route + baked, smoothed per-frame camera keys); `film.py` reads it (identical
  keyframes); `export_gltf.py` writes the keys to `scene.extras.tour`; viewer module
  `web/src/tour.js` (button, play/pause, scrubber, exit, door opens, stage Eingerichtet + Ganzes
  Haus forced); tests; README/CLAUDE.md script lists.
- In (follow-up of the owner, 2026-11-04): the route closes — after the OG it walks back down,
  out through the entrance and orbits to its start pose, so it can loop seamlessly; the viewer plays
  at 0.75× and has an "Endlos" (loop) toggle. The film gets the return leg too.
- Out (non-goals): a free first-person walk mode; EEVEE-quality
  lighting in the browser; re-rendering the film; saving `frechenlehen.blend` (unchanged output).

## Expected outcome

- `tour.build_tour()` reproduces the current film keys exactly (3693 frames, hash in
  `tests/golden/tour.json`); after the follow-up the walk through the house is unchanged and
  the last key equals the first.
- The viewer plays the Rundgang time-based at 0.75× the film speed, optionally endless; a screenshot of an interior frame shows
  the furnished room; "Beenden" restores the previous view.

## Open questions

none
