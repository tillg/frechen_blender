---
title: "Bug: fully metallic materials render black in the viewer"
priority: medium
areas: [web]
created: 2026-11-10
edited: 2026-11-10
---
# Bug: fully metallic materials render black in the viewer

**Where:** `web/src/materials.js` (`metalnessNode` from `MAT_DEF.metal`), `web/src/lighting.js`
(no environment map)

## Steps

1. Open `http://localhost:5377/kueche.html?cam=1.0,-1.6,1.5&at=2.5,-1.15,0.55&look=full`
   (stage Gerendert).
2. Look at the cup pulls on the blue fronts (`FL_Metall`, `metal=1.0`).

## Expected

Chrome-coloured, as in the Blender stills (EEVEE reflects the world).

## Actual

Black: a metal reflects only its environment, and the viewer has none. Affects every `metal=1.0`
material (`Metall`: cup pulls, cooktop rings, bath fittings, …; `Spiegel`). Worked around for the
kitchen with `Stahl` (`metal=0.45`, 2026-11-10), as `Alu` (`metal=0.15`) did for the desk; that
makes the steel less metallic in Blender too.
