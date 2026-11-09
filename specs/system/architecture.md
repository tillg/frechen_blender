---
title: "Architecture: Frechenlehen house model"
created: 2026-10-08
edited: 2026-11-09
---

# Architecture: Frechenlehen house model

## Overview

The house is described once, in a **pure-Python core** (`code/house_core.py` plus the sub-model modules
`code/ofen.py` (stoves), `code/desk.py` (Büro desk), `code/bad.py` (Bad Großeltern) and
`code/kueche.py` (Küche), no `bpy`). Two
**backends** turn its **Blueprint** into output
([ADR-001-XEWL](../architecture/adr-001-xewl-shared-python-core.md)):

- `build_house.py` builds the Blender scene. Blender renders the stills and the film from it.
- `export_gltf.py` writes a `.glb` for the three.js **viewer** in `web/`. GitHub Pages
  publishes the viewer.

Details on running the scripts and on pitfalls are in `CLAUDE.md`. The script table is in
`README.md`.

```mermaid
flowchart TB
    subgraph inp["input/"]
        PDF["plans PDF/PNG"]
        PH["detail photos"]
    end
    subgraph py["code/ — Python"]
        CORE["house_core.py<br/>pure Python, no bpy"]
        OF["ofen.py<br/>stoves, part of the core"]
        DK["desk.py<br/>desk, part of the core"]
        MO["mesh_ops.py<br/>triangulate · orient"]
        BH["build_house.py<br/>Blender backend"]
        EX["export_gltf.py<br/>glTF backend"]
        PA["paint.py"]
        WR["windrose.py"]
        GA["garden.py"]
        FI["film.py"]
        TO["tour.py<br/>route → camera keys"]
    end
    subgraph blender["Blender 5.2"]
        SC[("scene in frechenlehen.blend")]
        EV["EEVEE renderer"]
    end
    subgraph web["web/ — Vite + three.js"]
        GLB[("public/frechenlehen.glb<br/>generated")]
        APP["viewer<br/>WebGPURenderer + TSL"]
    end
    PDF -. measured by hand .-> CORE
    PH -. modelled by hand .-> CORE
    OF & DK <--> CORE
    CORE --> BH & EX
    CORE --> PA & WR & GA & FI
    CORE --> TO --> FI & EX
    MO --> EX
    BH & PA & WR & GA & FI --> SC
    SC --> EV --> OUT["tmp/film/*.png → mp4,<br/>docs/images/*.png"]
    EX -->|npm run blueprint| GLB --> APP
    APP -->|vite build · Actions| PAGES[("GitHub Pages")]
```

## Technology stack

| Part | Role |
|---|---|
| Python 3 | The core, `mesh_ops` and the glTF backend use only the standard library and run with the system `python3`. The Blender scripts run on Blender's own Python with `bpy`, `bmesh`, `mathutils`. |
| Blender 5.2 | Scene, materials (shader node trees), Geometry Nodes (grass), EEVEE render, AgX view transform. |
| Blender MCP server | How the agent runs code in the open Blender (`execute_blender_code`). |
| three.js 0.187 | Viewer: `WebGPURenderer` with TSL node materials. It falls back to WebGL2 automatically ([ADR-003-SKGB](../architecture/adr-003-skgb-webgpu-tsl.md)). |
| Vite 8 | Bundler and dev server for `web/`; vanilla JS, no framework. |
| pytest · Vitest · Playwright | Python tests, web unit tests, browser e2e (headless Chromium on the real GPU via `--use-angle=metal`, WebGL2 path). Playwright starts no server of its own: project `dev` tests `/`, project `preview` the build under `/frechen_blender/` (setup project `build` runs `npm run build` first), both on the one dev server on 5377. |
| GitHub Actions + Pages | Builds the `.glb` and the viewer on push to `main` and publishes `web/dist`. |
| ffmpeg | Encodes the film frames to H.264 MP4. |

## Components

### `house_core.py` — the core

