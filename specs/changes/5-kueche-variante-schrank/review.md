---
feature: 5-kueche-variante-schrank
title: "Review: Küche – Variante mit Schrank an der hinteren Wand"
status: applied
order: 5
created: 2026-11-12
edited: 2026-11-12
---
# Review: Küche – Variante mit Schrank an der hinteren Wand

**Scope:** `git diff main` (working tree, uncommitted) plus `web/e2e/variant.spec.js` · **Reviewed:** 2026-11-12

## Defects

- [MEDIUM] Swing clock and redraw trigger include the hidden saloon leaves · `web/src/slides.js`
  `swingingNodes`, `web/src/main.js` · in the default layout about 40 % of the back hall's 3 s slots
  swung an invisible leaf; hidden leaves in the frustum forced redraws · **fixed**: the leaves of a
  variant get a clock of their own (Vitest `slides.test.js`), the redraw boxes count visible nodes
  only.
- [MEDIUM] `gaeste_wc.spec.js` "the doors swing too" could be satisfied by a hidden saloon leaf ·
  **fixed**: waits on the three back-hall doors by name.
- [MEDIUM] `show.py` framed variant objects with `cut=eg`, where they are hidden · **fixed**:
  `view(…, names)` picks `eg_alt` when the matched objects are `alt` only (`test_show.py`).
- [LOW] The variant cabinet's plinth starts at z 0.005 below the floor boards' top · same as the
  default cabinet C (`speis()`), recessed 6 cm behind the fronts · accepted (unchanged pattern).
- [LOW] The stub's rnd comes from `GEO[(c, "EG_Waende")]["r"][-1]` (order coupling) · accepted:
  the test now pins it to the wall segment's rnd, so a change of order fails loudly.
- [LOW] The stub test compared materials, not rnd · **fixed** (compares the rnd values).
- Security: none.

## Standards

- No hard breaches: README synced; the facts stay in the core (ADR-001-XEWL), the backends only call
  `default_layout()`; shared rnd respected; test adaptations are the ones the user allowed.
- Judgement calls (accepted): the opening and wall coordinates (5.24/5.49/4.33/5.249/3.73) are
  repeated between `build_eg()`, `speis()` and `speis_alt()`, as in the rest of the core; the
  `'eg_alt'` literal in `main.js`/`toolbar.js`; `HIDE.eg_alt` repeats `HIDE.eg`; the hand-built face
  list of the curved top rail; `o` reused for several objects in `speis()`/`speis_alt()`.
- `garden_layout()` sees the alt objects (inside the footprint, no effect on the grass).
- `variant.spec.js` saves a screenshot in a default test: as `ui.spec.js` does ("for the eye").

## Spec

- `plan.md` dimensions of C and B's back disagreed with the built ones (and `architecture.md`) ·
  **fixed** in `plan.md`.
- Step 3 `Verify:` ("only the hash line per sheet") was false for the EG sheet (the stub's hatch is
  its own rectangle, drawing order changed; the sorted lines are the same) · **fixed**: the Verify
  says so.
- The web test checked Gebaut only by a screenshot · **fixed** (asserts the variant there too).
- The saloon leaves swing only into the Speis, not both ways · accepted: the viewer shows the
  motion one way, like every other animated door.
- New test hooks `__fl.inks()` / `__fl.spot` (not in the plan) · accepted: needed by the web test,
  recorded in `architecture.md`.
- No ADR contradicted.

## Verdict

Defects 6 (3 MEDIUM, 3 LOW; 4 fixed, 2 accepted). Standards: no breach, judgement calls accepted.
Spec: 5 findings (3 fixed, 2 accepted). Nothing CRITICAL/HIGH.
