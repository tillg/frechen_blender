---
feature: <change-name>
title: "Architecture: <short title>"
status: proposed
order: 3
created: YYYY-MM-DD
edited: YYYY-MM-DD
---
# Architecture: <short title>

## Approach

<How the change is built — the shape, not the steps.>

```mermaid
flowchart LR
    %% components and data flow this change adds or alters
```

## A12 impact

<Per line what the change touches, `none` where nothing — see reference/a12.md.>

- **Models:** …
- **Client:** …
- **Server:** …
- **Authorization:** …
- **Data:** …
- **Where it runs:** …

## Key decisions

| Decision | Alternatives considered | Why |
|---|---|---|
| | | |

<A decision that is hard to reverse, surprising without context and a real trade-off is an ADR
(`reference/adr.md`): create it with `scripts/new-adr.sh` and link it here as `ADR-NNN-HHHH`.>

## Integration points

<Existing code, models, roles and tests this change touches or depends on. Live ADRs it must obey.>
