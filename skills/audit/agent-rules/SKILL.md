---
name: agent-rules
description: Add standing rules to CLAUDE.md or AGENTS.md that stop the habits a hunt found. No implicit state machines, no fallbacks, no error handling for impossible cases, no abstractions for single-use code, surgical changes, no restating comments. Prefers a lint rule or a type over a sentence. Use when the user wants a habit prevented rather than cleaned up again, asks what to put in CLAUDE.md or AGENTS.md, or runs /agent-rules.
argument-hint: [habit to prevent]
---

# Standing rules for CLAUDE.md or AGENTS.md

The rules, with their sources:

- "Add to the global rules: never create implicit state machines; make state explicit when you write code." (Drix10/awesome-prompts, from the Steve Ruiz thread)
- "Don't add error handling, fallbacks, or validation for scenarios that can't happen." and "Do not hard-code values or create solutions that only work for specific test inputs." (Anthropic, Claude prompting best practices)
- A no-fallbacks policy. The reporter of openai/codex issue 6356 notes "Adding a no-fallbacks policy to AGENTS.md helps."
- "Do not design for rare or future cases nobody asked about." and "Ban comments unless the code is unusual for very good reason." (Drix10/awesome-prompts)
- Abstract only when there are three or more real call sites; do not create new files unless strictly required. (Codersera, 2026)
- Think before coding; simplicity first, no abstractions for single-use code; surgical changes, do not improve adjacent code; goal-driven execution. (Karpathy's four rules as summarized in 2026 posts)
- "Turn architectural rules into deterministic lint rules or construct the types so there's only one way to do something." (Drix10/awesome-prompts)

## Run

The habit to prevent is $ARGUMENTS, or whatever the last hunt in this session found. Read the project's CLAUDE.md or AGENTS.md first.

1. For the habit, prefer a mechanism over a sentence: a lint rule (no-floating-promises, errcheck, no-explicit-any, a custom rule for the status union), a type that makes the old shape unrepresentable, a test that fails on it, a CI check. Propose that first and offer to add it.
2. Only where no mechanism exists, propose the one or two sentences above that match, worded for this project, with the file and pattern that triggered it.
3. Keep the rules file short. Every rule added competes with the forty already there. If the file is already long, say which existing rule is weakest and could go.
4. Do not edit the file until the user has seen the proposal.

## Report

The mechanism proposed, the sentence proposed if any, and the diff to the rules file, waiting for approval.
