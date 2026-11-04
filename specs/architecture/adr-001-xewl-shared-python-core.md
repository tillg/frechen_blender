---
type: ADR
id: ADR-001-XEWL
title: One pure-Python core with a Blender and a glTF backend
description: The house is described once in code/house_core.py plus code/ofen.py for the stoves (no bpy); build_house.py (Blender) and export_gltf.py (glTF for the web viewer) are backends that only turn its Blueprint into output.
status: accepted
date: 2026-11-03
supersedes: []
superseded_by: []
---
# ADR-001-XEWL: One pure-Python core with a Blender and a glTF backend

## Context

The house exists only as Blender build scripts. The three.js viewer must show the same house,
and every later fix to a wall or a door must reach both outputs. The geometry code in
`build_house.py` is already free of `bpy` up to `flush_geometry()`.

## Decision

- Constants, `MAT_DEF`, paint colours, room-light positions, the windrose position, cross boards,
  the garden layout, primitives and builders live in `code/house_core.py`; the stove builders live in
  `code/ofen.py`, which `house_core` imports. Neither imports `bpy` or `mathutils`.
- `house_core.build()` returns a **Blueprint**: plain data.
- Backends only translate a Blueprint into output and repeat none of its facts:
  - `build_house.py`: Blender scene.
  - `export_gltf.py`: `.glb` for the viewer.
- The Blender scripts import the core with `sys.path` and `importlib.reload`.
- A headless parity snapshot proves the Blender output is unchanged by the split.

## Alternatives considered

- **Export `.blend` → glTF with Blender's exporter.** The procedural node materials don't survive,
  and the web build would need Blender in CI.
- **Port the builders to JavaScript.** Two copies of 1,300 lines that would drift apart.

## Consequences

- Every model change is made in the core (`house_core.py`, stoves in `ofen.py`).
- The Blender-only parts (node trees, font curves, Geometry Nodes, `mathutils.noise` shrubs) stay in
  the backends.
- A long-running Blender session must `reload` the core, or it uses stale code.

## History

- 2026-11-04: stove builders moved to `code/ofen.py` (part of the core), so the stove can be worked on apart from the house.