```mermaid
flowchart LR
    C["constants<br/>W_OUT, Z_OG, RIDGE_Z, ST_*…"] --> B
    B["builders<br/>build_eg, build_og, build_stairs,<br/>build_roof, build_cladding,<br/>build_cross_boards, …"] --> PR["primitives<br/>add, box, lbox, sweep, column,<br/>prism, boards, wall, frame"]
    PR --> GEO[("GEO, PARTS<br/>+ SMOOTH, PIVOT,<br/>OPENINGS, LEAVES")]
    MD[("MAT_DEF, PAINT,<br/>ROOM_LIGHTS, ROOM_LIGHT_H")]
    GL["garden_layout()"]
    GEO & MD & GL --> BP[("build() → Blueprint")]
```

- **Stoves.** `code/ofen.py` holds the Ofen sub-model (`ofen_neu()`), its placement in the Stube
  (`ofen_im_haus()`) and `werkstattofen()`; `house_core` imports it and calls them, `build_ofen()`
  stays in `house_core`. `ofen.py` uses the primitives and `GEO`/`PARTS` through `house_core` (the two
  modules import each other). Its materials are entries of `MAT_DEF`.
- **Desk.** `code/desk.py` the same way: the table builder `desk()` (Büro desk, OG laundry
  table), `desk_neu(c, x0, y0)` (table, two monitors, MacBook, keyboard, trackpad, built straight
  into collection `c`: `EG` at `DESK_AT`, or `Desk` at the origin) and `stuhl()`; `build_desk()`
  stays in `house_core`. The devices draw `rnd` from their own `random.Random(3)`, so no later part
  shifts. Each screen pane is an object with a `PIVOT` (lower-left corner) and a `TURN` (yaw);
  its material carries `image` (path under `web/public/`) and `size` (w, h in metres), mapped in
  object space by both backends (`local()` stores the mesh unturned).
- **Bad Großeltern.** `code/bad.py` the same way: `bad_neu(c, x0, y0)` builds the bathroom into
  collection `c` with the room's inner SW corner at (x0, y0) (`EG` at `BAD_AT`, or `Bad` at the
  origin), after `input/2026-11-08 input/grosseltern_v4.svg`: its own walls (12 cm niche wall,
  lintel, 1 m low wall), glass, walk-in shower with limestone cladding, Waschtrog, toilet + WC
  tiles (`toilet()`, `wainscot()`), the white Schrank (`_Schrank`) and the two interlocking
  sliding leaves (WC leaf open, both in `LEAVES`); own `random.Random(5)`. Its limestone floor is
  `BATH_EG` in the core; the outer walls and the shortened bedroom wall stay in `build_eg()`.
- **Küche.** `code/kueche.py` the same way: `kueche_neu(c, x0, y0)` builds Spülzeile, Ostzeile,
  Halbinsel, the Wamsler (`ofen.wamsler()`) with its hood, wall cabinets, Besenschrank and the
  Abzug (`c + "_Waende"`) straight into collection `c` with the room's inner NW corner at
  (x0, y0) (`EG` at `KUECHE_AT`, or `Kueche` at the origin, so the sub-model lies at y ≤ 0).
  Positions are written in house coordinates (those of `input/2026-11-09 input/speis_kueche_v6.svg`)
  and shifted; own `random.Random(14)`. The room's walls, the kitchen door and the Speis
  (`speis()`: shelves A/B, cabinet C, sliding leaf on the kitchen side, own `random.Random(9)`)
  stay in `house_core`.
- **Sub-models.** `build_ofen()` / `build_desk()` / `build_bad()` / `build_kueche()` return a
  Blueprint of the sub-model alone (`garden=None`, its dimension lines in `dims`) for
  `web/ofen.html` / `web/desk.html` / `web/bad.html` / `web/kueche.html`. A dimension label containing "angenommen" is an assumed
  measure (shown in italics).
- **Geometry accumulator.** Builders append vertices, faces, material names and an `rnd`
  value per face to `GEO[(collection, object)]`. Faces are polygons (quads or n-gons, may be
  concave) with no consistent winding. Each `add()` call is one **Part** (a closed solid,
  except the two open lamp cones); `PARTS` records its face range.
- **Local wall frames.** `frame(ax)` returns `P(u, t, z)`, so wall, door and cladding code
  works for walls along x and along y.
- **`MAT_DEF`** is a pure data table of the `FL_*` materials: `rgba`, `wood`, `speck`,
  `bump`, `alpha`, `emit`. **`PAINT`** holds the RAL overrides for the plain materials.
