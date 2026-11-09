---
title: "Domain: Frechenlehen house model"
created: 2026-10-08
edited: 2026-11-09
---

# Domain: Frechenlehen house model

## Purpose

A 3D model of the house **Frechenlehen**: an Alpine-style family house with two storeys, a
pitched roof, larch cladding on the west and the gables, balconies, a terrace and a small annex. The model is built from
the architect's plans and from detail photos. It serves the family (the owner, Till) to
see the house, walk through it on film, explore it in the browser and show it to others.
The README (German) is the user-facing description.

## Vocabulary

The code mixes German building terms (from the plans) with English code names. Kept as
the team uses them:

| Term | Meaning |
|---|---|
| **EG** (Erdgeschoss) | Ground floor, z = 0 … 2.40 m. |
| **OG** (Obergeschoss) | Upper floor, z = 2.70 … 4.90 m (`Z_OG`, `Z_OG_TOP`). |
| **Dach** | Roof: ridge runs east–west at 7.67 m, ~20° pitch, wide eaves (`EAVE_OH`) and gable overhangs (`GABLE_OH`). |
| **Grundriss** | Floor plan (`grundriss_eg.png`, `grundriss_og.png` in the folder of the current plans, see `LOG.md`), 1:100. |
| **Ansicht** | Elevation drawing. |
| **Putz** | Plaster, the white facade (RAL 9010). |
| **Laden / Läden** | Window shutters, blue RAL 5014. |
| **Cross boards** (Querbretter) | The two white boards across every shutter, per storey (`Laeden_Querbretter`, `OG_Laeden_Querbretter`). |
| **Lärche / Lärchenschalung** | Larch wood / the larch board cladding of the west side, the east gable and the annex. |
| **Windfang** | Entrance lobby behind the east front door, with a glazed double door. |
| **Stube** | Living room with the **Ofenbett**: a plastered stove with a bed above it and an **Ofenbank** (stove bench). The plans still label it "Kachelofen". |
| **Opening** | A hole in a wall: `W` window, `FD` french door, `WF` tall window with a fixed light below, `GD` glazed larch door, `D` solid door, `I` bare opening filled by a dedicated builder. |
| **Leaf** | An interior door leaf, normally opened flat against the wall. |
| **Component** | A named building part (e.g. entrance door). The name of a reference photo in `input/` is the component it shows. |
| **Route** | The camera path of the walkthrough, in `tour.py`, shared by the film and the viewer's Rundgang: orbit / path / turn / stair / hold segments; turning speed `TURN` and pause length `PAUSE` are one variable each. The route is closed: it ends at its start pose. |
| **Camera key** | One smoothed frame of the route at 25 fps: position (x, y, z), yaw, pitch (radians, model z-up) and lens (mm, 36 mm sensor width). `tour.build_tour()` bakes the route into them; the film and the viewer both play them. |
| **Rundgang** (viewer) | Live playback of the camera keys in the viewer, in stage Eingerichtet with the whole house and the entrance door open; it can pause (then the user looks around), be scrubbed, loop ("Endlos") and be left ("Beenden"). |
| **Collection** | Blender grouping. The house lives in `Haus` with sub-collections `FL_EG`, `FL_OG`, `FL_Dach`, `FL_Balkone`, `FL_Umgebung`, `FL_Referenz`. In the `.glb` it is `extras.collection` per node. |
| **rnd** | A random value per Part, stored per face, that varies the shade of boards and slabs. |
| **Core** (`house_core`) | The pure-Python description of the house: constants, materials as data, primitives, builders. It knows nothing about Blender or three.js. |
| **Blueprint** | What one core build returns: the GEO entries and their Parts, `SMOOTH`, `PIVOT`, `TURN`, `MAT_DEF`, paint colours, room lights and the garden layout. Not to be confused with "model", the whole 3D house. |
| **Backend** | Turns a Blueprint into output. **Blender backend** (`build_house.py`): the `.blend` scene. **glTF backend** (`export_gltf.py`): the `.glb` file. |
| **Part** | The geometry of one `add()` call: a closed solid (box, prism, sweep, …) with one `rnd` value. The unit for normal orientation. |
| **Parity snapshot** | Per-object fingerprint of the Blender build (vertex and face counts, bounding box, materials, `rnd` hash), compared with the golden. |
| **Viewer** | The three.js web page in `web/`. |
| **Sub-model** | A piece of the house built alone at its own origin with dimension lines, on its own page reached through the viewer's "Teilmodell" drop-down: the **Ofen** (`ofen.py`, `ofen.html`), the **Schreibtisch** (`desk.py`, `desk.html`), the **Bad Großeltern** (`bad.py`, `bad.html`; it brings walls of its own) and the **Küche** (`kueche.py`, `kueche.html`). The house places the same parts, only translated. |
| **Küche terms** | **Spülzeile** (sink run on the north wall, door frame → NE corner), **Ostzeile** (60 cm base unit on the east wall), **Halbinsel** (peninsula with the cooktop), **Abzug** (flue box in the NE corner from 1.80 m up), **Besenschrank** (broom cupboard behind the open kitchen door). |
| **Bad Großeltern terms** | **Nische** (the 1.20 m WC + Schrank strip in the south, split by a 12 cm wall), **verschränkte Schiebetüren** (two sliding leaves on offset tracks closing the Nische; at most one half open), **Raumteiler** (35 cm glass + 1 m wall with glass above, between shower and basin), **Waschtrog** (one 1.00 m trough basin, two mixers), **Hängeschrank** (hanging wardrobe in the Schrank). |
| **Speis A / B / C** | The pantry's built-ins: open shelf A on the Flur wall, open shelf B on the aisle, cabinet C back to back with B with doors to the Essen; all to the ceiling. |
| **Bildschirm** | A monitor pane of the Schreibtisch whose material shows a screen image (a screenshot) instead of a colour or procedural texture. |
| **Stage** | One of five looks in the viewer: **Skizze** (sketch), **Massenmodell** (massing model), **Detailmodell** (detailed model), **Gebaut** (built reality), **Eingerichtet** (furnished: Gebaut plus furniture). |
| **Timeline** | The bar that moves between stages. Its progress `p` runs from 0 to 3; integer values are the pure stages, values in between blend two neighbours. |
| **Cutaway** | Viewer setting that hides the roof ("Ohne Dach") or the roof and the OG ("Nur EG"). |
| **Clay / Ink / Paper** | The off-white Massenmodell material / the dark Skizze line colour / the Skizze background and surface colour. Surfaces drawn in paper hide the lines behind them (**hidden-line**). |
| **Garden layout** | The shared description of the garden: ground area, no-grass areas, grass density, clump shape and shrub placements. Each backend plants from it in its own way. |
| **No-grass area** | A rectangle where no grass grows: around house walls, terrace, gravel strip, beds, annex and the EG balcony (`no_grass`). The **windrose area** (`windrose`: star square plus four letter squares) is separate: Blender keeps grass off it, the viewer ignores it. |
| **Clump** (Grasbüschel) | One grass instance: 6 curved, tapering blades, 0.3–0.6 m tall. |
| **Shrub** (Strauch) | A rounded leafy bush in one of the beds (`Beet_Ost`, `Beet_West`), placed in groups of three with a gap. |
| **Room light** | A warm point light at one of the 23 `ROOM_LIGHTS` sites (x, y, floor z), `ROOM_LIGHT_H` above the floor. In Blender, one film fill light per site. In the viewer (fast mode) by day none is on; at dusk the `ROOM_N` sites nearest the camera are lit; with `hires=on` every site has its own light. |
| **Outside lamp light** | The viewer's warm spot under an `OUTSIDE_LIGHTS` bulb (gooseneck wall lamps): off by day; at dusk the `OUTSIDE_N` nearest the camera (fast mode) or all of them (`hires=on`). |
| **Light site** | A position a light can sit at: one `ROOM_LIGHTS` entry + `ROOM_LIGHT_H`, or one `OUTSIDE_LIGHTS` bulb. |
| **Light pool** | The viewer's fixed set of `ROOM_N` (6) room `PointLight`s and `OUTSIDE_N` (2) outside `SpotLight`s. Its members never change; at dusk each sits at one of the nearest sites, by day the whole pool is off (`visible = false`, out of the render list). |
| **Site distance** | How far a light site is from the camera for the ranking: `hypot(dx, dy, 3·dz)` while the camera is indoors (own storey first), else the plain 3D distance. |
| **Cut-off fade** | A pooled light's intensity factor `clamp((d_cut − d) / FADE, 0, 1)`, `d_cut` = distance of the nearest site left out, `FADE` = 1.0 m: a light leaves the pool already dark. |
| **Fast mode / Full quality (`hires`)** | The viewer's two modes, chosen per page load by the URL switch `hires`. Fast mode (default, Rundgang included): light pool, pixel ratio ≤ 1.5, no grass while the camera is indoors. `?hires=on` (film capture): none of these shortcuts. |
| **Quick check** (per-step check) | What runs after every change: the change's own new test alone, `pytest -m "not slow"` and Vitest (`scripts/check.sh quick`, ≤ 60 s), then a Show when the change is visible. |
| **Full check** (final check) | Everything: all pytest incl. slow tests, Vitest, all Playwright projects except `@eye` (`scripts/check.sh full`); once at the end of a change (after a Blender rebuild, save and still if the Blender output changed), at archive and on request. Known bugs in `specs/bugs/` don't count as new failures. |
| **Slow test** | A pytest test marked `slow` (the Blender parity tests: they start Blender); not in the quick check. |
| **`@eye` test** | A Playwright test that only makes pictures for a human (stills along the Rundgang); not in the default run, `--grep @eye` runs it. |
| **View URL** | The viewer's URL state: house `?cam=x,y,z&at=x,y,z&p=0…4&cut=` `all` / `noroof` / `eg`, sub-model pages `?cam=&at=&look=`, model coordinates (z up). |
| **Show** | Opening the user's browser at a view URL that frames changed objects (`code/show.py`), after the agent has looked at a screenshot of the same URL (`web/shot.js`). |

