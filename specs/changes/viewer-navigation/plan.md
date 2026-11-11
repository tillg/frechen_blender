---
feature: viewer-navigation
title: "Plan: one navigation for house and sub-models: model, Darstellung, Standpunkt"
status: applied
order: 4
created: 2026-11-10
edited: 2026-11-10
---
# Plan: one navigation for house and sub-models: model, Darstellung, Standpunkt

Order: the pure viewstate module first, then the toolbar on all pages (and re-pointing the
existing e2e tests), then persistence and Reset. After that, the `[python]` Standpunkte and routes
in the core, then their `[web]` consumers.

**Existing e2e tests (owner's agreement needed before step 2).** These tests click controls that go
away. **Re-pointed** means the same assertions, but the interaction goes through the drop-downs:

| Spec | Re-pointed | Deleted or changed |
|---|---|---|
| `ui.spec.js` | "Detailmodell selects the detail stage"; "Ohne Dach" → "1. Stock"; "Nur EG" → "Erdgeschoss"; furniture/cutaway; built-in Ofen; stoves burn; the URL tests | **Deleted:** "dragging the scrubber…" and "Play advances p and stops at 4" (behaviour removed). **Changed:** "controls don't overlap" loses `.fl-bar`. |
| `tour.spec.js` | Start through Standpunkt › Routen › "Um und durch das Haus" in every test | **Deleted:** the assertion "timeline bar hidden" / "visible again". **Changed:** "cutaway buttons are off during the tour" → "choosing a Modell or Standpunkt ends the route" (behaviour changed). |
| `stages.spec.js`, `bad.spec.js`, `gaeste_wc.spec.js` | "Rundgang" button → the route option | none |
| `ofen.spec.js`, `desk.spec.js`, `bad.spec.js`, `kueche.spec.js`, `gaeste_wc.spec.js` | View and look buttons → Standpunkt and Darstellung options; "Teilmodell" → "Modell"; "Haus" → "Ganzes Haus" | **Changed:** "share the menu style" checks the selects instead of the pressed button. |

**Found during apply, beyond the table above (agreed by the owner on 2026-11-10, including the camera jump):**

| Spec | Change | Why |
|---|---|---|
| `e2e-preview/preview.spec.js` | Ready signal "Detailmodell" button → "Darstellung" drop-down. "Teilmodell" → `choose(Modell)`. The way back to the house may end on `?m=haus`. | Missed when writing the table; same kind of re-pointing. |
| `tour.spec.js` › "Rundgang starts…", `bad.spec.js` / `gaeste_wc.spec.js` › "…not in the Rundgang" | Choose Ganzes Haus before the route; the assertions are unchanged. | The routes are listed only under Ganzes Haus, and these tests start from Erdgeschoss. |
| `ui.spec.js` › "the URL follows the view" | Choose 1. Stock before moving the camera, and poll on `p` instead of `cut`. | Switching to a house entry with nothing saved now jumps to its standard Standpunkt; it used to keep the camera. |

## Steps

- [x] [web] Pure saved-view module `web/src/viewstate.js`
  - Test first: `web/src/viewstate.test.js` covers:
    - "URL query wins over storage";
    - "stored query used when the URL has none";
    - "default when neither";
    - "keys are prefixed frechenlehen:<page>:<entry>";
    - "reset removes the key";
    - "storage that throws (private mode) falls back to the default".

    Fails today: the module does not exist.
  - Verify: `cd web && npx vitest run src/viewstate.test.js` → green; `bash scripts/check.sh quick`

- [x] [web] Shared toolbar `web/src/toolbar.js`: Modell / Darstellung / Standpunkt selects and
      Reset, at the top right on the house and on all five sub-model pages
  - Scope:
    - `nav.js` is removed, and so are the stage, cut, look and view buttons and the timeline
      bar.
    - The labels move into the page cfg.
    - The house entries switch the cut in place.
    - The house Standpunkt list is only "Von Südosten" for now (step 6 fills it).
    - The sun toggle becomes a small button beside Reset.
    - The existing e2e specs are re-pointed or deleted as in the table above.
  - Test first: new `web/e2e/nav.spec.js` covers:
    - "the three selects and Reset sit at the same box on index.html and every sub-model page";
    - "Modell lists Ganzes Haus, Erdgeschoss, 1. Stock, a separator, then the five sub-models";
    - "Darstellung lists the five stages on the house and the three looks on a sub-model";
    - "Erdgeschoss hides roof and OG".

    Fails today: no such selects.
  - Verify: `cd web && npx playwright test e2e/nav.spec.js` → green; all re-pointed specs green
    (`npx playwright test e2e/ui.spec.js e2e/tour.spec.js e2e/ofen.spec.js e2e/desk.spec.js e2e/bad.spec.js e2e/kueche.spec.js e2e/gaeste_wc.spec.js e2e/stages.spec.js`);
    screenshots of the house and the Ofen read at 1×.

- [x] [web] Persistence and Reset per model entry
  - Scope:
    - Every view change also stores the query (`viewstate.save`).
    - A page without a query opens the saved view.
    - Reset clears the key and the query and goes to the lowest Darstellung and the standard
      Standpunkt.
  - Test first: `web/e2e/nav.spec.js` covers:
    - "Ofen: Masse + Von oben survive leaving to the house and coming back";
    - "Erdgeschoss and Ganzes Haus remember their own Darstellung";
    - "a ?cam= link wins over the saved view";
    - "Reset gives Drahtmodell + Schräg on the Ofen, Skizze + Von Südosten on the house, and
      clears the saved view".

    Fails today: nothing is stored.
  - Verify: `cd web && npx playwright test e2e/nav.spec.js` → green; `bash scripts/check.sh quick`

- [x] [python] Standpunkte and routes in the core: `SPOTS`, `ROUTES`, `build_tour(route)` in
      `code/tour.py`
  - Starter set:
    - Outside: four diagonal views (Von Südosten = today's opening view).
    - Erdgeschoss and 1. Stock: "Von oben" and "Schräg von Südosten".
    - Inside: one spot per `ROOM_NAMES` room at `EYE`. "Bibliothek" is in the corner behind the
      desk (`desk.DESK_AT`), looking across the room.
    - Route "Durch die Stube & Küche": closed, from the Windfang round the sofa, the Essen, the
      Küche and the Speis aisle, back to its start.
  - Test first: `tests/test_tour.py` covers:
    - "build_tour() is unchanged (golden)" (exists);
    - "every route in ROUTES is closed";
    - "the first route is ROUTE";
    - "spot names are unique and entries valid";
    - "inside spots stand at EYE above their storey's floor and inside the house";
    - "extra routes match tests/golden/routes.json".

    Fails today: no `ROUTES` / `SPOTS`.
  - Verify: `.venv/bin/python -m pytest -q tests/test_tour.py` → green;
    `bash scripts/check.sh quick`

- [x] [blender] Camera clearance of the new route and the inside spots
  - Test first: a clearance check in Blender via MCP. It samples every frame of each extra route
    and each inside spot (BVH `find_nearest` ≥ 0.25 m, `ray_cast` between consecutive frames)
    and returns the offending frames and spots. It fails today if any waypoint is too close; the
    waypoints are fixed until it returns none. The `.blend` is not changed (`tour.py` is not
    built into Blender except `ROUTE`).
  - Verify: the MCP check returns `[]` for every extra route and spot

- [x] [python] Export Standpunkte and extra routes in the `.glb`
  - Test first: `tests/test_gltf.py` covers:
    - "scene.extras.spots lists SPOTS with name, entries, cam, at, fov";
    - "scene.extras.routes holds the extra routes by name, and extras.tour is unchanged".

    Fails today: no such extras.
  - Verify: `.venv/bin/python -m pytest -q tests/test_gltf.py` → green;
    `bash scripts/check.sh quick`

- [x] [web] House Standpunkte in the drop-down: filtered per entry, outside = orbit, inside =
      look around at eye height, "Eigene Ansicht" after a camera move
  - Test first: `web/e2e/nav.spec.js` covers:
    - "Bibliothek puts the camera at its spot, looking at its target; dragging turns the view
      in place";
    - "Erdgeschoss lists no OG room";
    - "orbiting switches the drop-down to Eigene Ansicht";
    - "Von Südosten restores orbiting".

    Fails today: only the one default spot.
  - Verify: `cd web && npx playwright test e2e/nav.spec.js` → green; Show:
    `node shot.js` of Bibliothek, Stube, Bichlach and the house entries, read at 1×

- [x] [web] Routen group: choosing a route plays it in the bottom bar; any route loops with Endlos
  - Scope:
    - `tour.js` takes the list of routes.
    - `web/film.mjs` and `tmp/threejs_film.mjs` select "Um und durch das Haus".
  - Test first: `web/e2e/tour.spec.js` covers:
    - "Durch die Stube & Küche starts at its first key and plays";
    - "with Endlos it wraps without a jump" (camera distance between the last and first frame
      < 5 cm);
    - "choosing a Standpunkt ends the route and keeps that Standpunkt".

    Fails today: one route only.
  - Verify: `cd web && npx playwright test e2e/tour.spec.js` → green;
    `node film.mjs` dry start (first 3 frames) succeeds

- [x] [docs] README: the navigation (three drop-downs, Reset, saved view, Standpunkte, Routen),
      component list and script table
  - Test first: none, no runtime surface
  - Verify: `grep -q "Standpunkt" README.md && grep -q "Durch die Stube" README.md`

- [x] Final check: `bash scripts/check.sh full` → green (no Blender rebuild: the Blender output is
      unchanged; the parity test confirms it)
  - Test first: none, final check
  - Verify: `bash scripts/check.sh full` exits 0

System docs are updated at `/spec:archive`. These go then:

- the "no room names" statements in `functional.md` (twice) and `architecture.md:377`;
- the Timeline / Play text in `domain.md`;
- the Cutaway term in `domain.md`.
