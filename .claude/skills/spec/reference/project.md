# This project: Frechenlehen

What the spec skills need to know about this repo. Read it when a change touches the build
scripts, the film or the web viewer — i.e. almost always. The project facts themselves live in the
repo's `CLAUDE.md` and `specs/system/`; this page only names what the workflow uses.

## Where things live

| Thing | Path | Notes |
|---|---|---|
| Build scripts (run inside Blender) | `code/build_house.py`, `paint.py`, `garden.py`, `film.py`, `windrose.py` | Run via the Blender MCP server, always in this order (see `CLAUDE.md` › Running). The scripts are the source of truth; nothing is hand-edited in the `.blend`. |
| Blender file | `frechenlehen.blend` | Saved after a rebuild; a headless render reads the saved file. |
| Inputs | `input/*.pdf`, `input/grundriss_eg/og.png`, detail photos `input/<component>.png` | Plans and reference pictures. |
| Pure-Python tests | `tests/` (once created), `python3 -m pytest -q` from the repo root | No bpy needed. |
| Web viewer | `web/` (once created): three.js; `npm test` (unit), `npx playwright test` (e2e) | |
| Scratch output | `tmp/` (gitignored): stills in `tmp/details/`, film frames in `tmp/film/`, logs | |

## Build and test commands

| Scope | Command | Notes |
|---|---|---|
| Python unit tests | `python3 -m pytest -q` | Only once `tests/` exists. |
| Rebuild the model | Blender MCP: exec `build_house`, `paint`, `windrose`, `garden`, `film`, then save | See `CLAUDE.md` › Running. |
| Visual check | Render a still from a temporary camera to `tmp/details/`, read the image, then remove the camera and restore `scene.camera` | The main verification for geometry, materials and lighting. |
| Film camera clearance | Sample every frame: BVH `find_nearest` ≥ 0.25 m plus `ray_cast` between consecutive frames | After any change to the route or to geometry along it. |
| Film render | headless Blender `-b frechenlehen.blend -a`, logged to `tmp/` | Long-running: follow `CLAUDE.md` › Working rules. |
| Web | `cd web && npm test && npx playwright test` | Screenshots to `tmp/`; read them at 1× before claiming a visual result. |

Run the relevant check once as a baseline before the first step of a change.

## What a change's `architecture.md` must say about impact

Its `## Impact` section lists, per line, what the change touches — `none` where nothing:

- **Build scripts**: which builders, constants or registries (`OPENINGS`, `LEAVES`, `GEO`, …) change.
- **Materials**: new or changed `FL_*` materials, `paint.py` colours.
- **Garden / film**: `NO_GRASS`, `ROUTE` segments, lights.
- **Web viewer**: modules, stages, assets.
- **Render / output**: still or film settings, re-render needed or not.

## Grill seeds

Questions `/spec:grill` puts on the frontier (skip what the artifacts already settle):

- Which plan or photo in `input/` is the source for this? Where do they disagree?
- Does it change coordinates or shared constants other builders rely on?
- Coplanar faces with existing parts? Shared `rnd` value needed?
- Does the film camera still clear all geometry?
- Which still(s) prove it — from where, at what detail?
- Does it touch the Blender build and the web viewer alike (shared core)?
