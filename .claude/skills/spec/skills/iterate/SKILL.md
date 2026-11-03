---
description: Fold the user's annotations (->, xxx, [ACCEPTED], [REJECTED], [DECISION], comments) in the spec artifacts into a clean, consistent version
disable-model-invocation: true
argument-hint: "[change-name or document-path]"
---

The user marks up the artifacts of a change — arrows, acceptances, rejections, inline comments.
This skill digests the markup into clean, settled documents and keeps the four artifacts (and any
proposed ADR) consistent with each other.

**Read first**: `.claude/skills/spec/reference/frontmatter.md`, `plan.md`, `adr.md`.

**Input**: optionally a change name or one document path. Otherwise the single open change in
`specs/changes/`; several and none obvious → **AskUserQuestion** to pick.

**Steps**

1. **Read every artifact** of the change (`proposal.md`, `domain.md`, `architecture.md`,
   `plan.md`, `review.md` if present) and the `proposed` ADRs it links.

2. **Scan every line for annotations** — including inside code blocks, tables and Mermaid:

   | Annotation | Meaning |
   |---|---|
   | `->` | the user's chosen option or direction |
   | `xxx` | marked for removal |
   | `[ACCEPTED]` | confirmed |
   | `[REJECTED]` | remove |
   | `[DECISION]` | a decision was made — read the context |
   | inline comments | corrections, additions, questions |

   Don't skip any.

3. **Apply each**: rejected / `xxx` → remove cleanly, no stubs; accepted / `->` → promote to a
   definitive statement, drop the other options and the "Option A/B" framing; decisions → rewrite
   the surrounding text as settled; comments → apply corrections, incorporate additions, flag
   questions.

4. **Consolidate**: no option blocks or markers left; preserved structure; Mermaid diagrams updated
   to the settled state.

5. **Propagate across artifacts**: a rejected approach removes its plan steps (and their tests); a
   scope change in the proposal updates the architecture; new concepts land in `domain.md`; a
   settled decision updates the Key-decisions table and — if it meets the three criteria — its
   `proposed` ADR (`## Decision` rewritten in place; a dropped one becomes `status: rejected` and
   moves to `specs/architecture/archive/`; then `bash .claude/skills/spec/scripts/gen-adr-index.sh`).
   New or changed plan steps keep the `plan.md` format (`[kind]`, `Test first:`, `Verify:`).
   Minimal, traceable edits.

6. **Frontmatter**: bump `edited` to today on changed files. If the change was `exploring` and all
   four artifacts now exist, set `status: proposed` on every file. Never downgrade a status.
   Update `title` when a `# …` heading changed.

7. **Present for review** — annotations found and how each was applied, ambiguous ones that need
   clarification, cross-artifact updates — and **AskUserQuestion** whether to finalize.

**Output**

```
## Iteration complete: <name>

### Annotations applied
- proposal.md: 3 (2 accepted, 1 rejected)
- plan.md: 2 steps removed (rejected architecture option)

### Needs clarification
- architecture.md line 42: "maybe a listener?" — replace the model rule, or add to it?

Next: /spec:grill, more markup + /spec:iterate, or /spec:apply.
```

**Guardrails**

- Never skip an annotation; flag ambiguity rather than guess; the user has the last word.
- Remove rejected content without traces. Keep `status` identical across the change's files.
- Edit with the Edit/Write tools, not sed/python in Bash. Mermaid for diagrams.
