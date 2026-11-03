# Change log: architect's plans

One chapter per delivery of plans from APPS Architekten. Each chapter lists what changed compared
with the previous plans and what the model does about it. Coordinates are model metres (origin =
outer SW corner, +x east, +y north, see `CLAUDE.md`).

## 2026-11-03: "neuer Entwurf" (plans dated 2026-10-19)

**Source:** `input/2026-11-03 input/` (`Grundriss Frechenlehen EG.pdf`, `… OG.pdf`,
`Ansichten neuer Entwurf.pdf`), compared with `input/processed/` (plans dated 2026-09-18).

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
- OG Bad/HWR partition: the new dimensions (3.25 / 15 / 2.25) are within 3 cm of the model, so it
  was left as it is.

### Not modelled

- Furniture changes in the plans (beds, wardrobes, Büro desk, OG fixtures shown as symbols).
  Furniture is not modelled, apart from the dining table.
- A thin line inside the WC Großeltern (x ≈ 1.75), whose meaning is unclear.

### Changes on request (not from the plans)

| # | Change | Model |
|---|---|---|
| U1 | **Kitchen.** Drawn the same in the old and new plans, but not modelled until now | Sink run on the north wall, a run on the east wall and a peninsula with the cooktop (spruce fronts, granite worktop). The Küche door now opens into the Flur, as drawn (before: into the kitchen, where it would hit the sink run). |
| U2 | **Ofenbett instead of the Kachelofen**, after `ofenbett-1200x800.jpg` | Plastered stove (1.0 × 2.0 m) along the Stube west wall with a rounded top edge and an arched recess at the floor. The fire is visible behind a glass door in the south end, and from the Flur through a fire window in the wall against which the stove's north end stands. Bench along the east face, and a bed on a corner post above the stove. The plans still say "Kachelofen" (footprint 1.5 × 1.5 m). The longer shape follows the photo. |
| U3 | **Bibliothek walls** | Already done: the Büro/Musikraum wall is E3. The X-marked wall at the offener Kamin is demolition in both plan versions and was already open, apart from its two stubs. |

### Other

- The reference plan images (`Referenz` collection) now show the new plans:
  `input/2026-11-03 input/grundriss_eg.png` / `grundriss_og.png`, rendered at 300 dpi.