- **Shutter cross boards** (`build_cross_boards()`) are computed from the shutter Parts, per
  storey (`Laeden_Querbretter`, `OG_Laeden_Querbretter`). Each board keeps its shutter's
  `rnd`.
- **Garden layout** (`garden_layout()`): ground, no-grass rectangles computed from `GEO`,
  windrose rectangles, density field, the grass clump and the shrub placements.
- **Room lights.** `ROOM_LIGHTS` (x, y, floor z) plus `ROOM_LIGHT_H`, the light height above
  the floor.
- **Randomness.** `build()` clears every registry and seeds `random` with 22, so builds are
  repeatable and both backends get the same `rnd` values. The clump uses
  `random.Random(5)` and the shrubs `random.Random(6)`.

`build()` returns the **Blueprint**: `geo`, `parts`, `smooth`, `pivot`, `mat_def`, `paint`,
`room_lights`, `garden`, `furniture` (objects shown only in the viewer stage "Eingerichtet"),
`dims` (sub-models only), `turn` (`TURN`: object → yaw in degrees about its pivot).

### `build_house.py` — Blender backend

It keeps only what needs Blender: `make_materials` (MAT_DEF → Principled BSDF node trees;
wood is noise stretched along the grain → ramp → hue/value by `rnd` → bump; all texture
coordinates in object space), `reset_collections`, `flush_geometry` (one mesh per GEO entry,
`rnd` face attribute, normals recalculated with bmesh, `SMOOTH`, origins at `PIVOT`, z rotation
from `TURN`; image materials map the picture through Texture Coordinate › Object),
`build_room_names` (font curves), `build_references` and `setup_scene` (sun, world, camera).

### `mesh_ops.py` and `export_gltf.py` — glTF backend

Standard library only ([ADR-002-MLQS](../architecture/adr-002-mlqs-gltf-own-writer.md)):
`python3 code/export_gltf.py web/public/frechenlehen.glb` (`--ofen` / `--desk` / `--bad` / `--kueche`: the sub-model's
`.glb` instead).

- `mesh_ops` does what bmesh does in Blender:
  - **triangulates** n-gons by ear clipping on the dominant plane of the Newell normal;
  - **orients** each Part outward: flood-filled consistent winding, flipped if the signed
    volume is negative. Open Parts keep their winding and are marked open.
- **One node per GEO object.** The name is the object name, `translation` is the pivot,
  `rotation` the `TURN` yaw.
  `extras.collection` holds the collection; `extras.smooth` marks `SMOOTH` objects,
  `extras.furniture` the `FURNITURE` objects.
- **One primitive per material**, with `POSITION`, `NORMAL` (flat, or averaged within a
  Part for smooth objects), `_RND` and uint32 indices. Accessor `min`/`max` are the stored
  float32 values.
- **Materials** `FL_<name>`: a `pbrMetallicRoughness` approximation. The full `MAT_DEF` entry,
  `kind` and paint go in `extras`. Materials of open Parts are `doubleSided`.
- **`scene.extras`:** `room_lights`, `ROOM_LIGHT_H`, `Z_OG`, `W_OUT`, `D_OUT`, `RIDGE_Z`,
  the garden layout and (house only, not the Ofen) `tour = {fps, frames}`, the camera keys of
  `tour.build_tour()` as JSON.
- **Hidden node `GA_Grasbuschel`:** the grass clump, with `_H` (0 at the root … 1 at the tip).
- **Axes:** z-up model → y-up glTF as `(x, z, -y)`, so north is −Z in three.js.

### `tour.py` — the route

A second pure-Python module beside the core (ADR-001-XEWL): it imports `HOUSE_C`, `Z_OG` from
`house_core`; the core never imports it. It holds `ROUTE` (orbit / path / turn / stair / hold
segments, the helpers `turn()` and `peek()`, the variables `EYE`, `TURN`, `PAUSE`) and
`build_tour()`, which bakes the route into one smoothed camera key per frame at 25 fps
`(x, y, z, yaw, pitch, lens)`. When the last raw frame equals the first, it smooths cyclically
(the window wraps, yaw offset by the full turn), so the last key equals the first and the route
loops without a seam. `tests/golden/tour.json` pins the keys (`UPDATE_TOUR_GOLDEN=1` after a
deliberate route change).

