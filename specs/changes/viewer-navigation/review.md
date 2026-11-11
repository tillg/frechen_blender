---
feature: viewer-navigation
title: "Review: viewer navigation"
status: applied
order: 5
created: 2026-11-11
edited: 2026-11-11
---
# Review: viewer navigation

**Scope:** `git show 46e5751` (1 commit) · **Reviewed:** 2026-11-11

## Defects

- [HIGH] Malformed URL view params become NaN state and are persisted · `web/src/main.js:173-176`, `:138-145`, `:185`; `web/src/submodel.js` ~163-185 · `?cam=abc`, `?cam=1,2`, `?fov=abc`, `?p=abc` → NaN camera/fov/progress; saveView writes it to `frechenlehen:index:<entry>`, bare `/` restores the broken view on every reload until localStorage is cleared · Fix: validate in one place (cam/at 3 finite numbers, fov finite 10..90, p finite), drop invalid keys before applyView and in initialQuery; viewstate tests for `cam=abc`, `p=abc`.
- [MEDIUM] Route frames written into the URL during a route · `web/src/main.js:143-144` (replaceState before the tour guard) · debounced saveView from onStart's setProgress(4) fires while the route plays; reload opens the route pose with p=4 · Fix: move the tour guard above replaceState.
- [MEDIUM] Beenden restores only the camera, not entry/stage · `web/src/main.js:233-242`, `web/src/tour.js:113-135` · route started from EG/1. Stock leaves model 'haus' + Eingerichtet with the old storey's pose · Fix: restore model and stage in leave(), or document.
- [LOW] Route name duplicated · `web/src/main.js:189` vs `code/tour.py:100` · rename drifts silently · Fix: export the name via `scene.extras`.
- [LOW] Reset cannot forget a saved view for an inside standard spot · `web/src/main.js:141` · latent (all standards are outside/overview today) · Fix: compare with the spot's rounding + fov, or store a home flag.

No security concerns.

## Standards

Hard:
- ADR-001-XEWL: route name typed in the viewer (`main.js:189`), eye-height rule re-derived (`main.js:154` `Z_OG - 0.3`, `Z_OG + 2`; `tour.EYE`/`tour.OG` not exported).
- Domain vocabulary: Darstellung has three names (`level` in `toolbar.js`, `look` in `submodel.js`, `stage`/`progress`/`p` in `main.js`).
- Plan names `viewstate.save`; module exports `write`.

Drive-bys / unused: `camera.updateMatrixWorld()` in `window.__fl.project` (`main.js:316`); unused `set disabled` (`toolbar.js:101`), returned `tools` (`toolbar.js:142`), `get route()` (`tour.js:155`); mid-file import with `# noqa: E402` in `tests/test_tour.py`.

Smells (judgement): Duplicated Code — `saveView` in `main.js:135-150` and `submodel.js:186-195`; `el()` ×3. Shotgun Surgery — entry→cut mapping in 4 places (`toolbar.js:10`, `main.js:125`, `main.js:132`, `ui.js:36`). `switchModel` re-implemented in `onStart`. "Inside" decided two ways (`applyView` vs `goSpot`). Primitive Obsession — SPOTS 6-tuples, `route:`/`spot:` string protocol sliced by index. Fragile `.fl-field:nth-child(3)` (`ui.css:28`). Spot room names duplicated from `ROOM_NAMES`.

## Spec

- Partial/deviating: Standpunkt groups are Außen/Übersicht/Erdgeschoss/1. Stock instead of "Standpunkte … Routen" (proposal.md:24); `ui.js` keeps more than the title (architecture.md:40); SPOTS tuple has an extra `group` field (architecture.md:20).
- Not asked for: bare URL opens the last-used house entry (`frechenlehen:index:last`).
- Test-first gaps: "storage that throws" uses null storage (try/catch never exercised); spots glTF test checks only names + first spot; "Endlos wraps without a jump" compares key table entries, not the camera; spot/extra-route clearance not in pytest (ticked [blender] step has no artifact).
- ADRs: none contradicted beyond the Standards items. Vitest 7/7, pytest test_tour+test_gltf 31 pass; Playwright not run by the reviewer.

## Verdict

- Defects: 5 (worst HIGH: NaN view persisted from malformed URL).
- Standards: 3 hard (worst: ADR-001-XEWL route name / eye-height in the viewer), several smells.
- Spec: 3 deviations, 1 unrequested feature, 4 test-first gaps.
- Fixed before archive (plan.md › Review fixes, test-first): HIGH — `viewstate.cleanView` drops
  malformed view keys from URL and storage; MEDIUM — a playing route writes nothing to the URL;
  MEDIUM — ending a route restores the Darstellung it started from (narrowed: the entry part is
  unreachable from the UI, routes are listed only under Ganzes Haus).
- Accepted as is: the two LOW defects, the Standards items and the Spec test gaps (no runtime risk
  found; candidates for a later tweak).
