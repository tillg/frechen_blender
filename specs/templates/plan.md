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
cycle. A `[model]` step comes before the steps that use the model.>

## Steps

- [ ] [model] <step>
  - Test first: none — models have no unit harness; asserted by step 2
  - Verify: model validation green (`validate-a12-models`, else `gradle :import:build`)
- [ ] [server] <step>
  - Test first: `server/app/src/test/java/…Test.java` › `<case>` — fails today: <why>
  - Verify: `gradle test` → green
- [ ] [client] <step>
  - Test first: `client/src/tests/…test.tsx` › `<case>` — fails today: <why>
  - Verify: `cd client && npm run compile && npx vitest run` → green

System docs are updated at `/spec:archive`.
