---
feature: waschbecken
title: "Proposal: Waschbecken on a chrome stand in all six places"
status: applied
order: 1
created: 2026-11-12
edited: 2026-11-12
---
# Proposal: Waschbecken on a chrome stand in all six places

## What

Every washbasin in the house gets the shape from today's photos (`input/2026-11-12 input/`): a
rectangular ceramic basin with straight sides, a flat rim and a tap deck at the back
(`waschbecken_einzeln.jpeg`: one mixer; `waschbecken_doppelt.jpg`: one long bowl with one
drain and two mixers). Each one stands on the **Waschbeckenständer** from
`waschbecken_staender.png`, a chrome tube frame that is more decoration than support: two front
legs with turned feet, a front rail, two side rails back to the wall ending in balls on wall
rosettes, two short back posts up to the basin and a chrome bottle trap. One core builder makes
all six. It replaces today's four different basins: the rounded `basin()` in the OG Bäder, the
`wc_basin()` on console legs, the Bad Großeltern's Waschtrog and the deep sink on the slate panel
in the OG Flur.

| # | Place (user's words) | In the model | Type | Size w × d (cm) | Today |
|---|---|---|---|---|---|
| 1 | Bei Oma & Opa | Bad Großeltern, east face of the low wall (`bad.py`) | double | 100 × 47 | Waschtrog 100 × 50 |
| 2 | Hinterer Windfang bei der Gästetoilette | EG back hall, Flur east wall (`gaeste_wc.py`) | single | 40 × 28 | hand basin 40 × 28 |
| 3 | Bad im 1. Stock am Ende des Gangs | OG Bad NW (5,57 m²), north wall | double | 120 × 47 | basin 62 × 48 |
| 4 | Unser Bad im 1. Stock | OG Bad S (6,66 m², off the SE bedroom), south wall | double | 100 × 47 | basin 62 × 48 |
| 5 | Gästetoilette | OG WC 2,30 (2,50 m², next to the Hauswirtschaftsraum), east wall | single | 50 × 40 | hand basin 40 × 28 |
| 6 | Im oberen Flur | OG Flur, right of the Waschküche door | single | 60 × 47 | deep sink 60 × 47 |

The user settled the sizes and site 5 on 2026-11-12. The sizes follow the free wall and floor at
each site:

- 1: the low wall is 1.20 m long.
- 2: as small as possible (user, 2026-11-12), so today's footprint 40 × 28 from the agreed
  `gaeste_wc_v3.svg` stays. The Garderobe's open passage lies 9 cm south of the basin. At 50 × 47,
  only 46 cm would stay free to walk in; at 40 × 28, 65 cm stay free, as today.
- 3: the north wall gives 2.26 m.
- 4: there are 1.25 m from the west wall to the window jamb.
- 5: the basin has to fit between the toilet and the door leaf, which stands open at 90°.
- 6: the Flur is wide.

## Why

The family has chosen the basins and the stand. Today the model shows four unrelated designs,
none like the chosen one.

## Scope

- In:
  - one core builder for the basin (single or double, any size) with its stand;
  - the six sites above;
  - the Bad Großeltern and Gäste-WC sub-model pages (they show the new basins and their dimension labels);
  - plan sheets, parity golden, `.blend`, README.
- In: the existing tests that pin the old basins get their basin assertions rewritten.
  - Agreed 2026-11-12, four in `tests/test_core.py`:
    `test_og_flur_waschbecken_right_of_the_waschkueche_door`, `test_wc_fixtures_after_the_photo`,
    the Gäste-WC test and the Bad Großeltern test. Their tile and slate assertions stay. The
    Gäste-WC sizes (14 / 40 / 14, 83 from the hinge jamb) stay too; only the shape assertions
    change. The OG WC mirror position moves with its basin (5.2 → 4.95).
  - Label strings, agreed 2026-11-12: 'Waschtrog 100' in `web/e2e/bad.spec.js` and
    `web/e2e-preview/preview.spec.js`. The Gäste-WC labels ('HWB 40', '83 frei') don't change.
- Out (non-goals):
  - No new sub-model page: the Bad Oma & Opa page shows the double, the Gäste-WC page the single.
  - No new module and no ADR.
  - No change to mirrors, tiles or the Flur's slate panel (see Open questions).
  - No new basin inside the EG Gäste-WC.
  - No nostalgic taps as in the stand photo: the mixers follow the basin photos.
  - The kitchen sink is not part of this change.

## Expected outcome

- In the viewer (stage Eingerichtet), in Blender and on the two sub-model pages, all six places
  show the rectangular basin on the chrome stand at the sizes in the table, with the top at 85 cm.
  Singles have one mixer, doubles two mixers over one bowl with one drain.
- No basin or stand touches a door leaf in any of its states, a toilet, a shower, a window reveal
  or another fixture.
- Every route camera and inside Standpunkt still stays ≥ 0.25 m from all geometry.
- `bash scripts/check.sh full` is green; the plan sheets and the parity golden are regenerated.

## Open questions

- **EG plank pattern:** replacing the old basins reshuffles the oak plank splits of the EG floor
  once (measured; architecture.md › Impact). This is accepted unless you object.
- **Mirrors, tiles, slate panel:** assumed unchanged.
  - The OG Bäder keep a plain mirror above the basin, as wide as the basin.
  - The OG WC keeps its black stepped frame and the back hall its wooden frame.
  - The OG Flur basin stands in front of the existing dark slate panel.
  - Say so if any of them should go or change.
- **Basin height:** 17 cm from the photos' proportions (no catalogue sheet in `input/`); top at
  85 cm everywhere, as today.
