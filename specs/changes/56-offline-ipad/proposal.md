---
feature: 56-offline-ipad
title: "Proposal: viewer offline on the iPad"
status: applied
order: 1
created: 2026-11-20
edited: 2026-11-20
---
# Proposal: viewer offline on the iPad

## What

The production viewer on GitHub Pages becomes an offline web app: opened once with network (in
Safari or as a home-screen app), it stores every file of the build and then runs without network:
house, all sub-models, plan sheets, Fotos & Vorlagen. A small badge shows the download progress
and "Offline bereit".

## Why

The user wants to look at the whole model on the iPad without network (issue #56). Copying
`web/dist` does not work: Safari on iOS does not run module scripts or fetch `.glb` from `file://`.

## Scope

- In: service worker generated from `web/dist` after the build, its registration on every page of
  the build, a web-app manifest and home-screen icon, the progress badge, Vorlagen markers opening
  in the same window when running as a home-screen app, README.
- Out (non-goals): the film `rundgang.mp4` offline; any change to the dev pages at `/`; tuning
  for the iPad's GPU; an install prompt.

## Expected outcome

- In the Playwright preview project: after the first load, with the browser offline, a reload of
  `/frechen_blender/`, a sub-model with a view query, a plan sheet and a Vorlagen page with all
  pictures load, every response coming from the service worker.
- On the iPad (checked by the user): "Zum Home-Bildschirm", open once online until "Offline
  bereit", then in flight mode the model opens.

## Open questions

- Performance and storage quota on the iPad can only be seen on the device.
