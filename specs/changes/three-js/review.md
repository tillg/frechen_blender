---
feature: three-js
title: "Review: shared Python core, glTF export and three.js viewer"
status: applied
order: 5
created: 2026-11-03
edited: 2026-11-03
---
# Review: shared Python core, glTF export and three.js viewer

**Scope:** `git diff 5f53d94...HEAD` (1 commit, b469b2f, 48 files) · **Reviewed:** 2026-11-03

Suites at review time: `python3 -m pytest -q` 32 passed (parity incl.), `npm test` 21 passed,
`npx playwright test` 16 passed (15 dev + 1 preview), actionlint exit 0.

## Defects

No CRITICAL/HIGH. Move of the builders into the core is faithful; `build()` resets all registries;
two builds identical; 0 mis-wound triangles in the glb.

- **[MEDIUM] Shrub leaves scale about the world origin during Massenmodell→Detailmodell** ·
  `web/src/garden.js:94` (`positionLocal.mul(uDetail)`) · three r187 `NodeMaterial.setupPosition`
  applies `instancedMesh()` (NodeMaterial.js:800) before `positionNode` (:804), so `positionLocal` is
  already instance-transformed; at p=1.5 east-bed leaves (x≈15) render at x≈7.7, inside the house.
  Grass (:75) only hides it because ground z≈0. No test covers in-between stages; confirmed from
  source, not screenshot · Fix: scale in instance space (rebuild matrices in `update(w)`) or about each
  instance translation; add an e2e at p=1.5.
- **[LOW] glTF accessor min/max written as float64** · `code/export_gltf.py:54-55` · 108/190
  accessors mismatch the float32 data → Khronos `ACCESSOR_MIN_MISMATCH`; three.js unaffected · Fix:
  round-trip through `struct.pack('<f')`.
- **[LOW] `SKIP_RND` stale, hides rnd regressions on `Laeden_Querbretter`** ·
  `tests/test_blender_parity.py:22` · comment "paint.py built it without rnd" no longer true · Fix:
  remove.
- **[LOW] Parity fingerprint misses parts moved within their object's bbox** ·
  `tests/blender/snapshot.py:27-36` · Fix: hash rounded vertex positions.
- **[LOW] Core facts duplicated** · `code/film.py:18,20` local `Z_OG`, `HOUSE_C`;
  `web/src/garden.js:12-16` re-implements `density()`, Vitest only checks JS against itself.
- **[LOW] Dead `sun` variable** · `web/src/main.js:54,57,82`.

**Security Concerns**

- **[MEDIUM] Pages workflow token scope** · `.github/workflows/pages.yml:10-13` · `pages: write` +
  `id-token: write` at workflow level reach the `build` job running `npm ci` (third-party install
  scripts) · Fix: `build` gets `contents: read` only, move `pages`/`id-token` to `deploy`; optionally
  pin actions to SHAs.

## Standards

**Hard violations** (minor)

- `code/build_house.py:91`: orphaned `# ---- geometry accumulator` header, now above
  `build_room_names` (principles §3).
- `code/paint.py:7`: docstring "Materialien aus build_house.py" is stale; they are `MAT_DEF` in the core.
- `code/film.py:18`: local `Z_OG = 2.70` despite importing `house_core` (ADR-001-XEWL; domain.md
  "import them from the core").

**Judgement calls** (Fowler baseline)

- **Repeated fact, diverging:** room-light height `z + 2.0` (`web/src/lighting.js:26`) vs `z + 2.1`
  (`code/film.py:168`); in neither core nor Blueprint. Strongest item.
- **Duplicated Code:**
  - `yup` ×4, two signatures (`main.js:12`, `lighting.js:7`, `garden.js:50`, `export_gltf.py:20`).
  - sRGB→linear ×3 (`paint.py:16`, `export_gltf.py:29`, `materials.js:13`).
  - Base-colour derivation ×3 (`build_house.py:31`, `export_gltf.py:92-95`, `materials.js:40-41`).
  - `ui.js:10-23` hard-codes `INK`/`PAPER`.
  - Absolute repo path hard-coded in 5 Blender scripts (`export_gltf.py:16` uses `Path(__file__)`).
- **Feature Envy vs ADR-001 "Backends only translate a Blueprint":** `export_gltf.py:152-158` reads
  `house_core.Z_OG/W_OUT/D_OUT/RIDGE_Z/DENSITY/…` as globals; `build_house.py:15` imports
  `Z_OG, ROOM_NAMES`.
- **Name convention as data:** `web/src/blueprint.js:29` `startsWith('Balkon_OG')`; a node extras flag
  would do.
