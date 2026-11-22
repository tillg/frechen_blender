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

- After `vite build`, a Vite plugin walks `web/dist`, writes the list of its files and a content
  hash of all of them into `web/dist/sw.js` (scope `/frechen_blender/`). Nothing is listed by hand.
- On install the worker fetches every listed file (`cache: 'reload'`) into one cache
  `frechenlehen-<hash>`; on activate it deletes the other `frechenlehen-*` caches (the origin
  `tillg.github.io` is shared with other repos: never touch foreign caches) and takes control.
- It answers GET requests from that cache, ignoring the query (the view lives in the URL), the
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

## Consequences

- First visit downloads the whole build (~62 MB); the page shows the progress and "Offline bereit".
- A worker once deployed stays on the devices that loaded it: removing it later needs a deploy of
  a `sw.js` that unregisters itself, not just deleting the file.
- The film is not offline.
