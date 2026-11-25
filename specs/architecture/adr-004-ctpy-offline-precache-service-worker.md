---
type: ADR
id: ADR-004-CTPY
title: "Offline web app: a build-generated precaching service worker"
description: The production build ships a service worker (sw.js, generated after vite build from the files in web/dist) that stores every file of the build on first visit and answers from that store, so the viewer runs offline, e.g. as a home-screen app on the iPad; dev pages register none.
status: accepted
date: 2026-11-20
supersedes: []
superseded_by: []
---
# ADR-004-CTPY: Offline web app: a build-generated precaching service worker

## Context

The model is to be looked at on an iPad without network (issue #56). Safari on iOS opens no local
`file://` pages with module scripts and `.glb` fetches, so copying `web/dist` to the device does
not work; a page served from the web can only work offline through a service worker.

## Decision

- After `vite build`, a Vite plugin walks `web/dist` and writes its files, grouped into caches, into
  `web/dist/sw.js` (scope `/frechen_blender/`): the live build in `frechenlehen-<hash>` (content hash
  of its files and the worker body), each plan version's files (`v/<id>/…`, ADR-005-JXWL) in
  `frechenlehen-v-<id>-<hash>` (hash of its files only). Nothing is listed by hand.
- On install the worker fetches every listed file not yet in its cache (`cache: 'reload'`), so a
  version stored by an earlier deploy is not fetched again; on activate it deletes the
  `frechenlehen-*` caches not in its list (the origin `tillg.github.io` is shared with other repos:
  never touch foreign caches) and takes control.
- It answers GET requests from the cache of the URL's group, ignoring the query (the view lives in the URL), the
  directory URL as its `index.html`; anything not in the list (the film `rundgang.mp4`, copied after
  the build, and Range requests) goes to the network.
- A new deploy changes `sw.js`; the browser installs the new worker on the next online load; the
  new content shows from the load after that.
- Only the production build registers the worker; the dev pages at `/` never do.

## Alternatives considered

- **Copy `web/dist` to the iPad, open locally:** Safari blocks module scripts and fetches on `file://`.
- **A local web server app on the iPad (a-Shell):** iPadOS suspends it in the background; no updates.
- **A library (Workbox / vite-plugin-pwa):** a dependency for ~60 lines; the file list is all we need.
- **Network-first with cache fallback:** every online load would re-download up to 62 MB.
- **One cache for the whole build (until 2026-11-25):** every deploy would re-download every plan
  version (~43 MB each).

## Consequences

- First visit downloads the whole build (~62 MB); the page shows the progress and "Offline bereit".
- A worker once deployed stays on the devices that loaded it: removing it later needs a deploy of
  a `sw.js` that unregisters itself, not just deleting the file.
- The film is not offline.

## History

- 2026-11-25 — one cache per plan version beside the live build's, kept across deploys (issue #59, ADR-005-JXWL).
