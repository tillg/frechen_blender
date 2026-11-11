---
title: "Bug: Darstellung-per-entry nav test flaky since the Schrank im Büro entry"
priority: medium
areas: [ui]
created: 2026-11-11
edited: 2026-11-11
---
# Bug: Darstellung-per-entry nav test flaky since the Schrank im Büro entry

**Where:** `web/e2e/nav.spec.js:100` ("Erdgeschoss and Ganzes Haus remember their own Darstellung;
the bare URL opens the last entry"), `web/src/toolbar.js` (`PAGES`), viewer `main.js` / `ui.js`
(per-entry Darstellung in storage)

## Steps

1. `cd web && npx playwright test e2e/nav.spec.js --project dev -g "remember their own Darstellung"`,
   five times in a row, with the sixth sub-model entry `['regal', 'Schrank im Büro', 'regal.html']`
   in `toolbar.js` `PAGES`.

## Expected

Passes every time: after Ganzes Haus › Gebaut, Erdgeschoss › Massenmodell and a reload, choosing
Ganzes Haus again shows `data-stage = built`.

## Actual

Fails 3 of 5 runs (and in `check.sh full`, 2026-11-11 20:01): `Expected: "built"`,
`Received: "massing"` at `nav.spec.js:111`. With the `regal` entry removed from `PAGES` it passed
4 of 4. The commit before (df18d96, Darstellung › Pläne on Ganzes Haus) also changed `ui.js` /
`main.js`; which of the two triggers the race is not yet known.
