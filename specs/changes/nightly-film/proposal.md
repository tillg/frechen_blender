---
feature: nightly-film
title: "Proposal: nightly Rundgang film when the model changed"
status: proposed
order: 1
created: 2026-11-10
edited: 2026-11-10
---
# Proposal: nightly Rundgang film when the model changed

## What

Every night at 01:00 the owner's Mac checks whether anything that shapes the three.js Rundgang film
changed on `origin/main` since the last film. If so, it renders the film in its own clone
(`just film` as today: capture on the real GPU, encode, commit, prune old films from the history,
force-push `main`), and a GitHub workflow then publishes a GitHub Release for the new film, which
reaches the owner as GitHub's release e-mail. Nothing changed → the run ends after a minute.

## Why

The film is made by hand (`just film`, ~26 min capture + encode + publish) and so lags behind the
model; after a day of model changes someone has to remember to run it. GitHub-hosted runners have no
GPU (software WebGL would be hours per film and may look different), so the Mac that already renders
it in 25 minutes does it unattended, at night, when nobody works in the repo.

## Scope

- In:
  - a **film fingerprint**: one hash over everything the film is made of (the generated
    `frechenlehen.glb`, the viewer under `web/`), stored next to the film as `film.sha256`;
  - a nightly script `scripts/film_night.sh`: own clone (`~/git/frechen_film`), reset to
    `origin/main`, fingerprint check, dev server on its **own port 5378**, `just film`, log to
    `tmp/`, a macOS notification when a run fails;
  - a launchd agent (01:00 daily, catches up after sleep) and a `just` recipe that installs it;
  - `just film-capture` / `film-publish` take the port and write `film.sha256`;
  - a workflow `film-release.yml`: after a push that brings a new `film.sha256`, a Release
    `rundgang-YYYY-MM-DD` (no asset: link to the film on Pages and in the repo), older film
    releases and their tags deleted;
  - README (German) and CLAUDE.md: the nightly film, the one-time wake setting, the port exception.
- Out (non-goals): rendering on GitHub-hosted runners; the Blender film (`film.py` / `film-render`);
  publishing the mp4 as a release asset; push messages other than GitHub's release e-mail; waking
  the Mac automatically (`pmset` needs sudo: a one-time manual step, documented).

## Expected outcome

- An unchanged `origin/main`: the nightly run logs "film unchanged" and exits 0 within ~2 min,
  no server left running, no commit.
- A changed model: by ~01:40 a new `YYYY-MM-DD_frechen_rundgang_threejs.mp4` and `film.sha256` on
  `main` (force-pushed, older films pruned as today), Pages serving it as `rundgang.mp4`, one
  Release `rundgang-YYYY-MM-DD` and an e-mail from GitHub about it.
- A failed run (port taken, capture error, lease lost because someone pushed meanwhile): no push,
  a macOS notification with the log path, the log in the film clone's `tmp/`.
- The owner's working clones and their dev server on 5377 are never touched.

## Open questions

- Does GitHub e-mail a watcher about a release published by `github-actions[bot]` (it does not for
  one's own actions)? Plan step 1 checks it before anything else is built; if not, the release
  must be created with another identity, or the message channel changes.
- The capture with the screen locked / display asleep at 01:00: does headless Chromium keep the
  Metal GPU? Checked by the first real nightly run; if not, a `caffeinate -d` around the capture.