## Concepts and entities

```mermaid
erDiagram
    HOUSE ||--|{ STOREY : has
    HOUSE ||--|| ROOF : has
    HOUSE ||--o{ BALCONY : has
    STOREY ||--|{ ROOM : contains
    STOREY ||--|{ WALL : contains
    WALL ||--o{ OPENING : has
    OPENING ||--o| COMPONENT : "filled by (door, window, niche)"
    ROOM ||--o{ FURNITURE : contains
    ROOM ||--o{ ROOM_LIGHT : "lit by"
    WALL ||--o{ CLADDING : "covered by (west)"
    COMPONENT }o--|| MATERIAL : uses
    FURNITURE }o--|| MATERIAL : uses
    HOUSE ||--|| SURROUNDINGS : "sits in"
    SURROUNDINGS ||--o{ GARDEN : "terrace, beds, meadow"
    ROUTE ||--|{ ROUTE_SEGMENT : has
    ROUTE ||--|{ CAMERA_KEY : "baked into"
    FILM ||--|{ CAMERA_KEY : keys
    VIEWER_RUNDGANG ||--|{ CAMERA_KEY : plays
```

```mermaid
erDiagram
    BLUEPRINT ||--|{ OBJECT_ENTRY : "GEO (collection, object)"
    OBJECT_ENTRY ||--|{ PART : "add() calls"
    PART ||--|{ FACE : "n-gons, maybe concave"
    FACE }o--|| MATERIAL_DEF : "material name"
    BLUEPRINT ||--|{ MATERIAL_DEF : MAT_DEF
    BLUEPRINT ||--o{ PAINT : "RAL overrides"
    BLUEPRINT ||--o{ ROOM_LIGHT : ROOM_LIGHTS
    BLUEPRINT ||--|| GARDEN_LAYOUT : garden
    OBJECT_ENTRY ||--o| PIVOT : "origin (EG_Haustuer)"
    BLUEPRINT ||--|| BLENDER_SCENE : "Blender backend"
    BLUEPRINT ||--|| GLB : "glTF backend"
    GLB ||--|| VIEWER : "loaded by"
```

