---
title: "Decisions"
created: 2026-11-08
edited: 2026-11-15
---

Choices made while nobody was there to ask are logged here
(`.claude/skills/spec/reference/decisions.md`); confirmed ones are removed after review.

**Contents**

- [2026-11-15 16:33 — Implement issues #35 … #30](#run-2026-11-15-1633)
  - [16:40 — Stack the issue branches; open one PR per issue, leave merging to the user](#run-2026-11-15-1633-1)
  - [16:40 — Work the issues strictly one after another, one agent per issue](#run-2026-11-15-1633-2)
  - [16:51 — #35 as a `/spec:tweak` that commits, no change directory](#run-2026-11-15-1633-3)
  - [16:51 — Replace the Blender parity tests by a compile-only guard of the Blender scripts](#run-2026-11-15-1633-4)
  - [17:20 — Rename the former Alternativ objects: `EG_Essen_Schrank`, `EG_Speis_Rueckwand`, `EG_Pendeltuer_S`/`_N`; lamps 13, 14 into `EG_Wandlampen`](#run-2026-11-15-1633-5)
  - [17:20 — The saloon leaves keep a door clock of their own, keyed by the name `_Pendeltuer`](#run-2026-11-15-1633-6)
  - [17:20 — Delete the tests of the switch and of the default layout; port the general ones](#run-2026-11-15-1633-7)
  - [18:02 — #31: nine Bereiche; every raster image of `input/` assigned, plan renders in "Pläne"](#run-2026-11-15-1633-8)
  - [18:02 — #31: markers as DOM links with a wall-ray occlusion test, not scene sprites](#run-2026-11-15-1633-9)
  - [18:02 — #31: one page `vorlagen.html?b=<key>`, fed by a small generated JSON; reached by a link in the house page's title box](#run-2026-11-15-1633-10)
  - [18:02 — #31: copies downsized to ≤ 1600 px JPEG and committed; the copy step is a one-off `sips` run](#run-2026-11-15-1633-11)
  - [19:01 — #33: shower strip 90 deep along the west wall; the north wall is the Waschküche partition, kept free above 1.20](#run-2026-11-15-1633-12)
  - [19:01 — #33: basin single 60 (was double 100) with mirror 80 × 85 on the east wall; toilet on the north wall; 3 lamps instead of 6](#run-2026-11-15-1633-13)
  - [19:01 — #33: rewrite the old Elternbad layout tests; the Rundgang stops in front of the glass](#run-2026-11-15-1633-14)

# 2026-11-15 16:33 — Implement issues #35 … #30 {#run-2026-11-15-1633}

- **Started by:** `/autonomous`
- **Task, as given:**

  > implement gh issues
  > Implement github issues. Don't wait fopr my, takes decisions as u think best. 
  > Do the issues in this order: #35, #34, #31, #33, #32, #29, #28, #27, #26, #30
  > Make sure to always commit & push in between. Use agents to save space in your context

  Added during the run:

  > Und ganz am Ende: Den Film neu genieren und publishen

## 16:40 — Stack the issue branches; open one PR per issue, leave merging to the user {#run-2026-11-15-1633-1}

- **Status:** open
- **Overrides:** `CLAUDE.md` › GitHub issues — work on an issue starts from current `main` (here: from the previous issue's branch); `/spec:archive` — archive only after the human's approval and with no `open` decisions (here: archived on the branch after self-review, decisions stay `open`).
- **Context:** ten issues in a fixed order, almost all of them change `code/house_core.py`, the committed `plans/*.svg` and the goldens; the user is away and asked to commit & push in between, not to merge.
- **Question:** how can later issues build on earlier ones while nothing is merged without the user?
- **Decision:** each issue gets its branch `issue/<n>-<slug>` from the previous issue's branch (#35 from `main`); per issue: final check green → `/spec:adversarial-code-review` → archive on the branch → push → PR with base = the previous issue's branch (`Closes #n`), label `[under review]`. No merge.
- **Why:** later issues build on earlier ones (#34's layout under #27/#26, #33/#29 next to #30's wall); merging to `main` (which deploys Pages) is the user's call.
- **Alternatives:** merge each PR after self-review (simpler history, but bypasses the human gate and deploys unreviewed); independent branches from `main` (conflicts on plans and goldens).
- **Consequences:** merge the PRs in order (#35 first); with "delete branch on merge" GitHub retargets the next PR to `main`. A change requested in an early PR has to be carried up the stack (rebase/merge the later branches).
  #35: branch issue/35-nur-noch-threejs from main, PR https://github.com/tillg/frechen_blender/pull/36 (a tweak: no change directory, so no archive step; `specs/system/` updated in place).
  #34: branch issue/34-alternativ-layout-standard from issue/35-nur-noch-threejs, PR https://github.com/tillg/frechen_blender/pull/37 (archived on the branch; full check: one red, `tour.spec.js` › ~30 fps lower bound, flaky under load, fails 2/5 on the base branch too).
  #31: branch issue/31-fotos-anzeigen from issue/34-alternativ-layout-standard, PR https://github.com/tillg/frechen_blender/pull/38 (archived on the branch; full check green).
  #33: branch issue/33-zwei-duschen from issue/31-fotos-anzeigen, PR (see the #33 commit / PR list) (archived on the branch; full check: 3 reds, two pinned lamp count / label fixed and rerun green, the ~30 fps test flaky, green alone).

## 16:40 — Work the issues strictly one after another, one agent per issue {#run-2026-11-15-1633-2}

- **Status:** open
- **Context:** the user asked to use agents to save context; the repo allows exactly one dev server (5377), which serves one working tree.
- **Question:** parallel worktrees per issue, or sequential?
- **Decision:** sequential, one `worker` agent per issue (on the issue branch in the main checkout); extra agents only inside an issue (exploration, review axes).
- **Why:** shared core, plan sheets and goldens would conflict; worktree work can't be shown on the one dev server.
- **Alternatives:** parallel worktrees (faster wall clock, but conflicts and no Show).
- **Consequences:** slower; each issue starts from the merged result of the one before.

## 16:51 — #35 as a `/spec:tweak` that commits, no change directory {#run-2026-11-15-1633-3}

- **Status:** open
- **Overrides:** `/spec:tweak` — unattended: don't commit, leave changes unstaged (here: committed and pushed on the issue branch, as the run's brief asks).
- **Context:** issue #35 "Nur noch threejs": drop the Blender tests and the rebuild/save steps from the workflow, keep the Blender scripts.
- **Question:** tweak or propose + apply?
- **Decision:** tweak: three steps (guard test, remove the Blender tests, docs); no code in `code/`, no new domain term, no ADR change (ADR-001-XEWL still holds: the Blender backend stays, it is only no longer checked). Review and archive run against the branch diff; with no change directory the review's Spec axis checks against the issue text.
- **Why:** mechanical change; a change directory would only repeat the issue.
- **Alternatives:** propose + apply (a proposal/plan for a deletion and doc edits).
- **Consequences:** no `specs/changes/35-*`; `specs/system/` updated in place.

## 16:51 — Replace the Blender parity tests by a compile-only guard of the Blender scripts {#run-2026-11-15-1633-4}

- **Status:** open
- **Context:** #35; `tests/test_blender_parity.py` (2 `slow` tests, start Blender), `tests/blender/snapshot.py` and `tests/golden/blender_snapshot.json` are the only tests that launch Blender. Last full check with parity green: `main` at 7805879 (pytest 195 passed in 67 s, Vitest 60, Playwright 106).
- **Question:** what stays to keep re-enabling Blender cheap?
- **Decision:** delete those three; add `tests/test_blender_scripts.py`, which compiles the six Blender scripts (`build_house`, `fire`, `paint`, `windrose`, `garden`, `film`) with the standard Python (no `bpy` needed). Keep `tests/fixtures/garden_blender.json` (read by `test_core.py`, no Blender), `test_film_release.py`, `test_tour.py` and `tests/golden/tour.json` (the three.js Rundgang uses the keys). `frechenlehen.blend` stays, frozen at 7805879.
- **Why:** faster dev cycles (the issue's motivation); a syntax check costs milliseconds and catches the cheapest kind of rot.
- **Alternatives:** keep parity as an opt-in marker (still drifts, golden goes stale); no guard at all.
- **Consequences:** the guard checks syntax only: the scripts can drift from the core's API unnoticed. The Blender BVH camera-clearance check of the route is dormant too; only the pure-Python route tests (`test_tour.py`: Wandlampen, Alternativ furniture) remain — a gap against all other geometry. To re-enable: restore `git show 7805879:tests/test_blender_parity.py`, `tests/blender/snapshot.py`, `tests/golden/blender_snapshot.json`, rebuild (CLAUDE.md › Blender backend), regenerate the golden, save the `.blend`.

## 17:20 — Rename the former Alternativ objects: `EG_Essen_Schrank`, `EG_Speis_Rueckwand`, `EG_Pendeltuer_S`/`_N`; lamps 13, 14 into `EG_Wandlampen` {#run-2026-11-15-1633-5}

- **Status:** open
- **Context:** `specs/changes/34-alternativ-layout-standard/` (issue #34): with Alternativ the only EG layout, the `EG_Alt_*` names name an alternative that no longer exists.
- **Question:** keep `EG_Alt_*`, rename, or reuse the names of the deleted default objects?
- **Decision:** `EG_Alt_Schrank` → `EG_Essen_Schrank` (cabinet C on the Essen's west wall), `EG_Alt_Speis` → `EG_Speis_Rueckwand` (B's board back), `EG_Alt_Pendeltuer_S`/`_N` → `EG_Pendeltuer_S`/`_N`; `EG_Alt_Wandlampen` (lamps 13, 14) folds into `EG_Wandlampen`; `speis_alt()` → `speis_essen()`.
- **Why:** "Alt" would mean nothing any more; the lamps had their own object only to carry the layout flag. `EG_Schrank` is taken (`bad.py`); reusing `EG_Speis_C` / `EG_Wandlampen_Essen` for different geometry would mislead readers of history and tests.
- **Alternatives:** keep `EG_Alt_*` (no churn, but misleading); reuse the deleted names (shorter diff in tests, but the same name for other geometry).
- **Consequences:** workers of #27 (Garderobe) and #26 (Küche hood) use the new names; old view URLs with `cut=eg_alt` fall back to the last/whole-house entry.

## 17:20 — The saloon leaves keep a door clock of their own, keyed by the name `_Pendeltuer` {#run-2026-11-15-1633-6}

- **Status:** open
- **Context:** `specs/changes/34-alternativ-layout-standard/`: `slides.js` gave the leaves of a layout variant (`extras.variant`) their own swing clock; without the flag they would join the back hall's clock.
- **Question:** fold the saloon leaves into the back hall's clock or keep their own?
- **Decision:** keep their own clock, keyed by name like the Büro door's (`_Buerotuer`).
- **Why:** five leaves on one clock would make each back-hall door move less often (and `gaeste_wc.spec.js`'s wait for a back-hall door flaky); the rhythm stays as it was in Alternativ.
- **Alternatives:** one shared clock (simpler code, but a visible change and a flaky e2e).
- **Consequences:** a name rule in `slides.js`; a renamed leaf would silently join the shared clock (`slides.test.js` pins it).

## 17:20 — Delete the tests of the switch and of the default layout; port the general ones {#run-2026-11-15-1633-7}

- **Status:** open
- **Context:** `specs/changes/34-alternativ-layout-standard/`: the issue asks to delete the default layout; several tests pin it or the switch.
- **Question:** which tests go, which are ported?
- **Decision:** deleted: `test_core.py` › `test_variant_main_objects` (default-only objects) and `test_default_layout_leaves_the_variant_out` (`default_layout()`); `test_plans.py` › `test_sheets_leave_the_variant_out`; `test_gltf.py` › `test_variant_extras`; `test_show.py` › `test_variant_objects_are_shown_in_their_entry`; `web/e2e/variant.spec.js` (entry `eg_alt`, `?layout=alt`, Skizze per variant); `lighting.test.js`'s per-layout cases. Ported: `test_variant_alt_objects` → `test_speis_essen` (same geometry asserts, new names, plus a check that no default-only object and no flag remain); the Wandlampen, lamp-clearance, swing, Speis-C geometry, route-clearance, light-count, Modell-list and door-clock tests to the one layout (counts 71 → 69 wall lights; EG lamps 35 → 33).
- **Why:** the switch and the default layout no longer exist; the general properties (lamp places, clearances, route) still hold and keep their tests.
- **Alternatives:** keep the switch tests skipped (dead weight).
- **Consequences:** none beyond the deleted code.

## 18:02 — #31: nine Bereiche; every raster image of `input/` assigned, plan renders in "Pläne" {#run-2026-11-15-1633-8}

- **Status:** open
- **Context:** `specs/changes/31-fotos-anzeigen/` (issue #31 "Fotos anzeigen"): "kopiere alle Fotos nach Bereichen"; `input/` holds 55 raster images, among them plan renders, agreed drawings, sketches and two monitor screenshots.
- **Question:** which areas, and what about pictures that are not photos of a place?
- **Decision:** Bereiche Stube, Küche & Essen, Garderobe & Gäste-WC (the back hall with its Windfang door: Garderobe + Toilette Mallnitz + Bad Mallnitz + back door), Haupteingang & Windfang, Bibliothek & Büro, Bad Oma & Opa, Außen & Garten, Ganzes Haus (floors, interior door, stair, standard basins, Wandlampe, Werkstattofen — it stands in three rooms) and Pläne (the four architect plan renders, no marker). Drawings and sketches go to their room; the monitor screenshots to Büro. PDFs and SVGs are not copied (the plans are the viewer's plan sheets). "Ganzes Haus" has a marker in the OG Flur (so the 1. Stock has one too).
- **Why:** every image in one place makes the test simple and exhaustive ("all photos"); the user's examples land where the issue says.
- **Alternatives:** exclude plans/screenshots (an exclusion list to maintain); one area per room incl. OG rooms (they have no photos of their own).
- **Consequences:** a new picture in `input/` fails `tests/test_vorlagen.py` until it is assigned and copied.

## 18:02 — #31: markers as DOM links with a wall-ray occlusion test, not scene sprites {#run-2026-11-15-1633-9}

- **Status:** open
- **Context:** `specs/changes/31-fotos-anzeigen/`: a clickable element in each room opens its page.
- **Question:** 3D sprite in the scene or an HTML element over the canvas?
- **Decision:** one `<a target="_blank">` per anchored Bereich, projected from its anchor; shown only from inside on its storey within 8 m, or from above with that storey cut open, or (Außen) from outside; and only when no wall object lies between camera and anchor; hidden in a route, `?hires=on` and on a plan sheet.
- **Why:** a real link (href, new tab, cursor, keyboard, testable in the production build without the test hook), no click-vs-orbit-drag logic, no WebGPU sprite material; the wall ray keeps the next room's marker from showing through the wall.
- **Alternatives:** sprites (depth test for free, but click handling and raycasting the sprites); overlays without occlusion (markers through walls).
- **Consequences:** furniture does not hide a marker (only walls do); the marker is a flat label of constant size, not a picture in the room.

## 18:02 — #31: one page `vorlagen.html?b=<key>`, fed by a small generated JSON; reached by a link in the house page's title box {#run-2026-11-15-1633-10}

- **Status:** open
- **Context:** `specs/changes/31-fotos-anzeigen/`: area pages plus a house-wide page, reachable from the UI.
- **Question:** one HTML per area or one page; where does the page get the manifest; where does the UI link it?
- **Decision:** one `vorlagen.html` (no `b`: index of all Bereiche); the manifest comes from `public/vorlagen.json`, written by `npm run blueprint` from `code/vorlagen.py` (git-ignored like the `.glb`); the house page's title box gets a link "Fotos & Vorlagen" (the toolbar stays as it is; its layout and lists are pinned by `nav.spec.js`).
- **Why:** one build input and script; the page must not load the 39 MB glb; a title link changes no toolbar test.
- **Alternatives:** an entry in the Modell drop-down (it lists models, not pages of photos); one HTML file per Bereich.
- **Consequences:** sub-model pages have no link to the photos (from there: the house page).

## 18:02 — #31: copies downsized to ≤ 1600 px JPEG and committed; the copy step is a one-off `sips` run {#run-2026-11-15-1633-11}

- **Status:** open
- **Context:** `specs/changes/31-fotos-anzeigen/`: the originals sum to ~150 MB (5712 × 4284 photos); `input/` is not served.
- **Question:** originals or copies; generated at build or committed?
- **Decision:** `python3 code/vorlagen.py --copy` (macOS `sips`): longest side ≤ 1600 px, JPEG quality 80, into `web/public/vorlagen/<key>/`; committed. Tests check that every copy exists and is ≤ 1600 px, never call `sips`.
- **Why:** the Pages build needs them; CI (Linux) has no `sips`; a 1600 px copy is plenty for a reference.
- **Alternatives:** full originals (slow page, big repo); Pillow at build time (new dependency).
- **Consequences:** a changed original needs `--copy` again; the repo grows by a few MB.

## 19:01 — #33: shower strip 90 deep along the west wall; the north wall is the Waschküche partition, kept free above 1.20 {#run-2026-11-15-1633-12}

- **Status:** open
- **Context:** `specs/changes/33-zwei-duschen/`: issue #33 wants two showers at the back wall, heads in the back corners, glass with a 60 cm passage in the middle. The door `TUER` is in the east wall, so the back wall is the west wall (x 5.59, borders Saschi). The Waschküche lies north (`ROOM_NAMES` 7.1, 4.4), so the north wall (y 2.62 .. 2.79) is the partition #30 will glaze in its top metre (ceiling 2.20 → sill 1.20).
- **Question:** strip depth, where the passage sits, and how to keep #30's metre free.
- **Decision:** strip 90 deep over the wall's full 2.22; panes at x 6.49 from each side wall to 30 cm short of the wall's middle (y 1.51), so the Parts (rails included) leave exactly 60 clear; heads on the west wall 30 from each side wall; limestone on the west wall and the strip's south-wall piece to 2.0, on the strip's north-wall piece only to 1.20. Nothing on the Bad side of the north wall above 1.20 (the lamp over the cistern goes). The north pane's end meets the north wall up to 2.0 (glass, not a fixture on the wall).
- **Why:** 90 × 111 per shower is a usual size and leaves 2.10 m for toilet and basin; the passage centred on the wall is "in der Mitte".
- **Alternatives:** 100 deep (only 2.00 left in front); passage aligned with the door (not in the middle).
- **Consequences:** #30 can place its glass anywhere along the north wall; at x ≤ 6.49 it sits above the NW shower's limestone, which ends at 1.20.

## 19:01 — #33: basin single 60 (was double 100) with mirror 80 × 85 on the east wall; toilet on the north wall; 3 lamps instead of 6 {#run-2026-11-15-1633-13}

- **Status:** open
- **Context:** with the strip on the west wall, the south wall keeps 35 cm between glass and window, and east of the window the open door leaf. The north wall may carry nothing above 1.20 (#30), so no mirror there. The only wall piece left for basin + mirror is the east wall north of the door's architrave (y 1.65 .. 2.62, 0.97).
- **Question:** where do toilet and basin go (the issue leaves it to us)?
- **Decision:** basin single 60 × 47 (one tap, as the Waschküche's) on the tiles of the east wall, centred on that piece, under a wood mirror 80 × 85 with two Wandlampen over it; toilet on the north wall at x 7.15 (≥ 40 free to the glass and to the basin's front, nothing within 60 in front); Taubenblau tiles stay on the north wall from the glass and on the east wall down to the door. Lamps: 2 over the mirror + the one left of the window (was 4 + 1 + 1 over the cistern).
- **Why:** the only arrangement that keeps the door leaf, the passage and #30's metre free; a 100 basin doesn't fit 0.97.
- **Alternatives:** double basin on the north wall without mirror (mirror is a must); toilet in the NE corner (then the basin has no wall).
- **Consequences:** one basin instead of two — the user may prefer a narrower double or a second mirror elsewhere.

## 19:01 — #33: rewrite the old Elternbad layout tests; the Rundgang stops in front of the glass {#run-2026-11-15-1633-14}

- **Status:** open
- **Overrides:** principles.md › never change a test to make it pass — here the issue changes the layout these tests pin (`test_elternbad_layout`, `test_elternbad_submodel`, `test_route_walks_into_the_elternbad_and_back_out`, the OG wall-light count).
- **Context:** the old tests assert the old shower, basin, lamp count and a Rundgang stop at x 5.95, which now lies inside the strip, behind the south pane.
- **Question:** rewrite or keep the tests; walk the camera through the 60 passage or not?
- **Decision:** rewrite them for the new layout (same kinds of checks, plus passage, toilet and #30 checks); the Rundgang walks in at y 1.15 and stops at x 6.85, 36 cm in front of the glass (south pane), looking through it at the back wall; turn right round and out as before. A new test keeps every Rundgang key in the Bad ≥ 0.25 m from its Parts.
- **Why:** the issue invalidates what they pin; a 60 passage leaves only ±5 cm for the 0.25 m camera clearance, which the route's smoothing could break.
- **Alternatives:** walk through the passage (risky clearance); leave the route (camera inside the glass).
- **Consequences:** tour goldens regenerated.
