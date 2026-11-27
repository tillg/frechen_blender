---
feature: 61-umbauten
title: "Domain: Umbauten EG/OG"
status: applied
order: 2
created: 2026-11-27
edited: 2026-11-27
---
# Domain: Umbauten EG/OG

## Concepts

- **Duschbad am Hintereingang** changes system term *Gäste-WC*: one room with toilet, basin and walk-in shower; the Garderobe there and the Flur basin are gone. Plan room name `Duschbad` (was `WC`); the plan room `Garderobe` is gone.
- **Schuhregal**: open spruce rack in the back hall on the Duschbad's north wall, with shoes (furniture).
- **Flur-Garderobe**: hook board with hat shelf and coats on the big Flur's south wall (house only).
- **WC Großeltern** changes: one room (WC + Einbauschrank) behind one sliding leaf.
- **Muldenlüfter**: the downdraft vent in the Halbinsel's cooktop; the hood is gone.
- **Trockenwand Speis**: a drywall on the Essen side of shelf B.

```mermaid
erDiagram
    BACK_HALL ||--|| DUSCHBAD : "door 76, outward"
    BACK_HALL ||--|| SCHUHREGAL : "on the Duschbad's north wall"
    FLUR ||--|| FLUR_GARDEROBE : "south wall"
    BAD_GROSSELTERN ||--|| WC_GROSSELTERN : "one sliding leaf"
    WC_GROSSELTERN ||--|| EINBAUSCHRANK : contains
```

## Vocabulary

| Term | Meaning |
|---|---|
| Duschbad | the former Gäste-WC by the back hall: WC, basin, shower |
| Muldenlüfter | downdraft extractor in the cooktop |
| Trockenwand | the drywall between Speis (shelf B) and Essen |
