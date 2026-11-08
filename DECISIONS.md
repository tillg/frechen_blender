---
title: "Decisions"
created: 2026-11-08
edited: 2026-11-08
---

# 2026-11-08 23:45 — Rundgang into the Bad Großeltern, stone floors in all WCs, new film {#run-2026-11-08-2345}

- **Started by:** user message (unattended: "Warte nicht auf mich, arbeite weiter ohne zu fragen")
- **Task, as given:** > Ändere die Rundgang-route so, dass wir auch einen Blick in die Dusche der
  Großeltern schauen und in ihre toilette. Die Toiletten sollten alle Steinböden bekommen. Wenn du
  damit fertig bist, mach den Film neu. Und überschreib einfach die alte Datei. … und dann committe
  & pushe alles, so dass keine Files dangling sind

## 23:45 — Run it as a tweak {#run-2026-11-08-2345-1}

- **Status:** open
- **Context:** spec workflow (`CLAUDE.md` › Spec-driven workflow): change or tweak.
- **Question:** `/spec:propose` a change, or `/spec:tweak`?
- **Decision:** tweak, 3 steps (WC floors, route, rebuild + film).
- **Why:** no new term, component or model file; both parts reuse existing mechanisms
  (`floor_cover` limestone list, `ROUTE` segments).
- **Alternatives:** a full change with proposal/architecture.
- **Consequences:** no `specs/changes/` directory; `specs/system/functional.md` and `README.md`
  updated in place.

## 23:46 — Which toilets, which stone {#run-2026-11-08-2345-2}

- **Status:** open
- **Context:** "Die Toiletten sollten alle Steinböden bekommen".
- **Question:** which rooms and which stone?
- **Decision:** the four WCs (EG by the back hall, the WC in the Bad Großeltern's niche, OG WC 2,26,
  OG WC 2,30) get the limestone of the EG Flur and the Bäder (`Kalkstein`), each over its room
  rectangle (`WCS`, `WC_EG`); the Schrank half of the niche keeps oak; door thresholds stay oak like
  the other limestone rooms.
- **Why:** "Toiletten" = the WCs; limestone is the one stone floor in the house.
- **Alternatives:** a new stone (e.g. slate) for the WCs; stone under the Schrank too.
- **Consequences:** fewer/more floor pieces shift the global random sequence: the golden's `rnd`
  hashes and the random-length pieces of `Kiesel`, `Terrasse`, `OG_Bodenbelag` changed (golden
  regenerated, `.blend` rebuilt and saved).

## 23:47 — Two existing tests changed: WCs were pinned as oak {#run-2026-11-08-2345-3}

- **Status:** open
- **Overrides:** "Never make tests pass by changing/removing them without explicit permission"
  (`CLAUDE.md` › Working rules)
- **Context:** `test_bathrooms_have_limestone_like_the_eg_corridor` asserted oak at OG WC 2,26 and
  at the WC Großeltern; `test_bad_built_into_the_grosseltern` asserted oak at the WC Großeltern.
- **Question:** keep them (and fail) or change them?
- **Decision:** changed only those assertions to the new requirement (WC points now Kalkstein; the
  Flur/HWR/Schrank oak points stay); the new `test_wcs_have_limestone_floors` covers all four WCs.
- **Why:** the user's request reverses exactly what they pinned; nothing else was weakened.
- **Alternatives:** stop and ask (the user said not to wait).
- **Consequences:** revert = restore the two assertions and drop the WC rects from `floor_cover`.

## 23:50 — Where the route looks into the shower and the WC {#run-2026-11-08-2345-4}

- **Status:** open
- **Context:** `code/tour.py` › `ROUTE`, Großeltern segment.
- **Question:** where to stand, in which order, how long?
- **Decision:** from the bedroom walk into the Bad to (1.2, 10.35), just south of the low wall:
  turn to the shower (NW, looking slightly down through its open south side), pause `PAUSE`, turn
  left to the WC in the niche (looking down at the toilet, the WC leaf is open), pause, then walk to
  the bedroom's corner beside the balcony door and continue as before.
- **Why:** one spot sees both; the shower entrance and the open WC half face it; clearance stays
  ≥ 0.25 m (checked: min 0.252 m over all 7632 frames, 0 ray hits).
- **Alternatives:** two separate stops; looking at the shower through the glass from the bedroom.
- **Consequences:** the route grows from 7157 to 7632 frames (305 s); tour golden regenerated.

## 23:55 — Known red e2e test left as is {#run-2026-11-08-2345-5}

- **Status:** open
- **Context:** `web/e2e/tour.spec.js` "the tour draws at most ~30 frames per second" needs > 15 fps.
- **Question:** fix, skip or accept?
- **Decision:** accepted as not caused by this work: it gets 8–12 fps with the model from before the
  Bad change too (machine under load: photoanalysisd, mediaanalysisd, Sophos); all other web tests
  pass.
- **Why:** reproduced with the HEAD glb earlier this evening.
- **Alternatives:** loosen the threshold (would weaken a test).
- **Consequences:** rerun when the machine is idle.

## 23:56 — Commit and push although the run is unattended {#run-2026-11-08-2345-6}

- **Status:** open
- **Overrides:** `/spec:tweak` › Unattended: "don't commit — leave changes unstaged"
- **Context:** the user asked: "committe & pushe alles, so dass keine Files dangling sind".
- **Decision:** commit to `main` and push (code, tests, goldens, `.blend`, docs, this file; then the
  new film).
- **Why:** explicit user request.
- **Consequences:** GitHub Pages redeploys from `main`.

## 23:57 — Film file size {#run-2026-11-08-2345-7}

- **Status:** open
- **Context:** the film is committed; GitHub rejects files over 100 MB; a crf-18 encode of the
  previous capture was 228 MB.
- **Decision:** encode with H.264 `-preset slow -crf 24` (yuv420p, 25 fps) into
  `2026-11-08_frechen_rundgang_threejs.mp4`, overwriting the earlier one as asked.
- **Why:** keeps it under the limit at a quality close to the earlier committed films.
- **Alternatives:** Git LFS; not committing the film.
- **Consequences:** if it still exceeds 100 MB, raise crf by 1–2 and re-encode.
