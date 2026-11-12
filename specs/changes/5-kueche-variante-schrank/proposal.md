---
feature: 5-kueche-variante-schrank
title: "Proposal: Küche – Variante mit Schrank an der hinteren Wand"
status: applied
order: 1
created: 2026-11-12
edited: 2026-11-12
---
# Proposal: Küche – Variante mit Schrank an der hinteren Wand

## What

A second EG layout, the **Alternativ** variant (issue #5), shown in the viewer's Modell drop-down as
**"Erdgeschoss - Alternativ"**; today's layout stays the default everywhere else. In the variant:

- the blue cabinet **C** (Mallnitz fronts, RAL 5014, 60 deep, to the ceiling) leaves the Speis and
  stands against the Essen's **west wall** (x 2.772, towards the annex with Elektro- and
  Maschinenraum), over its full width: from the south wall (y 0.415) to the back of shelf B
  (y 3.732), about 3.32 m;
- the Speis is closed towards the Essen by **shelf B** alone; from the Essen one sees B's back
  (a closed back panel, new);
- the Speis/Küche wall (x 5.24–5.49) is shortened by C's depth: it ends flush with B's back at
  y 3.732 instead of 3.13;
- the Speis **sliding leaf** and its rail go; the opening Küche → Speis (y 4.33–5.249) gets a
  **saloon door**: two wooden leaves, no handle, swinging both ways (like a Western saloon).

## Why

The family wants to try the cabinet on the back wall of the Essen (more room at the Speis, a quiet
wall of cupboards behind the table) without throwing away the agreed layout
(`input/2026-11-09 input/speis_kueche_v6.svg`). Both must be viewable side by side.

## Scope

- In: the variant geometry in the core (cabinet C on the west wall, B's back panel, shorter wall,
  saloon door); a variant flag through Blueprint → glTF extras → viewer; the Modell entry
  "Erdgeschoss - Alternativ" (EG cutaway with the variant's objects instead of the default's) with
  its URL value; the saloon leaves swinging in the viewer like the other animated doors.
- Out (non-goals): Blender scene, film and Rundgang (they keep the default layout); plan sheets
  (`plans/` stays the default; a variant sheet can follow on request); the Küche sub-model page
  (`kueche.html`); the 1. Stock and Ganzes Haus entries (default layout); Standpunkte of their own
  for the variant (the Erdgeschoss ones are reused).

## Expected outcome

- `Modell` lists "Erdgeschoss - Alternativ" right after "Erdgeschoss"; choosing it shows the EG
  with C on the west wall, B's back towards the Essen, the shortened wall and the two saloon
  leaves; "Erdgeschoss" and every other entry look exactly as today.
- The URL keeps the choice (reload → same entry).
- Blender build, film, Rundgang golden and plan sheets unchanged (parity golden, tour golden,
  `plans/` byte-identical).

## Settled

- Saloon leaves: **half height** (user, 2026-11-12): bottom ≈ 0.35 m, top ≈ 1.65 m, slightly
  arched top edge, framed with vertical slats, in the interior doors' pine (`Innentuer`); built
  **closed**, swung open and shut by the viewer.
- Cabinet C on the west wall: six columns of ≈ 55 cm (pairs with cup pulls where they meet, as
  today), same heights (top door, door over the upper half, three drawers) — assumption.
- Existing tests that name `EG_Speis` for C / the sliding leaf, and the pinned Modell list in
  `nav.spec.js`, may be adapted to the new object names / entry (user, 2026-11-12).
