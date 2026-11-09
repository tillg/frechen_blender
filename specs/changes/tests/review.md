---
feature: tests
title: "Review: quick checks and a browser view of every change"
status: applied
order: 5
created: 2026-11-09
edited: 2026-11-09
---
# Review: quick checks and a browser view of every change

**Scope:** working-tree diff on branch `tests` (uncommitted: 12 modified, 9 untracked paths) ·
**Reviewed:** 2026-11-09

## Defects

- [MEDIUM] Desk Show shots can catch blank monitors · `web/shot.js:12-14` · `__desk.ready` is set
  when the glb has loaded; the screen textures arrive later (`submodel.js` `textures` counter;
  `desk.spec.js:31` waits for `textures() === 2`) · Fix: for `__desk` also wait for
  `textures() === 2`.
- [LOW] `num()` rounds half-even, JS `toFixed` half-up (`0.0625` → `0.062` vs `0.063`) ·
  `code/show.py` `num()` · 1 mm in the URL; the viewer rewrites it · Fix: `Decimal` ROUND_HALF_UP
  + a tie case in `test_url_matches_the_viewer_format`.
- [LOW] `--p` silently ignored on sub-model pages · `code/show.py` `url()`/`main()` · Fix: reject
  `--p` with `--page` ≠ house (or drop `--p`, see Standards).
- [LOW] Storey cut by box-centre height, not by collection · `code/show.py` `view()` · no object is
  cut by its own level today (checked over `bp.geo`); accepted in `DECISIONS.md` 09:55.
- [LOW] `bbox()` uses unturned geometry (PIVOT/TURN objects: `EG_Haustuer`, screen panes) · an
  opened door or turned screen can leave the frame · Fix: document or apply TURN.
- [LOW] Only the first listening pid is checked; missing `lsof` → traceback instead of exit 2 ·
  `code/show.py` `main()`.
- [LOW] `shot.spec.js` asserts little (> 20 colours) and builds paths with `URL.pathname`
  (percent-encodes spaces), hard-codes `.venv` · Fix: non-background fraction, `fileURLToPath`,
  clear error when `.venv` is missing.
- [LOW] `playwright.config.js` argv sniffing for `@eye` (any argument containing it) · accepted in
  `DECISIONS.md` 10:05.
- Dropped on check: "`check.sh` `failed` unset on success" — `scripts/check.sh:35` sets `failed=0`.
- Security: none.

## Standards

Hard:
- `show.py` CLI flags `--p` and `--at` aren't in any plan step; README doesn't mention them
  (`principles.md` §3), CLAUDE.md mentions `--at` only — README and CLAUDE.md disagree. `--p` is an
  untraced drive-by nothing uses.
- `specs/bugs/blender-scripts-import-other-clone.md` `areas: [ui]` misfits (`ui` = layout,
  navigation, rendering; frontmatter.md says add new values there); no plan step creates the file
  (found during apply).
- `web/e2e/shot.spec.js:30` inline `(await import('node:fs')).readFileSync` although `node:fs` is
  imported at l.4; re-implements the decode of `e2e/pixels.js`.

Judgement calls: Duplicated Code (`shot.js` GPU args vs `playwright.config.js`; decode vs
`pixels.js`); Divergent Change (sub-model decided twice: `bp.garden is None` and
`o.page != "house"`); Mysterious Name (`SIDES["top"] = (0, -1)` uncommented); Primitive Obsession
(sides/cuts as bare strings); hidden coupling (argv sniffing in the config); `lambda` assignments in
`test_show.py`; one ~300-char unwrapped line in `project.md`.

## Spec

- (a) Step 1's Verify fails **now**: 5377 belongs to `~/git/frechen_blender` again — handed back
  on that session's request after apply; it passed when ticked. Environment state, not code.
- (a) `DECISIONS.md` `#run-2026-11-09-1015-1`/`-2` are `open` → the archive decisions gate will ask.
- (c) `tour-fps-below-15.md` cites `tour.spec.js:131` (test title); the assertion is l.138.
- (d) `shot.js` waits a fixed 500 ms after ready (not in the plan); `show.py` copies the viewer's FOV
  28/35 and ignores `?fov=` — grey zone of ADR-001-XEWL ("repeat none of its facts"), URL format
  duplication was accepted by the architecture, the FOV copy wasn't spelled out.
- (e) Step 3's Verify ends in the full `pytest -q`, which now fails on the parity bug found during
  apply; only step 8's Verify was amended.
- (b) scope creep: none material. (f) ADR contradictions: none outright.

## Verdict

- Defects: 8 (worst MEDIUM: desk shot before textures).
- Standards: 3 hard (worst: undocumented/untraced `--p`/`--at` CLI flags), 7 judgement calls.
- Spec: 6 (worst: step 3's Verify not amended for the parity bug; step 1's Verify red by
  environment).
- Fixed before archive (plan steps "Review fixes"): `num()` tie rounding (test-first); `--p` with a
  sub-model page exits 2 (test-first); desk texture wait in `shot.js` (desk shot read at 1×: both
  monitors show their screenshots); README names `--at`/`--p` (`--p` and `--at` are in `architecture.md`, so the
  "untraced" part of that Standards finding doesn't hold); step 3's Verify notes the parity bug;
  fps bug cites l.138; bug area `blender` added to `frontmatter.md`.
- Accepted as is: the other LOW defects (box-centre cut, unturned bbox, first pid, `shot.spec.js`
  strength, argv sniffing) and the judgement-call smells; step 1's Verify is red only while another
  clone holds 5377.
