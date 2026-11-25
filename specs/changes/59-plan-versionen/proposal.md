---
feature: 59-plan-versionen
title: "Proposal: Planversionen im Viewer"
status: applied
order: 1
created: 2026-11-25
edited: 2026-11-25
---
# Proposal: Planversionen im Viewer

## What

Frozen states of the plan ("Versionen", each a date and a name, e.g. "2026-11-25 Nach Vincent &
Silvia-Ideen") can be chosen in the house viewer from a new drop-down "Version"; "Aktuell" (the
live model) stays the default. Each version shows its own house (3D, Standpunkte, Rundgang, Vorlagen
markers) and its own six plan sheets, and every version is in the offline store on the iPad.

## Why

The plan changes with every round of ideas (issue #59). To compare or show an earlier state today
one has to dig in git; on the iPad, offline, there is no way at all.

## Scope

- In:
  - a version = a snapshot of the sources (`code/` + `plans/`) taken with `just version "<name>"`,
    committed as `versionen/<id>.tar.gz` and listed in `versionen/versionen.json` (id = date, name);
  - the build (`npm run blueprint`, so also CI) turns every snapshot into `v/<id>/frechenlehen.glb`
    (with the snapshot's own exporter) and `v/<id>/plans/*.svg`, cached per snapshot;
  - the drop-down "Version" on the house page, the choice in the URL (`?v=<id>`), the title naming a
    frozen version;
  - the offline worker keeps each frozen version in a cache of its own that survives deploys;
  - the update button is renamed "Update laden" (the word "Version" now means a plan version);
  - a test that the viewer loads every listed version;
  - the first version: today's state, "2026-11-25 Nach Vincent & Silvia-Ideen".
- Out (non-goals): versions before today (the current viewer cannot load them, spike 2026-11-25);
  parallel variants (branches); versioned sub-models, Fotos & Vorlagen and film (always current);
  a diff between versions; loading versions on demand.

## Expected outcome

- `http://localhost:5377/?v=2026-11-25` shows that version; the drop-down lists "Aktuell" and the
  version; choosing switches, the view (camera) stays.
- The plan sheets of a version come from its snapshot.
- After the first visit of the build, every version opens offline; a later deploy that changes only
  the live model downloads only the live build again (~63 MB), not the versions (~43 MB each).
- `just version "<name>"` adds a version in one command; the compatibility test fails when a viewer
  change breaks a listed version.

Storage on the iPad (settled 2026-11-25): Safari 17+ gives an origin up to 60 % of the disk, a
Home Screen web app the same, and exempts it from the 7-day eviction
(https://webkit.org/blog/14403/updates-to-storage-policy/); ~10 versions (~500 MB) fit.
