---
name: over-engineering
description: Review code or a diff only for over-engineering. Unrequested abstractions, interfaces with one implementation, helpers with one caller, configuration nothing sets, defensive checks on values that cannot be null, new files and dependencies the task did not need. Use when the user says over-engineered, too abstract, too many layers, unnecessary complexity, or runs /over-engineering.
argument-hint: [path or branch]
---

# Review this only for over-engineering

> Review this diff only for over-engineering. Flag every unrequested abstraction, fallback, new file, and dependency. Propose the minimal version.

Codersera, 2026. https://codersera.com/blog/how-to-stop-claude-code-over-engineering-2026/

Three hunts that follow from it:

> Find abstractions with a single caller.

> Find configuration options that nothing sets.

> Find defensive checks on values that cannot be null by construction.

The first two follow from Anthropic's note that Opus 4.5 and 4.6 add abstractions and flexibility nobody asked for; the third paraphrases the Tildes thread "the coming loop". Anthropic's own rule, from the Claude prompting best-practices page: "Don't add error handling, fallbacks, or validation for scenarios that can't happen."

## Run

Scope: $ARGUMENTS when given (a branch to diff against main, a directory), otherwise the whole repo. Report only.

For a diff, first write down what the task asked for in one sentence, then flag everything in the diff that the sentence does not require. For a repo, look for:
- Interfaces, base classes, or generics with exactly one implementation or instantiation.
- Helpers, hooks, and utilities with one call site.
- Options, flags, and parameters that every caller passes the same way, or that nothing passes.
- Null checks, try blocks, and validation on values the type system or the construction already guarantees.
- Layers that forward calls without changing them (service calls repository calls client, each one line).
- New files that hold one small function; new dependencies for something the standard library does.
- Comments that restate the line below them.

Then propose the minimal version: what the code would look like with the abstraction inlined.

Not a finding: an abstraction with one implementation today and a second one the user confirms is coming; a boundary that exists for testing and is used by a test.

## Report

One line per finding: file:line, what it is, how many callers or implementations it has, and the minimal version. Tier Confirmed, Likely, or Smell. End with how many candidates you dropped. If the user asks for a fix: inline, delete, and collapse; smallest diff; do not add anything.
