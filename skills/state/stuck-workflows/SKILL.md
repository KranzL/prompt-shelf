---
name: stuck-workflows
description: Find every workflow that can become permanently stuck, and every successful operation that can leave the system inconsistent. A job that fails between two writes, a state with no transition out, a retry budget that runs out silently, a webhook that never arrives. Use when the user asks about stuck jobs, orphaned records, half-finished operations, partial failures, or runs /stuck-workflows.
argument-hint: [path]
---

# Find every workflow that can become permanently stuck

> Find every workflow that can become permanently stuck.

> Find every successful operation that can leave the system inconsistent.

Both from the Drix10/awesome-prompts collection. https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise every multi-step operation: jobs, queues, sagas, checkout flows, onboarding, imports, deploys. Report only.

For each workflow, draw its steps and ask at every step: if this fails here, or the process dies here, what state is left and who moves it forward? Look for:
- Two or more writes to different stores or services with no transaction, outbox, or compensation.
- A state (processing, pending, locked) with no timeout and no transition back.
- Waiting on an external event (webhook, callback, email click) with no expiry or reconciliation.
- Retries that give up and record nothing.
- A step that reports success to the caller before its side effects are durable.
- Cleanup that only runs on the happy path.

For each candidate, name the exact step where the process dies, the state it leaves, and who or what would notice.

Not a finding: a step already covered by an idempotent retry, a reconciliation job, or a transaction.

## Report

One block per finding: the workflow, the step, the state left behind, how it is or is not noticed. Tier Confirmed, Likely, or Smell. End with how many candidates you dropped. If the user asks for a fix: make each step idempotent and resumable, add a timeout or reconciliation for every waiting state, and add a test that kills the process mid-step.
