---
feature: 31-fotos-anzeigen
title: "Domain: Vorlagen — the reference photos by place in the house"
status: applied
order: 2
created: 2026-11-15
edited: 2026-11-15
---
# Domain: Vorlagen — the reference photos by place in the house

## Concepts

**Vorlage** — a picture in `input/` the model was built after (photo, sketch, drawing, plan render).
Each one belongs to exactly one Bereich and has a short German caption.

**Bereich** (area) — a place in the house the Vorlagen are sorted by: a room or room group (Stube,
Küche & Essen, Garderobe & Gäste-WC, Haupteingang & Windfang, Bibliothek & Büro, Bad Oma & Opa),
"Außen & Garten", "Ganzes Haus" (elements used all over the house: floors, basins, Wandlampe,
doors, stair, Werkstattofen) and "Pläne" (the architect's plan renders). A Bereich has an
**anchor** (x, y, z in house coordinates) where its marker stands, or none (Pläne).

**Marker** — the clickable sign of a Bereich in the house viewer, at its anchor; it opens the
Bereich's page.

```mermaid
erDiagram
    BEREICH ||--|{ VORLAGE : contains
    BEREICH ||--o| ANCHOR : "marker at"
    BEREICH { string key; string title }
    VORLAGE { string source; string file; string caption }
    ANCHOR { float x; float y; float z }
```

## Vocabulary

| Term | Meaning |
|---|---|
| Vorlage | A reference picture from `input/`, copied to `web/public/vorlagen/<key>/` |
| Bereich | An area of the house the Vorlagen are sorted by; one page each |
| Marker | The clickable sign of a Bereich in the house viewer |
