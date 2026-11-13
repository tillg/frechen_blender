---
feature: 18-gaestebad-og
title: "Review: Gästebad im 1. Stock"
status: applied
order: 5
created: 2026-11-13
edited: 2026-11-13
---
# Review: Gästebad im 1. Stock

**Scope:** working tree vs `main` (uncommitted): `code/gaestebad.py` (new), `code/house_core.py`, the
Blender reload lists, `export_gltf.py`, `show.py`, `web/gaestebad.html` + `src/gaestebad.js` + wiring,
tests, README, CLAUDE.md. The regenerated `plans/`, golden and `.blend` were checked by diff.
**Reviewed:** 2026-11-13. The second pass ran after the longer shower and the sub-model; the first
pass on the layout alone was triaged and folded in.

## Defects

- [LOW] Importing `gaestebad` (or `gaeste_wc`, pre-existing) before `house_core` fails on the cycle.
  All entry points import `house_core` first. Accepted, same as `gaeste_wc`.
- [LOW] Floor of the Gästebad not pinned · *refuted*:
  `test_bathrooms_have_limestone_like_the_eg_corridor` samples (0.8, 6.0), (1.62, 6.0), (1.0, 6.49)
  and others, and checks that no stone lies twice.
- [LOW] The e2e ink threshold is weak. It follows the pattern of the other sub-model specs.
- From the first pass: the new parts draw from the global `random` stream. The removed door shifts
  it anyway, so `rnd`, the floor joints and the gravel change house-wide; this was accepted. The partition
  and the mirror now use `Random(18)`. The "EG rnd shift unexplained" finding was refuted, because
  `build_slabs()` and the later builders run after `build_og()`.
- Verified clean:
  - reload order
  - sub-model vs house walls and windows
  - registries
  - glass vs leaf (4.4 cm)
  - tray vs partition (opposite normals)
  - dimension labels vs geometry
  - web wiring
  - plans byte-identical on regeneration

## Standards

- No hard breaches. README, CLAUDE.md and project.md are in sync. There are no orphans: `bad_mirror`
  is still used by Bad S, and `WCS` keeps WC 2,30.
- The ADR-001-XEWL module list doesn't name `gaestebad.py` yet. It is updated at `/spec:archive`, as
  it was for the Schrankbett.
- Judgement calls:
  - `cm()` and the dims lambda are copied from `gaeste_wc.py`, the module pattern
  - `waende()` restates the coordinates of `build_og()`'s walls, as `schrankbett.waende()` does
  - `SN` is tied to the leaf only by a comment; the test pins the 3–7 cm gap

## Spec

- All steps are implemented and every pytest Verify passes. Spec numbers match the code: tray, glass,
  toilet, basin, mirror and dimension labels.
- No scope creep beyond the plan.
- Gap: the ADR-001 log entry, which is deferred to the archive.

## Verdict

- Defects: 3 LOW, one of them refuted. No CRITICAL, HIGH or MEDIUM remains open.
- Standards: 0 hard breaches; 1 documentation gap (ADR-001), deferred to the archive; 3 judgement calls.
- Spec: 0 missing steps; the same ADR gap.

Fixed before this pass: the `architecture.md` wording and the test tidy-ups from the first pass.
Accepted as is: the global-stream shift, the import order, the copied helpers (module pattern) and the
"WC" plan label dropped (intended).
