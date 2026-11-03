# Working principles

The rules every spec skill — and every change made outside the workflow — follows. The project's
`CLAUDE.md` imports this file, so it is the one place they are written.

## 1. Think before coding

Don't hide confusion; don't silently pick one reading.

- State assumptions as you proceed — don't gate on them.
- If several interpretations genuinely change the outcome and evidence can't decide, name them.
- If a simpler approach exists, say so, push back briefly, then proceed with the better one unless
  told otherwise.
- Stop and ask only for a truly ambiguous, costly-to-reverse fork. Everything else: proceed.

## 2. Simplicity first

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked. No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested. No error handling for impossible
  cases.
- Self-test: "Would a senior engineer call this overcomplicated?" If yes, rewrite.

## 3. Surgical changes

Touch only what the request requires. Match the existing file's style even if you'd do it
differently.

- Don't improve, refactor or reformat adjacent code that isn't broken.
- Remove imports, variables and functions **your** change orphaned. Leave pre-existing dead code
  alone — mention it instead.
- Test: every changed line traces directly to the request (for a spec change: to a plan step).
  Anything else is a drive-by — revert it or list it under "noticed this too".
- A user-visible change (feature, command, config, removed capability) updates `README.md` in the
  same change.

## 4. Test-first, goal-driven

Encode the success criterion as a test before writing code (`plan.md` in this directory):

- Bug fix → a failing test that reproduces it; confirm it fails; make it pass.
- Feature → a test for the new behaviour first, then implement.
- Refactor → run existing tests before and after; if the area lacks coverage, add a test first.

A step is done when its `Verify:` command passes. "Looks right" is not done. Never make a test pass
by weakening, skipping, deleting or mocking it without the user's explicit agreement.

## 5. Report plainly

Be concise. If tests fail, say so with the output; if a step was skipped, say that; when something
is done and verified, state it without hedging.
