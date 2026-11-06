---
feature: desk
title: "Proposal: Desk sub-model with monitors, MacBook, keyboard and trackpad"
status: applied
order: 1
created: 2026-11-06
edited: 2026-11-06
---
# Proposal: Desk sub-model with monitors, MacBook, keyboard and trackpad

## What

The Büro desk in the Bibliothek (between the two north french doors) moves out of `house_core.py`
into its own module `code/desk.py` and becomes a sub-model like the Ofen: built alone for its own
page `web/desk.html` (linked from the house page, linking back), and placed into the house by
`desk.desk_neu()` at `DESK_AT`. On it: two large LG monitors showing the two screenshots of
`input/2026-11-06 input/` (`screen_a12.png` left, `screen_pilcrow.png` right), edge to edge at
about 170° (turned towards the chair); the MacBook Pro closed, left, partly under the left monitor,
with a softly lit Apple logo; a white Magic Keyboard and a white Magic Trackpad. Also (user, same
session): the back door gets a black lever handle inside and outside.

## Why

The user wants to remodel their desk apart from the house, the way the Ofen is worked on.

## Scope

- In: `code/desk.py` (the table as it is today, the chair at it, the devices); `build_desk()` and
  `--desk` export; `web/desk.html` + `web/src/desk.js`; the "Schreibtisch" link in the house tools
  and "← Haus" back; image textures for the two screens (Blender and viewer); tests; README.
- Out (non-goals): a new desk shape (the table keeps today's dimensions); content on the MacBook
  screen (no third screenshot); cables, lamps, other office furniture; changing the Ofen page.

## Expected outcome

- `http://localhost:5377/desk.html` shows the desk with monitors (the two screenshots legible),
  MacBook, keyboard and trackpad, dimension lines, three looks like the Ofen page.
- The house shows the same desk in the Bibliothek in "Eingerichtet"; the Blender render too.
- All tests green; parity golden regenerated deliberately; `.blend` rebuilt and saved.

## Open questions

none — assumptions (monitor model, sizes, which screenshot on which screen) are stated in
`architecture.md`.
