---
feature: 34-alternativ-layout-standard
title: "Review: Alternativ becomes the EG layout"
status: applied
order: 5
created: 2026-11-15
edited: 2026-11-15
---
# Review: Alternativ becomes the EG layout

**Scope:** working-tree diff against `issue/35-nur-noch-threejs` (uncommitted) · **Reviewed:** 2026-11-15

## Defects

- [MEDIUM] README.md (house_core row) still described 35 EG lamps "je Aufteilung 33", the Essen west-wall pair "nur in der vereinbarten Aufteilung", "die der anderen Aufteilung bleiben dunkel"; film.py row "(vereinbarte Aufteilung)". Fix: rewrite to the one layout, 33 EG lamps. — **fixed**
- [LOW] Old `?cut=eg_alt` URLs / stored `eg_alt` views: no crash, fall back to the last entry or Ganzes Haus; the orphaned localStorage key stays. — accepted
- [LOW] `code/film.py` docstring "(WALL_LIGHTS, default layout)". — **fixed**
- [LOW] Lamp counts (69, 35 + 35 − 2, site indices) hard-coded in several tests. — accepted: the counts are the assertion.
- [LOW] `input/2026-11-14 input/lampen_eg_svg.py` names the removed layouts. — **fixed** (see Standards 2)

## Standards

1. HARD: README stale (as Defects). — **fixed**
2. HARD: `input/2026-11-14 input/lampen_eg_svg.py` broke (6-tuple unpack, 34 numbers asserted against 32 lamps). — **fixed**: numbers without 11, 12, 5-tuple, legend without layouts; runs. The agreed drawing itself stays as agreed.
3. HARD: `wandlampe(…, obj=None)` orphaned (added in #22 only for the per-layout objects). — **fixed**: parameter removed.
- Drive-by/naming: `alt` local in `slides.test.js` — **fixed** (`saloon`); `lighting.test.js` comment EG 33 = 32 + the Ofen bed's — **fixed**.
- Judgement calls, accepted: name-keyed clocks in `slides.js` (decision run-2026-11-15-1633-6, same pattern as `_Buerotuer`); object list repeated in `test_tour.py` (explicit names make a rename fail loudly); magic coordinate 3.715 for B's back in `test_eg_lamps_clear` (the board-back plane, as in the core); docstrings mentioning "the layout Alternativ (#5)" kept as provenance.
- specs/system stale — updated at archive.

## Spec

- Plan step 3 partial (README lamp sentences missed by its Verify grep) — **fixed**.
- Deletions match decision run-2026-11-15-1633-7; `show.view()` lost its `names` parameter (served only `eg_alt`): not scope creep, orphan removal.
- No ADR contradicted.

## Verdict

Defects: 5 (worst MEDIUM, fixed). Standards: 3 hard (all fixed) + judgement calls (accepted as above). Spec: 1 partial step (fixed). Final check re-run after the fixes.
