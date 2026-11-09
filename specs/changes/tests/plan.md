---
feature: tests
title: "Plan: quick checks and a browser view of every change"
status: applied
order: 4
created: 2026-11-09
edited: 2026-11-09
---
# Plan: quick checks and a browser view of every change

**Blocked in this clone until step 1 is done:** today `python3` (Homebrew 3.15) has no pytest,
`web/node_modules` is missing, and the server on 5377 runs from `~/git/frechen_blender`.

Baseline right after step 1 (the last time with the old rules): `.venv/bin/python -m pytest -q`
and `cd web && npm test && npx playwright test`, durations logged to `tmp/` (2026-11-09: pytest
22 s, Playwright 6.9 min). Baseline counts "no new failures" (frame-rate test: step 2).

## Steps

- [x] [config] Environment for this clone: `requirements-dev.txt` (pytest pinned, e.g.
  `pytest==9.0.2`), `.venv/` in `.gitignore`, `python3 -m venv .venv && .venv/bin/pip install -r
  requirements-dev.txt`, `cd web && npm install`, the one dev server on 5377 started from this
  clone (only with the user's OK to stop the other clone's server)
  - Test first: none — environment set-up
  - Verify: `.venv/bin/python -m pytest --version && grep -q "^\.venv/" .gitignore && (cd web &&
    npx vitest --version) && lsof -a -p "$(lsof -tiTCP:5377 -sTCP:LISTEN)" -d cwd | grep -q
    frechen_blender2/web` → exit 0
- [x] [docs] Bug file `specs/bugs/tour-fps-below-15.md` (`priority: low`, `areas: [ui]`): "the tour
  draws at most ~30 frames per second" got 13.98 fps on 2026-11-08 (needs > 15)
  - Test first: none — bug record
  - Verify: `test -f specs/bugs/tour-fps-below-15.md && grep -q "13.98" specs/bugs/tour-fps-below-15.md`
    → exit 0
- [x] [config] pytest marker `slow`: `pytest.ini` registers it (`--strict-markers`), both tests in
  `tests/test_blender_parity.py` carry `@pytest.mark.slow`
  - Test first: none — test configuration; checked by collection
  - Verify: `test "$(.venv/bin/python -m pytest -q -m 'not slow' --collect-only | grep -c
    blender_parity)" = 0 && test "$(.venv/bin/python -m pytest -q --collect-only | grep -c
    blender_parity)" = 2 && .venv/bin/python -m pytest -q` → exit 0 (green when ticked, 09:50; the
    parity test is red since 09:51 while `specs/bugs/blender-scripts-import-other-clone.md` is open)
- [x] [python] `code/show.py` › `bbox()` and `view()`: frame named objects (outside → nearest facade,
  20° up, `cut=all`; inside → from above ~55° SE, `cut=eg` / `noroof` by storey; `p=4`; `--from`
  override)
  - Test first: `tests/test_show.py` › `test_front_door_is_seen_from_the_east` (`EG_Haustuer`: camera
    east of `W_OUT`, `cut=all`, every bbox corner inside the 28° × 16:9 frustum),
    `test_inside_object_cuts_the_storeys_above` (`EG_Tisch`: `cut=eg`, camera above the box;
    an `OG_` object: `cut=noroof`), `test_from_overrides_the_side` — fail today: no `show.py`
  - Verify: `.venv/bin/python -m pytest -q tests/test_show.py && .venv/bin/python -m pytest -q -m
    "not slow"` → green
- [x] [python] `show.py` › `url()` (house and sub-model pages) and the CLI: refuses (exit 2, names the
  owning path) when the listener on 5377 is not this repo's `web/`, else `open`s the URL; `--print`
  only prints
  - Test first: `tests/test_show.py` › `test_url_matches_the_viewer_format` (keys and order as
    `main.js` writes them, 3 decimals; `--page ofen` gives `ofen.html?cam=&at=&look=`) and
    `test_server_owner_is_checked` (pure `server_is_ours(lsof_text, repo)` on captured `lsof`
    outputs for this repo and for `~/git/frechen_blender`) — fail today: no `url` / `server_is_ours`
  - Verify: `.venv/bin/python -m pytest -q tests/test_show.py` → green; `.venv/bin/python
    code/show.py EG_Haustuer --print` prints a `http://localhost:5377/?cam=…` URL
- [x] [web] `web/shot.js <url> <png>`: one headless screenshot at 1× after the first rendered frame
  (`__fl` / `__ofen` / `__desk` ready), GPU flags as in `playwright.config.js`
  - Test first: `web/e2e/shot.spec.js` › "shot.js writes a screenshot of the URL" (runs the script on
    the `show.py --print` URL of `EG_Haustuer`; the PNG exists, 1280×720, not one flat colour) —
    fails today: no `shot.js`
  - Verify: `cd web && npx playwright test e2e/shot.spec.js` → green; read
    `tmp/web/shot-haustuer.png` at 1×: the front door fills a good part of the picture
