---
name: false-screens
description: Find every place where the screen can show something false. Stale data after a mutation, a success state that did not happen, a zero or empty list that is really a failed load, a spinner that never ends, a count that disagrees with the rows. Use when the user asks what the UI can lie about, about stale or misleading UI state, or runs /false-screens.
argument-hint: [path]
---

# Find every place where the screen can show something false

> Find every place where the screen can show something false.

Credited to @Nikzaaaaad in the Drix10/awesome-prompts collection, following Steve Ruiz's thread of 2026-10-31. https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise every screen, page, and component. Report only.

For each thing the screen asserts (a number, a status, a list, a success message, a button's enabled state), ask where the value comes from and whether the source can be wrong, stale, or missing at the moment it renders. Look for:
- A failed load that renders as empty, zero, or a default instead of an error.
- Success shown before the server confirmed, with no rollback on failure.
- A mutation that does not invalidate or refetch what it changed.
- A catch block that swallows the error and leaves the old data on screen.
- Loading flags that can stay true forever, or two flags that can both be true.
- Derived numbers computed from a different source than the rows they summarize.
- Hard-coded or mock rows left in a real screen.

For each candidate, name the user-visible lie and trace the path that produces it.

## Report

One line per finding: file:line, what the screen shows, what is actually true, and the path that gets there. Tier each Confirmed (path traced), Likely (shape present, path untraced), or Smell. Confirmed first. End with how many candidates you dropped.
