# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Blender 5.2 model of the house "Frechenlehen", generated entirely by Python scripts in `code/` from the architect's plans (`input/*.pdf`, rendered to `input/grundriss_eg/og.png`) and detail photos in `input/` (file name = component, e.g. `entrance_door_from_outside.png`). The README (German) is the user-facing doc; keep its component list and script table in sync when adding user-visible features.

The house is described once, in `code/house_core.py` plus `code/ofen.py` (the stoves) and `code/desk.py` (the Büro desk; all pure Python, no `bpy`/`mathutils`). `house_core.build()` returns a **Blueprint** (`geo`, `parts`, `smooth`, `pivot`, `mat_def`, `paint`, `room_lights`, `garden`, `furniture`, `dims`); `house_core.build_ofen()` / `build_desk()` return the Ofen / desk sub-model alone (no house, `garden=None`, dimension lines in `dims`) for `web/ofen.html` / `web/desk.html` (both drawn by `web/src/submodel.js`). Two backends turn it into output: `build_house.py` (Blender scene) and `export_gltf.py` (`.glb` for the three.js viewer in `web/`). Make every model change in the core; neither backend nor the viewer repeats its facts (ADR-001-XEWL).

## Running

The scripts run *inside* Blender, normally via the Blender MCP server (`mcp__blender__execute_blender_code`):

```python
for s in ("build_house", "fire", "paint", "windrose", "garden", "film"):
    exec(open(f"/Users/tgartner/git/frechen_blender/code/{s}.py").read())
bpy.ops.wm.save_mainfile()
```

Always rebuild in this order: `fire`, `paint`, `garden` and `film` all depend on objects (or materials) that `build_house` recreates. Every script is idempotent (re-running replaces its own collection/objects). No hand edits live in the `.blend`; the scripts are the source of truth. Every Blender script imports the core with `sys.path` + `importlib.reload(house_core)`; without the reload a long-running Blender session would silently keep the old core. Without the MCP, the same rebuild runs headless: `Blender -b frechenlehen.blend --python <script that execs the six and saves>`.

Tests:

- `python3 -m pytest -q` (repo root): core, `mesh_ops`, glTF export, and the **parity test**, which builds headless in Blender and compares a per-object fingerprint with `tests/golden/blender_snapshot.json`; it also checks that the saved `frechenlehen.blend` is the current build. A deliberate change to the Blender output: regenerate with `UPDATE_GOLDEN=1 python3 -m pytest -q tests/test_blender_parity.py`, diff the golden, then rebuild and save the `.blend`.
- `cd web && npm test && npx playwright test`: Vitest units and Playwright e2e (projects `dev` and `preview`, the latter on the production build under `/frechen_blender/`, built first by the setup project `build`). Both run against the one dev server on 5377; Playwright starts no server of its own (only `npm run dev` on 5377 if nothing runs there). Headless Chromium runs on the real GPU (`--use-angle=metal`); WebGPU is off there, so the viewer runs on its WebGL2 fallback. Screenshots go to `tmp/web/`.
- Visual checks are still needed: render stills from a temporary camera to `tmp/details/` and look at them (then remove the temp camera and restore `scene.camera`).

## Architecture of `house_core.py` (and the Blender backend)

