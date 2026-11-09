---
name: unenforced-invariants
description: Find every invariant the application relies on but does not enforce, and every impossible state the data model permits. A parent that must have a child, a total that must equal its parts, an order that must have a payment before shipping. Use when the user asks about invariants, impossible states, assumptions the code makes, making illegal states unrepresentable, or runs /unenforced-invariants.
argument-hint: [path]
---

# Find every invariant the application relies on but does not enforce

> Find every invariant my application relies on but does not enforce.

> Find every impossible state my data model permits.

Both from the Drix10/awesome-prompts collection, which grew out of Steve Ruiz's thread of 2026-10-31. https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise the whole repo including the schema. Report only.

An invariant is a sentence the code would state as "always" or "never" if it could: a shipped order always has a payment; a user is never in two teams; items never total more than the invoice. Read the domain code and write those sentences down. Then for each, look for where it is enforced: a type that cannot express the violation, a constraint, a check at the boundary that writes. If there is none, find the path that violates it: a second entry point, a retry, a partial failure, a migration, a manual edit.

Also read the data model and list the states it can represent that the domain never intends. Nullable fields, independent booleans, and free-text statuses are the usual source.

For each candidate, construct the reachable counterexample. If you cannot construct one, it is a Smell, not a finding.

## Report

One block per invariant: the sentence, where the code relies on it, where it is or is not enforced, and the counterexample path. Tier Confirmed, Likely, or Smell. End with how many candidates you dropped. If the user asks for a fix: enforce each invariant at its authoritative boundary, prefer a type or constraint over a check, and add a regression test that constructs the old counterexample.
