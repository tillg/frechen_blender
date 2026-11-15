---
feature: 32-dusche-badewanne
title: "Review: shower and bathtub in the Gästebad"
status: applied
order: 5
created: 2026-11-15
edited: 2026-11-15
---
# Review: shower and bathtub in the Gästebad

**Scope:** `git diff a95ce39...HEAD` (three axes on the first layout, commit 209bf40); a second Defects pass on
the final layout (`git diff 944636c...HEAD -- code/ tests/`, after the user's four additions) · **Reviewed:** 2026-11-15

## Defects

First pass: no CRITICAL/HIGH. Geometry checked by AABB over the 268 OG bath parts: no unintended intersections.
- [MEDIUM] README `house_core.py` row still described the old Gästebad (shower 115 × 139, Doppelwaschbecken 120,
  mirror 140 × 85, 32 OG lamps, 4 over the mirror) · README.md:38 · stale user docs · **fixed**.
- [LOW] "bodengleiche Dusche" vs the ceramic tray · **resolved** by the user's addition (-17: `tray=False`).
- [LOW] the Rundgang clearance test checks the camera keys only, not the segments between them ·
  tests/test_tour.py · **accepted**: the route only peeks in from the Flur (≥ 1 m from every Gästebad part);
  the same pattern as the Elternbad's test.
- [LOW] docstring said toilet and shower draw from the global stream · **fixed**.

Second pass (final layout): no blocking defects. Tub segments all closed, no zero-area faces, inner rings
inside outer rings; tub top 5 mm under the sill along the window; tap on the plaster west wall in the foot
half; glTF export clean (20536 triangles).
- [LOW] module docstring still described the built-in 170 tub · code/gaestebad.py:1-12 · **fixed**.
- [LOW] no numeric test of segment closure · **accepted**: the export and the AABB checks were run once;
  `hi < zo + 0.75` pins the sill margin.
- [LOW] hidden embeds (glass corner 4 mm into the slabs, feet 18 mm into the floor's limestone, rim and
  body 5 mm coplanar with the same rnd) · **accepted**: invisible.

## Standards

- (hard) README stale numbers and lamp wording (as above) · **fixed** (README, CLAUDE.md, system docs).
- No orphaned constants (`GA`, `PB`, `YP`, `ZR`, `FY` gone with their uses). Judgement calls: short lambda
  names `K`/`T` in `wanne()` (the module's and `waschbecken()`'s style); `(dx, dy, z)` threaded through
  (the house-wide pattern).

## Spec

- Plan's Test first named `test_gaestebad_og_shower` · **fixed** (`_og_shower_and_tub`).
- Step 2 (Rundgang guard) is not test-first: the route is unchanged; stated in the plan.
- Shower depth label vs spec (131 vs 130) · superseded by the additions; spec, decisions and labels agree now
  (101 × 141, way in 53 to the shower edge, 50 to the pane's rail).
- Left/right from the door, window over the tub, rims under the sill: verified by tests.

## Verdict

Defects: 1 MEDIUM (fixed), 3 LOW (2 fixed/resolved, 1 accepted). Standards: 1 hard (fixed), judgement calls only
otherwise. Spec: 1 minor (fixed), 1 noted. The user's four additions during apply (-17 … -20) changed the layout
after the first pass; each went test-first, and the final Defects pass looked at the slipper tub's segments,
the glass, the tap and the glTF export.