- **House:** a main block of 14.885 × 12.887 m with an annex (Elektroraum, Heizung) in the SW corner.
- **Storeys:** EG and OG. They are joined by an open stair with 15 risers (18.0/25.5 cm) and
  a stairwell in the OG slab.
- **Rooms:** EG has Stube, Küche/Essen, Bibliothek, Speis, Oma & Opa (bedroom open to its Bad,
  WC in the Bad's niche) and the Windfang. OG has
  Nadine & Till, Waschküche, Saschi, Bichlach, Jugend and Yoga, plus bathrooms and WCs.
  Their names are written on the floor (Blender only).
- **Materials:** about 35 named materials (`FL_*`). Kinds:
  - plain colour
  - procedural wood with grain along an axis
  - speckled stone
  - bumped plaster
  - glass
  - emissive: stove fire, lamp filaments

## Stages of the viewer

```mermaid
stateDiagram-v2
    direction LR
    Skizze --> Massenmodell: p 0 → 1
    Massenmodell --> Detailmodell: p 1 → 2
    Detailmodell --> Gebaut: p 2 → 3
    Gebaut --> Eingerichtet: p 3 → 4
    Eingerichtet --> Skizze: replay
    note right of Skizze: visible ink lines on paper (hidden-line)
    note right of Massenmodell: clay surfaces, soft shadows, lines fade out
    note right of Detailmodell: real materials, daylight
    note right of Gebaut: dusk sky, low sun, warm lights nearest the camera
    note right of Eingerichtet: like Gebaut, with furniture
```

- **Play** runs `p` from its current value to 3 at 4 s per stage. It stops at 3; Play at 3
  restarts from 0. **Clicking a stage name** jumps there; **dragging the scrubber** sets `p`.
- **The sun toggle** switches between day and dusk lighting from p 1.5 on. Any timeline move
  resets it.
- **Garden per stage.** In Skizze, each shrub is one ink circle and there is no grass. In
  Massenmodell, shrubs are clay blobs and there is no grass. In Detailmodell and Gebaut,
  grass and leaves grow in with the detail blend.

## Actors

| Actor | Does |
|---|---|
| Owner (Till) | Gives plans and photos, asks for changes, watches stills, films and the viewer. |
| Claude (agent) | Edits the core and the scripts, runs them in Blender over the Blender MCP server, runs the tests, renders stills and films and checks them. |
| Blender 5.2 | Runs the Blender scripts, holds the scene, renders with EEVEE. |
| Browser | Loads the viewer from GitHub Pages or the Vite dev server. |
| Family and friends | Open the viewer link. |
| Architect (indirect) | Source of the plans (`input/*.pdf`). |

## Processes

```mermaid
flowchart LR
    P[plans + photos in input/] --> E[edit code/house_core.py]
    E --> T[pytest · npm test · playwright]
    E --> R[rebuild in Blender:<br/>build_house → paint → windrose → garden → film]
    R --> S[render stills to tmp/details/]
    S -->|looks wrong| E
    S -->|ok| F[save .blend, render film headless]
    F --> M[ffmpeg → frechenlehen_rundgang.mp4]
    E --> W[npm run dev: .glb regenerated, viewer]
    W -->|push to main| G[GitHub Pages]
```

1. **Rebuild.** Run all Blender scripts in a fixed order. Each one replaces only its own
   collection or objects. Save the `.blend`.
2. **Verify a change.** Run the test suites. Render a still from a temporary camera and look
   at it, then remove the camera. For the viewer, look at the Playwright screenshots in
   `tmp/web/`.
3. **Deliberate change to the Blender output.** Regenerate the parity golden, diff it, then
   rebuild and save the `.blend`.
4. **Film.** Bake the route into camera keys (`tour.build_tour()`), render one frame per key
   headless and encode them. The viewer's Rundgang plays the same keys live.
5. **Refresh the README views:** `docs/images/ansicht_*.png`.
6. **Publish the viewer:** merge to `main`; the Pages workflow builds and deploys.

## Rules and constraints

- **One source of truth.** Geometry, material parameters, paint colours, cross boards, room
  lights, the windrose position and the garden layout are defined only in `house_core.py`.
  Neither backend nor the viewer repeats them
  ([ADR-001-XEWL](../architecture/adr-001-xewl-shared-python-core.md)). No hand edits live in
  the `.blend`.
- **Same randomness.** `build()` seeds `random` with 22, so `rnd` values and board splits match
  in both outputs.
- **Faces point outward.** Every closed Part is oriented to a positive signed volume, as
  Blender's normal recalculation does. Open Parts (the two lamp cones) are double-sided.
- **Object space = world space.** GEO vertices are in world coordinates, except pivoted
  objects, which are shifted by the pivot (and stored unturned when they have a `TURN`). Wood grain lines up the same way in Blender and in
  the `.glb`.
- **The garden is alike, not identical.** Both outputs plant from the same garden layout;
  blades and leaves land in different spots, and the browser uses 25 % of the grass density.
- **Skizze is hidden-line.** Only the visible edges are drawn. `SMOOTH` objects (pebbles,
  outside lamps) get no lines.
- **The cutaway never hides the ground.** "Ohne Dach" hides `Dach` (with `Verschalung_West` and the annex roof `Dach_Anbau`).
  "Nur EG" also hides `OG` and the OG balconies (`Balkon_OG_*`).
- **Coordinates:** metres. The origin is the outer SW corner, +X east, +Y north, Z up. The
  `.glb` stores `(x, z, -y)`.
- **Accuracy:** plan measurements are about ±5 cm. Pink-hatched walls are walls. Lighter
  hatching marks a closed-up door.
- **Faces that overlap in one plane** must share one `rnd` value or be offset by
  millimetres, or they z-fight.
- **Colours:** facade and windows RAL 9010, shutters RAL 5014. Doors stay
  natural wood.
- **The route camera** (film and viewer Rundgang) stays ≥ 0.25 m from all geometry and never
  passes through a wall.
