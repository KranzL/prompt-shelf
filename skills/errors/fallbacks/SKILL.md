---
name: fallbacks
description: Find every fallback and judge it. Mock data returned when the API fails, a default that hides a missing config, try A then B then C, an in-memory store when the database is down, a generated id when no match exists. Almost all are workarounds for a bug that should surface. Use when the user asks about fallbacks, mock data in production code, defaults that hide failures, silent degradation, or runs /fallbacks.
argument-hint: [path]
---

# Find every fallback

> grep -i fallback

From openai/codex issue 6356, where the reporter wrote: "Almost all fallbacks are hacks or workaround for various issues." https://github.com/openai/codex/issues/6356

## Run

Scope: $ARGUMENTS when given, otherwise the whole repo. Report only.

Start literally: search for fallback, fall back, falling back, default to, mock, sample data, placeholder, `||` and `??` after an await or a config read, and catch blocks that return a value. Then read each hit and ask: when this branch runs, what has gone wrong, and would the person running the system want to know? Fallbacks that hide a failure are the finding. Look for:
- Mock or sample data served when a request fails.
- `process.env.X || 'real-looking-default'` for anything that differs between environments.
- A chain of alternatives where the later ones silently change behavior.
- A second code path kept just in case that no test covers.
- An in-memory or file store used when the real one is unreachable.

Not a finding: a documented graceful degradation the product chose (a cached page when the origin is down, with a visible notice); a default for a genuinely optional setting.

## Report

One line per finding: file:line, what failure the fallback hides, what the system does instead, and who would want to know. Tier Confirmed, Likely, or Smell. End with how many candidates you dropped. If the user asks for a fix: remove the fallback, let the failure reach the error boundary, and test that a dead dependency fails loudly. The reporter of the Codex issue also notes that a no-fallbacks line in AGENTS.md helps; see /agent-rules.
