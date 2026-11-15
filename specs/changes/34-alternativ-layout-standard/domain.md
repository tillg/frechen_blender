---
feature: 34-alternativ-layout-standard
title: "Domain: Alternativ becomes the EG layout"
status: applied
order: 2
created: 2026-11-15
edited: 2026-11-15
---
# Domain: Alternativ becomes the EG layout

## Concepts

- **Variante** — removed: there is one EG layout again; no object belongs to "one layout only".
- **Speis A / B / C** — changes system term: A and B stay open spruce shelves; B gets a closed back
  of vertical spruce boards towards the Essen; C is the painted cabinet on the Essen's west wall
  from the south wall to B's back (six leaf columns of Mallnitz fronts). The Speis opens to the
  Küche through two half-height saloon leaves without handles (no sliding leaf, no wall stub).
- **Modell** (drop-down) — changes system term: Ganzes Haus, Erdgeschoss, 1. Stock │ the
  sub-models.

```mermaid
erDiagram
    SPEIS ||--|| SHELF_A : "on the Flur wall"
    SPEIS ||--|| SHELF_B : "on the aisle"
    SHELF_B ||--|| BOARD_BACK : "closed towards the Essen"
    ESSEN ||--|| CABINET_C : "on its west wall"
    SPEIS ||--|{ SALOON_LEAF : "two, to the Küche"
```

## Vocabulary

| Term | Meaning |
|---|---|
| Pendeltür | The two half-height saloon leaves between Speis and Küche (`EG_Pendeltuer_S`/`_N`). |
