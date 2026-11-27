---
feature: 61-umbauten
title: "Review: Umbauten EG/OG"
status: applied
order: 5
created: 2026-11-27
edited: 2026-11-27
---
# Review: Umbauten EG/OG

**Scope:** `git diff main` (uncommitted working tree, 0 commits) plus `code/garderobe.py` · **Reviewed:** 2026-11-27

## Defects

- [MEDIUM] Global random stream diverged after the EG floor cover, so untouched parts (roof, garden, balconies, OG floor) got new `rnd` · `house_core.build_slabs()` · **fixed**: `restream(st, EG_FLOOR_DRAWS)` with the exact count 1575, measured as a state match against main (the first count missed `random.uniform` draws); `test_umbau_61_keeps_the_rnd_of_untouched_parts` pins it.
- [MEDIUM] The limestone strip ended at `HALF` 0.964 while the WC opening reaches `WP` 1.024 · `bad.py` floor · **fixed**: limestone in the whole niche up to the leaf line. The toilet stays at its old axis 0.482 (accepted: 3 cm off the opening's centre, so lamp 30 and the tests stay unchanged).
- [LOW] `gaestebad.PA` is now a literal 1.319 · accepted: the EG partition is gone, so the OG glass has no EG wall left to follow.
- [LOW] Circular import: `garderobe.LAMPE_H` is read at house_core module level · accepted: the same pattern as `waschkueche.LAMPE_H` on main.
- [LOW] Burn counts were not checked · **fixed**: 44, 4, 103 and 1575 checked as exact state matches against main.

## Standards

- Tests removed or rewritten for removed features (hood, Garderobe in the back hall, Waschküche shower, two leaves): the user approved them explicitly (2026-11-27).
- `tmp/` reference to the drawing · **fixed**: the drawing and its generator are now in `input/2026-11-27 input/`.
- Smells (judgement calls, accepted): magic burn counts (named constants per site, explained in comments), local offset lambdas (the modules' existing style), `HALF` keeps its name with a new comment.

## Spec

- The proposal said the opening was "east"; it is the west opening over the WC · **fixed** in proposal.md.
- Vorlagen Bereich keeps its title "Garderobe & Gäste-WC" (accepted: e2e pins it, the photos still apply).
- The room name "Duschbad" on the plan sheets is not in the proposal (domain.md has it) · accepted, to be confirmed by the user.

## Verdict

Defects 5 (worst: rnd stream, fixed), Standards 3 (worst: test rewrites, approved by the user), Spec 3 (worst: a wording contradiction, fixed).
