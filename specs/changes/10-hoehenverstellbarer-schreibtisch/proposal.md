---
feature: 10-hoehenverstellbarer-schreibtisch
title: "Proposal: Höhenverstellbarer Schreibtisch"
status: applying
order: 1
created: 2026-11-12
edited: 2026-11-12
---
# Proposal: Höhenverstellbarer Schreibtisch

## What

The Büro desk in the Bibliothek (issue #10) becomes a 190 × 100 cm solid cherry top (Kirschbaum,
4 cm) on the cast-iron crank frame of `input/2026-11-12 input/schreibtischgestell.jpg` ("Wien"):
two arched end legs, a foot tube between them, gearboxes on the legs, two drive rods, four lifting
spindles under two flat top bars, a hand wheel on one leg. In the viewer (house in Eingerichtet and
the Schreibtisch sub-model) the desk cranks up from 75 to 105 cm and back now and then, the top with
everything on it (monitors, MacBook, keyboard, trackpad) and the spindles rising while the hand
wheel turns. Blender and the film show it at 75 cm.

## Why

The user's desk is a cherry board on such a frame; the model shows a plain spruce table today.

## Scope

- In: `code/desk.py` (Büro desk only), a new material `Kirschbaum`, a lift registry in the core
  and its glTF extras, the viewer's lift clock (`slides.js`, `main.js`, `submodel.js`), the desk
  sub-model's views and dimensions, README.
- Out (non-goals): the OG laundry table (`desk.desk()` stays as it is); the "WIEN" lettering, gears'
  teeth, screws; animating the lift in Blender/the film; a user control for the height.

## Expected outcome

- Top 190 × 100 × 4 cm Kirschbaum, same centre in x and same back edge (2 mm off the north wall)
  as today's desk; frame black iron, within the top's footprint.
- Lift 30 cm (75 → 105 cm): every lifted part stays clear of all other geometry in both states;
  only the spindles run inside the frame's housings and legs, by design.
- Viewer: up in 3 s, rests 4 s, down in 3 s, rests 4 s; the hand wheel turns 4 times per stroke
  (more would alias at 30 fps).
- All other objects of the house keep their geometry and `rnd` values (parity golden: only the
  desk's objects and the chair change).

Frame sizes are read off the photo (assumed, marked "(angenommen)" in the dimensions): legs 70 cm
deep, 10 cm thick, 50 cm high, feet 14 cm, arch 42 × 22 cm; legs 1.50 m apart outside; foot tube
Ø 8 cm; hand wheel Ø 26 cm.

## Open questions

none (top size 190 × 100 and the animated height settled by the user, 2026-11-12).
