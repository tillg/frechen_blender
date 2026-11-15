---
feature: 34-alternativ-layout-standard
title: "Proposal: Alternativ becomes the EG layout"
status: applied
order: 1
created: 2026-11-15
edited: 2026-11-15
---
# Proposal: Alternativ becomes the EG layout

## What

Issue #34 ("Alternativer Layout Plan soll der normale werden"): the EG variant *Alternativ*
(cabinet C on the Essen's west wall, B's closed board back, the two saloon leaves to the Speis,
the two Wandlampen on B's back) becomes the one and only EG layout. The default layout's own parts
(cabinet C south of B, the 60 cm wall stub to it, the Speis sliding leaf with its rail, the Essen's
two west-wall Wandlampen) are deleted, and with them the whole switch: `VARIANT`,
`default_layout()`, the wall-light layout tags, the Modell entry "Erdgeschoss - Alternativ"
(cutaway `eg_alt`), `?layout=alt`, `FILM_LAYOUT=alt`.

## Why

The family chose the Alternativ. Two layouts cost a switch in core, glTF, viewer (visibility, ink,
lights, door clocks), Show, plans and film, and every later EG issue (#27 Garderobe, #26 Küche hood)
would have to keep both in mind.

## Scope

- In: core (`speis()`, `speis_alt()`, Wandlampen, Blueprint), glTF extras, viewer (`main.js`,
  `toolbar.js`, `lighting.js`, `ink.js`, `slides.js`), `show.py`, `export_plans.py`, the dormant
  Blender scripts' `default_layout()` calls, `web/film.mjs`, tests, plan sheets, README, CLAUDE.md.
  The former Alternativ objects get names without "Alt".
- Out (non-goals): any change to the Alternativ geometry itself; the Rundgang route (it already
  clears the Alternativ's cabinet); the agreed drawing `input/2026-11-09 input/speis_kueche_v6.svg`
  (it shows the old C; left as the record of that agreement); the Blender `.blend` (dormant, #35).

## Expected outcome

- `house_core.build()` has no `EG_Speis_C`, `EG_Speis_Schiebetuer`, `EG_Speis_Waende`,
  `EG_Wandlampen_Essen`, no `EG_Alt_*`; it has `EG_Essen_Schrank`, `EG_Speis_Rueckwand`,
  `EG_Pendeltuer_S`/`_N`; lamps 13, 14 are in `EG_Wandlampen` (69 wall lights instead of 71).
- The Modell drop-down lists Ganzes Haus, Erdgeschoss, 1. Stock; Erdgeschoss shows the new layout
  with its two lamps lit at dusk.
- The plan sheets show cabinet C on the Essen's west wall and the saloon leaves.
- `check.sh full` green.

## Open questions

none — the naming is decided and logged (`DECISIONS.md`).
