# Architecture decision records

Where lasting decisions go, in what shape, and when a decision earns one. Modelled on the w12
spec layout; skills that write ADRs read this file first.

## Layout

```
specs/architecture/
  index.md                       generated — scripts/gen-adr-index.sh, never edited by hand
  adr-001-kqzt-keycloak-as-idp.md  live: status proposed | accepted
  archive/                       status superseded | rejected — history, not read by default
```

File: `adr-NNN-hhhh-<slug>.md`; id `ADR-NNN-HHHH` — the next free number plus a random 4-letter
hash, so two branches that pick the same number coexist after a merge without renumbering.
`scripts/new-adr.sh <slug>` (in this plugin's `scripts/`) creates the file from
`specs/templates/adr.md` and prints the id. **Cite the full id everywhere**, never the bare number.

## Frontmatter and body

```yaml
---
type: ADR
id: ADR-001-KQZT
title: Keycloak as identity provider
description: One sentence stating the decision — feeds the generated index.
status: proposed
date: 2026-10-28
supersedes: []
superseded_by: []
---
```

Sections: `## Context` (2–3 sentences), `## Decision` (the binding constraint — what we do, what we
don't), `## Alternatives considered` (brief), `## Consequences` (optional), `## History` (optional:
one dated line per later change to the decision). ≤ 1,500 words. One decision per ADR.

## Lifecycle

| `status` | Set by | Meaning |
|---|---|---|
| `proposed` | `/spec:propose`, `/spec:grill`, `/spec:iterate` while a change is open | Decided for the change, not yet in the code base. Still live and binding for that change. |
| `accepted` | `/spec:archive` when the change lands | Binding for all new code. |
| `superseded` | a later ADR with `supersedes: [ADR-…]` — the old one gets `superseded_by` and moves to `archive/` in the same change | History. |
| `rejected` | `/spec:iterate` or `/spec:archive` when a proposed decision is dropped; the file moves to `archive/` | History. |

A **changed** decision rewrites `## Decision` in place and adds one dated line to `## History`. Never
an "Amendment" section, never a second ADR for the same decision.

After any ADR change run `bash "$PLUGIN/scripts/gen-adr-index.sh"` (`--check` is the mechanical
verify for a plan step that adds an ADR).

## When a decision is an ADR

All three must hold — otherwise it is a row in the change's `## Key decisions` table
(`architecture.md`; promoted to `specs/system/architecture.md` at archive):

1. **Hard to reverse** — changing your mind later costs real work.
2. **Surprising without context** — a future reader would ask "why on earth?".
3. **A real trade-off** — there were genuine alternatives, picked for specific reasons.

Qualifies: architectural shape, integration patterns, technology with lock-in (IdP, database,
message bus), boundary and ownership decisions, deliberate deviations from the obvious A12 path
(e.g. a rule in a listener instead of the model, a custom component instead of an engine), constraints
invisible in the code. Doesn't: a single model's field layout, an endpoint's DTO, a naming choice —
those are Key-decisions rows or just the spec.

Before proposing an ADR, read `specs/architecture/index.md`: a change that contradicts a live ADR is
a **critical** finding in `/spec:grill` and `/spec:adversarial-code-review`, and needs a superseding
ADR, not a quiet workaround.
