---
feature: 2d-plan-export
title: "Review: 2D plan export"
status: applying
order: 5
created: 2026-11-11
edited: 2026-11-11
---
# Review: 2D plan export

**Scope:** working tree on branch `2d-plan-export` vs `main` (0 commits; modified `CLAUDE.md`,
`README.md`, `code/house_core.py`, `pytest.ini`; new `code/export_plans.py`, `tests/test_plans.py`,
`plans/*.svg`) · **Reviewed:** 2026-11-11

## Defects

No CRITICAL or HIGH. Green: `pytest -m "not slow"` 134 passed; `tests/test_plans.py` (incl. slow) 24
passed; parity + tour passed. Export byte-identical under different `PYTHONHASHSEED` and equal to the
committed `plans/`. `build()` repeated / after sub-model builds: `DOORS` stays 22. Core diff additive
only (no geometry or random-sequence change). All 22 door records open to the as-built leaf side.

- **[MEDIUM] Door swings always drawn as 90° quarter arcs** although 8 leaves are built flat
  (`angle=180`). · `code/export_plans.py:613-627` (`door_swings`), `code/house_core.py:433-434` · The
  architect reads a swing the house does not have; README and domain say the plan draws "the opened
  angle". · Draw the leaf at `angle`, or document the symbol as the conventional 90° swing (user's
  choice).
- **[MEDIUM/LOW] "Modellstand" hash covers only `bp.geo`.** · `code/export_plans.py:36-42` · Renaming
  a room, moving an anchor or changing `DOORS`/`CUT`/`ROOM_CUT` changes the sheets but not the hash. ·
  Also hash `bp.doors`, `bp.plan_rooms` and the cut constants.
- **[LOW] Room anchor inside a wall → bare `KeyError`** (`regions[None]`). · `code/export_plans.py:426-440`
  · Only the test catches it. · Raise `ValueError` naming the room.
- **[LOW] SVG text not XML-escaped.** · `code/export_plans.py:663-666` · No current name contains
  `&<>`. · `xml.sax.saxutils.escape`.
- **[LOW] Door-record tests thin:** counts plus one door's side; arc sweep direction unchecked. ·
  `tests/test_plans.py:14-33, 198-213` · A swapped side on the other 21 doors would pass. · Loop over all
  records (leaf side, sweep sign).
- **[LOW] `back_door` records hard-coded directions** `closed=(0,-1), open=(1,0)`. ·
  `code/house_core.py:547` · Stale if its frame changes. · Derive from `P`.
- **[LOW] CPU-time assertion (≤ 30 s)** may flake on a loaded machine. · `tests/test_plans.py:190-192`.
- **[LOW] `build_ofen()` / `build_desk()` don't clear `DOORS`.** · `code/house_core.py:2226-2240` ·
  Harmless now (no doors in their Blueprint).
- **[LOW, fragility] EG cut at exactly 1.80 m touches vertices** of `EG_Treppe` and an `EG_Waende` box.
  Stable ±0.1 mm today. · Optional test: no vertex within 1 mm of `CUT`/`ROOM_CUT`.

## Standards

Hard:
- **ADR-001-XEWL (model facts only in the core):** the backend classifies model objects by name —
  `export_plans.py:182` (`_Waende`, `EG_Anbau`, `Putz`), `:187` (`Balkone`, `Boden`, `Decke`), `:208`
  (`Gelaende`, `Kiesel`, `Kiesstreifen`), `:347` (`_Fenster_Tueren`). Fix: core constants/flags (like
  `BEDS` / `NO_GRASS`).
- **Plan step 1** ("build()/build_*() clear it"): `build_ofen` / `build_desk` don't clear `DOORS`.

Drive-bys: none. Unused output: `section()` returns `"h"`, nobody reads it; `DOORS.z` only read by
tests.

