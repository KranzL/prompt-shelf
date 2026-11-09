---
name: racing-async
description: Find every async action that can run twice or race. Double submits, overlapping fetches where the older response wins, effects that fire on every render, retries of non-idempotent calls, work whose correctness depends on timing or order. Use when the user asks about race conditions, double requests, retry safety, idempotency, stale responses, or runs /racing-async.
argument-hint: [path]
---

# Find every async action that can run twice or race

> Find every async action that can run twice or race.

Credited to @Nikzaaaaad in the Drix10/awesome-prompts collection. Two companions from the same collection:

> Find every operation that is unsafe to retry.

> Find everything whose correctness depends on timing or execution order.

https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise the whole repo. Report only.

For every async action (handler, effect, job, queue consumer, webhook), ask three questions. Can it start again before the first run finishes? If two runs overlap, which one wins, and does the result depend on the order they finish? If it is retried after a partial failure, does it do the work twice? Look for:
- Submit handlers with no disabled state, no in-flight guard, and no request id.
- Fetch-on-change with no cancellation or sequence check, so the slow older response overwrites the fast newer one.
- Read, then write, with no lock, version, or conditional update in between.
- Retry loops around calls that create, charge, send, or increment.
- Webhook or queue handlers with no idempotency key.
- Tests that pass only because awaits happen to resolve in order.

Build the interleaving on paper: two runs, the steps of each, and the order that breaks it. That is the evidence.

Not a finding: a pure read with no side effect; a handler already guarded by a mutex, a unique key, or a sequence number.

## Report

One block per finding: file:line, the two runs and the interleaving that breaks it, what ends up wrong. Tier Confirmed, Likely, or Smell. End with how many candidates you dropped. If the user asks for a fix: make the operation idempotent or deduplicate it, then add a test that runs it twice concurrently.
