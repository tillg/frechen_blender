---
type: ADR
id: ADR-001-XEWL
title: One pure-Python core with a Blender and a glTF backend
description: The house is described once in code/house_core.py (no bpy); build_house.py (Blender) and export_gltf.py (glTF for the web viewer) are backends that only turn its Blueprint into output.
status: proposed
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
  the garden layout, primitives and builders live in `code/house_core.py`. It imports neither `bpy`
  nor `mathutils`.
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

- Every model change is made in `house_core.py`.
- The Blender-only parts (node trees, font curves, Geometry Nodes, `mathutils.noise` shrubs) stay in
  the backends.
- A long-running Blender session must `reload` the core, or it uses stale code.