Judgement calls (smells): Duplicated Code (45° tick path `:521`/`:655`, `<text stroke="none"` replace
`:647`/`:658`); Repeated Switches (side dispatch `SIDES` `:471`, lookups `:477`/`:514`, `VIEWS`); Data
Clumps (5-tuples in `room_regions` `:337`); Mysterious Name (`CUT` = heights vs `section()["cut"]` =
parts); Long Function (`room_regions` ~80 lines, `project` ~60); test hack `class Out(type(Path()))` with
`cpu` (`tests/test_plans.py:72`); 4 lines > 120 chars.

## Spec

- **Implemented but wrong — west cladding missing from both Grundrisse.** `Verschalung_West`
  (z 0.25–7.55) lives in collection `Dach`; `plan_objects` (`export_plans.py:185-187`) keeps only the
  storey and `Balkone`, so both cut planes (EG 1.80, OG 4.25) pass through it and nothing is drawn.
  Domain: "Parts that the cut plane passes through are drawn as cut." Untested. (The Spec reviewer
  also named `Verschalung_Ost`; it starts at z 4.90, above the OG cut, so it is correctly absent.)
- **Implemented but wrong — door angle** (see Defects, MEDIUM): domain "the plan draws the leaf and a
  quarter arc from them (hinge, width, side, angle)"; `angle` is recorded, ignored.
- **Partial — elevation clipping:** architecture "An elevation … is clipped to the house plus a margin";
  `elevation_body` (`:630-636`) fits all non-furniture, non-garden items, no clip.
- **Test-first gaps:** steps 6 and 9 (tick marks, text rotation on vertical sides, "no label overlaps a
  wall") have no asserting test; they rest on a Look that left no PNGs.
- **No `DECISIONS.md` entries** for apply-time choices (determinism/currency tests marked slow, the
  "Bibliothek" merge).
- Shortcut (accepted): Bad area test hard-codes the shaft dimensions from `bad.py`.
- ADRs: no contradiction; ADR-001-XEWL's text still names only two backends — update at archive.
- Verify runs: plans/tour/gltf 55 passed, parity 3 passed. Not run: rsvg "Look" checks, Playwright,
  `check.sh full`.

## Verdict

- Defects: 9 findings, worst MEDIUM (door swing angle ignored).
- Standards: 2 hard (ADR-001-XEWL name classification in the backend; `DOORS` not cleared in two
  builders), plus smells.
- Spec: 5 findings, worst "implemented but wrong" (cladding missing from both Grundrisse).

The user chose "fix now" (2026-11-11). The fixes are plan steps 13–21, each test-first:

- **Fixed:**
  - ADR-001-XEWL: a `PLAN` table of object classes in the core; the exporter names no model object (a test pins it).
  - West cladding cut in both Grundrisse.
  - Conventional 90° door symbol (the user's choice): the leaves as built are left out of section and projection via `DOORS` `leaf` boxes (with the lever handles), and `angle` is dropped.
  - All 22 door records are checked (leaf side, arc sweep); `back_door` takes its directions from `P`.
  - The "Modellstand" hash covers doors, rooms, `PLAN` and the cut heights.
  - A misplaced room anchor raises `ValueError` naming the room; SVG text is escaped; `build_ofen`/`build_desk` clear `DOORS`.
  - New test: "no room label overlaps a wall".
  - Elevation text in `architecture.md` matches the code (the user's choice); README, `domain.md`, `CLAUDE.md` updated; `plans/` re-exported.
- **Accepted as is:**
  - The CPU-time budget: chosen deliberately at apply.
  - The smells: judgement calls, no defect.
  - The unused `"h"` / `DOORS.z`: harmless.
  - The cut at exactly 1.80 touching vertices: stable ±0.1 mm.
  - The Bad shaft dimensions hard-coded in the test.
  - ADR-001-XEWL's text naming two backends: archive updates it.
- **Open:** the final check (`check.sh full`) was deferred by the user to the end of the whole procedure. The baseline before the fixes had 2 Playwright reds unrelated to this change: `nav.spec.js:99` (Ganzes Haus Darstellung) and `tour.spec.js:132` (14.97 fps < 15).
