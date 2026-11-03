# Grilling and domain modelling

The interview `/spec:grill` runs. Adapted from Matt Pocock's `grilling` and `domain-modeling`
skills (mattpocock/skills, MIT License, © 2026 Matt Pocock); the outputs are redirected into this
project's spec files.

## The interview

Interview the user relentlessly until you reach a shared understanding. Map the change as a
**design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already
settled — the questions you can ask *now* without guessing at answers you haven't heard. Ask the
whole frontier in one round: number each question and give your recommended answer. Then wait for
the user's answers before the next round.

```
❓ **Q1** - **<question title>**: <question body; may offer choices>

➡️ <your recommended answer>

---

❓ **Q2** - …
```

Each round reshapes the tree: settled decisions push the frontier outward and unblock questions
that depended on them. A question whose answer depends on another question still open in this
round belongs to a *later* round.

**Facts are your job, decisions are the user's.** When a question needs a fact from the
environment (code, models, docs), look it up — dispatch a sub-agent or read the file — don't ask the
user for it. Don't block on it: only the questions downstream of a running lookup wait. The
*decisions* go to the user, and you wait.

The session is done when the frontier is empty: every branch visited, nothing silently assumed.
Don't act on it until the user confirms the shared understanding.

Start the first round from what the artifacts leave open, hedge on, or contradict; add the
grill seeds from `project.md` where the change touches the build, the film or the viewer.

## Keeping the model sharp (during the interview)

- **Challenge against the glossary.** A term that conflicts with `specs/system/domain.md` is called
  out at once: "The glossary defines *X* as …, but you seem to mean …. Which is it?"
- **Sharpen fuzzy language.** Vague or overloaded terms get a precise canonical term proposed:
  "'account' — the Customer or the User?"
- **Discuss concrete scenarios.** Stress-test relationships with specific edge cases that force
  precise boundaries between concepts.
- **Cross-reference with code and models.** When the user states how something works, check whether
  the code or the Document Model agrees; surface contradictions.
- **Capture as you go — don't batch.** A resolved term goes into the change's `domain.md`
  (concept section and Vocabulary table) right away; a term that changes a system term is noted as
  "changes system term X". A resolved decision goes into the `## Key decisions` table of the
  change's `architecture.md` (decision · alternatives · why) right away — and, only when it meets
  the three criteria in `adr.md`, becomes a `proposed` ADR (`scripts/new-adr.sh`).

Never write `GLOSSARY.md`, `GLOSSARY-MAP.md` or `docs/adr/`: the spec files are the record.
