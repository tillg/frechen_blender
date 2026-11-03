---
feature: <change-name>
title: "Plan: <short title>"
status: proposed
order: 4
created: YYYY-MM-DD
edited: YYYY-MM-DD
---
# Plan: <short title>

<Ordered, test-first steps — format and kinds in reference/plan.md. Each step is one red → green
cycle. A `[python]` core step comes before the `[blender]`/`[web]` steps that use it.>

## Steps

- [ ] [python] <step>
  - Test first: `tests/test_….py` › `<case>` — fails today: <why>
  - Verify: `python3 -m pytest -q` → green
- [ ] [blender] <step>
  - Test first: <check run in Blender via MCP> — fails today: <why>; else `none — visual only`
  - Verify: rebuild, render a still to `tmp/details/<name>.png` and read it: <what it must show>
- [ ] [web] <step>
  - Test first: `web/…test.js` or `web/e2e/….spec.js` › `<case>` — fails today: <why>
  - Verify: `cd web && npm test && npx playwright test` → green

System docs are updated at `/spec:archive`.
