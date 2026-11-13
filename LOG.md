# Change log: architect's plans

One chapter per delivery of plans from APPS Architekten. Each chapter lists what changed compared
with the previous plans and what the model does about it. Coordinates are model metres (origin =
outer SW corner, +x east, +y north, see `CLAUDE.md`).

## 2026-11-03: "neuer Entwurf" (plans dated 2026-10-19)

**Source:** `input/2026-11-03 input/` (`Grundriss Frechenlehen EG.pdf`, `… OG.pdf`,
`Ansichten neuer Entwurf.pdf`), compared with `input/2026-09-18 input/` (plans dated 2026-09-18).

**Method:** both floor plans are still 1:100, now on A3 instead of A4. I aligned the new plans to
the old ones by image cross-correlation (EG offset 218.4/70.8 pt, OG 212.88/141.36 pt) and then
compared them three ways: as colour overlays (red = old only, green = new only), side by side with
a world-coordinate grid, and as vector fills (filled shapes in world coordinates). The elevations
are now drawn at 1:128, so I measured them against the house width (14.89 m) and the depth
(12.89 m).

**How the new plans read:** pink (RAL-style red) now marks *new construction* everywhere: the
annex, the terrace, the balconies, the Stube glazing, bricked-up openings and the new partitions. A
dashed line with crosses marks demolition. Most pink areas are therefore already in the model and
are not changes between the two plan versions. Only the differences below are.

### EG (ground floor)

| # | Change | Old plans | New plans | Model |
|---|---|---|---|---|
| E1 | **Schuppen replaced by an annex: Elektroraum + Heizung** | Wooden shed inside the SW notch, x 0–2.36, y 0–5.15 | Timber-framed annex (wood hatching, walls 0.20 m), outside x −1.64…2.35, y 0.25…5.13, so it sticks out 1.64 m west of the house. Elektroraum 7.68 m² (north), Heizung 7.68 m² (south), partition at y 2.59–2.79. Outside door in the west wall at y 3.50–4.30. Door Elektroraum → Heizung at x −1.14…−0.34. Flat roof x −1.94…2.36, y −0.07…5.41 (OG plan), top ≈ 2.4 m (elevations) | implemented |
| E2 | **Terrace drawn to size** | Only the label "Terrasse 35,9 m²" | 11.97 × 3.00 m, x 2.35–14.32, y −3.02…0 | south terrace now starts at the annex (x 2.36) and is 3.0 m deep. It still runs on into the east entrance paving, as before. |
| E3 | **Büro and Musikraum become one room** | Partition with a double door between them (x ≈ 11.2) | Partition gone | wall removed |
| E4 | **WC Großeltern: new access** | Door from the Großeltern bedroom (east wall, y 9.02–9.90). Toilet on the south wall at x 1.46, basin on the north wall | Bedroom door closed. Sliding door from the Bad Großeltern in the dividing wall (x 0.56–1.25). Toilet at x ≈ 1.17, basin on the east wall (y ≈ 9.12) | implemented. The leaf is shown slid open to the east, because the plan's arrow points west and there is no room for it there. |
| E5 | **Dining room: south window becomes a French door** | Elevation: window x 6.62–7.92, sill 1.03 m | South elevation: French door with shutters, floor to 2.0 m (same opening) | FD with shutters |
| E6 | **Shaft in the Bad Großeltern** | Nothing in the EG. Both versions already draw a pipe at this spot in the OG (Yoga room) | Square 0.30 × 0.32 m in the NE corner of the Bad, x 2.04–2.34, y 12.12–12.44: probably a vertical installation shaft that now runs down into the EG | plastered box from floor to ceiling, x 2.04–2.36, y 12.12–12.47 |

### OG (upper floor)

| # | Change | Old plans | New plans | Model |
|---|---|---|---|---|
| O1 | **West windows of Yoga room and Bad: fixed lower part** | Floor-length openings at y 11.26–12.23, 8.96–9.95, 6.77–7.76, drawn with door swings | Same openings with no door swing. The elevation splits them at ≈ 1.0 m: fixed glazing below, one tilt-and-turn sash above | new window type "WF" (fixed light under a transom, one sash above) |
| O2 | **WC 2,30: width dimensioned** | No dimensions (model: east wall at x 10.00–10.15) | Dimension chain: 1.20 inner width, 15 cm wall, 2.075 depth | east wall moved to x 9.92–10.07 |

