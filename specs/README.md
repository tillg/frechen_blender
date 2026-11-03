# specs/

What the Frechenlehen model does today, why, and the work in flight. **Truth pages** state current
rules in the present tense; git records how they got there. The workflow that maintains them is the
`spec` plugin in `.claude/skills/spec/` (`/spec:overview` explains it).

## What lives where

| Folder | Holds |
|---|---|
| `system/` | Truth pages: `domain.md` (start here), `architecture.md`, `functional.md` (what the model and film show today). |
| `architecture/` | Live ADRs, flat `adr-NNN-hhhh-slug.md` (`proposed`/`accepted`), plus the generated `index.md`. `architecture/archive/` holds `superseded`/`rejected` ones — history, not read by default. |
| `changes/<name>/` | One open change: `proposal.md`, `domain.md`, `architecture.md`, `plan.md`, and `review.md` once reviewed. Deleted at `/spec:archive` — git history is the archive. |
| `bugs/` | Known, unfixed bugs, one `<slug>.md` per bug with a `priority` and `areas`. The fixing commit deletes the file. Created with the first bug. |
| `templates/` | The page templates the skills copy. |

`DECISIONS.md` at the repo root logs choices made while nobody was there to ask (created on first use).

## The three rules

1. **One fact, one page.** A rule is stated in exactly one place; every other mention links to it.
2. **No history in truth pages.** No "previously", no dated banners, no change ids in headings. A
   replaced rule is edited in place. An ADR whose decision changes rewrites `## Decision` and adds
   one dated line to `## History`.
3. **Small pages.** A truth page ≤ 1,500 words, an ADR ≤ 1,500. Over the cap, split — never raise
   it.

## Frontmatter

Every page starts with YAML frontmatter. Change files carry `feature`, `title`, `status`, `order`,
`created`, `edited`; system pages only `title`, `created`, `edited`; bug files `title`,
`priority`, `areas`, `created`, `edited`; ADRs their own set. The schema and the `status`
lifecycle: `.claude/skills/spec/reference/frontmatter.md` and `adr.md`.

## Links

Relative markdown links only; keep the file name or ADR id in the link text. Cite ADRs by their
full id. Mermaid is the diagram format.