- [x] [web] `@eye`: "stills along the Rundgang (for the eye)" tagged `@eye`, excluded by
  `grepInvert: /@eye/` in `playwright.config.js` (`npx playwright test --grep @eye` runs it; user's
  OK 2026-11-09)
  - Test first: existing e2e suite green before and after, except the known frame-rate bug
    (refactor of the suite's selection)
  - Verify: `cd web && npx playwright test --list | grep -c "for the eye"` → `0`;
    `npx playwright test --grep @eye` → green
- [x] [config] `scripts/check.sh quick|full`: runs the tier with `.venv/bin/python`, prints seconds
  per part and the total, tees to `tmp/check-<ts>.log`, warns when quick > 60 s, exits non-zero on
  any failure
  - Test first: none — shell wrapper; its parts are the suites themselves
  - Verify: `bash scripts/check.sh quick` → exit 0, table printed, total ≤ 60 s;
    `bash scripts/check.sh full` → only the known bugs may fail (frame rate; parity while
    `specs/bugs/blender-scripts-import-other-clone.md` is open), Playwright part ≤ ~7 min (budget
    raised from 5 min with the user's OK 2026-11-09: measured 389 s)
- [x] [docs] Workflow rules:
  - `.claude/skills/spec/reference/project.md`: defines the **per-step check** (= `check.sh quick`
    + the step's own test + Show) and the **final check** (= Blender rebuild/save/still if the
    Blender output changed, then `check.sh full`); per-kind verify; commands with `.venv/bin/python`
  - spec plugin texts made generic: `reference/plan.md` (Verify column, cycle step 4: "per-step
    check"), `skills/apply/SKILL.md` (per step: per-step check + Show, new tab per visible step,
    links in the summary; final check once before `applied`), `skills/tweak/SKILL.md` (per-step
    check + Show), `skills/archive/SKILL.md` (final check)
  - `CLAUDE.md`: Tests (tiers, `.venv`, `check.sh`, `show.py`, `shot.js`, `@eye`); Working rules
    ("Verify before claiming done" = quick check + Show; full check at end of apply / archive; web
    rule: a `shot.js` of the Show URL; `show.py` refuses another clone's server)
  - `README.md` › Tests (German): `.venv`, `check.sh quick|full`, `show.py`
  - Test first: none — documentation only
  - Verify: `grep -q "check.sh quick" CLAUDE.md && grep -q "show.py" CLAUDE.md && grep -q
    "final check" .claude/skills/spec/skills/apply/SKILL.md && ! grep -q "full relevant suite"
    .claude/skills/spec/skills/apply/SKILL.md && grep -q "check.sh quick"
    .claude/skills/spec/reference/project.md && grep -q "show.py" README.md` → exit 0

### Review fixes (`review.md`, 2026-11-09)

- [x] [python] `show.num()` rounds ties like JS `toFixed` (half away from zero)
  - Test first: `tests/test_show.py` › `test_url_matches_the_viewer_format` gains `0.0625` →
    `0.063` and `-0.0625` → `-0.063` — fails today: Python rounds half-even (`0.062`)
  - Verify: `.venv/bin/python -m pytest -q tests/test_show.py && bash scripts/check.sh quick` → green
- [x] [python] `show.py --p` only for the house page: with `--page ofen|desk|bad` it exits 2 with a
  message (the sub-model URL has no stage)
  - Test first: `tests/test_show.py` › `test_stage_only_on_the_house_page` (`show.main(["--page",
    "bad", "--p", "2", "--print"])` → `SystemExit` code 2) — fails today: prints a URL, returns 0
  - Verify: `.venv/bin/python -m pytest -q tests/test_show.py && bash scripts/check.sh quick` → green
- [x] [web] `shot.js` waits for the desk's two screen textures (`__desk.textures() === 2`, as
  `desk.spec.js` does) before the screenshot
  - Test first: none — a load race that can't be made to fail reliably; checked by the shot
  - Verify: `cd web && node shot.js "$(../.venv/bin/python ../code/show.py --page desk --print)"
    ../tmp/web/shot-desk.png` → exit 0; read the PNG at 1×: both monitors show their screenshots
    (needs this clone's dev server on 5377)
- [x] [docs] Docs and records: README › Tests names `--at x,y,z` and `--p`; step 3's Verify notes
  the parity bug; `tour-fps-below-15.md` cites `tour.spec.js:138`; `frontmatter.md` gains the area
  `blender` (build scripts, Blender output) and `blender-scripts-import-other-clone.md` uses it
  - Test first: none — documentation only
  - Verify: `grep -q -- "--at x,y,z" README.md && grep -q "tour.spec.js:138"
    specs/bugs/tour-fps-below-15.md && grep -q "areas: \[blender\]"
    specs/bugs/blender-scripts-import-other-clone.md && grep -q "\`blender\`"
    .claude/skills/spec/reference/frontmatter.md` → exit 0

System docs are updated at `/spec:archive`.
