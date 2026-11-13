---
feature: 3-bad-nadine-till
title: "Proposal: Bad Nadine & Till"
status: applying
order: 1
created: 2026-11-13
edited: 2026-11-13
---
# Proposal: Bad Nadine & Till

## What

Issue #3: the OG Bad S of Nadine & Till (room x 5.59..8.59, y 0.40..2.62) is rearranged. The door
to the Schlafzimmer moves to the south end of the east wall, the toilet takes its old place (NE
corner, facing the south window), the corner shower is lengthened east towards it with its entrance
at the west wall, the mirror becomes the Gästebad's wood-framed one with four Wandlampen over it,
and one Wandlampe each goes left of the window and over the cistern. The room becomes a sub-model
of its own (`code/elternbad.py`, `web/elternbad.html`), like the Gästebad.

```
 y 2.62 ┌────────────── north wall ───────────────┬──┐
        │ ║ shower 213 × 98      head ◦   ║  ▣ WC │▒▒│ tiles N + E (WC corner)
        │ ║                               ║  (lamp│▒▒│ toilet axis 8.14, faces south
 y 1.64 │  60 open ┆════ glass 153 ═══════╝ over) │──┘ y 1.66
        │ (exit at                                │
        │  the wall)                              ╪ door 0.65..1.58, hinged south,
        │                                  ┌──────┤ leaf open 90° into the Bad
        │   ┌─basin 100─┐                  │ leaf │
 y 0.40 └───┴───────────┴──[ window ]──────┴──────┘ x 8.59
        5.59  mirror 110      6.84    7.72  lamp 8.155
              4 lamps above
```

## Why

The owners asked for it (issue #3): sitting on the toilet you look out of the window; the shower
gets longer; the bath gets the house's standard Wandlampen (#19) and the Gästebad's mirror.

## Scope

- In:
  - Door: east wall opening 0.65..1.58 (93 wide like today), hinged at the south jamb, opened 90°
    into the Bad (user's choice 2026-11-13; it cannot open flat: hinged north the leaf would sweep
    the toilet, flat south it would cover the window). Its south jamb sits 25 cm off the south wall
    so the leaf with its levers (`DOORS` box from y 0.625) clears the window lamp, which reaches y 0.61.
    The old opening 1.65..2.58 is closed.
  - Toilet: back to the north wall, axis 8.14 (45 cm from the east wall), facing south to the
    window; Taubenblau subway tiles (`wainscot`) on the north wall from the shower glass to the east
    wall and on the east wall from the north wall to the door architrave (user's choice).
  - Shower: stays in the NW corner, y 1.64..2.62, lengthened east to x 7.72 (the window's east
    jamb; 2.13 × 0.98, 20 cm short of the cistern). Reading of "Ausgang an der Wandseite": the
    entrance is the 60 cm gap on the long south edge at the west wall; glass 153 from there to the
    east end and a full glass end panel towards the toilet. Head on the north wall over the glass
    part, away from the entrance.
  - Basin and mirror: Waschbecken doppelt 100 stays on the south wall west of the window, on one
    axis with the mirror, 6.19: 5 cm east of today, so its end stays 15 cm from the window reveal
    (rule of 2026-11-12) and the mirror keeps 5 cm to the west wall. Mirror "genauso wie im Gästebad": the same 10 cm wooden frame, 85 high, bottom
    at 1.17 — but 110 wide, not 140 (the wall span allows 125). Four Wandlampen over it at the
    quarters of its width at `WANDLAMPE_SPIEGEL_H`.
  - Wandlampen: one on the south wall left of the window seen from inside (east of it, centred in
    7.72..8.59), one on the north wall over the cistern; both at `WANDLAMPE_H`. With the four over the
    mirror the OG has 35 Wandlampen (was 29).
  - Sub-model: `code/elternbad.py` (`elternbad_neu(c, x0, y0, z=0, walls=False)`, origin = the
    room's inner SW corner), `house_core.build_elternbad()`, `export_gltf.py --elternbad`,
    `web/elternbad.html` with dimension lines, `show.py --page elternbad`, toolbar entry.
  - Rundgang (user request 2026-11-13): instead of peeking in, it walks through the new door to the
    back (west) wall, turns right until its back is to the wall, pauses, and walks straight out.
  - Shower walls (user request 2026-11-13): limestone slabs to 2.0 on the west and north wall like the
    Bad Großeltern's; the floor already is the same limestone (`BATHS_OG`).
  - Modell drop-down (user request 2026-11-13): the sub-models grouped by storey, `Erdgeschoss` first,
    then `1. Stock`.
  - Blender rebuild, parity golden, tour golden, plan sheets.
- Out (non-goals): swinging the leaf in the viewer; tiles inside the shower; any change to the
  Schlafzimmer beyond the closed old opening.

## Expected outcome

- In the house and on `elternbad.html`: the layout above; the toilet faces the window; no part of
  the leaf (open 90°) touches a lamp, the window reveal, the basin or the toilet; the shower glass
  stays clear of the toilet; the old door is wall.
- The window lamp stands behind the open leaf in every as-built view (the leaf is shown open).
- 35 Wandlampen in the OG; the dusk view lights the Bad.
- The Rundgang walks into the Bad to its west wall, turns right to face the door, pauses, walks out;
  camera ≥ 0.25 m from all geometry.
- The Modell list shows the sub-models under the headings Erdgeschoss and 1. Stock.

## Open questions

none
