---
name: duplicated-truth
description: Find every place a value is stored twice and can drift apart. A count beside the rows it counts, a status on the parent and on the child, a cached copy with no invalidation, a derived field written instead of computed. Use when the user asks about duplicated state, two sources of truth, data that drifts or desyncs, or runs /duplicated-truth.
argument-hint: [path]
---

# Find every place a value is stored twice and can drift apart

> Find every place a value is stored twice and can drift apart.

Credited to @Nikzaaaaad in the Drix10/awesome-prompts collection. The longer form from the same collection:

> Find every piece of state or data that has more than one source of truth and could drift out of sync. For each, show where it's written, where it's read, and how they could disagree.

https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise the whole repo including the schema. Report only.

Look for:
- A value stored in two tables, two stores, or a store and a URL.
- A derived value (total, count, isComplete, displayName) persisted instead of computed, with the inputs also stored.
- A client-side copy of server state with its own setter.
- The same list of allowed values written out in two or more files.
- A cache with a write path that does not invalidate it.
- Denormalized columns with no trigger or job keeping them in step.

For each pair, find every write to each copy and check whether a single operation updates both. A write that touches one copy only is the drift path.

Not a finding: a deliberate cache with documented invalidation; a read model fed by events; a snapshot that is supposed to stay as it was.

## Report

One block per pair: the two locations, every writer of each, and the write that updates only one. Tier Confirmed (you found the lone writer), Likely, or Smell. End with how many candidates you dropped. If the user asks for a fix: pick the authoritative copy, compute or derive the other, and add a test that checks consistency across every consumer.