### Roof and elevations

| # | Change | Old plans | New plans | Model |
|---|---|---|---|---|
| R1 | **East gable clad with vertical boards** | Plain gable | Vertical boards in both gables (the west face was already clad in the model, from the photo) | east gable clad with larch boards |
| R2 | **Gable windows partly covered by planks** | Gable windows open, framed by trims | The gable boards run on over all four gable windows (east and west) | slats of board width with 6 cm gaps over the glass, inside the trims |

### Checked and unchanged

- Wall layout (gray wall fills), all exterior openings in EG and OG, both staircases, the positions of the gable
  windows, balconies (sizes and position), roof overhangs, ridge and the whole east, north and
  south elevation apart from E5.
- The EG dimension chain along the south side (31 / 2.05 / 41.5 / 2.47 / 25 / 3.07 / 50 / 5.30 /
  53.5) matches the model.
- Back door (west wall of the small Flur): the new plan has it at y 7.41–8.38, in line with the inner
  door; the old plan had it about 0.6 m further south. The model has had the new position from the start.
- OG Bad/HWR partition: the new dimensions (3.25 / 15 / 2.25) are within 3 cm of the model, so it
  was left as it is.

### Not modelled

- A thin line inside the WC Großeltern (x ≈ 1.75), whose meaning is unclear.
- Musikraum: a small stair with a down arrow (x 6.25–7.25, y 8.9–11.2, in both plan versions) and
  the open fireplace (x 8.67–9.05, y 8.87–9.52). Neither is furniture, and their meaning in the plan is unclear.

### Changes on request (not from the plans)

