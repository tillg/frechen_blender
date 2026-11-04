---
feature: viewer-rundgang
title: "Review: Rundgang in the web viewer"
status: applied
order: 5
created: 2026-11-04
edited: 2026-11-04
---
# Review: Rundgang in the web viewer

**Scope:** working tree, only the change's files and hunks (a parallel agent's uncommitted
changes excluded) · **Reviewed:** 2026-11-04 (steps 1–6; steps 7–10 — closed route, `look_at` paths, cyclic smoothing, loop/speed, the fixes below — are not yet reviewed)

## Defects

- [MEDIUM] Resize while paused keeps a stale fov (`fovFor` only in `apply()`) · `web/src/tour.js`,
  `main.js` resize · wrong crop until next play/seek · re-apply on resize while the tour is on.
- [MEDIUM] Sun toggle while paused skews the sun: `createLighting` gets the live `controls.target`,
  which the pause moves into the house · `main.js`, `lighting.js` · pass a fixed copy of the target.
- [LOW-MEDIUM] Cutaway buttons stay live during the tour ("Nur EG" while in the OG) · disable them.
- [LOW] Drag momentum survives pause/resume and Beenden · reset damping before resume/leave.
- [LOW] Time step not clamped (negative on start, jump after a background tab) · clamp dt.
- [LOW] Beenden restores only the camera (stage/cutaway stay) · document it.
- [LOW] `UPDATE_GOLDEN` over the whole suite also rewrites `tour.json` · own variable.
- [LOW] Viewer breaks if the .glb lacks `extras.tour` · accepted: `npm run blueprint` always runs first.
- [LOW] `fovFor` test repeats its formula; "view turned" e2e check is a screenshot diff · use known
  numbers / camera direction.

## Standards

No hard violations. Judgement calls: `yup` duplicated in `tour.js` and `main.js`; the 36 mm sensor
and the 90° door angle repeated in the viewer; "frames" means smoothed keys in the viewer but raw
frames in `tour.build_frames()`; magic `setProgress(4)`; tour extras gated by `if bp.garden:`;
`ui.js` edited despite the architecture decision "tour.js builds its own button and bar"; stale
3480 in proposal/architecture.

## Spec

All six steps present with tests; refactor proven bit-identical (3693 frames). Drift: proposal
says 3480 frames / 139 s, architecture "1 m ahead" (code: 5 cm), "Beenden restores the previous
view" vs. camera-only restore, `ui.js` edit. No ADR contradicted.

## Verdict

Defects 9 (worst MEDIUM) · Standards 0 hard, 8 judgement calls · Spec 4 drifts. Fixed in steps 7–10
together with the user's follow-up (slower playback, loop, closed route): both MEDIUMs, cutaway
during tour, damping, dt clamp, own golden variable, test strength, spec drift. Accepted: missing
`extras.tour` guard, `yup` duplication (one line), sensor/door constants in the viewer (they
describe the film camera, not the house).
