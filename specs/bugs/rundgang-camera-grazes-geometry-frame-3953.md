---
title: "Bug: Rundgang camera grazes geometry at frame 3953"
priority: low
areas: [blender]
created: 2026-11-10
edited: 2026-11-10
---
# Bug: Rundgang camera grazes geometry at frame 3953

**Where:** `code/tour.py` route / `FL_Kamera_Rundgang`, film frame 3953 (camera at x 9.7, y 8.0,
z 2.73) and a ray hit between frames 6920 and 6921

## Steps

1. Open the saved `frechenlehen.blend` headless.
2. Sample `FL_Kamera_Rundgang` on every frame: BVH `find_nearest` against all meshes of `Haus`,
   plus a `ray_cast` between consecutive camera positions (the clearance check of `CLAUDE.md`).

## Expected

Every frame ≥ 0.25 m from all geometry, no ray hit between frames.

## Actual

Min distance 0.0066 m at frame 3953; 52 frames closer than 0.25 m; ray hits at frames 3953 and
6921. The same on the build of
commit 4cf41cc (found during the kitchen tweak of 2026-11-10, not caused by it).

## Evidence

Clearance script output on both builds:
`{"min": [0.0066, 3953, [9.7, 8.0, 2.73]], "ray_hits": [3953, 6921], "frames": [1, 7612]}`