- **Geometry accumulator.** Nothing is created with `bpy.ops`. Builders call `add()` / `box()` / `lbox()` / `sweep()` / `column()` / `prism()` / `boards()`, which append vertices/faces to `GEO[(collection, object)]`; each `add()` call is one **Part** (a closed solid, recorded in `PARTS`). In Blender, `flush_geometry(bp)` turns each entry into one mesh object inside collection `FL_<collection>` under root collection `Haus` and recalculates normals, so face winding does not matter; the glTF backend does the same with `mesh_ops` (ear clipping, per-Part orientation).
- **Local wall frames.** `frame(ax)` returns `P(u, t, z)`: `u` runs along a wall, `t` across it. Wall/door/cladding code is written once in `u/t` and works for both wall orientations.
- **`wall()`** builds an axis-aligned wall with openings `(a, b, sill, head, kind[, shutters])`. The kinds are `W` window, `FD` french door, `GD` glazed larch door (also the big west windows), `D` solid door, and `I` bare opening, filled afterwards by a dedicated builder (`entrance_door`, `back_door`, `stube_niche`, `panel_door`). Exterior openings are recorded in `OPENINGS` (and gable windows in `GABLE_WIN`) so `build_cladding()` can cut the west larch cladding around them. Call cladding after all walls.
- **Interior doors.** Door entries in `interior()` are `(a, b)` for an open passage, or `(a, b, swing, hinge[, flat, style])`. Leaves are opened flat against the room wall by default (so the film camera passes freely); use `flat=False` (90°) where a room corner is too close. `hinge="ab"` makes a double door and `style="glazed"` the Windfang door. Every leaf is recorded in `LEAVES` for clash checks against the walls.
- **Materials.** `MAT_DEF` defines `FL_*` materials: `rgba` for plain colours, `wood` / `speck` for procedural textures in object space, `bump` for plaster. `PAINT` (in the core) overrides the base colour of plain materials only: `FL_Putz`, `FL_Rahmen` (white shutter cross boards), `FL_Laden` (RAL 5014); `paint.py` applies it in Blender, the viewer reads it from the material extras. Textured materials ignore it. The shutter cross boards are built in the core (`build_cross_boards()`, per storey).
- **`rnd` face attribute.** Each `add()` call gets a random value that the shaders use for per-board/per-slab variation. Parts that overlap in the same plane (frame corners, rails vs. stiles) must share one `rnd` value, otherwise they visibly z-fight. `wall()` and the cladding trims already do this.
- **Stoves in `ofen.py`.** The Ofen sub-model (`OFEN_*`, `ofen_neu()`: stove, benches, bed with mattress and checked blanket), its placement `ofen_im_haus()` and `werkstattofen()` live in `code/ofen.py`, so the stove can be worked on apart from the house. `house_core` imports it and calls those functions; `ofen.py` reaches the primitives and `GEO`/`PARTS` as `hc.*` (`import house_core as hc`; the modules import each other, so no `from house_core import …`). Materials stay in `MAT_DEF`. Blender scripts that build (`build_house.py`, `garden.py`) `reload(ofen)` and `reload(desk)` before `reload(house_core)`.
- **Desk in `desk.py`.** `desk_neu(c, x0, y0)` builds table, monitors, MacBook, keyboard and trackpad straight into collection `c` (house: `EG` at `DESK_AT`; sub-model: `Desk` at the origin), `stuhl()` the chair; the devices draw `rnd` from their own `random.Random`, so no later part shifts. The screen panes are objects with a `PIVOT` (lower-left corner) and a `TURN` (yaw); their materials carry `image` (under `web/public/`) and `size`, mapped in object space in both backends (`house_core.local()`). The textures are committed JPEGs, made once with `sips` from `input/2026-11-06 input/`.
- **`PIVOT`** puts an object's origin at a hinge (`TURN` adds a yaw about it; both backends store the mesh unturned). Besides the screen panes, only `EG_Haustuer` uses it; `film.py` swings it open by rotating it 90° about z.
- Coordinates are in metres: origin at the outer SW corner, +X east, +Y north. Constants such as `Z_OG`, `STAIR_HOLE`, `FOOT`, `CORRIDOR_EG` and the stair constants `ST_*` are shared between builders.

## Other scripts

