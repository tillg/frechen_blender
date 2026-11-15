# This project: Frechenlehen

What the spec skills need to know about this repo. Read it when a change touches the build
scripts, the film or the web viewer — i.e. almost always. The project facts themselves live in the
repo's `CLAUDE.md` and `specs/system/`; this page only names what the workflow uses.

## Where things live

| Thing | Path | Notes |
|---|---|---|
| Core | `code/house_core.py` and its sub-model modules | Pure Python; the backends `export_gltf.py` (viewer) and `export_plans.py` (plan sheets) are live. |
| Blender scripts (dormant, issue #35) | `code/build_house.py`, `fire.py`, `paint.py`, `windrose.py`, `garden.py`, `film.py` | Not run by the workflow; `tests/test_blender_scripts.py` only compiles them. Re-enabling: `CLAUDE.md` › Running › Blender backend. |
| Blender file | `frechenlehen.blend` | Frozen at `7805879` (last parity-green build); not rebuilt. |
| Inputs | `input/*.pdf`, `input/grundriss_eg/og.png`, detail photos `input/<component>.png` | Plans and reference pictures. |
| Pure-Python tests | `tests/`, `.venv/bin/python -m pytest -q` from the repo root | No bpy needed, no test starts Blender; tests marked `slow` re-export the plan sheets. |
| Web viewer | `web/`: three.js; `npm test` (unit), `npx playwright test` (e2e) | The one dev server on 5377 (`CLAUDE.md`). |
| Scratch output | `tmp/` (gitignored): stills in `tmp/details/`, film frames in `tmp/film/`, logs | |

Environment: a repo-local `.venv` (`python3 -m venv .venv && .venv/bin/pip install -r
requirements-dev.txt`) and `cd web && npm install`.

## The two checks

**Per-step check** (after every `/spec:apply` step and every tweak step; budget 60 s):

1. the step's own new test, run alone (a Playwright spec: `npx playwright test <file> -g "<case>"`);
2. `bash scripts/check.sh quick` (`pytest -m "not slow"` + Vitest; prints the time per part);
3. **Show**, when the step has a visible effect in the viewer: `.venv/bin/python code/show.py
   <object…> --print` gives the view URL (`--from n|e|s|w|top` for another side, `--page
   ofen|desk|bad|kueche|gaeste_wc|regal|schrankbett|gaestebad|elternbad` for a sub-model); look at it first with `cd web && node shot.js '<url>'
   ../tmp/web/<name>.png` and read the PNG at 1× (object hidden → retry with `--from`); then
   `.venv/bin/python code/show.py <object…>` opens it in the user's browser (a new tab). It refuses
   when the server on 5377 runs from another clone: switching is the user's call.

**Final check** (once after the last plan step, before `status: applied`; at `/spec:archive`; on
request):

1. `bash scripts/check.sh full` (all pytest incl. `slow` (plan sheets), `npm test`, all Playwright projects
   except `@eye`; about 7 min for Playwright; a viewer tab open in the browser slows it and the frame-rate test). Known bugs in `specs/bugs/` don't count as new
   failures.

## Per step kind

| Kind | Per-step check | Show / look |
|---|---|---|
| `[python]` | the new pytest test + `check.sh quick` | core change visible in the viewer → Show |
| `[web]` | the new Vitest test or Playwright spec alone + `check.sh quick` | screenshots at 1×; Show for a visible change |
| `[blender]` | **dormant** (issue #35): no step of this kind until Blender is re-enabled (`CLAUDE.md` › Running › Blender backend); then: rebuild via MCP + `check.sh quick` | then: a still from a temporary camera to `tmp/details/`; film route: camera clearance check |
| `[docs]` / `[config]` | the mechanical check in `Verify:` | — |

## Build and test commands

| Scope | Command | Notes |
|---|---|---|
| Quick tier | `bash scripts/check.sh quick` | Log in `tmp/check-<ts>.log`; warns above 60 s. |
| Full tier | `bash scripts/check.sh full` | Same log; exits non-zero on any failure. |
| `@eye` stills | `cd web && npx playwright test --grep @eye` | Pictures for a human; not in the default run. |
| Viewer film | `just film` (capture of the browser Rundgang, encode, publish) | Long-running: follow `CLAUDE.md` › Working rules. |
| Rebuild, still, Blender film camera clearance, Blender film render | dormant with the Blender backend | `CLAUDE.md` › Running › Blender backend; route clearance meanwhile only by `tests/test_tour.py`. |

The baseline before the first step of a change is the final check.

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
- Does the Rundgang camera still clear all geometry (`tests/test_tour.py` covers Wandlampen and Alternativ furniture only)?
- Which Show screenshot(s) prove it — from where, at what detail?
- Does it touch the viewer and the plan sheets alike (shared core)?
