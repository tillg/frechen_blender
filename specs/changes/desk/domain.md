---
feature: desk
title: "Domain: Desk sub-model with monitors, MacBook, keyboard and trackpad"
status: applied
order: 2
created: 2026-11-06
edited: 2026-11-06
---
# Domain: Desk sub-model with monitors, MacBook, keyboard and trackpad

## Concepts

**Schreibtisch (desk sub-model).** The Büro desk in the Bibliothek with its chair and devices,
modelled at its own origin (desk's SW corner) and placed into the house unrotated. Like the Ofen,
it has its own page with dimension lines.

**Screen image.** A material that shows a picture (a screenshot) on a monitor pane instead of a
colour or a procedural texture.

```mermaid
erDiagram
    DESK ||--|| TABLE : "today's top and legs"
    DESK ||--|| CHAIR : "spruce board chair"
    DESK ||--|{ MONITOR : "two LG 32 inch"
    MONITOR ||--|| SCREEN_IMAGE : shows
    DESK ||--|| MACBOOK : "left of the monitors"
    DESK ||--|| KEYBOARD : white
    DESK ||--|| TRACKPAD : white
```

## Vocabulary

| Term | Meaning |
|---|---|
| Schreibtisch | The desk sub-model (`code/desk.py`, `web/desk.html`) |
| Bildschirm | A monitor pane with a screen image |
