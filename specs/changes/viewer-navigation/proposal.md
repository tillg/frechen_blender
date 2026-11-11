---
feature: viewer-navigation
title: "Proposal: one navigation for house and sub-models: model, Darstellung, Standpunkt"
status: applied
order: 1
created: 2026-11-10
edited: 2026-11-10
---
# Proposal: one navigation for house and sub-models: model, Darstellung, Standpunkt

## What

Every viewer page (house and the five sub-models) gets the same panel at the top right: three
drop-downs and a Reset button.

1. **Modell:** Ganzes Haus, Erdgeschoss, 1. Stock, a separator line, then Ofen, Schreibtisch,
   Bad Oma & Opa, Küche, Gäste-WC.
2. **Darstellung:**
   - House: Skizze, Massenmodell, Detailmodell, Gebaut, Eingerichtet.
   - Sub-model: Drahtmodell, Masse, Gerendert.
3. **Standpunkt** has two groups:
   - **Standpunkte**: named camera poses, e.g. "Bibliothek" (in the corner behind the desk,
     looking across the room) and the outside views. The sub-models list their existing views
     (Schräg, Von oben, …).
   - **Routen** (Ganzes Haus only): "Um und durch das Haus" (today's Rundgang) first, then
     shorter walks such as "Durch die Stube & Küche", each loopable.
4. **Reset** returns the current model to its lowest Darstellung (Skizze / Drahtmodell) and its
   standard Standpunkt.

Each model remembers its Darstellung and Standpunkt in the browser, so reopening it shows the
same view.

## Why

Today the controls sit in different places and take different forms:

- The house has stage buttons in a bottom timeline bar, cutaway buttons, a sun toggle, a
  "Rundgang" button and the "Teilmodell" drop-down.
- The sub-model pages hard-code view and look buttons in each HTML file.

Nothing is remembered between visits. The only walk is the 2½-minute full route, and there is no
quick way to stand in a given room.

## Scope

- In:
  - A shared toolbar module used by `main.js` and `submodel.js`. The view and look labels move
    into each page's config.
  - The cutaway becomes the house entries of the Modell drop-down: Ganzes Haus = `all`,
    Erdgeschoss = `eg`, 1. Stock = `noroof`. The "Ohne Dach" label disappears.
  - The bottom timeline bar (▶, scrubber, stage buttons) is removed. The Darstellung drop-down
    replaces it. The bar remains only for a running route.
  - Persistence per model entry in `localStorage`, plus Reset.
  - Named house Standpunkte and extra closed routes, defined in the core (`code/tour.py`) and
    exported in the `.glb`.
  - The capture scripts (`web/film.mjs`, `tmp/threejs_film.mjs`) start the route through the new
    drop-down.
  - README.
- Out (non-goals):
  - Free first-person walking.
  - Unifying the house's five stages with the sub-models' three looks.
  - Changing the Blender film or `ROUTE` (its keys stay byte-identical).
  - New sub-model views.
  - An animated stage blend (the "Vom Strich zum Haus" play is dropped, as the owner chose).

## Expected outcome

- On every page the three drop-downs and Reset sit at the same screen position.
- Choose "Bichlach" + Gerendert on the house, open the Ofen, choose Masse + "Von oben", reload,
  go back to Ganzes Haus: each page opens where it was left.
- Reset on the Ofen gives Drahtmodell + Schräg. A shared link (`?cam=…`) still wins over the
  stored view.
- "Bibliothek" puts the camera at eye height (1.6 m) in the corner behind the desk, with the
  whole room in view. Mouse drag looks around in place, without orbiting through walls.
- "Durch die Stube & Küche" plays with play/pause, scrubber, Endlos and Beenden, and loops
  without a jump.
- The public page now shows room names (owner's choice, 2026-11-10). The rule "the viewer shows no
  room names" is dropped from the system docs at archive.

## Open questions

- **Sun toggle (Tag/Abend):** settled 2026-11-10. It is a small toggle button beside Reset, house
  only, enabled from Detailmodell on (as in the mock).
- **Initial list of Standpunkte and routes:**
  - Default for Ganzes Haus: four diagonal outside views (Von Südosten = standard, Südwesten,
    Nordosten, Nordwesten) and one inside view per floor-labelled room (`ROOM_NAMES`: Stube,
    Küche, Bibliothek, Oma & Opa, Nadine & Till, Waschküche, Saschi, Bichlach, Jugend, Yoga).
  - Default for Erdgeschoss and 1. Stock: "Von oben", "Schräg von Südosten" and their storey's
    rooms.
  - Routes: "Um und durch das Haus" and "Durch die Stube & Küche".
  - More can be added later as one line each in `tour.py`.
- **Existing e2e tests:** about 60 interactions click controls that disappear. The owner agreed
  on 2026-11-10 to re-point, delete and change them as listed in `plan.md`.
