---
feature: tests
title: "Proposal: quick checks and a browser view of every change"
status: applied
order: 1
created: 2026-11-09
edited: 2026-11-09
---
# Proposal: quick checks and a browser view of every change

## What

Two check tiers instead of "the full suite after every step": a **quick check** (step's own test,
pytest without Blender, Vitest; target ≤ 60 s) after each change, and the **full check** (all
pytest incl. Blender parity, all Playwright projects) once at the end of `/spec:apply`, at
`/spec:archive` and on request. The visual check after a change becomes a **Show**: a new
`code/show.py` computes a viewpoint on the changed objects and opens the user's browser on the dev
server at that URL, so the change is clearly visible; Claude checks the same URL first with one
screenshot (`web/shot.js`). One entry point `scripts/check.sh quick|full` runs and times the tiers.

## Why

The workflow waits on tests. Measured 2026-11-09: pytest 22 s (Blender parity 8 s), Vitest ~3 s,
**Playwright 52 tests 6.9 min** (slowest: "stills along the Rundgang (for the eye)" 66 s,
"Detailmodell is coloured" 35 s, four more > 16 s), plus a Blender rebuild and still per
`[blender]` step. `/spec:apply` runs the full relevant suite after **every** step, so a `[web]`
step costs ≥ 7 min of waiting. What the user actually wants after a change is to look at it
quickly, in the browser, at the right spot.

## Scope

- In:
  - Environment: a repo-local `.venv` (git-ignored) with `requirements-dev.txt` (pytest pinned);
    `check.sh` and the docs use `.venv/bin/python`. `cd web && npm install` in this clone.
  - pytest marker `slow` (Blender parity tests); quick = `-m "not slow"`.
  - `code/show.py` (pure Python): object names (or a point) → view URL (`?cam=&at=&p=&cut=` on the
    house page; `?cam=&at=&look=` on `ofen.html` / `desk.html` / `bad.html`), framing the objects'
    bounding box (outside: nearest facade; inside: from above, storeys above cut away; `--from`
    override); opens it with `open`; refuses when the server on 5377 is another clone's.
  - `web/shot.js <url> <png>`: one headless screenshot of a URL (Claude's own look before the link
    goes to the user).
  - `scripts/check.sh quick|full`: runs the tier, prints the time per part and the total, logs to
    `tmp/check-<ts>.log`, warns when the quick check exceeds 60 s.
  - "Stills along the Rundgang (for the eye)" leaves the default Playwright run (tag `@eye`, run on
    request) — agreed by the user 2026-11-09.
  - The flaky frame-rate test is recorded as a bug in `specs/bugs/`; baselines count "no new
    failures".
  - Workflow rules: `CLAUDE.md`, `README.md` › Tests, `.claude/skills/spec/reference/project.md`
    (defines the per-step and the final check), and the spec plugin texts (`apply`, `tweak`,
    `archive`, `reference/plan.md`) made generic: "per-step check" / "final check" as defined in
    `project.md`.
- Out (non-goals):
  - Rewriting or deleting tests (beyond moving the `@eye` stills out of the default run).
  - Fixing the flaky frame-rate test (bug file only).
  - Upstreaming the generic plugin texts to agents1 (follow-up).
  - CI test jobs (Pages only builds today; unchanged).
  - Blender stills per step for core changes (the browser shows the same core); one still at the
    end of apply when the Blender output changed; per-step stills stay for Blender-only changes.
  - Named views per room (later, if a spot keeps coming up).
  - Parallel Playwright workers; any change to the model or the viewer's rendering.

## Expected outcome

- `bash scripts/check.sh quick` green in ≤ 60 s, printing per-part times.
- `.venv/bin/python code/show.py EG_Haustuer` opens `http://localhost:5377/?cam=…&at=…&p=…&cut=…`
  in the browser with the front door filling a good part of the view; an interior object opens
  with the storeys above cut away.
- After a `[web]` or core step, `/spec:apply` waits ≤ ~1 min, not ≥ 7 min, and a browser tab opens
  on the change.
- `bash scripts/check.sh full` green apart from the known bugs (frame rate; Blender parity while the scripts import the
  other clone's core), Playwright part ~7 min.