### Other Blender scripts

Each one imports the core with `sys.path` + `importlib.reload(house_core)`, so a
long-running Blender session picks up core edits.

| Script | Responsibility | Depends on |
|---|---|---|
| `paint.py` | Overwrites the base colour of plain materials with `PAINT`. | `FL_*` materials from `build_house` |
| `windrose.py` | Compass rose at `WINDROSE_CENTER`/`WINDROSE_R`, in its own collection. | core |
| `garden.py` | Meadow: a Geometry Nodes scatter of grass clumps over an emitter grid built from the garden layout (no grass on `no_grass` or `windrose`). Leafy shrubs at the layout's shrub placements. | core, `Beet_*` objects |
| `film.py` | Keys `FL_Kamera_Rundgang` with `tour.build_tour()` (frame range = key count), room fill lights (`Innenlicht`) at `ROOM_LIGHTS` + `ROOM_LIGHT_H`, opens `EG_Haustuer`. | core, `tour.py`, `EG_Haustuer` pivot |

### `web/` — the viewer

```mermaid
sequenceDiagram
    participant M as main.js
    participant L as blueprint.js
    participant Ma as materials.js
    participant Li as lighting.js
    participant U as ui.js
    participant S as stages.js
    M->>L: load BASE_URL + frechenlehen.glb
    L-->>M: {root, objects, byName, extras}
    M->>Ma: TSL materials from the material extras
    M->>M: ink.js lines, garden.js grass and shrubs
    M->>Li: sun, hemisphere, sky, light pool (or per-site lights with hires)
    M->>Li: prewarm(compileAsync), before the first frame
    U->>S: progress p (play / click / scrub)
    S-->>M: weights {sketch, massing, detail, built, furnished}
    M->>M: uPaper, uDetail, uInk, dusk from the weights
    M->>Li: before each draw: update(camera, indoors)
```

- **`stages.js`.** `weights(p)` gives five weights that sum to 1, with a smoothstep blend
  between neighbouring stages. `stageAt(p)` gives the nearest stage. No three.js.
- **`materials.js`.** One `MeshStandardNodeMaterial` per `FL_*` material, built from the
  extras: plain, wood (noise along the grain, ramp, `_rnd` variation), speck, bump, alpha,
  emit, image (`texture()` over `positionLocal` / `size`, loaded in the background; a missing
  file is logged). The colour is `mix(paper, clay, …)` → `mix(clay, detail, uDetail)`. In Skizze the
  surfaces are paper and write depth, so the ink lines are hidden-line.
- **`ink.js`.** `EdgesGeometry` (30°) per mesh except `SMOOTH` and furniture objects, merged into one
  `LineSegments` per collection.
- **`lighting.js`.** Day: sun from Blender's angle, hemisphere, sky. Dusk: low warm sun,
  deep-blue sky, warm room and outside-lamp lights. `createLighting(…, { hires })`:
  - **Fast mode** (default): a **light pool** of `ROOM_N` = 6 `PointLight`s and `OUTSIDE_N` = 2
    `SpotLight`s (targets 1 m below), created once. `setDusk(v)` sets `visible = v > 0` on the
    pool. `update(cameraPos, inside)` (called by `main.js` right before each `renderer.render`;
    a no-op by day) ranks each kind's sites by site distance (`hypot(dx, dy, 3·dz)` while
    `indoors()`), moves pooled light *k* to the *k*-th nearest site and sets
    `intensity = base · v · clamp((d_cut − d) / FADE, 0, 1)` (`base` 9 room / 14 outside,
    `FADE` 1.0 m). `prewarm(compile)` makes the pool visible, awaits
    `renderer.compileAsync`, catches a failure, and restores the day/dusk visibility; `main.js`
    awaits it after `renderer.init()`.
  - **`hires`**: one light per site (23 + 8), always in the render list, intensity `base · v`.
  - `LAMP_LIGHTS` (the reading lamp above the Ofen bed) are lit by day and at dusk in both modes.
- **`hires`.** `main.js` reads `?hires=on` once; it also sets the pixel ratio (full vs. ≤ 1.5)
  and whether the grass is hidden while `indoors()` (fast mode only, Rundgang included), and
  `saveView()` keeps it in the URL.