| # | Change | Model |
|---|---|---|
| U1 | **Kitchen.** Drawn the same in the old and new plans, but not modelled until now | Sink run on the north wall, a run on the east wall and a peninsula with the cooktop (spruce fronts, granite worktop). The Küche door now opens into the Flur, as drawn (before: into the kitchen, where it would hit the sink run). |
| U2 | **Ofenbett instead of the Kachelofen**, after `ofenbett-1200x800.jpg` | Plastered stove (1.0 × 2.0 m) along the Stube west wall with a rounded top edge and an arched recess at the floor. The fire is visible behind a glass door in the south end, and from the Flur through a fire window in the wall against which the stove's north end stands. Bench along the east face, and a bed on a corner post above the stove. The plans still say "Kachelofen" (footprint 1.5 × 1.5 m). The longer shape follows the photo. |
| U4 | **Furniture after the new plans** (viewer: new last stage "Eingerichtet") | EG: double bed with two nightstands (Großeltern), grand piano with bench (Musikraum), desk with chair (Büro), shelving on three walls (Speis); the dining table with 14 chairs also moves into this stage. OG: double bed (Yoga), twin beds with nightstands and a wardrobe (Schlafen NE), double bed, nightstands and wardrobe (Schlafen SW), washer, dryer and a cupboard (HWR), double bed against a headboard unit with a divider, nightstands and a long wardrobe (Schlafen SE). Doors whose opened leaf would hit the furniture now open as the plan draws them: hinge side Yoga, OG SW, OG SE and Speis; 90° instead of flat for Jugend, OG NE, OG SW, OG SE and Speis. The divider in Schlafen SE is 1.20 m high (no height in the plan), so the film camera passes over it. |
| U5 | **Jugend (OG, north, up the stairs and to the right): two bunk beds instead of the plan's double bed** | Along the west and east walls, starting at the door wall. The door wall only has about 1.2 m on each side of the door, too short for a 2 m bed. Ladders are at the north ends, on the room side. |
| U3 | **Bibliothek walls** | Already done: the Büro/Musikraum wall is E3. The X-marked wall at the offener Kamin is demolition in both plan versions and was already open, apart from its two stubs. |
| U6 | **Corner stove after the sketches in `input/2026-11-04 input/` instead of the Ofenbett (U2)** | Same model as the sub-model `ofen.html`, in the Stube's NW corner where the plan draws the "Kachelofen": 1.20 × 1.20 m, free corner cut, fire door in the diagonal face. Bed along the north wall towards the Stube door, long bench along the west wall. Both are 2.00 m in the sketches, shortened to fit: the bed to 1.90 m (it would reach 5 cm into the Stube door opening), the bench to 1.60 m (the west wall only has 1.71 m up to the passage to the Essen). The fire window to the Flur is gone; the new stove's fire door faces the room. |
| U7 | **Bibliothek (Musikraum + Büro)** | Grand piano turned 30° to the left (counter-clockwise from above; first 15°, then "etwas mehr") about its case centre. Desk moved from the NE corner to the north wall between the two french doors, exactly as wide as the wall between them (10.919–12.867, 1.95 m; depth as before). Small workshop stove after `werkstattofen.jpeg` (40 × 40 × 105 cm, sizes estimated from the photo, no flue pipe modelled) on the Flur wall, 10 cm east of the wall stub at the offener Kamin and 10 cm off the wall. |
| U8 | **Schlafen SE (master bedroom, OG)** | The headboard unit with its divider (U4) is now a plain plastered wall, 15 cm thick, right behind the bed head (x 11.48–11.63, y 0.98–3.98), still 1.20 m high. A second workshop stove like the Bibliothek's (U7) stands in the corner between the Bad wall and the WC 2,30 wall, 10 cm off both, turned 45° to face the room (the plan draws a chimney connection there). |
| U9 | **Bibliothek bookcase; outside lamps at dusk** | Old-style bookcase in dark walnut (plinth, three bays, five shelves, stepped cornice), floor to ceiling on the Flur wall opposite the desk, from 1 m east of the workshop stove to the Büro door, filled with books of random size and dark colours. The Büro door now opens as the plan draws it (hinge on the east side) and stands at 90° against the east wall instead of lying flat on the bookcase wall. Viewer: at dusk every wall lamp outside casts a warm spot down and its filament glows (by day it is off). |
| U10 | **West windows of Yoga room and Bad (replaces O1's fixed light)** | No fixed glazing below any more but wall: sill 0.85 m above the OG floor (first 0.95, where the fixed light ended; then 10 cm lower on request), and the window now reaches up to the ceiling (4.90). An ordinary window with two sashes; the window type "WF" is gone. Like before, no iron bars (the cladding bars only the small windows, up to 1 m high). |
| U11 | **Flickering fire; the Ofen fed from the Flur** | The flames are no longer static geometry but a component (code/fire.py, web/src/fire.js): the stoves record their fire beds, and tongues sized to each bed leap, breathe and sway (Blender: F-curve noise plus a flickering light; viewer: animated from the Detailmodell on, on the Ofen page in Gerendert). The Ofen gets a second fire door on its back; in the house it sits flush in the Flur face of the Stube/Flur wall (opening 48 × 56 cm, sill 40), centred on the grey area the plan draws in that wall, with its own fire. |
| U12 | **Ofen bed: no blanket, a ladder** | The red checked blanket on the Ofen bed is removed (the thin cream mattress stays). At the foot end, three rungs run from the wall to the bed's corner post (at a quarter, half and three quarters of the bed height), so one can climb up. The three rim boards now stand straight up and are only 5 cm high (before 11 cm, leaning out 25°). A small reading lamp like the one in ofenbett-1200x800.jpg: the outdoor gooseneck lamp at 40 %, on the wall above the head end (filament lit at dusk in the viewer). |
| U13 | **East OG: balcony doors; the Ofen lamp on** | The three east OG windows onto the long balcony (Schlafen SE y 1.74–2.67 and 4.15–5.04, Schlafen NE y 9.86–10.78) are french doors now (on request; the plan draws them with a slightly different symbol than the other windows, the elevation hides their lower part behind the railing). The lamp above the Ofen bed is switched on: its filament glows by day too, Blender has a small warm light there (collection Innenlicht), the viewer an always-on point light. |

### Other

- The reference plan images (`Referenz` collection) now show the new plans:
  `input/2026-11-03 input/grundriss_eg.png` / `grundriss_og.png`, rendered at 300 dpi.
