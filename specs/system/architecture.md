---
title: "Architecture: Frechenlehen house model"
created: 2026-10-08
edited: 2026-10-08
---

# Architecture: Frechenlehen house model

## Overview

A set of Python scripts that run **inside Blender**. They build the scene procedurally into
one `.blend` file, and Blender renders stills and a film from it. There is no server, no
package and no test suite. Details on running the scripts and on pitfalls are in
`CLAUDE.md`. The script table is in `README.md`.

```mermaid
flowchart TB
    subgraph inp["input/"]
        PDF["plans PDF/PNG"]
        PH["detail photos"]
    end
    subgraph code["code/"]
        BH["build_house.py"]
        PA["paint.py"]
        WR["windrose.py"]
        GA["garden.py"]
        FI["film.py"]
    end
    subgraph blender["Blender 5.2"]
        SC[("scene in frechenlehen.blend")]
        EV["EEVEE renderer"]
    end
    PDF -. measured by hand .-> BH
    PH -. modelled by hand .-> BH
    BH --> SC
    PA --> SC
    WR --> SC
    GA -->|reads bounding boxes| SC
    FI -->|camera + lights| SC
    SC --> EV --> OUT["tmp/film/*.png → mp4,<br/>docs/images/*.png"]
```

## Technology stack

| Part | Role |
|---|---|
| Python 3 (Blender's own) | All model code: `bpy`, `bmesh`, `mathutils`. |
| Blender 5.2 | Scene, materials (shader node trees), Geometry Nodes (grass), EEVEE render, AgX view transform. |
| Blender MCP server | How the agent runs code in the open Blender (`execute_blender_code`). |
| ffmpeg | Encodes the film frames to H.264 MP4. |

## Components

### `build_house.py` — the house

It runs in three layers. Only the last one needs Blender:

```mermaid
flowchart LR
    C["constants<br/>W_OUT, Z_OG, RIDGE_Z, ST_*…"] --> B
    subgraph pure["pure Python"]
        B["builders<br/>build_eg, build_og, build_stairs,<br/>build_roof, build_cladding,<br/>balcony, kachelofen, …"] --> PR["primitives<br/>add, box, lbox, sweep, column,<br/>prism, boards, wall, frame"]
        PR --> GEO[("GEO dict<br/>+ SMOOTH, PIVOT,<br/>OPENINGS, LEAVES")]
        MD[("MAT_DEF")]
    end
    subgraph bound["Blender-bound"]
        GEO --> FL["flush_geometry → meshes"]
        MD --> MM["make_materials → node trees"]
        RN["build_room_names<br/>font curves → mesh"]
        RF["build_references<br/>image planes"]
        SS["setup_scene<br/>sun, world, camera"]
    end
```

- **Geometry accumulator.** Builders never call `bpy`. They append vertices, faces,
  material names and an `rnd` value per face to `GEO[(collection, object)]`. Faces are
  polygons (quads or n-gons, may be concave) with no consistent winding.
  `flush_geometry()` makes one mesh per entry. It writes the `rnd` face attribute,
  recalculates normals with bmesh, applies `SMOOTH` and moves origins to `PIVOT`.
- **Local wall frames.** `frame(ax)` returns `P(u, t, z)`, so wall, door and cladding code
  works for walls along x and along y.
- **`MAT_DEF`** is a pure data table. `make_materials()` turns it into Principled BSDF node
  trees:
  - **wood:** noise stretched along the grain axis → colour ramp → hue/value varied by `rnd`
    → bump
  - **speck:** isotropic noise → ramp
  - **bump:** noise → bump
  - **alpha:** blended
  - **emit:** emission
  All texture coordinates are **object space**.
- **Randomness.** `random.seed(22)` makes builds repeatable.
- The only `bpy` dependencies are `make_materials`, `build_room_names` (Blender font
  curves), `build_references`, `reset_collections`, `flush_geometry`, `setup_scene` and
  `mathutils.Vector` (used in `setup_scene`).

### Other scripts

| Script | Responsibility | Depends on |
|---|---|---|
| `paint.py` | Overwrites the base colour of plain materials with RAL colours and adds shutter cross boards. | `FL_*` materials and shutter objects from `build_house` |
| `windrose.py` | Compass rose, in its own collection. | — |
| `garden.py` | Meadow: a Geometry Nodes scatter of grass clumps over an emitter grid, with no grass inside the bounding boxes in `NO_GRASS`. Shrubs in the beds. | scene objects from `build_house` |
| `film.py` | `ROUTE` → per-frame camera keys on `FL_Kamera_Rundgang`, room fill lights (`Innenlicht`), opens `EG_Haustuer`. | `EG_Haustuer` pivot, room layout |

## Data

- **Source of truth:** the scripts. The constants and builder calls in `code/*.py` are the
  model's data.
- **Generated:** `frechenlehen.blend` (committed, ~5.6 MB), `frechenlehen_rundgang.mp4`
  (committed, ~45 MB), `docs/images/*.png`.
- **Scratch:** `tmp/` (git-ignored): film frames, detail stills, logs.

## System boundaries and external systems

- **Input:** `input/` (PDFs, rendered plan PNGs, colour swatches, photos).
- **Output:** the `.blend`, the MP4 and README images. Nothing is served over a network.
- **External tools:** Blender, the Blender MCP add-on and ffmpeg. There are no web
  dependencies and no JavaScript in the repo.

## Infrastructure

Everything runs locally on the owner's Mac (arm64). A headless film render is
`Blender -b frechenlehen.blend -a`, at about 1 s per frame for 3480 frames. Git with GitHub
is the only remote. The MP4 is linked raw from GitHub.
