---
name: inconsistent-rules
description: Find every business rule implemented differently across entry points. The API, the UI, the CLI, the job, the import, and the admin tool each with their own version of validation, pricing, or permissions. Use when the user asks about rules duplicated across entry points, inconsistent validation, API versus UI drift, or runs /inconsistent-rules.
argument-hint: [path]
---

# Find every business rule implemented differently across entry points

> Find every business rule implemented differently across entry points.

From the Drix10/awesome-prompts collection. https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise the whole repo. Report only.

List the entry points: HTTP handlers, GraphQL resolvers, CLI commands, queue consumers, scheduled jobs, import scripts, admin pages, webhooks, tests that set up data directly. For each business rule (who may do this, what makes it valid, how it is priced, what state it moves to), find every entry point that applies it and compare the implementations line by line. Look for:
- Validation that exists on one entry point and not another.
- The same calculation with different rounding, defaults, or edge handling.
- Permission checks in the UI but not in the API, or in the API but not in the job.
- A state transition allowed by an admin tool that the main flow forbids.

The finding is the pair of implementations and the input where they disagree.

## Report

One block per rule: the entry points, the differing implementations with file:line, and an input that gets a different answer from each. Tier Confirmed (you have the input), Likely, or Smell. End with how many candidates you dropped. If the user asks for a fix: consolidate the rule at its authoritative boundary and test every entry point against it.
