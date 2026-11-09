---
name: magic-values
description: Find every magic number and hard-coded copy that should be a token or live in config. Unexplained numbers, timeouts and limits typed inline, user-facing strings in logic, colors and sizes outside the design tokens, URLs and ports in code. Use when the user asks about magic numbers, hard-coded strings, config that should be extracted, design tokens, or runs /magic-values.
argument-hint: [path]
---

# Find every magic number and hard-coded copy

> Find every magic number and hard-coded copy that should be a token or live in config.

Credited to @Nikzaaaaad in the Drix10/awesome-prompts collection. https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise the whole repo. Report only.

Look for:
- Numbers in logic with no name: `if (retries > 3)`, `setTimeout(fn, 30000)`, `.slice(0, 50)`, `* 1.08`.
- The same number or string typed in more than one file.
- User-facing copy inside logic or deep in components when the project has a strings, i18n, or content layer.
- Colors, spacing, font sizes, and breakpoints written inline when a token system exists.
- Hosts, ports, bucket names, and URLs in code; `process.env.X || 'some-default'` with a real value as the default.
- Role names, plan names, and feature keys as string literals compared in several places.

For each, ask whether a second person would need to know this value, whether it differs by environment, or whether it already exists under a name somewhere else.

Not a finding: 0, 1, and 2 in ordinary arithmetic; array indexes; a value used once right next to a clear name; test fixtures.

## Report

Group by value. For each: the value, every location, and where it should live (an existing config, token, or constants module if there is one). Tier Confirmed (repeated or environment-dependent), Likely, or Smell. End with how many candidates you dropped.
