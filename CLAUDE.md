# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Blender 5.2 model of the house "Frechenlehen", generated entirely by Python scripts in `code/` from the architect's plans (`input/*.pdf`, rendered to `input/grundriss_eg/og.png`) and detail photos in `input/` (file name = component, e.g. `entrance_door_from_outside.png`). The README (German) is the user-facing doc; keep its component list and script table in sync when adding user-visible features.

## Running

The scripts run *inside* Blender, normally via the Blender MCP server (`mcp__blender__execute_blender_code`):

```python
for s in ("build_house", "paint", "windrose", "garden", "film"):
    exec(open(f"/Users/tgartner/git/frechen_blender/code/{s}.py").read())
bpy.ops.wm.save_mainfile()
```

Always rebuild in this order: `paint`, `garden` and `film` all depend on objects that `build_house` recreates. Every script is idempotent (re-running replaces its own collection/objects). No hand edits live in the `.blend`; the scripts are the source of truth.

Film render (headless, ~1 s/frame, 3480 frames at 1280×720, 25 fps, EEVEE; output settings are set by `film.py` and stored in the file):

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b frechenlehen.blend -a > tmp/render-$(date +%Y%m%d-%H%M%S).log 2>&1
```

Frames go to `tmp/film/frame_####.png`; the result is `frechenlehen_rundgang.mp4` (ffmpeg is installed). A headless render reads the file as saved when it starts, so save first and restart it after model changes.

There is no test suite. Verify changes by rendering stills from a temporary camera to `tmp/details/` and looking at them (then remove the temp camera and restore `scene.camera`).

## Architecture of `build_house.py`

- **Geometry accumulator.** Nothing is created with `bpy.ops`. Builders call `add()` / `box()` / `lbox()` / `sweep()` / `column()` / `prism()` / `boards()`, which append vertices/faces to `GEO[(collection, object)]`; `flush_geometry()` turns each entry into one mesh object inside collection `FL_<collection>` under root collection `Haus`. Normals are recalculated at flush, so face winding does not matter.
- **Local wall frames.** `frame(ax)` returns `P(u, t, z)`: `u` runs along a wall, `t` across it. Wall/door/cladding code is written once in `u/t` and works for both wall orientations.
- **`wall()`** builds an axis-aligned wall with openings `(a, b, sill, head, kind[, shutters])`. The kinds are `W` window, `FD` french door, `GD` glazed larch door (also the big west windows), `D` solid door, and `I` bare opening, filled afterwards by a dedicated builder (`entrance_door`, `back_door`, `stube_niche`, `panel_door`). Exterior openings are recorded in `OPENINGS` (and gable windows in `GABLE_WIN`) so `build_cladding()` can cut the west larch cladding around them. Call cladding after all walls.
- **Interior doors.** Door entries in `interior()` are `(a, b)` for an open passage, or `(a, b, swing, hinge[, flat, style])`. Leaves are opened flat against the room wall by default (so the film camera passes freely); use `flat=False` (90°) where a room corner is too close. `hinge="ab"` makes a double door and `style="glazed"` the Windfang door. Every leaf is recorded in `LEAVES` for clash checks against the walls.
- **Materials.** `MAT_DEF` defines `FL_*` materials: `rgba` for plain colours, `wood` / `speck` for procedural textures in object space, `bump` for plaster. `paint.py` overwrites the base colour of plain materials only: `FL_Putz`, `FL_Rahmen` (white shutter cross boards), `FL_Laden` and `FL_Kachel` (both RAL 5014). Textured materials ignore it.
- **`rnd` face attribute.** Each `add()` call gets a random value that the shaders use for per-board/per-slab variation. Parts that overlap in the same plane (frame corners, rails vs. stiles) must share one `rnd` value, otherwise they visibly z-fight. `wall()` and the cladding trims already do this.
- **`PIVOT`** puts an object's origin at a hinge. Only `EG_Haustuer` uses it; `film.py` swings it open by rotating it 90° about z.
- Coordinates are in metres: origin at the outer SW corner, +X east, +Y north. Constants such as `Z_OG`, `STAIR_HOLE`, `FOOT`, `CORRIDOR_EG` and the stair constants `ST_*` are shared between builders.

## Other scripts

- `garden.py` (collection `Garten`): the meadow is a Geometry Nodes scatter of grass-clump instances on an emitter grid, with 10 % density in the viewport. Areas without grass come from the scene bounding boxes of the objects listed in `NO_GRASS`, so `view_layer.update()` must run first. It also plants the shrubs into the `Beet_*` objects.
- `film.py`: `ROUTE` is a list of `orbit` / `path` / `look` / `stair` / `hold` segments, baked to per-frame keys on `FL_Kamera_Rundgang`, plus fill lights in collection `Innenlicht`. After changing the route or furniture, check that the camera clears all geometry: sample every frame and use a BVH `find_nearest` distance (≥ 0.25 m) plus a `ray_cast` between consecutive frames.
- `windrose.py`: its own collection, independent of the rebuild.

## Pitfalls seen in this project

- **Coplanar faces with the same normal z-fight.** Offset new parts by millimetres (e.g. the stairwell edge boards stand 6 mm proud of the slab edge) rather than aligning them with existing faces.
- **Reading the plans.**
  - Pink-hatched wall in `grundriss_eg.png` is wall, not an opening. The original vector extraction only read gray wall fills.
  - A wall segment with lighter hatching is a closed-up door. Two parallel lines without hatching between hatched wall stubs are an opening (e.g. the Großeltern Bad opens to the bedroom).
  - Stair: 15 risers at 18.0/25.5 need 3.57 m of run, more than the plan draws ("Treppe wird verschoben"). The OG stairwell opening confirms the full length.
  - To map world coordinates to plan pixels, use the page transform in `build_references()` (1:100, 28.3465 pt/m).
- **Render look.** EEVEE with the AgX view transform washes out strong emission and bright saturated colours. Keep emission strengths low (the stove fire uses 1.2).
