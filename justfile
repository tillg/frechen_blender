# Frechenlehen recipes. `just film` makes the Rundgang film from the three.js viewer and publishes it.

set shell := ["bash", "-euo", "pipefail", "-c"]

today := `date +%F`
film := today + "_frechen_rundgang_threejs.mp4"
frames := "tmp/film_web"

# Capture, encode, keep only this film and the one before (also in the git history), commit, force-push
film: film-capture film-encode film-publish

# Capture the viewer's Rundgang frame by frame (~26 min) on the dev server of this checkout
film-capture:
    #!/usr/bin/env bash
    set -euo pipefail
    owner=$(lsof -tiTCP:5377 -sTCP:LISTEN || true)
    started=""
    if [ -n "$owner" ]; then
      cwd=$(lsof -a -p "$owner" -d cwd -Fn | sed -n 's/^n//p')
      [ "$cwd" = "$PWD/web" ] || { echo "port 5377 serves $cwd, not this checkout — stop that server first"; exit 1; }
    else
      (cd web && npm run dev > ../tmp/dev-server-film.log 2>&1 &)
      started=1
      for i in $(seq 1 180); do curl -sf -o /dev/null http://localhost:5377/ && break; sleep 1; done
    fi
    (cd web && npm run blueprint > /dev/null)
    rm -rf {{frames}} && mkdir -p {{frames}}
    log=tmp/film-capture-$(date +%Y%m%d-%H%M%S).log
    echo "capturing, log: $log"
    (cd web && node film.mjs) 2>&1 | tee "$log"
    [ -z "$started" ] || kill "$(lsof -tiTCP:5377 -sTCP:LISTEN)"

# Encode the frames: H.264, 25 fps, two-pass at the bitrate that ends near 90 MB (GitHub: < 100 MB)
film-encode:
    #!/usr/bin/env bash
    set -euo pipefail
    n=$(ls {{frames}}/frame_*.png | wc -l | tr -d ' ')
    kbps=$(python3 code/film_release.py kbps "$n")
    echo "$n frames, ${kbps} kbit/s -> {{film}}"
    in=(-framerate 25 -i {{frames}}/frame_%04d.png -c:v libx264 -preset slow -b:v "${kbps}k" -pix_fmt yuv420p -passlogfile tmp/ffmpeg2pass)
    ffmpeg -hide_banner -loglevel error -y "${in[@]}" -pass 1 -an -f mp4 /dev/null
    ffmpeg -hide_banner -loglevel error -y "${in[@]}" -pass 2 -movflags +faststart {{film}}
    size=$(stat -f %z {{film}})
    echo "{{film}}: $((size / 1000000)) MB"
    [ "$size" -lt 99000000 ] || { echo "too big for GitHub"; exit 1; }

# Delete all but the newest two films (also from main's git history), commit and force-push main
film-publish:
    #!/usr/bin/env bash
    set -euo pipefail
    [ "$(git branch --show-current)" = main ] || { echo "run on main"; exit 1; }
    [ -z "$(git status --porcelain --untracked-files=no)" ] || { echo "uncommitted changes: commit them first"; exit 1; }
    git fetch -q origin
    lease=$(git rev-parse origin/main)
    git merge-base --is-ancestor "$lease" main || { echo "origin/main has commits main lacks: pull first"; exit 1; }
    for f in $(python3 code/film_release.py prune .); do
      if git ls-files --error-unmatch "$f" > /dev/null 2>&1; then git rm -q "$f"; else rm -f "$f"; fi
    done
    git add {{film}}
    git diff --cached --quiet || git commit -q -m "Rundgang film (three.js viewer, hires) of {{today}}; older films removed"
    python3 code/film_release.py purge main
    git push --force-with-lease=main:"$lease" origin main
    git reflog expire --expire=now --all && git gc -q --prune=now
    echo "films: $(ls *_frechen_rundgang_threejs.mp4 | tr '\n' ' ')  .git: $(du -sh .git | cut -f1)"
