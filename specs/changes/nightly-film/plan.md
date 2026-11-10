---
feature: nightly-film
title: "Plan: nightly Rundgang film when the model changed"
status: proposed
order: 4
created: 2026-11-10
edited: 2026-11-10
---
# Plan: nightly Rundgang film when the model changed

## Steps

- [ ] [config] Release workflow `.github/workflows/film-release.yml` (push to `main` touching
  `film.sha256`, and `workflow_dispatch`): release `rundgang-YYYY-MM-DD` with fingerprint + links,
  no asset, older `rundgang-*` releases deleted with their tags; first proves the e-mail (until
  step 4 there is no `film.sha256`: the workflow then names the fingerprint `none`)
  - Test first: none — GitHub-only; today `gh release list` shows no `rundgang-*` release and no
    e-mail can arrive. The owner sets "Watch → Custom → Releases" first.
  - Verify: push the workflow, `gh workflow run film-release.yml` → `gh release list` shows exactly
    one `rundgang-*` release, a second run creates none (same fingerprint); **the owner confirms the
    release e-mail arrived**. No e-mail → stop and settle the channel (proposal › Open questions).
- [ ] [python] The `.glb` export is byte-for-byte deterministic
  - Test first: `tests/test_gltf.py` › `export is deterministic` — two `export_gltf.py` runs into
    two files give identical bytes; fails today only if the export is not deterministic (then fix
    the export first: the fingerprint depends on it)
  - Verify: `.venv/bin/python -m pytest -q tests/test_gltf.py -k deterministic` → green
- [ ] [python] `film_release.fingerprint(repo)` and the `fingerprint` / `needed` CLI
  - Test first: `tests/test_film_release.py` › `fingerprint follows the film's inputs` — on a
    throw-away repo: equal for equal inputs; changes when the `.glb`, a `web/src` file, a tracked
    `web/public` texture or `package-lock.json` changes or a viewer file is renamed; unchanged by
    `README.md`, `code/build_house.py`, `tests/`, an untracked file; `needed` exits 0 without
    `film.sha256`, 1 when it matches, 0 when it differs — fails today: no `fingerprint`
  - Verify: `.venv/bin/python -m pytest -q tests/test_film_release.py` → green
- [ ] [config] `just film-capture port=<p>` starts/stops its own Vite on a port ≠ 5377 and refuses a
  taken port; `just film-publish` writes and commits `film.sha256`
  - Test first: none — recipes; today `just --show film-capture` has no `port` and `film-publish`
    no `film.sha256`
  - Verify: `just --show film-capture | grep -q 'port'` and `just --show film-publish | grep -q
    film.sha256`; `just film-capture port=5378` with a dummy listener on 5378 (`python3 -m
    http.server 5378 &`) exits non-zero with "port 5378 is taken"; a short real capture
    (`node film.mjs http://localhost:5378/ 0 24` via the recipe's server) writes 25 frames
- [ ] [config] `scripts/film_night.sh`: film clone, reset to `origin/main`, `npm ci`, blueprint,
  `needed`, `film-capture port=5378` → `film-encode` → `film-publish`, log
  `tmp/film-night-<ts>.log`, notification on failure, server stopped by a trap
  - Test first: none — orchestration; checked by running it: today the script does not exist
  - Verify: (a) `FILM_CLONE=~/git/frechen_film bash scripts/film_night.sh` twice → the first run
    clones and (no `film.sha256` yet) renders and publishes for real (~30 min, force-pushes `main`:
    the owner says when; working clones pull afterwards); the second logs "film unchanged",
    exits 0 in < 3 min, `lsof -iTCP:5378 -sTCP:LISTEN` empty; (b) with 5378 taken: exit 1, a
    notification, nothing pushed
- [ ] [config] launchd agent: `scripts/launchd/film-night.plist.in`, `just film-night-install` /
  `film-night-uninstall` (absolute paths, install-time `PATH`, 01:00 daily)
  - Test first: none — today `launchctl print gui/$UID/net.frechen.film-night` fails
  - Verify: `plutil -lint ~/Library/LaunchAgents/net.frechen.film-night.plist` OK;
    `launchctl print gui/$(id -u)/net.frechen.film-night` shows the calendar interval 01:00;
    `launchctl kickstart gui/$(id -u)/net.frechen.film-night` runs the script (log written,
    "film unchanged")
- [ ] [docs] README (German): nightly film, one-time setup (`just film-night-install`, `sudo pmset
  repeat wakeorpoweron MTWRFSU 00:55:00`, Watch → Releases), where the log is; CLAUDE.md: the 5378
  exception for the film clone in the one-dev-server rule
  - Test first: none — docs
  - Verify: `grep -q film-night-install README.md && grep -q 5378 CLAUDE.md`

Final check: one real night (or a `kickstart` after a model change pushed): film, `film.sha256` and
the Release appear, the e-mail arrives, the working clones are untouched; `bash scripts/check.sh
full`.

System docs are updated at `/spec:archive`.
