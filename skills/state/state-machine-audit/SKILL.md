---
name: state-machine-audit
description: One-file audit of every explicit and implicit state machine in the app, with states, invariants, transition tables, reachable invalid states with evidence, and prioritized fixes with regression tests. The long form of the implicit-state-machines hunt. Use when the user wants state machines documented in one place, a transition table, or an audit that ends in fixes, or runs /state-machine-audit.
argument-hint: [path]
---

# Audit the state machines and document them in one file

> Find the app's explicit and implicit state machines and document their states, invariants, and transition tables in one file. Identify invalid states or transitions the code can actually reach, with evidence, including through retries and concurrency. Prioritize confirmed bugs by impact, group related fixes into issues, then fix them with regression tests and keep the document updated.

Credited to @trevin in the Drix10/awesome-prompts collection. https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise the whole repo.

1. Discover. Find every state machine, explicit (an enum with a switch, a workflow table) and implicit (flags, status strings, nullable phases). Run /implicit-state-machines first if the repo is large.
2. Document. Write STATE_MACHINES.md at the repo root, or where the user says. One section per machine: name, where it lives, the states, the invariants the code relies on, and a transition table (from, event, to, guard).
3. Prove. For each machine, list the states and transitions the data permits but the table does not. Try to reach each one through a real path: retry, double submit, race between two async actions, error mid-transition, reload. Record the path as evidence. Drop the ones you cannot reach and say so.
4. Prioritize. Rate each confirmed bug 1 to 10 for how often it happens and 1 to 10 for how bad it is. Below 5 when multiplied: file an issue and leave the code alone. Group fixes that share a root cause.
5. Repair, only after the user has seen the document and agreed. One machine per change. Replace the flags or strings with an explicit type and an allowed-transitions table. Add a regression test that fails on the old code for each confirmed bug. Run the existing tests. Update the document so it matches the code.

## Report

Point at the document. Summarize the confirmed bugs with their scores, the issues filed, and anything left alone and why.
