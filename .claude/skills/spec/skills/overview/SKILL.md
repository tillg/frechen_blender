---
description: Show the spec workflow — where every open change stands, what's next, how mature it is — plus the workflow reference and a Mermaid diagram with the current step highlighted
disable-model-invocation: true
---

Show the workflow overview and assess the current status.

**Read first**: `.claude/skills/spec/reference/frontmatter.md`.

**Steps**

1. **Open changes**: `bash .claude/skills/spec/scripts/spec-status.sh`. None → "No open changes.
   Run `/spec:propose` to start one, or `/spec:tweak` for a small change." Also, if the project
   still lacks a client unit or e2e harness (`reference/a12.md`), suggest a first change that sets
   one up.

   Otherwise a table, one row per change:

   | Change | Summary | Phase | Next |
   |---|---|---|---|
   | `<name>` | 1 line from `proposal.md` | see below | see below |

   Phase from the frontmatter `status` (majority rule, `frontmatter.md`): `exploring` →
   Exploring; `proposed` → Proposed; `applying` → Applying (N/M); `applied` → Applied + "reviewed"
   if `review.md` exists. Warn under the table when files disagree on `status`/`feature`, or the
   status contradicts the checkboxes, or an `applied` change is older than a few days ("`specs/system/`
   is out of date until you archive").

   Next: Exploring → `/spec:propose`; Proposed → `/spec:grill`, markup + `/spec:iterate`, or
   `/spec:apply`; Applying → `/spec:apply`; Applied, no review → `/spec:adversarial-code-review`;
   Applied, reviewed → `/spec:archive`.

2. **Per change, a detail block**: read the artifacts; 2-line summary; the pipeline with the position
   marked:

   ```
   propose → [grill | iterate] → apply ← HERE (3/7) → adversarial-code-review → archive
   ```

   the next action; and an honest **maturity** rating — Ready / Almost there / Needs work — with 1–3
   sentences: thorough or thin artifacts, clear scope, key decisions and A12 impact covered, plan
   concrete and test-first (every step with `[kind]`, `Test first:`, `Verify:`; without them at best
   "Almost there"), open questions or placeholders.

3. **Decisions**: if `DECISIONS.md` exists, count open decisions and pending reverts
   (`decisions.md`); N > 0 → one line "Decisions: N open, P pending reverts — review before
   archive" and offer the review (**AskUserQuestion** "Review now" / "Later").

4. **System description and ADRs**: `specs/system/` present (list the pages) or missing (suggest
   writing it); `specs/architecture/index.md` — number of live ADRs, and whether
   `bash .claude/skills/spec/scripts/gen-adr-index.sh --check` is current.

5. **Write the diagram** `specs/workflow.md` (overwrite): a Mermaid `flowchart LR` of the pipeline
   `propose --> grill & iterate --> apply --> review --> archive`, the `tweak` side lane, and for
   each open change a `style <node> fill:#2e7d32,color:#fff` on its current node (none open →
   `propose`). Mention the path: "Diagram with the current step highlighted: `specs/workflow.md`
   (the `/spec-status` pane shows the same in the terminal)."

6. **Workflow reference** (print as is):

   ---
   # Spec workflow

   A lightweight workflow for thinking a change through before implementing it, adapted to A12.

   ```
   propose → [grill | iterate] → apply → adversarial-code-review → archive
   small change:  tweak (inline plan → test-first → specs/system → one commit)
   ```

   | Skill | Purpose |
   |---|---|
   | `/spec:overview` | Status, phase, maturity, this reference, `specs/workflow.md` |
   | `/spec-status` | The status pane (terminal sidebar; a mod, hence no `spec:` prefix) |
   | `/spec:propose` | Create a change: proposal, domain, architecture (A12 impact, key decisions, ADRs), test-first plan |
   | `/spec:grill` | Design-tree interview; answers folded into the artifacts |
   | `/spec:iterate` | Fold your markup (`->`, `[ACCEPTED]`, `[REJECTED]`, comments) into clean artifacts |
   | `/spec:apply` | Implement the plan test-first: red → green → verify → tick; A12 helpers per step kind |
   | `/spec:tweak` | Small change without a change directory: inline plan, test-first, one commit |
   | `/spec:adversarial-code-review` | Defects · Standards · Spec in parallel; writes `review.md` |
   | `/spec:archive` | Tests, decision review, `specs/system/` + ADRs updated, commit, delete the change |

   Artifacts live in `specs/changes/<name>/` (`proposal`, `domain`, `architecture`, `plan`,
   `review`), truth pages in `specs/system/`, ADRs in `specs/architecture/`
   (`specs/README.md`). `status` runs `proposed → applying → applied`; the directory is deleted at
   archive.
   ---

**Output shape**: `## Spec overview` → `## Open changes` (table + detail blocks) → `Decisions:` line
(if any) → `## System description & ADRs` → diagram path → `## Workflow reference`.

**Guardrails**: lead with the table; read the artifacts before judging; be honest in the maturity
rating; keep summaries to 2 lines; count checkboxes mechanically, never by eye.
