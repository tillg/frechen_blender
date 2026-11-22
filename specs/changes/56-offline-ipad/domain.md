---
feature: 56-offline-ipad
title: "Domain: viewer offline on the iPad"
status: applied
order: 2
created: 2026-11-20
edited: 2026-11-20
---
# Domain: viewer offline on the iPad

## Concepts

**Offline-App.** The production viewer stored on a device: every file of one build, kept by the
browser, so the pages open without network. It belongs to one build (one deploy); the next online
visit after a deploy fetches the new one.

```mermaid
erDiagram
    BUILD ||--|| OFFLINE_APP : "stored as"
    OFFLINE_APP }o--|| DEVICE : "kept on"
```

## Vocabulary

| Term | Meaning |
|---|---|
| Offline-App | The viewer build stored on a device by its service worker; opens without network. |
| Offline bereit | The badge text once every file of the build is stored. |
