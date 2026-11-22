---
feature: 56-offline-ipad
title: "Review: viewer offline on the iPad"
status: applied
order: 5
created: 2026-11-20
edited: 2026-11-20
---
# Review: viewer offline on the iPad

**Scope:** working tree on `issue/56-offline-ipad` against `main` (uncommitted) · **Reviewed:** 2026-11-20

## Defects

- [HIGH] After a deploy, a tab opened before it is served from the new cache (`skipWaiting`, new
  worker controls open pages): old JS could read new data. · `web/src/sw.js` · In practice the
  viewer fetches its `.glb` once at start and every other change of page loads new HTML; plan
  sheets are plain SVG. · Accept; the next load is consistent.
- [MEDIUM] A 404 or exceeded quota during install fails silently: the badge stays at "n / m". ·
  `web/src/sw.js`, `web/src/offline.js` · Fix: report the failure in the badge, ask for persistent
  storage (`navigator.storage.persist()`).
- [MEDIUM] `apple-mobile-web-app-capable` missing (older iOS ignores the manifest's `standalone`). ·
  `web/index.html` · Fix: add the meta.
- [MEDIUM] In the home-screen app a Vorlagen marker replaces the house page; back via "3D-Haus"
  loses the camera. · `web/src/markers.js` · Accept (no new window outside the offline store is the
  point).
- [MEDIUM] The build under `localhost:5377/frechen_blender/` gets the worker too (cache-first). ·
  Accept: that is the production build, as on Pages; the tests use fresh contexts.
- [LOW] Update test cannot tell new content from old (same files). · Accept: it checks the store
  switch and offline after it.
- [LOW] Badge screenshot written to `test-results/`, not `tmp/web/`. · Fix.
- [LOW] `encodeURI` escapes `[` `]`, the browser does not. · Fix.
- [LOW] `VERSION` ignores the worker body: a worker-only fix keeps the cache name. · Fix: hash the
  body too.
- [LOW] Security: the origin `tillg.github.io` is shared with the owner's other repos, which could
  write into `frechenlehen-*` caches. · Accept (same owner).

## Standards

- Hard: badge screenshot outside `tmp/` (fixed with the defect above).
- Hard (user decision): `web/e2e/vorlagen.spec.js` fakes `navigator.standalone` by an init script:
  "never mock without permission".
- Judgement: `web/src/precache.js` (Node, `node:crypto`) lives in `src/` for Vitest's
  `src/**/*.test.js`; the build plugins sit in `web/`. Kept.
- Judgement: `gone` in `offline.js` names a timer: rename `hideTimer`.
- Drive-bys: none beyond the plan; `serviceWorkers: 'block'` for the preview project is in
  architecture.md's Impact.

## Spec

- Plan step 2's test text says `serviceWorker.ready`; the test waits for `controller` (stricter). ·
  Fix the plan text.
- Manifest only on `index.html` (architecture.md: start page). Kept.
- `display-mode: standalone` besides `navigator.standalone` in `markers.js`: the standard form of
  the same check. Kept.
- No test asserts that dev pages register no worker. Kept (`import.meta.env.PROD`).

## Verdict

Defects: 10, worst HIGH (accepted, see above). Standards: 4, one needs the user's permission.
Spec: 4, none blocking.

Fixed before archive (plan steps 6 and 7, user approved 2026-11-21): failed install reported in the
badge ("Offline nicht möglich") and persistent storage requested; `apple-mobile-web-app-capable`;
version hash covers the worker body; `[` `]` unescaped; badge screenshot in `tmp/web/`; `gone` →
`hideTimer`; plan text of step 2. The user allowed the `navigator.standalone` init script. Accepted
as is: the HIGH (old tab, new store), marker in the same window, worker on the local build path,
update test on the store switch only, shared origin, `precache.js` in `src/`.
