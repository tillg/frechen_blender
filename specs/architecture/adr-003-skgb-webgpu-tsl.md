---
type: ADR
id: ADR-003-SKGB
title: WebGPURenderer with TSL node materials for the viewer
description: The viewer renders with three.js WebGPURenderer and builds its procedural materials and stage blending as TSL node graphs, relying on the automatic WebGL2 fallback.
status: accepted
date: 2026-11-03
supersedes: []
superseded_by: []
---
# ADR-003-SKGB: WebGPURenderer with TSL node materials for the viewer

## Context

The hardest part to carry into the browser is the procedural materials: wood grain, speckle and
plaster bump driven by `rnd`. On top of those, the four stages blend between paper, clay and the
real materials.

## Decision

- Use `WebGPURenderer` (`three/webgpu`) with TSL node materials (`three/tsl`):
  - `MeshStandardNodeMaterial` built from the material extras;
  - stage blending with `mix()` on uniforms.
- The three.js version is pinned exactly.
- Browsers without WebGPU, including headless Chromium in the tests, use the automatic WebGL2
  fallback.
- If a TSL feature we need breaks, only the affected material falls back to the WebGL path.

## Alternatives considered

- **`WebGLRenderer` with GLSL `onBeforeCompile` patches.** Rock solid, but brittle across three.js
  releases, and every patched shader needs its own uniforms.

## Consequences

- TSL maps almost 1:1 onto Blender's Noise → ColorRamp → Bump.
- The TSL API still changes between releases, so upgrades need the material tests.
