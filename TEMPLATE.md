---
name: skill-name
description: What the prompt does in one sentence, then the words a user would say when they want it, then "or runs /skill-name".
argument-hint: [path]
---

# The prompt, as a title

> The prompt, verbatim.

Author, date. URL. If it came through a collection, name it and keep the per-line credit.

## Run

Scope: $ARGUMENTS when given, otherwise the whole repo. Report only; change nothing unless the user asks.

What to look for, in a few bullets. Where the problems hide (retries, concurrency, error paths). What is not a finding.

## Report

One line per finding: file:line, what it is, what goes wrong. Tier each Confirmed (traced a reachable path), Likely (shape is there, path untraced), or Smell. Confirmed first. End with how many candidates you dropped. If the user asks for a fix: fix by class, smallest diff, with a test that fails on the old code.
