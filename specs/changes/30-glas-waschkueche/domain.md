---
feature: 30-glas-waschkueche
title: "Domain: glazed top metre in the Bad / Waschküche partition"
status: proposed
order: 2
created: 2026-11-16
edited: 2026-11-16
---
# Domain: glazed top metre in the Bad / Waschküche partition

## Concepts

**Oberlicht** (interior clerestory): a fixed glazed band at the top of an interior wall, here in the partition
between the Bad Nadine & Till and the Waschküche: sill 1.20, up to the ceiling, satin glass (Milchglas) so the
Bad's daylight reaches the windowless Waschküche without a view into the Bad.

```mermaid
erDiagram
    PARTITION ||--|| OBERLICHT : "top metre"
    OBERLICHT ||--|{ PANE : "three, between two mullions"
    SHOWER_PANE }o--|| OBERLICHT : "ends on mullion 1"
```

## Vocabulary

| Term | Meaning |
|---|---|
| Oberlicht | The glazed band at the top of the Bad / Waschküche partition (sill 1.20 to the ceiling). |
| Pfosten | A mullion of the Oberlicht; the first stands on the shower glass line (x 6.49). |
