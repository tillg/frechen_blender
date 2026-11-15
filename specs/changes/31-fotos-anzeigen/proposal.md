---
feature: 31-fotos-anzeigen
title: "Proposal: Vorlagen — the reference photos by place in the house"
status: applied
order: 1
created: 2026-11-15
edited: 2026-11-15
---
# Proposal: Vorlagen — the reference photos by place in the house

## What

Every picture in `input/` that served as a reference ("Vorlage") is copied, downsized, into
`web/public/vorlagen/<Bereich>/` and shown on a page per area of the house (`vorlagen.html?b=<key>`),
plus an index of all areas. In the house viewer, each area has a clickable marker in its room (e.g.
the Stube: the Ofen photos; the Garderobe / Gäste-WC corner: Garderobe and Toilette Mallnitz) that
opens its page. Elements found all over the house (standard basins, Wandlampe, floors, doors, stair)
get their own page, "Ganzes Haus", reachable from every area page, the index and the house page.

## Why

Issue #31: the photos shaped the model (the green-tiled Mallnitz toilet became our blue-tiled WC, the
Mallnitz Garderobe, the Ofen in the Stube …), but today they are only file names in `input/`. The
user wants to see them where they belong, from the 3D model.

## Scope

- In: the area manifest in the core (`code/vorlagen.py`: area, title, anchor in the house, photos
  with caption); the downsized copies (committed); `vorlagen.html` (index + area pages, also in the
  production build); markers in the house viewer; a link "Fotos & Vorlagen" on the house page;
  README.
- Out (non-goals): markers on the sub-model pages; editing or uploading photos from the page;
  the PDFs and SVG drawings in `input/` (the plan PDFs are in the viewer as plan sheets; the agreed
  drawings' PNG renders are included); any change to the model geometry, plan sheets or Rundgang.

## Expected outcome

- All 55 raster images in `input/` are assigned to exactly one area and copied (pytest).
- Each area page shows its photos with captions, without console errors, in dev and under
  `/frechen_blender/` (Playwright, both projects).
- Standing in the Stube (eye height) a marker is visible; clicking it opens the Stube page with the
  Ofen photo; the same in the Garderobe corner for Garderobe + Toilette Mallnitz (Playwright).
- Markers are hidden in the Rundgang and in the film capture (`?hires=on`).

## Open questions

none — decided unattended, see `DECISIONS.md` (run `run-2026-11-15-1633`).
