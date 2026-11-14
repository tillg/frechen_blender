---
feature: 22-lampen-eg
title: "Review: Lampen im EG"
status: applied
order: 5
created: 2026-11-14
edited: 2026-11-14
---
# Review: Lampen im EG

**Scope:** `git diff origin/main` (working tree on `issue/22-lampen-eg`, 1 interim commit 42de283) · **Reviewed:** 2026-11-14

## Defects

- [MEDIUM] The hood's light sat 4 cm off the wall (against the 50 cm rule of `WALL_LIGHTS`) and the test pinned it ·
  code/kueche.py · hot spot on the tiles at dusk · **fixed**: 50 cm out, under the hood; test asserts it.
- [MEDIUM] `build_gaestebad()` / `build_elternbad()` returned wall lights without their tags · **fixed** (`wall_variant`),
  and `default_layout()` treats a missing tag list as "both layouts".
- [LOW] `build_kueche()` did not clear the light lists (grew on repeated calls) · **fixed**.
- [LOW] e2e `stages.spec.js`: the Stube check is a box (any light in the Stube) instead of the old fill light's exact
  point · accepted: the fill light is gone by request; the old check after `lookFrom` passed only by coincidence
  (the controls lift that camera to 3.3 m) and was dropped, the URL Stube view checks it properly.
- [LOW] Clearance checks the as-built leaves and the film-opened front door, not every animated sweep · accepted after a
  manual check: Büro door swings into the Bibliothek (lamp 2 in the Windfang), the leaf by lamp 23 is static, the Bad's
  sliding leaves run 45 cm from lamp 29, lamp 36 is 1.15 m from the back door's hinge (leaf 0.78) and 0.78 m from
  the WC door's (leaf 0.70); lamps 33/34 sit south of the WC wall, the WC door swings north.
- Verified clean: no reference to the removed lamp mechanism left in code/web/tests; Ofen light transform; viewer boot
  order (`lights` before `setCutaway`); sub-model pages don't use lighting; skip_words only on the Grundriss; strip
  and lip share rnd, normals opposed.

## Standards

- Fixed: orphaned `scale` of `lamp()` (its only user was the old reading lamp); module-level lambdas `m_`/`t_` → `_mid`,
  `_third`; a 2/6-space indentation in `test_tour.py`; the hires dusk test's alt exemption now tied to the layout.
- Accepted judgement calls: `kueche.py` appends its light to `WALL_LIGHTS` directly (it is not a Wandlampe); the
  placement test repeats the agreed list as literals (deliberate pin against the drawing); layout as strings
  "main"/"alt" (the existing `VARIANT` convention); parallel light lists (one per light, cleared together).

## Spec

- No missing lamp: per room as in the issue (34 rows + the Ofen bed's = 35, 33 per layout), hood strip present.
- Disclosed scope beyond the issue: the OG Bad Nadine & Till's leftover fill light removed (#3 forgot it).
- Stale plan wording (test names, the 3 removed tests) **fixed**; deviations from the drawing documented
  (lamp 1 at 13.57, lamps 13/14 on boards, skip_words instead of FURNITURE; Ansichten show the lamps through openings).
- No ADR contradicted; every ticked step's test exists and passes.

## Verdict

Defects 5 (worst MEDIUM, both fixed); Standards 4 hard (fixed) + judgement calls (accepted); Spec 1 stale-text item
(fixed). After the fixes: quick check green, parity green (only the film lights moved), house geometry unchanged by them.
