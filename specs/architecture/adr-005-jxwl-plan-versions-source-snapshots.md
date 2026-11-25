---
type: ADR
id: ADR-005-JXWL
title: "Plan versions: committed source snapshots, built by their own exporter"
description: A plan version is a committed tar.gz snapshot of code/ and plans/ (versionen/<id>.tar.gz, listed in versionen/versionen.json); the build turns each into its house .glb with the snapshot's own export_gltf.py and copies its plan sheets, and the current viewer must load every listed version.
status: proposed
date: 2026-11-25
supersedes: []
superseded_by: []
---
# ADR-005-JXWL: Plan versions: committed source snapshots, built by their own exporter

## Context

Frozen states of the plan are to be shown in the viewer and kept offline (issue #59). The model is
code, the `.glb` is generated and git-ignored (ADR-002-MLQS). `just film` rewrites `main`'s history
(purge of old films, force-push), so a commit SHA does not stay valid. A spike (2026-11-25) showed
that the current viewer cannot load a `.glb` exported at a commit of 2026-11-08: newer viewer code
expects extras (`spots`, `routes`, `swing`, …) the old exporter did not write.

## Decision

- Freezing a version (`just version "<name>"`) writes `versionen/<id>.tar.gz`: `git archive HEAD
  code plans` (committed state, ~0.7 MB), and appends `{id, name}` to `versionen/versionen.json`
  (id = date `YYYY-MM-DD`, unique). A snapshot is never changed after it was committed.
- The build (`code/versionen.py`, run by `npm run blueprint`) unpacks each snapshot and runs **its
  own** `code/export_gltf.py <out>`; the plan sheets are the snapshot's committed `plans/*.svg`.
  Output: `web/public/v/<id>/` plus `web/public/versionen.json` for the viewer; cached per snapshot
  hash in `tmp/versionen/`.
- The viewer is backward compatible with every listed version: it tolerates extras a version lacks.
  A test opens every listed version; a viewer change that breaks one is not done.
- Versions start 2026-11-25; earlier states are not versions.

## Alternatives considered

- **Pin a commit SHA, rebuild in CI from the history:** the film purge rewrites every SHA; CI would
  need the full history.
- **Commit the built `.glb`:** ~6 MB gzipped per version instead of 0.7 MB, and the snapshot could
  no longer be re-exported.
- **Re-export old core code with today's exporter:** the exporter and the core change together; old
  core code does not run under a new exporter.
- **Freeze the whole web build (old viewer + data):** no compatibility burden, but every version would
  carry its own viewer without the version menu and with its own service worker scope.

## Consequences

- Every viewer change keeps reading the oldest listed version's `.glb` (the compatibility test).
  Features added later appear in old versions only where the old data allows.
- The snapshot's exporter runs with today's Python (stdlib only).
- A version's Vorlagen links point at today's Fotos & Vorlagen pages, and its image textures (the
  desk's screens, `web/public/textures/`) load from today's build: renaming or deleting one breaks
  the versions that use it (the compatibility test shows it).
- Building needs Python ≥ 3.11.4 (`tarfile` extraction filter).
