---
feature: 56-offline-ipad
title: "Plan: viewer offline on the iPad"
status: applied
order: 4
created: 2026-11-20
edited: 2026-11-20
---
# Plan: viewer offline on the iPad

## Steps

- [x] [web] Generate `dist/sw.js` after the build (`web/offline-build.js`): file list of `dist`
  (without `sw.js`; the film is copied after the build) and a content hash, prepended to the
  worker body
  - Test first: `web/src/precache.test.js` › "lists every file but the worker, sorted, as relative
    URLs", "the hash changes when one file's content changes, not with the order", "the worker
    source carries version and list in front of the body" — fails today: no `precache.js`
  - Verify: `cd web && npx vitest run src/precache.test.js` → green
- [x] [web] Service worker, registration on every page of the build, manifest and icon: offline
  reload serves house, sub-model with query, plan sheet, Vorlagen with pictures
  - Test first: `web/e2e-preview/offline.spec.js` › "offline after the first visit" — first load,
    `serviceWorker.ready`, context offline, reload `/frechen_blender/?m=haus`, `bad.html?cam=…`,
    `plans/eg.svg`, `vorlagen.html?b=garderobe` (every picture loads); each response
    `fromServiceWorker()` (the first visit waits for `serviceWorker.controller`: all stored), among them `frechenlehen.glb` and `bad.glb`, the house drawn (ink
    pixels); manifest linked; and › "a new build replaces the stored one; offline then the new
    one" (VERSION rewritten in `dist/sw.js`, `update()`, only the new `frechenlehen-*` cache left,
    offline reload) — fails today: no worker, offline reload fails
  - Verify: `cd web && npx playwright test --project=preview offline.spec.js` → green
- [x] [web] Progress badge: "Offline: n / m" while storing, then "Offline bereit" for 4 s
  - Test first: same spec › "the badge reports the download and Offline bereit, then goes; not on
    the next visit" — fails today: no badge
  - Verify: `cd web && npx playwright test --project=preview offline.spec.js` → green; screenshot
    of the badge read at 1×
- [x] [web] Vorlagen markers open in the same window in a home-screen app
  - Test first: `web/e2e/vorlagen.spec.js` › "as a home-screen app (standalone) the marker opens the
    page in the same window" —
    `navigator.standalone` set by an init script; the marker has no `target` — fails today:
    `target="_blank"`
  - Verify: `cd web && npx playwright test --project=dev vorlagen.spec.js` → green
- [x] [docs] README: how to put the viewer on the iPad (home screen, wait for "Offline bereit"),
  the film stays online, the new files; markers in the same window as a home-screen app
  - Test first: none — docs
  - Verify: `grep -n "Offline bereit" README.md` → matches

Review fixes (review.md, user approved 2026-11-21; the `navigator.standalone` init script in
`vorlagen.spec.js` allowed by the user):

- [x] [web] A failed install says so: the badge shows "Offline nicht möglich" when a file can't be
  stored (404, quota) instead of hanging at "n / m"; the page asks for persistent storage
  - Test first: `web/e2e-preview/offline.spec.js` › "a file that can't be stored stops with a
    message" — `dist/sw.js` rewritten with a missing file in FILES and a new VERSION — fails today:
    the badge stays at "Offline: n / m"
  - Verify: `cd web && npx playwright test --project=preview offline.spec.js` → green
- [x] [web] The build hash covers the worker body; `[` `]` stay unescaped as the browser sends
  them; `apple-mobile-web-app-capable`; badge screenshot to `tmp/web/`; `gone` → `hideTimer`
  - Test first: `web/src/precache.test.js` › "the version changes with the worker body" and
    "encodes a path as the browser requests it" (with `a[1].jpg`) — fails today: hash over the
    files only; `encodeURI` gives `a%5B1%5D.jpg`
  - Verify: `cd web && npx vitest run src/precache.test.js` → green

System docs are updated at `/spec:archive`.
