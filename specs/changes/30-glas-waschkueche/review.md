---
feature: 30-glas-waschkueche
title: "Review: glazed top metre in the Bad / Waschküche partition"
status: applied
order: 5
created: 2026-11-16
edited: 2026-11-16
---
# Review: glazed top metre in the Bad / Waschküche partition

**Scope:** `git diff aa8b119...HEAD` (2 commits) · **Reviewed:** 2026-11-16

## Defects

- [LOW] `test_wandlampen_og_placements` hard-coded 1.10 instead of `waschkueche.LAMPE_H` · tests/test_core.py · drift
  not caught · **fixed**: uses the constant.
- [LOW] `lighting.test.js` re-pinned to new output · web/src/lighting.test.js:108 · rationale unverified · accepted:
  verified by computing the six nearest sites from the .glb (site 30 = Saschi's lamp, 25 = the west table lamp
  dropped); logged in decision run-2026-11-15-1633-34.
- [LOW] lowered lamps vs. table clutter not checked · accepted: a bbox sweep of all OG parts against the four lamps
  found no overlap; Show `tmp/web/30-waschkueche.png` shows the shades clear above the stacks.
- Checked clean: coplanar faces, shared rnd, global random stream (only OG_Innentueren, OG_Waende, OG_Wandlampen
  changed), sub-model = house.

## Standards

No hard breaches. Judgement calls: the opening + `oberlicht()` pair is wired at two call sites (house, sub-model)
as every sub-model's walls are (`waende()` pattern) — accepted; short local names in `oberlicht()` match the file's
style; the lighting re-pin (see Defects).

## Spec

- proposal said "satin glass 1.00 m high … glass to the ceiling": the 1.00 m includes the frame (glass 0.88 clear,
  head board 7 cm) · **fixed** in proposal.md.
- the test exempted the shower pane without checking it ends on the mullion · **fixed**: asserts the pane and its
  rail lie within the mullion's width and reach it.
- Show evidence: `tmp/web/30-waschkueche.png`, `30-bad.png`, `30-top.png`, `30-sub.png`, `30-waschkueche-up.png`.
- Test-first: both tests were seen red before the code (lamp test: placements; Oberlicht test: no glass), committed
  together.

## Verdict

Defects 3 (worst LOW), Standards 0 hard (judgement calls only), Spec 2 (worst: wording). Fixed: lamp constant,
pane-on-mullion assertion, proposal wording. Accepted: lighting re-pin, duplicated two-call wiring.