- **Blender scene values copied into the viewer:** camera and sun (`main.js:25,27`,
  `lighting.js:8,11`). ADR-001 allows backend-only values, so this is a note.
- **Asymmetric names:** `Laeden_Querbretter` vs `OG_Laeden_Querbretter`. Documented.
- **Primitive Obsession:** rect/shrub tuples in `GardenLayout`, `ROOM_LIGHTS` triples.
- **Production-unused:** `mesh_ops.sub` is test-only; the `"e2e"` npm script is not in the plan.

## Spec

- **(a) Step 5 Verify not encoded:** "the diff to the previous golden touches only: the `Garten`
  shrub objects; the emitter …; `GA_Grasbuschel` … unchanged". `tests/test_blender_parity.py:35-41`
  only regenerates or compares the whole golden. The golden regenerations can't be audited from the
  single commit.
- **(a) Step 12** says "shutter region is bluish (with white cross boards)".
  `web/e2e/stages.spec.js:65-81` never checks the cross boards.
- **(c)/(f) ADR-001-XEWL broken:** room-light height 2.0 vs 2.1 (above, baked into the golden). README
  camera `build_house.py:230-231` vs `main.js:24-26`. Sun 50°/35° `build_house.py:216` vs
  `lighting.js:8`. `cutLevel` by name prefix.
- **(d) Shortcuts:**
  - stale `SKIP_RND` (above);
  - the `garden_layout` test (`tests/test_core.py:95-102`) only checks shrubs already inside a bed,
    so a shrub outside both beds passes. The plan asks "inside `Beet_Ost`/`Beet_West`".
- **(e) Tests weaker than the plan text:**
  - Step 11 "none are clay-coloured": `mid < 0.05` with mid = luma 110–205 (`stages.spec.js:37`), so
    clay (≈235) is never counted.
  - Step 11 "camera aimed at the closed south facade … inside the facade rectangle": the test compares
    whole-canvas ink from the default SE view (`stages.spec.js:43-51`).
  - Step 4 text still names a single `("EG","Laeden_Querbretter")` and "Parity is identical". The code
    splits the boards per storey; `architecture.md` was updated, `plan.md` not.
  - Step 16 was rewritten openly with reasons; not weaker.
- **Process:** apply-time choices (per-storey boards, open at Skizze/4 s per stage, sun toggle below
  p 1.5, `--use-angle=metal`) went into `architecture.md`'s decision table, not `DECISIONS.md` (which
  doesn't exist).
- **(b) Scope creep:** small and reasonable: extra mesh_ops/gltf tests, the UI panel-background
  assertion, per-stage glass `depthWrite`.

## Verdict

- Defects: 7 findings (2 MEDIUM: shrub leaves scale about the origin, Pages token scope; 5 LOW).
- Standards: 3 minor hard violations (worst: `film.py` local `Z_OG`) plus judgement calls (worst:
  room-light height 2.0 vs 2.1).
- Spec: 9 findings (worst: ADR-001-XEWL breach, light height diverging between backends; step 5/11
  tests weaker than plan).
- **Fixed before archive** (plan.md › "Review fixes", each test-first, seen red):
  - **Shrub leaves.** They now grow about a per-instance centre. Done with an
    `InstancedBufferAttribute`, because in r187 `instancedBufferAttribute(typedArray, 'vec3')` drops
    the instanced flag and reads the array per vertex. The first fix attempt hit exactly that; the
    test was tightened to cover the whole footprint and both beds.
  - **Room-light height.** `ROOM_LIGHT_H = 2.1` lives in the core and the scene extras. The viewer's
    lights move up 0.1 m; the Blender output is unchanged.
  - `film.py` reads `Z_OG`/`HOUSE_C` from the core.
  - glTF `min`/`max` are now float32.
  - `SKIP_RND` is removed.
  - Pages write tokens are scoped to `deploy`.
- Suites after the fixes: pytest 34 passed (parity unchanged), Vitest 21, Playwright 17
  (dev + preview), actionlint 0.
- **Accepted as is:** the remaining LOWs, Standards judgement calls and Spec test-weakness items:
  - parity fingerprint without vertex hash;
  - dead `sun` in `main.js`;
  - `density()` copy in `garden.js`;
  - camera/sun values in the viewer (allowed by ADR-001);
  - `Balkon_OG` prefix;
  - step 11/12 tests vs plan wording;
  - step 4 plan text;
  - `DECISIONS.md` vs the `architecture.md` table;
  - the minor stale comments/headers.
- **Noticed, not fixed:** the grass uses the same `positionLocal.mul(...)` pattern (`garden.js:75`).
  It scales only height, about world y = 0, so clumps float ~2.5 cm mid-transition. Not visible;
  left alone.
