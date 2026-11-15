---
feature: 26-haube-induktion
title: "Proposal: the hood over the cooktop, the Wamsler's pipe higher into the wall"
status: proposed
order: 1
created: 2026-11-15
edited: 2026-11-15
---
# Proposal: the hood over the cooktop, the Wamsler's pipe higher into the wall

## What

Issue #26: the steel hood of the old form (`EG_Haube` / `Kueche_Haube`) moves from the Wamsler
on the east wall to the induction cooktop on the Halbinsel. There it hangs from the ceiling as an
island hood, same style (rolled lip, straight skirt, rail, canopy narrowing to a stack into the
ceiling), centred on the cooktop, its lip 65 cm above the cooktop, with the four Haubenspots (#22)
in a strip under it. The Wamsler keeps its flue pipe (black, Ø 12) but it now rises to 1.80 m and
bends into the east wall there, with a wall rosette; nothing else stands above the Wamsler.

## Why

The user wants the extraction over the cooktop where the cooking happens; a wood cooker needs a
flue, not a hood (issue text: „Bei dem Holzofen soll dafür das Ofenrohr vom Ofen weiter oben in die
Wand laufen“).

## Scope

- In: `code/kueche.py` (hood rebuilt over the cooktop, its spots and light), `code/ofen.py`
  (`wamsler()`: pipe bend at 1.80, rosette), tests, plan sheets, README / CLAUDE.md / docstrings.
- Out (non-goals): wall cabinets (there are none), the Abzug (flue box) in the NE corner, the
  agreed drawing `speis_kueche_svg.py` (it does not draw the hood), the Blender backend (dormant).

## Expected outcome

- In the house and on `kueche.html` the hood hangs over the cooktop, centred to < 1 cm, lip at
  1.55 (cooktop 0.905), stack into the ceiling; the Rundgang and every Standpunkt keep ≥ 0.25 m
  from it, the Küche Standpunkt still sees the room.
- Above the Wamsler only its pipe: from the flue collar up to ~1.80, then horizontally into the east
  wall, ending in a rosette on the wall face.
