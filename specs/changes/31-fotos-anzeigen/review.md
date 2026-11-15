---
feature: 31-fotos-anzeigen
title: "Review: Vorlagen — the reference photos by place in the house"
status: applied
order: 5
created: 2026-11-15
edited: 2026-11-15
---
# Review: Vorlagen — the reference photos by place in the house

**Scope:** working-tree diff on `issue/31-fotos-anzeigen` against `issue/34-alternativ-layout-standard` (uncommitted) · **Reviewed:** 2026-11-15

## Defects

- [MEDIUM] Room markers show through walls from a low camera outside with a cutaway (`needsRay` skipped the wall ray for every outside camera; `markerVisible` had no height limit). · `web/src/markers.js` · label over an exterior wall · **Fixed:** the wall ray now runs for every marker (`needsRay` removed); e2e "from outside at the wall, not through it".
- [LOW] Only `*_Waende` occlude; `EG_Anbau` (PLAN `wall_objects`) not. · `code/export_gltf.py` · **Fixed:** `vorlagen_walls` includes the PLAN wall objects (`test_vorlagen_extras`).
- [LOW] Furniture and the stove do not occlude. · accepted (DECISIONS run-2026-11-15-1633-9).
- [LOW] Missing `vorlagen.json` → blank page; unknown `?b=` → index; `vorlagen.py` without argument → IndexError. · accepted: the JSON is produced by every `npm run blueprint`/build.
- [LOW] Wall raycast without BVH on every drawn frame (two wall meshes, ≤ 8 markers, only candidates within 8 m). · accepted; no frame-rate test changed.
- [LOW] Hard-coded 55 in `test_every_input_image_is_assigned_once`; constants in `markers.test.js`. · accepted: the count makes a new picture a conscious change; unit tests use fixed fixtures.

## Standards

- README "Lokal" line lacked `vorlagen.html`; CLAUDE.md `web/` bullet lacked the new modules. · **Fixed.**
- Anchors hand-typed in `code/vorlagen.py` rather than `house_core.py`. · accepted: a pure-Python module beside the core, imported by the backend like `tour.py`; ADR-001-XEWL holds (one source, the viewer repeats nothing).
- Smells (judgement): `room` read only by the test (kept: it documents and checks the anchor's room); "Bild/Bilder" twice; image-loaded check duplicated in two specs. · accepted.

## Spec

- No e2e for the Garderobe marker in its corner. · **Fixed:** "the Garderobe marker shows in the Garderobe corner".
- Seven area pages not loaded in e2e (index loads every cover; Garderobe and Ganzes Haus fully). · accepted.
- `?hires=on` covered by unit test only. · accepted.
- Plan step 1 named `test_anchors_in_free_air_on_their_storey`; the test is `…_in_their_room`. · **Fixed** in plan.md.
- "Ganzes Haus" is one page for all house-wide elements (lamp, basins, floors, doors, stair, Werkstattofen) — the issue's "eine HTML Seite für Elemente, die im ganzen Haus verteilt sind". · as intended.

## Verdict

Defects: 6 (worst MEDIUM, fixed). Standards: 3 (docs fixed; rest judgement calls accepted). Spec: 5 (2 fixed, rest accepted). No open CRITICAL/HIGH.
