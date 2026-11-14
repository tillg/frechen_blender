---
feature: 22-lampen-eg
title: "Domain: Lampen im EG"
status: applying
order: 2
created: 2026-11-14
edited: 2026-11-14
---
# Domain: Lampen im EG

## Concepts

**Wandlampe** (system term from #19): now also in the EG, over the Ofen bed (instead of the reading
lamp) and, in the Essen, tied to the layout: two lamps belong to the default layout, two to the
variant Alternativ, like the variant's furniture.

**Haubenspots**: four small spots built into a strip under the Küche hood's back edge, lit at dusk.

**Fill light** (ROOM_LIGHTS): only the Speis keeps one; every other room is lit by its lamps.

```mermaid
erDiagram
    ROOM ||--o{ WANDLAMPE : "on its walls"
    WANDLAMPE }o--o| LAYOUT : "default or Alternativ (Essen only)"
    WANDLAMPE ||--|| WALL_LIGHT : "lit at dusk"
    HAUBE ||--|{ HAUBENSPOT : "4 in a strip"
```

## Vocabulary

| Term | Meaning |
|---|---|
| Haubenspots | The four spots in a strip at the back edge of the Küche hood's underside. |