- `garden.py` (collection `Garten`): the meadow is a Geometry Nodes scatter of grass-clump instances on an emitter grid, with 10 % density in the viewport. Where grass grows, the clump shape and the shrub placements come from the **garden layout** in the core (`garden_layout()`: `NO_GRASS` bounding boxes computed from `GEO`, the windrose area from `WINDROSE_CENTER`/`WINDROSE_R`, density, clump, shrubs). It plants the leafy shrubs into the `Beet_*` beds.
- `export_gltf.py`: Blueprint → `.glb` (standard library only). One node per GEO object (`extras.collection`, `extras.smooth`, `extras.furniture` for the objects of the last viewer stage "Eingerichtet"), one primitive per material with `POSITION`/`NORMAL`/`_RND`, `MAT_DEF` + paint in material extras, room lights and the garden layout in `scene.extras`, positions as `(x, z, -y)`. `web/public/frechenlehen.glb` is generated (`npm run blueprint`, run before `dev`/`build`/`test`) and git-ignored.
- `web/` (Vite, three.js `WebGPURenderer` + TSL, ADR-003-SKGB): `blueprint.js` (load), `stages.js` (timeline weights), `materials.js` (TSL from the extras), `ink.js` (Skizze lines), `lighting.js` (day/dusk, room lights), `garden.js`, `ui.js`, `tour.js` (Rundgang), `main.js`. A dev-only test hook is `window.__fl`. GitHub Pages deploys `web/dist` from `main` (`.github/workflows/pages.yml`).
- `tour.py` (pure Python, own file so the route can be edited apart from house and film): `ROUTE` is a list of `orbit` / `path` / `turn` / `stair` / `hold` segments (`turn` turns on the spot at `TURN` °/s, left `L` or right `R`; `peek()` = look along a room's left wall, then swing right; the pauses are `PAUSE` s; a `path` first turns at `TURN` to face its way); `build_tour()` bakes it to smoothed per-frame camera keys `(x, y, z, yaw, pitch, lens)`. `film.py` keys `FL_Kamera_Rundgang` with them (plus fill lights in collection `Innenlicht`); `export_gltf.py` writes them to `scene.extras.tour`, which the viewer's "Rundgang" (`web/src/tour.js`) plays. `tests/golden/tour.json` pins the keys; after a deliberate route change: `UPDATE_TOUR_GOLDEN=1 python3 -m pytest -q tests/test_tour.py`. The route is closed (it ends at its start pose), so `build_tour()` smooths cyclically and the viewer can loop it. After changing the route or furniture, check that the camera clears all geometry: sample every frame and use a BVH `find_nearest` distance (≥ 0.25 m) plus a `ray_cast` between consecutive frames.
- `fire.py` (collection `Feuer`): the flickering-fire component. `tongues(w, h)` (pure, also used by `export_gltf.py` → `scene.extras.fires` → `web/src/fire.js`) lays out flame tongues on each bed in `house_core.FIRES` (recorded by the stoves); in Blender each tongue flickers via F-curve noise, plus a flickering light per fire.
- `windrose.py`: its own collection, independent of the rebuild.

## Pitfalls seen in this project

- **Coplanar faces with the same normal z-fight.** Offset new parts by millimetres (e.g. the stairwell edge boards stand 6 mm proud of the slab edge) rather than aligning them with existing faces.
- **Reading the plans.**
  - Pink-hatched wall in `grundriss_eg.png` is wall, not an opening. The original vector extraction only read gray wall fills. The pink coloring is only for the Behörde: It shows what are new constructual elemenst.
  - A wall segment with lighter hatching is a closed-up door. Two parallel lines without hatching between hatched wall stubs are an opening (e.g. the Großeltern Bad opens to the bedroom).
  - Stair: 15 risers at 18.0/25.5 need 3.57 m of run, more than the plan draws ("Treppe wird verschoben"). The OG stairwell opening confirms the full length.
  - To map world coordinates to plan pixels, use the page transform in `build_references()` (1:100, 28.3465 pt/m).
- **Render look.** EEVEE with the AgX view transform washes out strong emission and bright saturated colours. Keep emission strengths low (the stove fire uses 1.2).

## Claude config: everything comes from this repo

User-wide Claude config (`~/.claude/…`) is switched off for this project (`.claude/settings.json`, `.claude/settings.local.json`), so all instructions, agents, MCP servers and settings live in the repo. The `spec` plugin in `.claude/skills/spec/` is copied from agents1.

A project file cannot remove user-scope hooks and status line (`disableAllHooks` would also disable the spec pane), permission allow-lists, `autoMode`, or UI settings. For a fully clean session, start with `claude --setting-sources project,local`.

## Working rules

- **Subagents first** for search-heavy, parallelizable or multi-file work. Use `explorer` / `researcher` / `worker` (cheaper models), not `general-purpose` (runs on Opus).
- **Never mock** anything without explicit permission. **Never make tests pass by changing/removing them** without explicit permission.
- **Never create or switch branches** without explicit permission. Git worktrees go in `.worktrees/`.
- **Verify before claiming done** (here: render stills, see "Running"). "Looks right" is not done.
- **Be extremely concise when reporting.** Sacrifice grammar for concision.
- **Consult the advisor** before a large plan, when an error repeats, and before calling a long task done.
- **Web apps (three.js viewer):** test with the Playwright MCP before calling it done: use the dev server, `open` it, verify it responds. Never report a visual change as working without having seen it in a screenshot: zoom on the changed spot, check edges/last row/outer column too, use `scale:"css"` (1×) for fine lines, and say what exactly was checked. Reproduce a user-reported glitch before fixing it. Give the user an `http://localhost` URL (fresh query, never a fresh port) to reload, not `file://`. Artifacts go to `tmp/`.
- **Exactly one dev server, never more.** It runs on port 5377 (`cd web && npm run dev`, pinned with `--strictPort`) and serves both pages: Haus `http://localhost:5377/`, Ofen `http://localhost:5377/ofen.html`; under `http://localhost:5377/frechen_blender/` it also serves the production build `web/dist/` as GitHub Pages does (`web/serve-build.js`; `npm run build` refreshes it). If something already listens on 5377 (`lsof -iTCP:5377 -sTCP:LISTEN`), reuse it, also when another session started it; start it only if the port is free, and never on another port. A saved `code/*.py` makes the server re-run `npm run blueprint` and reload open pages (`web/blueprint-watch.js`); the view survives the reload because it lives in the URL (`?cam=&at=&p=&cut=`, Ofen `?cam=&at=&look=`). The tests use this server too; no exception, not even for a test run.
- **Long-running processes (>~30 s, e.g. the film render):** tee to `tmp/<name>-$(date +%Y%m%d-%H%M%S).log`, `open` the log, run in the background, check at least every 10 min; no progress for ~10 min → treat as stuck.
- **ETAs** are absolute, Europe/Berlin, `YYYY-MM-DD HH:MM`.
- **Diagrams:** compact ASCII in chat; important ones as Mermaid in `docs/diagrams/<name>.mmd` (plus `.svg` when a visual diagram is asked for).

## Spec-driven workflow

Every non-trivial change goes through the `spec` plugin (`.claude/skills/spec/`):

```
propose → [grill | iterate] → apply → adversarial-code-review → archive
small change:  tweak
```

- Start reading at `specs/README.md`; `specs/system/` is the truth about the model today,
  `specs/architecture/index.md` lists the binding ADRs (cite them by full `ADR-NNN-HHHH` id).
- `/spec:overview` shows where every open change stands; the `/spec-status` pane shows it live.
- Project commands and step kinds (`[python]`, `[blender]`, `[web]`):
  `.claude/skills/spec/reference/project.md`.
- Choices made while nobody was there to ask go into `DECISIONS.md`
  (`.claude/skills/spec/reference/decisions.md`).

Working principles of the workflow:

@.claude/skills/spec/reference/principles.md
