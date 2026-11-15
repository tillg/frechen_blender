---
name: film-render
description: Make the Rundgang film — the viewer's capture (`just film`, live) or the Blender render (dormant) — with commands, frame paths and mp4 naming. Use when asked to render, capture or encode the film.
---

**The Blender render is dormant** (issue #35): `frechenlehen.blend` is frozen at `7805879` and not rebuilt since, so a render from it shows the house of that commit. Re-enable Blender first (`CLAUDE.md` › Running › Blender backend). The live film is the viewer's (`just film`, below).

Blender film render (dormant; headless, ~1 s/frame, 1280×720, 25 fps, EEVEE; output settings are set by `film.py` and stored in the file):

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b frechenlehen.blend -a > tmp/render-$(date +%Y%m%d-%H%M%S).log 2>&1
```

Frames go to `tmp/film/frame_####.png` (ffmpeg is installed). The viewer's Rundgang film is made with `just film` (capture with `web/film.mjs` to `tmp/film_web/`, two-pass encode near 90 MB, keep only the newest two films, purge older ones from `main`'s history, commit, force-push; steps: `just film-capture`, `film-encode`, `film-publish`). The capture uses `?hires=on`, which turns off the viewer's speed shortcuts — light pool, pixel-ratio cap, no grass indoors —, so every frame is full quality. Rendered films are named `YYYY-MM-DD_frechen_rundgang_blender.mp4` and `YYYY-MM-DD_frechen_rundgang_threejs.mp4` (render date, repo root; H.264, yuv420p, 25 fps). A headless render reads the file as saved when it starts, so save first and restart it after model changes.
