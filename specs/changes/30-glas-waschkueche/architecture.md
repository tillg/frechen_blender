---
feature: 30-glas-waschkueche
title: "Architecture: glazed top metre in the Bad / Waschküche partition"
status: applied
order: 3
created: 2026-11-16
edited: 2026-11-16
---
# Architecture: glazed top metre in the Bad / Waschküche partition

## Approach

`code/elternbad.py` owns the partition (the room's north wall) and defines the Oberlicht once: `OBERLICHT =
(a, b)` (x 5.69 .. 8.49), the sill `SILL` (1.20, exists), the mullions `PFOSTEN` (x 6.49 = the shower glass line,
7.49) and a builder `oberlicht(c, dx, dy, z0, z1)`. Both callers cut the opening with a `wall()` kind `I` op
(`interior(..., ops=[(a, b, z0 + SILL, z1, "I")])`, one random draw as before) and call the builder:
`house_core.build_og()` and `elternbad.waende()` (sub-model). The builder puts a pine lining (`Innentuer`) of the
full wall depth into the opening (sill and jambs 5 cm, a 7 cm head board under the ceiling, two 6 cm mullions),
glazing beads 2 × 2 cm both sides of each pane and `Milchglas` 8 mm in the wall's middle, all in `<c>_Innentueren`
with one `rnd` from an own `random.Random(30)`. Not `<c>_Fenster_Tueren`: the plans' room regions (cut at 2.15)
skip frames, so Bad and Waschküche would merge; as a built-in the head board, cut there, parts them. The four Waschküche lamps over the table get a fifth entry (height
`waschkueche.LAMPE_H` = 1.10: lamp top 1.185, shade rim 23 cm over the table).

```mermaid
flowchart LR
    E[elternbad.py: OBERLICHT, PFOSTEN, oberlicht()] --> O[house_core.build_og: partition + oberlicht]
    E --> W[elternbad.waende: sub-model partition + oberlicht]
    K[waschkueche.LAMPE_H] --> L[house_core.WANDLAMPEN_OG]
    O --> G[export_gltf / export_plans]
```

## Impact

- **Build scripts:** `elternbad.py` (constants, `oberlicht()`, `waende()`), `house_core.build_og()` (partition),
  `WANDLAMPEN_OG` (four heights), `waschkueche.py` (`LAMPE_H`). Registries: none (`OPENINGS` only for exterior).
- **Materials:** none new (`Innentuer`, `Milchglas`).
- **Garden / film:** none; route unchanged (clearance test added).
- **Web viewer:** none (the .glb carries it).
- **Render / output:** plan sheets regenerated (the OG cut at 1.55 now cuts the Oberlicht); Blender dormant.

## Key decisions

| Decision | Alternatives considered | Why |
|---|---|---|
| Dedicated builder in `elternbad.py`, opening by kind `I` | `wall()` kind `W` | `W` builds larch sashes with glazing bars (an exterior window); an interior fixed light is a lining + glass. |
| Full-depth pine lining, mullion on the shower glass line | frame only in the wall's middle | The shower pane ends on the wall face; a recessed frame would leave it ending in the air. |
| `Milchglas` | clear `Glas` | Privacy for the Bad (showers, toilet) seen from the Waschküche at eye height; satin glass still passes the light. |
| 10 cm piers to the side walls | glass corner to corner | Clean plaster corners; 2.80 of 3.00 m glazed. |
| Lamps lowered under the sill on the same wall | other walls | West: cupboard + cabin, east: tower + basin, north: door — no free wall; over the table is where the work light belongs. |

No ADR needed.

## Integration points

`house_core.interior()`/`wall()` (kind `I`), `elternbad.waende()`, `WANDLAMPEN_OG`, `tests/test_core.py`
(`test_elternbad_layout`, `test_wandlampen_og_placements`), `tests/test_tour.py`. Obeys ADR-001-XEWL (described
once in the core, used by both callers and all backends).
