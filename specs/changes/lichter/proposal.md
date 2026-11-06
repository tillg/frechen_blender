---
feature: lichter
title: "Proposal: lights off by day, only the nearest at dusk"
status: applied
order: 1
created: 2026-11-05
edited: 2026-11-06
---
# Proposal: lights off by day, only the nearest at dusk

## What

In the web viewer, the room lights (23 `ROOM_LIGHTS`) and the outside wall lamps (8
`OUTSIDE_LIGHTS`) are switched **off** by day — removed from lighting (`visible = false`), not just
left at intensity 0. At dusk only a few of them are on: the 6 room lights and 2 outside lamps
**nearest to the camera** (inside the house, rooms of the camera's own storey first), re-chosen as
the camera moves, in the orbit and in the Rundgang alike.

A new URL switch **`hires=on`** gives full quality for the film capture: it turns off every speed
shortcut that changes the picture — the lights are per site as today, the pixel ratio is not
capped, the grass stays visible indoors. Without it (default) the viewer runs in fast mode, the
browser Rundgang included.

Assumption: "Tagsüber / am Abend" means the viewer's day/dusk lighting (`lighting.js`, the
Tag/Abend toggle and the Gebaut/Eingerichtet stages). The Blender film's `Innenlicht` fill lights
have no day/dusk and stay as they are.

## Why

Today all 31 lights stay in the scene at every stage. By day they sit at intensity 0, yet three.js
still evaluates every one of them per fragment in every material; at dusk all 31 are lit. That is
GPU load for lights that contribute nothing (day) or almost nothing (far rooms at dusk) — felt most
on the WebGL2 fallback and in the Rundgang. The film capture, however, must keep full quality,
so it needs a switch that says so instead of being tied to the tour state.

## Scope

- In: `web/src/lighting.js` (a fixed pool of 6 room and 2 outside lights, off by day, moved to the
  nearest sites at dusk with a storey-aware distance, faded at the cut-off; per-site lights with
  `hires`), `web/src/main.js` (`hires` URL switch for lights, pixel ratio and grass indoors — it
  replaces the "grass stays in the Rundgang" exception; the per-frame `update()` call; dev `__fl`
  hooks), the unit and e2e tests, `README.md` (Gebaut line, `hires=`), the `film-render` skill
  (capture with `hires=on`), the capture memory.
- Out (non-goals): the Blender film lights (`film.py`, `Innenlicht`); the switched-on lamp above
  the Ofen bed (`LAMP_LIGHTS`, one light, lit by day and at dusk — unchanged); the fire's look;
  `ROOM_LIGHTS` / `OUTSIDE_LIGHTS` positions and their export (unchanged, `blueprint.test.js` still
  expects 23); shadow-casting room lights; a toolbar button for `hires`; the Ofen page; drawing on
  demand and the 30 fps tour/fire cap (unchanged in both modes).

## Expected outcome

- Fast mode, at p ≤ 2 (and with the sun toggle on Tag): no room light and no outside lamp is in the
  render list: `visible` is false on all of them.
- Fast mode, at dusk: exactly 6 room lights and 2 outside lamps are visible, placed at the sites
  nearest the camera; from inside a room, that room's light is among them, and the others are
  rooms of the same storey (OG at the Galerie: no EG site in the pool).
- Moving the camera never changes which light objects exist or are visible, only their positions
  and intensities — so no material pipeline is rebuilt while orbiting or touring (three.js hashes
  light ids into the material cache key). The dusk variant is compiled once at load (prewarm), so
  the first dusk — e.g. the Rundgang start — does not stall.
- No visible pop when the nearest set changes: a light fades to 0 within 1.0 m of the cut-off.
- Fast mode: no grass while the camera is indoors, in the Rundgang too.
- `?hires=on`: 23 + 8 per-site lights as today, pixel ratio = `devicePixelRatio`, grass visible
  indoors; the switch survives a reload (kept in the URL).
- **Visible change:** in the Gebaut overview from the default camera (SE, ~35 m away) only the
  SE corner's windows and the two SE outside lamps glow; the rest of the house stays dark. The
  existing check "Gebaut is darker outside, with warm windows" (Stube glazed doors) still holds:
  the Stube light is the 2nd nearest room light from that camera.
