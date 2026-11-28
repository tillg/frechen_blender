# #63 Bad Großeltern: Dusche ins WC, Waschbecken an die Nordwand, großes Westfenster

status: applied

## Why
Request 2026-11-28 (after "Nach Telko mit Alex"): the shower moves into the WC room, the Einbauschrank goes; the freed
NW corner takes the basin, the freed west wall a big window, ceiling-high like the west side's OG windows. The user
chose variant B of `input/2026-11-28 input/bad_grosseltern_optionen.svg` with the 198 window.

## What
- `bad.py`: niche 1.30 clear (front wall 22 cm north, `NICHE` 1.42); toilet stays (x 0.482); walk-in shower 90 x 130
  east of it (`XS` 1.148, glass `GL` 75 from the south wall, entry 55, limestone to 2.0, head on the east wall) as in
  `gaeste_wc.py`; Einbauschrank, old shower, low wall, both panes and the Waschbecken doppelt gone; Waschbecken
  einzeln 60 on the north wall at `BX` 0.40 (west of the north window) under a mirror 60 x 85; `WESTFENSTER` (house y
  10.285 .. 12.265, sill 0.75, head the EG ceiling). Global draws burnt (`OLD_DRAWS` 10), own rng draws kept.
- `house_core.py`: the window in the EG west wall (its draws burnt), the bedroom passage from the new niche front,
  lamp 29 over the new mirror, plan label "WC Großeltern" moved, the window's cladding trims draw no rnd.
- `tour.py`: the Bad stop 25 cm further north (clear of the parked leaf), looks at basin + window, then into the niche.

## Defaults chosen
Sliding leaf, north window and the limestone strip along the west wall stay; floor limestone in the whole niche.

## Also in this change: the Stube's Ofen as a triangle (request 2026-11-28)
The firebox stays small, the fire faces the room: `ofen.py` `ofen_neu()` builds a triangle in the corner, legs
`OFEN_A` 1.00 along Flur wall and west wall, the front (141) with the 65 fire door on the hypotenuse at 45°, arch and
legs under it; back door, height, bed and benches (`BANK_AT` 1.205) unchanged. Variant B of
`input/2026-11-28 input/ofen_dreieck_optionen.svg`. Sofa left as it is.
