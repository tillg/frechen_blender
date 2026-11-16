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
  - [19:36 — #32: shower SW, tub 180 × 75 along the west wall under the window, partition shortened to 6.15, WC niche to the SE, basin 60 on the north wall; 4 lamps instead of 5](#run-2026-11-15-1633-15)
  - [19:36 — #32: the tub built in, white ceramic shell with a limestone apron](#run-2026-11-15-1633-16)
  - [20:20 — #32: the user's addition: limestone shower floor and walls, glass instead of the partition, 9 cm further forward; tub 170](#run-2026-11-15-1633-17)
  - [20:45 — #32: the user's second addition: the shower glass 10 cm longer, to y 6.34; the way in 50 cm](#run-2026-11-15-1633-18)
  - [21:10 — #32: the user's third addition: a freestanding slipper tub after today's photo, head end to the shower, a glass pane between them; a new Fotos-Bereich "Gästebad"](#run-2026-11-15-1633-19)
  - [21:25 — #32: the user's fourth addition: the tub's tap out of the outer wall at the foot end, no standpipe](#run-2026-11-15-1633-20)
  - [21:07 — #29: shower cabin on the Waschküche's west wall north of the table, basin 60 on the east wall north of the machines; the basket cupboard shortened to two baskets per shelf](#run-2026-11-15-1633-21)
  - [21:07 — #29: the cabin's glass door built closed (no PIVOT/SWING), limestone on floor patch and west wall, one lamp over the mirror in the tower lamp's slot](#run-2026-11-15-1633-22)
  - [21:07 — #29: a module `code/waschkueche.py` without a sub-model page](#run-2026-11-15-1633-23)
  - [21:45 — #29: the user's change: cabin in the NW corner right of the door, two inward-folding glass doors, 20 cm to the cupboard; the room door opens 90°](#run-2026-11-15-1633-24)
  - [22:15 — Skip the baseline full check for stacked issues](#run-2026-11-15-1633-25)
  - [22:05 — #28: the whole Waschküche on the OG baths' limestone (`waschkueche.ROOM` in `BATHS_OG`); the cabin's own patch dropped; three oak assertions of #29 flipped](#run-2026-11-15-1633-26)
  - [22:27 — #27: "left wall" = east wall, "back end" = south wall; hooks over the whole east wall, the coats between Wandlampe 33 and the hook tips](#run-2026-11-15-1633-27)
  - [22:27 — #27: a dozen shoes = 6 pairs; coats and shoes as furniture `EG_Kleidung` with new fabric materials; the bench assertions replaced](#run-2026-11-15-1633-28)
  - [23:06 — #29 follow-up: one tweak branch for two user follow-ups, committed; the washer tower 4 cm from the table, the basin 15 cm from the tower](#run-2026-11-15-1633-29)
  - [23:10 — #31 bug: duplicates found by a 16 × 16 average hash (> 16 of 256 bits apart); two pairs, the larger copy kept, captions merged, the others in `DOPPELT`](#run-2026-11-15-1633-30)
  - [23:40 — #26: the hood as an island hood hung from the ceiling over the Halbinsel's cooktop; lip 65 above it; the Wamsler's pipe bends into the east wall at 1.80](#run-2026-11-15-1633-31)
  - [23:40 — #26: the hood and Haubenspots tests rewritten to the new place](#run-2026-11-15-1633-32)

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
  #33: branch issue/33-zwei-duschen from issue/31-fotos-anzeigen, PR https://github.com/tillg/frechen_blender/pull/39 (archived on the branch; full check: 3 reds, two pinned lamp count / label fixed and rerun green, the ~30 fps test flaky, green alone).
  19:55: on the user's request ("merge the pending PRs to main") PRs #36–#39 were merged into main (13692f8, c5b0f1a, 337cf95, 9290f63), branches deleted, issues #35 #34 #31 #33 [done]. Later PRs target main and wait for the user.
  #32: branch issue/32-dusche-badewanne from issue/33-zwei-duschen (now in main), PR https://github.com/tillg/frechen_blender/pull/41 (base main; archived on the branch; full check 110/111, the red a pinned old label, fixed, green alone).
  #29: branch issue/29-waschkueche-becken-dusche from issue/32-dusche-badewanne, PR https://github.com/tillg/frechen_blender/pull/42 (archived on the branch; full check 109/111: `bad.spec.js:49` green alone, the ~30 fps test load-flaky). After the user's change (-24, a post-archive change on the branch, system docs updated in place): full check 111/111.
  #28: branch issue/28-waschkueche-fliesenboden from issue/29-waschkueche-becken-dusche (a tweak that commits, as #35: no change directory, `specs/system/` updated in place; full check 109/111: `desk.spec.js:77` green alone, the ~30 fps test load-flaky, red alone at 8 fps), PR https://github.com/tillg/frechen_blender/pull/43.
  #27: branch issue/27-garderobe-jacken from issue/28-waschkueche-fliesenboden, PR https://github.com/tillg/frechen_blender/pull/45 (archived on the branch; full check 110/111: the ~30 fps test load-flaky, green alone; after the review fixes the quick check is red only on `test_vorlagen`'s input count, caused by the untracked `kleiner-schreibtisch.webp` of #44).
  ~23:20: on the user's request ("merge the pending PRs to main") PRs #41, #42, #43, #45 were merged into main (e3c743d, 28ca48f, 212f365, 090110b), branches deleted, issues #32 #29 #28 #27 [done].
  #26: branch issue/26-haube-induktion from fix/waschkueche-zwei-maschinen, PR https://github.com/tillg/frechen_blender/pull/47 (archived on the branch; full check: pytest red only on the pre-existing `test_vorlagen` input count, Playwright 109/111: `bad.spec.js:49` green alone, the ~30 fps test load-flaky).
  #29 follow-up + #31 bug (no issue of their own, decisions 29, 30): branch fix/waschkueche-zwei-maschinen from issue/27-garderobe-jacken (= main 090110b after the merge), PR against main, `Refs #29, Refs #31`, no labels; full check 110/111 + pytest 213/214: the ~30 fps test load-flaky (green alone), `test_vorlagen`'s input count red only from the untracked #40/#44 inputs.

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
  #32: the Gästebad's layout tests (`test_gaestebad_og_walls`, `test_gaestebad_og_shower`, `test_gaestebad_submodel`, the OG wall-light counts, `web/e2e/gaestebad.spec.js` labels; after the user's addition (-17) also the partition and the ceramic tray they pinned) rewritten for shower + tub; the Rundgang route unchanged (it only peeks in from the Flur), a new test keeps it ≥ 0.25 m from the Gästebad's Parts.

## 19:36 — #32: shower SW, tub 180 × 75 along the west wall under the window, partition shortened to 6.15, WC niche to the SE, basin 60 on the north wall; 4 lamps instead of 5 {#run-2026-11-15-1633-15}

- **Status:** open
- **Context:** issue #32: the OG Gästebad (x 0.31 .. 2.57, y 5.46 .. 8.57) gets a bathtub besides the shower. Entering through the Flur door (east wall, y 7.66 .. 8.47, leaf open flat against the east wall down to y 6.91) one faces the west wall (outer wall): a small high window (y 5.72 .. 6.32, sill 1.48) and the big window (y 6.77 .. 7.76, sill 0.75). The user wants the shower on the left (south) and the tub to its right along the back wall, with a view out of the window from the tub; basin and toilet "sensibly".
- **Question:** where do shower, tub, toilet and basin go, and what happens to the partition (over the EG Gäste-WC's) and the WC niche?
- **Decision:** shower in the SW corner, 101 × 131 (west wall to the partition, south wall to the tub), walk-in on the old tray, head on the south wall; tub 180 × 75 built in along the west wall from the big window's south edge (y 6.77) to the north wall, rim 0.58 under the 0.75 sill, back rest at the north end so one looks out of the window ahead to the right. The partition stays over the EG one but ends at y 6.15 (was 6.54), so the shower opens east between it and the tub (62 cm). The WC niche moves east of the partition (115 wide, toilet centred, Taubenblau tiles on its three walls). Basin single 60 × 47 on the north wall between tub and door (x 1.15 .. 1.75) with a wood mirror 80 × 85; lamps: two over the mirror, one over the tub's head end, one over the toilet (4; the west-wall lamp would now hang in the shower).
- **Why:** follows the issue's arrangement literally; the partition keeps the WC out of sight from the door and still stands over the EG one; the north wall is the only free wall for the basin (east wall: door and leaf; south: shower and WC).
- **Alternatives:** tub 170 from the north wall and the shower closed by glass to the north (a 42 cm throat to its entrance); no partition, toilet in the open room (WC seen from the door); basin double 120 (does not fit beside the tub).
- **Consequences:** OG wall-light count 32 → 31 (pinned in several tests, `lighting.test.js`, `stages.spec.js`); BATHS_OG follows `YP`; plan sheets re-exported.

## 19:36 — #32: the tub built in, white ceramic shell with a limestone apron {#run-2026-11-15-1633-16}

- **Status:** open
- **Context:** the issue leaves the tub's look open (no reference photo in `input/`); the tub stands between two walls (west, north) and the shower.
- **Question:** freestanding tub or built in?
- **Decision:** built in: a white `Keramik` shell (rim 6 cm, bottom at 0.15, rim top 0.58), its apron (east face) and south end (towards the shower) clad with the house's limestone (`hc.limestone()`, as in the Bäder's showers); a chrome deck mixer with spout on the south rim, drain at that end, the back rest end to the north. Own `random.Random(32)`.
- **Why:** a freestanding tub wedged against two walls and the shower looks wrong and wastes the 75 cm; the limestone ties it to the house's walk-in showers; materials reused from `MAT_DEF`.
- **Alternatives:** freestanding white tub on feet; Taubenblau tiles on the apron (they mark the WCs).
- **Consequences:** none beyond the new Parts in `<c>_Sanitaer` / `<c>_Fliesen`.
  Superseded by -19 (the user asked for the freestanding tub of today's photo).

## 20:20 — #32: the user's addition: limestone shower floor and walls, glass instead of the partition, 9 cm further forward; tub 170 {#run-2026-11-15-1633-17}

- **Status:** open
- **Context:** during the run the user added (via the coordinator): „Die Dusche im oberen Gästebad sollte als Boden auch die Stein fließen haben und auch die Wände die hintere und die Seite Wand sollten mit Stein fließen ausgelegt werden. Und die Wand zwischen Dusche und Toilette sollte durch eine Glaswand ersetzt werden, die etwas weiter nach vorne geht als die jetzige Wand.“ The layout of -15 has the shower in the SW corner, the partition (to y 6.15) between it and the WC niche, the tub from y 6.77.
- **Question:** which walls are "hintere" and "Seite"; how far is "etwas weiter nach vorne"; how does the shower keep its entrance when the glass reaches further towards the tub?
- **Decision:** floor: no ceramic tray, the room's limestone runs through (`tray=False`, as in the Bäder S and Großeltern); limestone to 2.0 on the back wall (west, around the small window: up to its sill 1.48 over the full width, above only beside it) and on the side wall (south, with the head, on the slabs); the partition goes, a glass wall stands on its west face line (x 1.319) from the south wall to y 6.24 (9 cm further forward than the wall's 6.15); the WC niche, now glass to the east wall, keeps the toilet centred between glass and wall. To keep the shower's entrance ≥ 60 cm clear between the glass and the tub, the tub is 170 (y 6.87 .. 8.57) instead of 180; the window still spans 89 cm of it.
- **Why:** "hintere Wand" = the back wall of -15 (west), "Seite" = the shower's other wall (south; the east side is the glass); a few cm forward is what "etwas" says, and more would close the way in; 170 × 75 is a standard tub.
- **Alternatives:** keep the 180 tub with a 50 cm entrance; glass further forward with a door; keep the partition and add glass in front of it.
- **Consequences:** the partition over the EG one is gone (its test rewritten, appended to -14); `BATHS_OG` splits the Gästebad at the glass line (one rectangle put the WC 2,30's floor probe on a joint); one draw less from `Random(18)` (the mirror's rnd changes).

## 20:45 — #32: the user's second addition: the shower glass 10 cm longer, to y 6.34; the way in 50 cm {#run-2026-11-15-1633-18}

- **Status:** open
- **Context:** the user (via the coordinator): „das glas der Dusche im oben Gästebad bitte noch 10cm länger“. The glass of -17 ran from the south wall to y 6.24, leaving 60 cm to the tub; a test pinned ≥ 60.
- **Question:** lengthen the glass at the cost of the way in, or keep 60 cm by shortening the tub to 160?
- **Decision:** the glass ends at y 6.34 (88 long); the tub stays 170, so the way into the shower is 50 cm (51.5 to the shower edge, 50.4 between glass rail and tub cap). The clearance test's bound goes from 60 to 50.
- **Why:** the user asked for exactly this; 50 cm is a usual minimum for a walk-in opening; a 160 tub is short to lie in, and the user did not ask to change it.
- **Alternatives:** tub 160 with 60 cm kept; a hinged glass door.
- **Consequences:** `test_gaestebad_clearances` bound 60 → 50 (the user's request supersedes the earlier own choice); labels "Glas 88", "Durchgang 52"; toilet lamp at y 5.90.

## 21:10 — #32: the user's third addition: a freestanding slipper tub after today's photo, head end to the shower, a glass pane between them; a new Fotos-Bereich "Gästebad" {#run-2026-11-15-1633-19}

- **Status:** open
- **Context:** the user (via the coordinator): „Und die Badewanne ersetzen durch eine wie im heutigen input directory. Mit dem Kopfende zur Dusche. Und zwischen der Dusche und der Badewanne auch eine Glasscheibe“. The photo `input/2026-11-15 input/badewanne.webp`: a white freestanding slipper tub on four claw feet, rolled rim, one end raised as a back rest, a floor-standing chrome filler. The tub of -16/-17 was built in (limestone apron), 170 from y 6.87. #31's photo pages assign every image of `input/` to one Bereich; none holds the OG Gästebad.
- **Question:** size and heights of the tub; where the pane and the filler go; which Bereich gets the photo.
- **Decision:** slipper tub 165 × 75 (body; the rolled rim 1.2 cm wider), 3.5 cm off the west wall, from y 6.89 to 8.54; rim at the head end (south, to the shower) 74, at the foot end 60 — both under the window's 75 sill, so the window stays free (the photo's head end is higher; here the sill limits it); four claw feet as turned white parts; filler beside the tub on the east at y 7.40 (short of the basin's 60 cm front zone), its gooseneck over the rim; drain at the foot end. A glass pane at y 6.865 from the west wall's slabs to 5 cm past the tub's east side; the shower's north edge moves 1 cm (6.855 → 6.865) to keep the way in at 50 cm (now measured to the pane's rail). The basin moves 1 cm east (1.45 → 1.46) to stay 5 cm from the wider tub. The photo goes to a new Bereich "Gästebad" (room "Bad" OG, marker in the room); `test_anchors_in_free_air_in_their_room` keyed PLAN_ROOMS by (name, storey), which holds the OG's two "Bad" only once — it now accepts any room of that name. The photo is copied by `vorlagen.py --copy`; the other new file in that folder (`waschtisch.avif`) is not part of #32 and stays untracked.
- **Why:** the user's words; 165 fits the 1.69 m between pane and north wall with air on both ends; a rim above the sill would cover the window the user wants to look out of.
- **Alternatives:** tub 170 touching pane and wall; head end 80 as in the photo (over the sill); the photo under "Ganzes Haus" (it is not house-wide).
- **Consequences:** the limestone apron and the built-in shell are gone; "Kopfende 74", "Rand 60", "Wanne 165 × 75", "Dusche 101 × 141", "Durchgang 53"; 56 pictures in `input/`.
  The floor-standing filler was replaced by -20.

## 21:25 — #32: the user's fourth addition: the tub's tap out of the outer wall at the foot end, no standpipe {#run-2026-11-15-1633-20}

- **Status:** open
- **Context:** the user (via the coordinator): „Und bei der Badewanne im Gästebad soll das Wasser also der Wasserhahn aus der Wand an der anderen Seite kommen also an der Außenwand nicht diese Stange, die mitten im Raum steht“. -19 had a floor-standing filler east of the tub.
- **Question:** which wall and where on it?
- **Decision:** a chrome wall tap on the west wall (the outer wall the tub stands along) at the foot end (y = tub end − 35 cm, 17 cm above the foot rim, under no window: the big window ends at 7.76): rosette, mixer body with lever, spout reaching 20 cm over the rim; a hand shower on a wall holder above it. Nothing stands on the floor beside the tub.
- **Why:** "an der anderen Seite" = the other end from the head end (the foot end); "an der Außenwand" = the west wall; the north wall at the foot is an inner wall.
- **Alternatives:** the tap on the north wall behind the foot end (inner wall, not what the user said).
- **Consequences:** `TAP` replaces `FY`; a test pins the tap on the outer wall at the foot end and nothing on the floor east of the tub.

## 21:07 — #29: shower cabin on the Waschküche's west wall north of the table, basin 60 on the east wall north of the machines; the basket cupboard shortened to two baskets per shelf {#run-2026-11-15-1633-21}

- **Status:** open
- **Overrides:** `CLAUDE.md` › Working rules — never make tests pass by changing them (`test_waschkueche_open_cupboard_with_laundry_baskets_on_the_west_wall` pins three baskets per shelf; the shortened cupboard holds two)
- **Context:** `29-waschkueche-becken-dusche`; issue #29 leaves the positions open („so wie du denkst“). The room (x 5.59 .. 8.59, y 2.79 .. 6.06, no window) is full: table on the whole south wall (to y 3.59), cupboard on the west wall (y 3.61 .. 5.95), washer, washer + dryer on the east wall (y 3.61 .. 4.85), door x 7.15 .. 8.17 in the north wall with its leaf open flat to the west (sweep r ≈ 1.0 about x 7.175). No free 1.10 × 1.10 square exists; the south wall is to stay free above 1.20 (#30 glazes it).
- **Question:** where do cabin and basin go, and what gives way?
- **Decision:** cabin outer x 5.59 .. 6.69, y 3.61 .. 4.71 (against the west wall, its south glass along the table's front edge); the cupboard keeps its place on the west wall, now y 4.73 .. 5.95, two baskets per shelf (6 instead of 9); basin 60 × 47 on the east wall centred y 5.28 (north of the tower, ≥ 5 cm outside the leaf's sweep), Taubenblau tiles 84 wide behind it, wood mirror 80 × 85 above.
- **Why:** keeps door, leaf, table and machines; the cabin's door faces the 1.28 m free middle of the room; nothing on the south wall; basin by the door like the WC 2,30's.
- **Alternatives:** NW corner (needs the room door at 90°, which would stand between door and cabin and block an east cabin door); SW/SE corner on the south wall (against #30); moving the machines to the west wall (larger rearrangement); shortening the table (its west part would still be blocked).
- **Consequences:** the table's west 1.10 m is only reachable from the east; #28 (tile floor) must absorb or leave out the cabin's floor rectangle `waschkueche.DUSCHE` (else coplanar slabs).
  Same override: `test_elternbad_layout`'s toilet filter had no northern bound and caught the cabin's hinge in the next room; it now uses the test's own `room()` scope.

## 21:07 — #29: the cabin's glass door built closed (no PIVOT/SWING), limestone on floor patch and west wall, one lamp over the mirror in the tower lamp's slot {#run-2026-11-15-1633-22}

- **Status:** open
- **Context:** `29-waschkueche-becken-dusche`; the issue asks for glass walls, one an opening door; animation and cladding are open.
- **Question:** animate the door? Limestone or blue tiles in the shower? Lamps over the mirror?
- **Decision:** the door (60 wide, north part of the east glass, hinged north, opening out) is built closed with two hinges and a bar handle each side, no PIVOT/SWING; floor patch and west wall in limestone to 2.0 like the house's other showers; one Wandlampe centred over the mirror at 2.10, in the `WANDLAMPEN_OG` slot of the tower lamp it replaces (entries may now carry their height).
- **Why:** an animated leaf adds viewer clocks and tests for little; limestone matches every other shower; the slot keeps `WALL_LIGHTS` order (viewer lighting tests index it).
- **Alternatives:** PIVOT + SWING leaf; Taubenblau tiles in the shower; two lamps like the Gästebad's 80 mirror (appended, shifting the light order).
- **Consequences:** none beyond the model; animation can be added later.

## 21:07 — #29: a module `code/waschkueche.py` without a sub-model page {#run-2026-11-15-1633-23}

- **Status:** open
- **Context:** `29-waschkueche-becken-dusche`; the brief allows a builder in house_core or a module.
- **Question:** where does the code live?
- **Decision:** `code/waschkueche.py` (constants `DUSCHE`, `BY`, …, builder `waschkueche_neu(c, z)`), house only.
- **Why:** #28 (floor) and #30 (south wall glazing) need the cabin's and the room's numbers; same shape as `elternbad.py`.
- **Alternatives:** functions in house_core (no reload entry, but the core grows); a sub-model page (not required).
- **Consequences:** reload entries in `build_house.py` and `garden.py`; CLAUDE.md lists the module.

## 21:45 — #29: the user's change: cabin in the NW corner right of the door, two inward-folding glass doors, 20 cm to the cupboard; the room door opens 90° {#run-2026-11-15-1633-24}

- **Status:** open
- **Context:** the user (via the coordinator), after PR #42: „Zu der Dusche in der Waschküche bitte platziere sie lieber, wenn man in die Waschküche reinkommt. Gleich rechts in dem Eck. Und sie soll im Eck sein mit zwei Glaswänden, die man aufklappen kann. Und dann noch ein Spalt von 20 cm bis zu dem Schrank.“ The door is in the north wall (x 7.15 .. 8.17); entering one faces south, so "rechts" is west: the NW corner (west wall × Flur wall). The room door's leaf, hinged at the west jamb, opened flat against that very wall (to x 6.19). The Schrank there is the basket cupboard on the west wall.
- **Question:** how do two glass walls open in a corner 20 cm from the cupboard and beside the door leaf, and where does the door leaf go?
- **Decision:** cabin outer x 5.59 .. 6.69, y 4.96 .. 6.06 (west and north wall clad in limestone to 2.0, head on the west wall); its south and east sides are each a glass **bifold door** (two panels on a wall profile, hinged between them, folding into the cabin — "aufklappen"), built closed; the cupboard runs from the table (y 3.612) to exactly 20 cm before the cabin (y 4.76), two baskets per shelf. The room door keeps its hinge but opens 90° (`flat=False`), its leaf standing at x 7.15, 46 cm east of the cabin.
- **Why:** outward-swinging leaves 1.09 wide could open only about 20° (the cupboard 20 cm away, the open room door 46 cm away); inward-folding panels need no room outside. A 90° leaf is how the house already opens doors where a corner is too close (CLAUDE.md › Interior doors).
- **Alternatives:** hinged outward doors (blocked as above); re-hinge the room door at the east jamb (its leaf would hit the basin); open the room door into the Flur (the Flur basin and the WC door are in the way).
- **Consequences:** the room door's leaf stands into the room; the cabin is outside its sweep; `test_waschkueche_open_cupboard…` finds the leaf by its 90° position; the "Hauswirtschaftsraum" plan label stays over the table.

## 22:15 — Skip the baseline full check for stacked issues {#run-2026-11-15-1633-25}

- **Status:** open
- **Overrides:** `/spec:apply` step 3 and `.claude/skills/spec/reference/project.md` — "The baseline before the first step of a change is the final check."
- **Context:** the user asked to find where the time goes (`tmp/timing/report_2026-11-15.md`): a full check takes 12–14 min (92 % Playwright, `workers: 1`); the baselines of #34, #31 and #32 cost 33 min although each base branch's final check had just run.
- **Question:** keep a full baseline per issue, or rely on the previous worker's final check?
- **Decision:** from #28 on, an issue stacked on the previous issue's branch uses `check.sh quick` as its baseline; the final full check at the end stays mandatory.
- **Why:** the base was verified minutes before; the quick tier still catches a broken base. ~5 min saved per issue.
- **Alternatives:** keep the full baseline (safer when the previous final check was not re-run after a last fix, as in #33/#32); run Playwright with more workers (bigger saving, but a test-config change the user should decide on tomorrow — in the report).
- **Consequences:** a red left by the previous issue shows up only in the next final check; the worker then fixes it as its own commit. Revisit with the timing report.

## 22:05 — #28: the whole Waschküche on the OG baths' limestone (`waschkueche.ROOM` in `BATHS_OG`); the cabin's own patch dropped; three oak assertions of #29 flipped {#run-2026-11-15-1633-26}

- **Status:** open
- **Context:** issue #28: „Die Waschküche soll keinen Holzboden bekommen, sondern einen Fliesenboden.“ The house has one tile floor, the limestone of the EG Flur and all baths/WCs (`floor_cover()`); #29 laid a limestone rectangle under the shower cabin only (`waschkueche.DUSCHE`), oak around it. Three assertions (`test_waschkueche_shower_cabin`: oak points around the cabin and "stone only inside it"; `test_bathrooms_have_limestone…`: HWR point (7.0, 4.0) oak) pin the old floor.
- **Question:** which tile, how to avoid two coplanar slab layers at the cabin, and what to do with the tests that pin oak?
- **Decision:** the bathrooms' limestone, laid over the room's inner outline `ROOM` = (5.59, 8.59, 2.79, 6.06) (new constant in `waschkueche.py`, added to `BATHS_OG` like `elternbad.ROOM`); the cabin's patch `[waschkueche.DUSCHE]` leaves the `floor_cover` call, so the cabin floor is part of the one tiling. The three oak assertions are flipped to limestone at equal strength (the requirement they pinned is superseded by the issue); a new test pins the whole room (no oak, none under walls, ≥ 95 % covered, no overlapping slabs, continuous across the cabin outline). Done as a `/spec:tweak` that commits (as #35, decision 3).
- **Why:** "Fliesenboden" in this house is the limestone of the baths (README: Kalksteinplatten); a second tile kind would be a new material nobody asked for. One rectangle instead of room + patch: `floor_cover` does not subtract corridor rects from each other, so both would z-fight.
- **Alternatives:** Taubenblau metro tiles (wall tiles, not floor); keep the patch and lay the room around it as an exclusion (more code, same picture).
- **Consequences:** the room floor rises 4 mm (oak top +0.014 → stone +0.018); the room door's leaf (bottom +0.010) dips 8 mm into it, as the Elternbad door does already. Plans: the elevations' painter order changed with the floor parts (no visible content change in `og.svg`). #30 can use `waschkueche.ROOM`.

## 22:27 — #27: "left wall" = east wall, "back end" = south wall; hooks over the whole east wall, the coats between Wandlampe 33 and the hook tips {#run-2026-11-15-1633-27}

- **Status:** open
- **Context:** `27-garderobe-jacken`, issue #27 (Garderobe ohne Bank, viele Haken links, Kleiderstange hinten mit fünf Mänteln, Schuhregal darunter). The niche is x 1.419 .. 2.358, y 5.475 .. 6.574; its open passage is in the north wall, so walking in you head south. The issue does not say how far the hooks run or how the coats share the 94 cm with the lamps on the partition and the hooks.
- **Question:** which walls, and how to fit hooks, rod coats and Wandlampe 33 (on the partition at y 5.84, 1.70, inside the coat zone)?
- **Decision:** left = east wall (hook board, as the old one), back end = south wall. Hook board over the whole east wall (1.35 .. 2.00), 23 hooks in two staggered rows (1.50 / 1.65), hat shelf raised to 1.95 so the upper row clears its brackets (now 14 deep). Rod 1.78 high, 27 cm from the south wall, wall to wall (Stahl); five coats at x 1.66 .. 2.16, i.e. clear of the lamp (≤ 1.63) and 8 cm clear of the hook tips (≥ 2.238). Shoe shelf 33 deep along the south wall, boards at 4 / 26 / 48 cm (two 20 cm levels). Wandlampen 33/34 stay.
- **Why:** "viele viele Haken" needs the whole wall; jackets on hooks hang flat by the wall beside the coats. The lamp positions come from the agreed lamp plan.
- **Alternatives:** hooks only in front of the coat zone (≈ 55 cm, ~12 hooks); move lamp 33 north (coats could spread over the full width, but the lamp plan changes).
- **Consequences:** the coats hang tightly (10 cm pitch). If the lamp is to move later, the coats can spread.

## 22:27 — #27: a dozen shoes = 6 pairs; coats and shoes as furniture `EG_Kleidung` with new fabric materials; the bench assertions replaced {#run-2026-11-15-1633-28}

- **Status:** open
- **Context:** `27-garderobe-jacken`: „ein Dutzend Schuhe“; `test_gaeste_wc_submodel` and `web/e2e/gaeste_wc.spec.js` pin the bench (35 × 110 at 45, "59 frei", "Bank 35 × 110", six hooks at 165, hat shelf at 185).
- **Question:** 12 shoes or 12 pairs; where the illustrating items live; what happens to the tests that pin the bench?
- **Decision:** 12 shoes = 6 pairs, 3 per level (Halbschuhe, Turnschuhe, Stiefel). Coats and shoes in a new object `<c>_Kleidung`, in `FURNITURE` (stage Eingerichtet, not on the plan sheets), from their own `random.Random(27)` with explicit `rnd`. New materials `Loden`, `Kamel`, `Anthrazit`, `Leder`, `Gummi`; `Jeans`, `Wolle`, `Leinen` reused. The bench/six-hooks/185 assertions are replaced by assertions of the new layout (the issue removes the bench).
- **Why:** literal reading; 4 pairs per 90 cm level would be crowded. Furniture keeps loose items off the architect's plans.
- **Alternatives:** 12 pairs (would need 4 levels or overlapping shoes); coats inside `_Garderobe` (on the plan sheets).
- **Consequences:** five new `FL_*` materials in the viewer; the plan sheet `eg.svg` changes (bench gone, rod and shoe shelf in).

## 23:06 — #29 follow-up: one tweak branch for two user follow-ups, committed; the washer tower 4 cm from the table, the basin 15 cm from the tower {#run-2026-11-15-1633-29}

- **Status:** open
- **Overrides:** `/spec:tweak` — unattended: "don't commit" (here: one commit per follow-up, as #35/#28 did, decision 3); the tweak is on a branch `fix/waschkueche-zwei-maschinen` without an issue of its own.
- **Context:** the user, after PR #42/#45: „In der Waschküche reichen zwei Waschmaschinen. Also bitte behalte den Turm an Waschmaschinen und nimm die dritte, die daneben steht weg. Dadurch können die beiden Waschmaschinen, die übereinander stehen, etwas näher an den Tisch verrutschen, und das Waschbecken kann auch noch etwas in diese Richtung und von der Tür weg.“ The tower stood at y 4.23 .. 4.85, the third machine at 3.61 .. 4.21 next to the table (to y 3.592); the basin on `BY` = 5.28. In the same branch the bug „die Toilette aus Mallnitz ist doppelt auf der Seite“ (Fotos & Vorlagen, #31).
- **Question:** how far do tower and basin move?
- **Decision:** the tower takes the third machine's place: y 3.632 .. 4.252, 4 cm from the table (enough to pull it out). The basin keeps its old relation to the tower: tiles 3 cm, basin 15 cm from it, `BY` = 4.70 (58 cm further from the door). Mirror and lamp move with it. One branch from `issue/27-garderobe-jacken`, one commit per follow-up, PR with `Refs #29, Refs #31`, no labels.
- **Why:** "etwas näher an den Tisch" = as close as the old third machine stood; the basin keeps the spacing that was agreed in #29 and gains the most distance from the door.
- **Alternatives:** centre the basin between tower and cabin (y ≈ 4.98, closer to the door than the user wants); a bigger gap to the table (the tower would block less of the table end, but the user asked for "näher").
- **Consequences:** the tour clearance test now also covers the tower (green: the Waschküche Standpunkt at (8.25, 3.3) keeps 33 cm). `og.svg` changes.

## 23:10 — #31 bug: duplicates found by a 16 × 16 average hash (> 16 of 256 bits apart); two pairs, the larger copy kept, captions merged, the others in `DOPPELT` {#run-2026-11-15-1633-30}

- **Status:** open
- **Context:** the user (screenshot of `vorlagen.html?b=garderobe`): „die Toilette aus Mallnitz ist doppelt auf der Seite“. `toilette mallnitz.jpeg` (4032 × 3024) and `bad_mallnitz.jpeg` (768 × 1024) are the same photo, not byte-identical. `test_every_input_image_is_assigned_once` wants every raster image of `input/` assigned exactly once; no PIL in `.venv`.
- **Question:** how to find near-identical photos, which copy to keep, and how to keep the "every image accounted for" rule?
- **Decision:** a regression test hashes every shown copy (`sips` → 16 × 16 BMP, grayscale average hash, min over the four 90° turns) and requires > 16 differing bits for every pair. Over all 56 photos it found two duplicates: the Mallnitz toilet (3 bits) and `ofenbett-1200x800.jpg` vs the Stube Entwurf `Pasted 04-11-2026 at 07.49.12.png` (10 bits; looked at: the same picture); the closest different pictures are 23 apart (the two Ofen sketches, the two Grundrisse). Kept the larger source each (toilette mallnitz, 4032 px; the Entwurf, 2382 px) with merged captions; the others go into `vorlagen.DOPPELT` (duplicate → kept), which the assignment test counts with the shown ones; their `web/public/vorlagen/` copies removed, input files kept.
- **Why:** threshold halfway between the duplicates (≤ 10) and the closest distinct pictures (≥ 23); sips is already the copy tool (macOS only, like `--copy`).
- **Alternatives:** byte or size comparison (misses rescaled copies); threshold 5 as briefed (misses the Ofenbett pair).
- **Consequences:** the test needs macOS `sips` (pytest is not run in CI). Stube 10 → 9 pictures, Garderobe 4 → 3. Code docstrings that cite `bad_mallnitz.jpeg` / `ofenbett-1200x800.jpg` as the model's source stay valid (the files remain in `input/`).

## 23:40 — #26: the hood as an island hood hung from the ceiling over the Halbinsel's cooktop; lip 65 above it; the Wamsler's pipe bends into the east wall at 1.80 {#run-2026-11-15-1633-31}

- **Status:** open
- **Context:** issue #26 („Abzughaube vom Wamsler verschieben zum Induktionsherd … das Ofenrohr vom Ofen weiter oben in die Wand laufen“). The cooktop (Kochfeld, x 7.18–7.95, y 3.12–3.58) lies on the Halbinsel, 60 cm from the east wall; no wall cabinets anywhere. The Wamsler already had a pipe, bent into the wall at 1.30 under the hood. The Rundgang passes south of the Halbinsel (nearest key (7.97, 2.75, 1.6)); the Küche Standpunkt (8.35, 2.7, 1.6) looks north-west across the cooktop.
- **Question:** what kind of hood, how high, and where does the pipe enter the wall?
- **Decision:** the same old-form steel hood (rolled lip, straight skirt, rail, canopy narrowing to a stack), made symmetric as an island hood hung from the ceiling, centred on the cooktop, 90 × 60 (cooktop 77 × 46), lip 65 cm above the cooktop (1.555), the stack 2 cm into the ceiling; the rail on the north (cook's) side; the four Haubenspots (#22) in a strip along its middle under the lip, the one light under its centre. The pipe (Ø 12, black) rises from the flue collar to 1.80, bends 90° into the east wall there, a rosette (Ø 20) on the wall face. Nothing else above the Wamsler.
- **Why:** the cooktop is not at a wall, so no wall chimney hood; 65 cm is the usual clearance; the old form keeps the look the user agreed to on 2026-11-10; 1.80 is "weiter oben" and stays under the Abzug's level.
- **Alternatives:** wall chimney hood on the east wall (not over the cooktop); a flat ceiling extractor (other look); lip at 70–75 cm (keep in mind if the Standpunkt view suffers).
- **Consequences:** the Rundgang passes 0.29 m from the hood's south face (guarded by `test_routes_and_spots_clear_the_kueche_hood`); the agreed drawing `speis_kueche_svg.py` does not show the hood and stays as it is. The Küche Standpunkt looked across the cooktop and the hood filled the top third of its view (`tmp/web/26-spot-60.png`): moved to (6.2, 3.3, 1.6) → (8.5, 4.8, 1.1), west of the Halbinsel, seeing sink run, Wamsler with its pipe, Ostzeile, cooktop and hood.

## 23:40 — #26: the hood and Haubenspots tests rewritten to the new place {#run-2026-11-15-1633-32}

- **Status:** open
- **Context:** `test_kueche_old_steel_hood_above_the_herd` and `test_haube_spots` pin the hood over the Wamsler at the east wall (lip 1.62, strip at `XE`, light 50 from the wall). Issue #26 moves the hood.
- **Question:** may tests be changed for this issue?
- **Decision:** replace them by `test_kueche_hood_over_the_cooktop` (centred on the cooktop, lip 65 above it, skirt, rail, a single tapering canopy, stack into the ceiling, clear of the Küche's parts) and a rewritten `test_haube_spots` (one strip, 4 evenly spaced spots under it, one light under the hood's centre); add `test_nothing_above_the_wamsler_but_its_pipe` and `test_wamsler_pipe_into_the_wall_higher_up`.
- **Why:** the issue itself asks for the move; the new tests keep every property of the old ones that still holds.
- **Alternatives:** keep the old tests (they cannot hold after the issue).
- **Consequences:** the comment "right of the hood" on Wandlampe 8 in `test_eg_wandlampen` becomes stale; reworded to "right of the Wamsler". `web/src/lighting.test.js` pins the six lit sites seen from the Stube: the hood's light (site 2) moved 1.4 m away, the Windfang's lamp (site 31) takes its place.
