---
title: "Bug: the Blender scripts import the core from the other clone"
priority: medium
areas: [blender]
created: 2026-11-09
edited: 2026-11-09
---
# Bug: the Blender scripts import the core from the other clone

**Where:** `code/build_house.py:11-12` (`PROJECT = "/Users/tgartner/git/frechen_blender"`), the
`sys.path.insert(0, "/Users/tgartner/git/frechen_blender/code")` lines in `garden.py`, `fire.py`,
`paint.py`, `film.py`, `windrose.py`, and `film.py:90` (render output path); test
`tests/test_blender_parity.py` › `test_rebuild_matches_golden_snapshot`.

## Steps

1. In `~/git/frechen_blender2`, leave `code/` unchanged; edit `code/house_core.py` in
   `~/git/frechen_blender` (uncommitted edits there on 2026-11-09).
2. `.venv/bin/python -m pytest -q tests/test_blender_parity.py`

## Expected

The parity test (and every Blender rebuild) uses this clone's `code/`; it passes as it did at
09:40 and 09:50 on 2026-11-09.

## Actual

It fails: `rnd` checksums differ on every object (geometry identical), because Blender builds the
other clone's core. Moving this clone's files has no effect on the result.

## Evidence

`tmp/check-20261109-100105.log` (full check, `objects differ from golden`); the other clone shows
` M code/house_core.py` etc. in `git status`, its `house_core.py` differs from this clone's (new
`import kueche`, Küche door), and its `code/*.py` were modified 09:51–10:08, after the last green
parity run here (09:50).
