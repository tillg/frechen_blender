# Autonomous run – 2026-09-24 evening

Task: when the film render is done, commit and push everything so that no untracked file remains.

## Decisions & assumptions

1. **Film = mixed model state (as chosen before).** Frames 1–2338 were rendered at 15:28 (before the Großeltern Bad/WC fix, bathroom fixtures and floor room names); frames 2339–3480 come from the current model. The user chose "continue" over a full re-render, so I encode the frames as they are.
2. **Encoding:** `ffmpeg -framerate 25 -i tmp/film/frame_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart frechenlehen_rundgang.mp4` (H.264/yuv420p plays everywhere, incl. browsers via the GitHub raw link; faststart for streaming).
3. **"No untracked file":** `tmp/` and `*.blend1` are git-ignored on purpose (scratch renders, Blender backups); they are *ignored*, not untracked, and stay out of the repo. Everything else gets committed, including `CLAUDE.md`, `input/ofen_stuben.jpg` and this file.
4. **README images refreshed** (`docs/images/ansicht_*.png`) after the render finishes, because they still show the old lavender bushes; same camera positions as before, entrance door closed for the stills.
5. **No Playwright testing:** the project is a Blender model, not a web app – there is no stack to start or data to enter. Verification instead: MP4 metadata (frame count, duration, resolution), spot-checking frames across the old/new boundary, `git status` clean after push.
6. **Empty frame repaired.** `frame_2339.png` was 0 bytes: it was being written when the first run was stopped at 16:43, and the resumed run skipped it because the file existed. I deleted it and rendered that single frame again (`-f 2339`) before encoding.

## Results

- `frechenlehen_rundgang.mp4`: 3480 frames, 139.2 s, 1280×720, 25 fps, H.264/yuv420p, 44.9 MB (below GitHub's 100 MB limit). Spot-checked at 12 s, 40 s, 70 s, 93.5/93.6 s (old/new model boundary: no visible jump), 120 s and 138 s.
- README images re-rendered with the green shrubs.
- Committed and pushed everything; `git status` is clean, no untracked files (only the git-ignored `tmp/`, `*.blend1`, `.DS_Store` stay local).
- Public download link (no GitHub login needed): https://github.com/tillg/frechen_blender/raw/main/frechenlehen_rundgang.mp4

## Open points for review

- The film shows the model in two states (see 1.). A full re-render (~1 h) would make the EG part show the Großeltern fix, the bathroom fittings and the room names too.
- Bathrooms still have oak floors; tiles would be more realistic.
- `film.py` still creates new `Innenlicht_*` lights with rising name suffixes on every run (pre-existing, cosmetic).
