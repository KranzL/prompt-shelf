---
name: implicit-state-machines
description: Find all of the implicit state machines in the app. Boolean flags that only make sense together, status strings compared in many places, nullable fields whose null means a phase, and the impossible combinations they allow. Use when the user asks about implicit state machines, piles of booleans, flag combinations, status handling, or invalid states, or runs /implicit-state-machines.
argument-hint: [path or branch]
---

# Find all of the implicit state machines in my app

> find all of the implicit state machines in my app

Steve Ruiz, 2026-10-31. https://x.com/steveruizok/status/2116552016218710389

An implicit state machine is a set of values that together encode a phase of the program, without a type or table saying which combinations are legal. Every flag added to fix one bug quietly becomes a state.

## Run

Scope: $ARGUMENTS when given (a directory, a file, or a branch to diff against), otherwise the whole repo. Report only; change nothing unless the user asks.

Look for:
- Three or more booleans in one component, struct, or table that describe the same thing (isLoading, isError, isSuccess, hasSubmitted).
- A status or state string compared with == or switch in several files, with no union, enum, or table defining the allowed values and transitions.
- Nullable fields whose null means a phase (startedAt == null means not started).
- Branches that say "this should never happen", retries, and concurrency: that is where invalid states hide.

For each cluster, write down the states the code intends, the transitions it performs, and the combinations the data permits but the author never meant. Then trace whether an unintended combination is reachable: through a retry, a race, an error path, a reload. Walk the unhappy paths; a happy-path read never shows them.

Not a finding: a single loading flag; state a framework owns with nothing layered on top; a status union that already has an exhaustive switch.

## Report

Group by cluster. For each: the file and lines, the intended states, the reachable impossible combination with the path that reaches it, and a tier. Confirmed means you traced the path. Likely means the shape is there and the path is plausible but untraced. Smell means it only looks like one. Confirmed first. End with how many candidates you dropped.

The tiers come from kr4chinin's find-implicit-state-machines skill.

If the user then asks for a fix: one explicit status union or enum per cluster, an allowed-transitions table, and a test that fails on any transition not in the table. Make illegal states unrepresentable rather than guarded.
