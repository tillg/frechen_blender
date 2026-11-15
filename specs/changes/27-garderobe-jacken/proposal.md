---
feature: 27-garderobe-jacken
title: "Proposal: Garderobe für viele Jacken"
status: applying
order: 1
created: 2026-11-15
edited: 2026-11-15
---
# Proposal: Garderobe für viele Jacken

## What

The Garderobe niche beside the Gäste-WC (issue #27) loses its bench. Instead: on the left wall (the
east wall, seen walking in through the open passage in the north wall, heading south) a wooden
hook board over the whole wall with many iron hooks in two staggered rows and the hat shelf above;
across the back end (south wall) a hanging rod from wall to wall with five coats on hangers; under
the coats a low shoe shelf with two 20 cm levels holding a dozen shoes (6 pairs).

## Why

With many jackets on the hooks nobody can sit on the bench anyway; the family wants room for many
jackets and a place for long coats and shoes.

## Scope

- In: `code/gaeste_wc.py` (`_Garderobe`: no bench, hook board, 23 hooks, hat shelf, rod, shoe
  shelf; new object `_Kleidung`: five coats on hangers, 12 shoes), `EG_Kleidung` in `FURNITURE`,
  new `FL_*` materials for coat fabrics and shoes, tests, the sub-model page's colour map and
  labels, plan sheets regenerated, README/CLAUDE.md.
- Out (non-goals): jackets on the hooks, hats on the shelf; the Wandlampen of the Garderobe stay
  where they are (the coats keep clear of them); the drawing `gaeste_wc_v3.svg` is not redrawn;
  the Rundgang route (it stays ≥ 1.35 m from the niche).

## Expected outcome

The sub-model page and the house show the niche with hooks along the left wall, five coats on a rod
at the back and two shoe levels below them; no part clashes with walls, lamps or the three door
leaves; coat hems stay above the shoe shelf; no other object's geometry or `rnd` changes.