- **`garden.js`.**
  - **Grass:** an `InstancedMesh` of the clump, scattered per 25 cm cell, outside
    `no_grass`, within 30 m of the house, at 25 % of Blender's density.
  - **Shrubs:** an ink circle in Skizze, a clay blob in Massenmodell, a leaf cloud in
    Detailmodell and Gebaut. The leaves grow about a per-instance centre, an
    `InstancedBufferAttribute`.
- **Visibility.** `main.js` feeds materials, lights and garden a merged view
  (`built + furnished`), so Eingerichtet looks like Gebaut. One `applyVisibility()` (on
  progress and cutaway changes) shows an object iff the cutaway does not hide it and, for
  `extras.furniture`, the stage is Eingerichtet.
- **`ui.js`.** Title, timeline bar (play/pause, scrubber 0–4, stage names), cutaway buttons
  and the sun toggle. `body.dataset.stage`/`cutaway` mirror the state. It returns `setCut` so
  the tour can disable the cutaway buttons.
- **`tour.js`.** The Rundgang: builds its own button and tour bar (play/pause, scrubber,
  "Endlos", "Beenden"). Playback is time-based at `SPEED = 0.75`: `step(t, dt, T, loop)` advances
  (dt clamped) and wraps or clamps, `poseAt(frames, fps, t)` lerps between keys (yaw unwrapped),
  `fovFor(lens, aspect)` turns the lens into a vertical fov (`2·atan(18/lens/aspect)` landscape,
  `2·atan(18/lens)` portrait, as Blender's sensor fit AUTO), re-applied on resize. Orientation:
  direction `(cos p·cos y, cos p·sin y, sin p)` through `yup` and `camera.lookAt`. While playing,
  OrbitControls are off; on pause their target sits 5 cm ahead of the camera. Start: stage
  Eingerichtet, cutaway Ganzes Haus, `EG_Haustuer` rotated 90°. Beenden: door closed, previous
  camera, target and fov restored. `drawDue` caps drawing at 30 fps while the tour is on; the
  sun stays anchored to a fixed copy of the start target.
- **Sub-model pages.** `submodel.js` draws a sub-model page (views, looks Drahtmodell / Masse /
  Gerendert, walls, grid, sun, dimension lines from `dims`); `ofen.js`, `desk.js`, `bad.js` and
  `kueche.js` only configure it. `nav.js` builds the "Teilmodell" drop-down (one list of pages, relative URLs,
  the current page preselected); `ui.js` puts it into the house toolbar, `submodel.js` into every
  sub-model page.
- **View in the URL.** `main.js` and `submodel.js` read `?cam=&at=` (model coordinates) plus
  `p`/`cut` (house) or `look` (sub-models) on load and write them back with `history.replaceState`,
  debounced to 300 ms, on every controls change, stage, cutaway or look change.
- **`blueprint-watch.js`** (Vite plugin, dev server only, off under Vitest): watches `code/*.py`;
  a save runs `npm run blueprint` (debounced, one export at a time, again if saved meanwhile)
  and then sends a full reload; a failed export is logged and does not reload. `export_gltf.py`
  writes the `.glb` atomically (temp file + `os.replace`), so a page never reads a half-written
  file.
- **`serve-build.js`** (Vite plugin, dev server only): serves the production build `web/dist/`
  under `/frechen_blender/`, the GitHub Pages path, so the one dev server shows source and build.
- **Test hook.** `window.__fl` (`setProgress`, `setCutaway`, `setSurfaces`, `lookFrom`,
  `project`, state getters incl. `lights` (visible room / outside lights), `hires`, `pixelRatio`,
  `tour`, `tourKey`), only outside production builds; `window.__ofen`
  / `window.__desk` / `window.__bad` / `window.__kueche` on the sub-model pages.

## Key decisions

ADRs: [ADR-001-XEWL](../architecture/adr-001-xewl-shared-python-core.md) (shared core),
[ADR-002-MLQS](../architecture/adr-002-mlqs-gltf-own-writer.md) (own glTF writer),
[ADR-003-SKGB](../architecture/adr-003-skgb-webgpu-tsl.md) (WebGPURenderer + TSL).

| Decision | Alternatives considered | Why |
|---|---|---|
| The core's output is called **Blueprint** | "Model" | "Model" means the whole 3D house (scene, `.blend`). |
| The **parity test** pins the Blender build to `tests/golden/blender_snapshot.json` (per object: counts, bbox, materials, `rnd` hash) and checks the saved `.blend` | Visual checks only | Moving code between core and backends can change the output silently. Deliberate changes regenerate the golden. |
| Stages change by **crossfade** | Construction build-up | Smaller scope; build-up is a later candidate. |
| A sub-model may bring **its own walls** (`bad.py`: niche wall, lintel, low wall) | Walls in `build_eg()`, only fixtures in the module | The sub-model page must show them; one place describes the room (ADR-001-XEWL). Outer walls stay in `build_eg()`. |
| Speis shelves and cabinet are **built-ins** (`EG_Speis`, stage Gebaut) | Furniture (`EG_Moebel`, Eingerichtet) | Cabinet C replaces a wall; floor-to-ceiling joinery belongs to the house like the kitchen. |
| Sub-model navigation is **one drop-down** built by `nav.js` | A link per sub-model on each page | With four sub-models the links no longer fit; one page list in one place. |
| Leaves are modelled **open** (kitchen door 90° into the Küche, Speis sliding leaf slid south) | Closed | The Rundgang walks through the kitchen door and looks into the Speis aisle. |
| **GitHub Pages**, public and indexable; deploys on push to `main` | Local only; password; `noindex` | Family and friends need a link; the film is already public; the viewer shows no room names. |
| **Desktop browsers** only; **German UI**, English code and specs | Mobile too; one language | Keeps light, shadow and line budgets free of mobile limits; matches the README and the code base. |
| Look: **same palette, recognisably the same house** as the Blender renders | Pixel parity | A starting point, tuned in later iterations. |
| The core holds the **garden layout**; each backend scatters and grows plants itself | Core computes every instance; web-only garden | Shared layout without forcing Geometry Nodes or `mathutils.noise` into pure Python. Blades and leaves differ in detail, by design. |
| Browser grass at **25 %** of Blender's density, within 30 m | Full density | ~4 M triangles is too heavy; 25 % still reads as a meadow. |
| **Cross boards** in the core, **per storey** | In `paint.py` from mesh islands; one EG object | Both backends show them; per storey so "Nur EG" hides the OG boards. |
| Windrose area = star square + four letter squares (`WR_LABEL_HALF` 0.6 m); the viewer ignores it | Blender font bounding boxes | The letters' real extent needs Blender font metrics. The viewer draws no rose, so grass grows there. |
| **Skizze is hidden-line**; no lines for `SMOOTH` objects | X-ray lines; lines everywhere | Interior parts and ~1,600 pebbles would be ink noise. |
| Garden per stage: circles → clay blobs → grass and leaves | Edge lines for every leaf | ~1,400 leaves per shrub would be ink noise. |
| The **cutaway hides whole collections**; `Verschalung_West` goes with `Dach` | Section planes with caps | Simplest; section cuts are a later candidate. |
| The page **opens at Skizze**; Play takes 4 s per stage; the sun toggle is off below p 1.5 | Autoplay | Starting from the first line is the point of "Vom Strich zum Haus". |
| **Room-light height** `ROOM_LIGHT_H` is a core fact read by `film.py` and the viewer | A height per backend | One source of truth (ADR-001-XEWL). |
| Shrub leaves grow about a **per-instance centre** attribute | `positionLocal.mul(uDetail)` | In three.js 0.187 `positionLocal` is already instance-transformed when `positionNode` runs. `instancedBufferAttribute(typedArray, 'vec3')` drops the instanced flag, so a real `InstancedBufferAttribute` is needed. |
| e2e runs headless Chromium with `--use-angle=metal` (WebGL2 path) | SwiftShader | SwiftShader took 1.6 s per frame; headless Chromium has no WebGPU. The WebGPU path is checked by hand. |
| **Open Parts** (lamp cones) are exported double-sided | Guess an orientation | An open surface has no well-defined outward side. |
| The route lives in its own module **`code/tour.py`**, not in the Blueprint | `ROUTE` in `house_core.py` or `film.py` | The route can be edited apart from house and film. |
| The `.glb` carries the **baked, smoothed camera keys** as JSON in `scene.extras.tour` | Export the segments and re-implement the baking in JS; binary accessor | One implementation of the route math (ADR-001-XEWL); JSON is small and matches room lights and garden. |
| `tour.js` builds its own button and bar; `ui.js` only returns `setCut` | Tour controls in `ui.js` | Keeps the tour separable. |
| The viewer plays at **0.75×**; the film keeps its pace | Lower `WALK` in `tour.py` | The slower pace was asked for the browser only. |
| Screen images mapped in **object space around the pane's pivot** | UVs through accumulator, `mesh_ops` and writer | The project already maps textures in object space; no new vertex attribute in three code paths. |
| Screenshots downscaled once (`sips`) and **committed as JPEG** under `web/public/textures/` | Embed the PNGs in the `.glb`; convert at build time | CI is Ubuntu + stdlib (no `sips`, no Pillow); the house page should not load 8.6 MB more. |
| The **route is closed** in `tour.py`, for the film too | A viewer-only return leg | One route (ADR-001-XEWL); the viewer can loop it. |
| Viewer dusk lights are a **fixed light pool** moved to the sites nearest the camera | Keep one light per site and toggle `visible` on the nearest N | three.js 0.187 hashes the id of every light in the render list into each material's cache key; a changing set would recompile every material while the camera moves. |
| Separate pools: **6 room lights, 2 outside lamps**, cut-off fade 1.0 m | 4 + 2 with a 1.5 m fade; one ranking over all 31 sites | Point and spot lights can't share a pooled object, and from outside the lamps would starve the rooms. With 4 the last light was nearly always faded (sites lie centimetres apart in distance). 8 lights instead of 31. |
| Rank sites by distance to the **camera**; indoors the height difference counts **3×** | Distance to the orbit target; plain 3D distance everywhere | The camera is where the viewer stands. Plain 3D fills slots with rooms through floor or ceiling, whose light only leaks (no shadows); outside, a vertical penalty would darken the EG windows in the overview. |
| By day the pool is **out of the render list** (`visible = false`); the dusk variant is **prewarmed** at load | Intensity 0 by day (no recompile ever); accept the stall | Day lighting costs nothing per fragment. Without the prewarm the first dusk (e.g. the Rundgang start) stalled ~0.8 s; one compile at load is cheaper. |
| One URL switch **`hires=on`** for full quality (all lights, full pixel ratio, grass indoors); speed shortcuts apply in the Rundgang too | Shortcuts off whenever the tour runs; a capture-only flag | The browser Rundgang should be fast; the film capture asks for full quality by name. The capture script forces it. |

## Data

- **Source of truth:** the core. The constants and builder calls in `code/house_core.py` are
  the model's data; the backends and the viewer repeat none of them.
- **Generated, committed:** `frechenlehen.blend` (~5.8 MB, must equal the current build),
  `frechenlehen_rundgang.mp4` (~45 MB), `docs/images/*.png`,
  `tests/golden/blender_snapshot.json`.
- **Generated, git-ignored:** `web/public/frechenlehen.glb` (`npm run blueprint`, run before
  `dev`, `build` and `test`, and by the dev server after each saved `code/*.py`), `web/dist/`.
- **Scratch:** `tmp/` (git-ignored): film frames, detail stills, web screenshots, logs.

## System boundaries and external systems

- **Input:** `input/` (PDFs, rendered plan PNGs, colour swatches, photos).
- **Output:** the `.blend`, the MP4, the README images and the viewer page.
- **External tools:** Blender, the Blender MCP add-on, ffmpeg, Node/npm (three.js, Vite and
  the test tools from npm), GitHub Actions and Pages.

## Infrastructure

Model work runs locally on the owner's Mac (arm64). A headless film render is
`Blender -b frechenlehen.blend -a`, at about 1 s per frame, one frame per camera key. The MP4 is
linked raw from GitHub. `.github/workflows/pages.yml` builds on `ubuntu-latest`
(Python 3.13, Node 24) and deploys `web/dist` to `https://tillg.github.io/frechen_blender/`
(base path `/frechen_blender/`). Only the deploy job holds `pages: write`/`id-token: write`.
