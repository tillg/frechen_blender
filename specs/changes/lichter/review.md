---
feature: lichter
title: "Review: lights off by day, only the nearest at dusk"
status: applied
order: 5
created: 2026-11-06
edited: 2026-11-06
---
# Review: lights off by day, only the nearest at dusk

**Scope:** working-tree diff against `HEAD` (4cc6df4, uncommitted: `web/src/lighting.js`,
`web/src/main.js`, `web/src/lighting.test.js`, `web/e2e/stages.spec.js`, `README.md`,
`.claude/skills/film-render/SKILL.md`; memory file outside the repo) · **Reviewed:** 2026-11-06

## Defects

Static review only (tests not rerun by this axis). No CRITICAL or HIGH.

- **[MEDIUM] Prewarm is a single point of failure for startup** · `web/src/main.js:147` · `await lights.prewarm(() => renderer.compileAsync(…))` has no try/catch and runs before `setAnimationLoop`. If `compileAsync` rejects or hangs (WebGL2 fallback, device lost), the loop never starts: blank page, and `__fl.ready` is never set. · Fix: wrap in try/catch (or race a timeout) and start the loop regardless.
- **[MEDIUM] Prewarm costs startup time for a dusk variant that may never be used** · `web/src/lighting.js:73` · The default load is p = 0 (day). The prewarm adds the dusk compile to every page load; the day variant still compiles on the first render. · Fix (if startup matters): prewarm in idle time after the first frame. The e2e "first dusk" timing only logs, so nothing guards it.
- **[MEDIUM] Resize listener is registered after the longer await** · `web/src/main.js:147, 164` · A resize during `compileAsync` is lost: stale `camera.aspect` and renderer size until the next resize. Before this change the gap was only `renderer.init()`. · Fix: register the listener before the awaits.
- **[MEDIUM] Film capture silently degrades without `?hires=on`** · `tmp/threejs_film.mjs:14` (gitignored) · An old capture command without the flag now films the 6 + 2 pool and no grass indoors. Only `SKILL.md` guards against it. · Fix: the script appends `hires=on` if missing, or asserts `__fl.hires === true`.
- **[LOW] The dev-block `renderer.render` runs before `lights.update`** · `web/src/main.js:206` · At p ≥ 2 that first draw uses the pool at its initial sites. It's redrawn by the loop, so it's a wasted render, not a visible error. · Fix: call `update` first, or rely on the loop.
- **[LOW] Dark halo at the cut-off** · `web/src/lighting.js:81-87` · When several sites are about equally far, the last pooled lights all fade toward 0 together (by design: the cut-off fade). · Fix: hysteresis or a wider band (a design change).
- **[LOW] Tests pin constants and site order** · `web/src/lighting.test.js`, `web/e2e/stages.spec.js` · 6, 2, 23, 8, `FADE` 1.0 and the site indices (`[15,3,18,0,5,17]` and others) are hard-coded, so reordering `ROOM_LIGHTS` in the core breaks them. The prewarm unit test uses a fake `compile`. That the prewarm works is guarded only by the tour timing e2e tests.
- **[LOW] `hires` is dropped on the Ofen link** · `web/src/ui.js:31` · Harmless: the Ofen page has no pool.

## Standards

No hard violations: the README is updated, and every hunk traces to a plan step.

- **Drive-by (minor):** `web/src/lighting.js:3` header wording changed ("every OUTSIDE_LIGHTS bulb" → "the OUTSIDE_LIGHTS bulbs"). It is arguably accurate now that fast mode doesn't light every bulb, but it is a reword.
- **Judgement calls (Fowler):**
  - Duplicated Code: base intensities `9` / `14` appear in `setDusk` and in `update`; the spot "1 m below" target appears 3×; the `[x, -z, y]` rounding appears in the e2e and in `main.js`.
  - Data Clumps: `place(sites, lights, base, cam, w)`.
  - Mysterious Name: `d`, `dk`, `w`.
  - Repeated Switches: `hires` checks spread over `lighting.js` and `main.js` (≥ 5).
  - Feature Envy (dev hook only): `__fl.lights`.

## Spec

No missing steps, no scope creep, nothing implemented wrong, no test-first gaps, no ADR contradiction. The unit tests (41) and the docs grep were rerun and pass.

- **Coverage (minor):**
  - The Tag toggle path (`toggleSun` → pool off) is covered only by the `setDusk` unit test.
  - The step 3 test asserts the fade formula and `< 0.3`, not the plan's "≈ 0.16".
  - The step 4 "first dusk" timing is logged, not asserted.
  - That `main.js` awaits the prewarm before the first frame is guarded only by the tour timing e2e tests.

## Verdict

- Defects: 8 findings (4 MEDIUM, 4 LOW); worst: the prewarm has no error handling.
- Standards: 0 hard, 1 minor drive-by, 5 smell judgement calls; worst: duplicated base intensities `9` / `14`.
- Spec: 0 gaps, 4 minor coverage notes; worst: the Tag toggle path has no e2e test.

**Fixed before archive** (user's choice, plan steps 9–11, 2026-11-06):
- prewarm catches a failed compile and the viewer runs on (unit test);
- the resize listener sits before the awaits;
- `tmp/threejs_film.mjs` forces `hires=on` and stops unless `__fl.hires` is true.

After the fixes: unit 42 passed, e2e 48 passed.

**Accepted as is:**
- Prewarm on every load (MEDIUM): the trade-off decided at apply. One compile at load beats a ~0.8 s stall at the first dusk or Rundgang start.
- All LOWs: the extra dev render is redrawn by the loop; the halo is the designed cut-off fade; the pinned site indices are the plan's exact expectations; the Ofen link has no pool.
- The Standards smells and the comment reword: local, readable, and within the touched function.
- The Spec coverage notes: the paths are covered by unit or tour tests.
