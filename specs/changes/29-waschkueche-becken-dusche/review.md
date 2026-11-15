---
feature: 29-waschkueche-becken-dusche
title: "Review: basin and shower in the Waschküche"
status: applied
order: 5
created: 2026-11-15
edited: 2026-11-15
---
# Review: basin and shower in the Waschküche

Scope: `git diff 9d5b8be...HEAD` (efbb348 proposal, fda5924 implementation); three axes in parallel sub-agents.

## Defects

- [MEDIUM] Global random stream shifted (`hc.shower` head/drain draw `random.random()`; the floor patch and the
  2-basket cupboard change the number of draws), against the "own random stream" docstring. — **Fixed (docstring)**: the
  same pattern as `gaestebad`/`elternbad` (both call `hc.shower` the same way); later parts' per-board variation changes
  once, as with every earlier bath change. Accepted.
- [LOW] Circular import: `import waschkueche` before `house_core` fails (`WANDLAMPEN_OG` reads `waschkueche.BY` at
  module level). Same shape as `BATHS_OG` reading `elternbad.ROOM`; every entry point imports `house_core` first. Accepted.
- [LOW] The basin's sweep check covers only the basin's parts. Accepted: tiles and mirror sit on the wall (x ≥ 8.58),
  far outside the sweep (x ≤ 8.18).
- [LOW] Elternbad toilet filter bounded by `hi[1] < 2.62` instead of its room. — **Fixed**: uses the test's `room()`.
- [LOW] `basket_cupboard(n=3)` default not exercised. Accepted: the existing call relies on it, the result is unchanged
  (0.66).

## Standards

- Hard: two existing tests edited — the cupboard test (9 → 6 baskets, logged as override in run-2026-11-15-1633-21) and
  the Elternbad filter (scoped to its room; added to -21's Consequences).
- Drive-by: unused `YS`, `YN` in `waschkueche.py` — **fixed** (removed).
- Judgement: `DUSCHE[3]` indexed tuple; cabin numbers restated as literals in tests (deliberate: tests pin numbers);
  Waschküche facts at four places in house_core (each call site needs them). Accepted.

## Spec

- The glass door is built closed (proposal non-goal, -22) — the issue's "zu öffnende Tür" is modelled as a hinged leaf
  with hinges and grips, not animated. Flag for the user.
- The door has no top rail over it (only the fixed panes have one): deliberate, a frameless hinged door. Accepted.
- South-wall assertion was vacuous (its box started at y 3.56). — **Fixed**: now scans every Sanitaer/Fliesen/Spiegel
  part on the south wall's face above 1.20.
- Test-first: red runs were seen in the session (module missing; basin `BY` missing; Rundgang test red without the core
  wiring) but committed together with the code.
- Full check: 109/111; `bad.spec.js:49` green alone (load), `tour.spec.js:132` (~30 fps) the known load-flaky test,
  red alone too (8.98 fps).

## Verdict

Defects 5 (worst MEDIUM, fixed/accepted), Standards 3 (worst hard: test edits, logged), Spec 4 (worst: vacuous
assertion, fixed). No open CRITICAL/HIGH.
