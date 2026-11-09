---
name: swallowed-errors
description: Find every error that gets swallowed silently. Empty catch blocks, catch-and-log with the flow continuing as if nothing happened, ignored error returns, promises with no rejection handler, errors turned into default values. Use when the user asks about swallowed errors, empty catches, ignored errors, silent failures, or runs /swallowed-errors.
argument-hint: [path]
---

# Find every error that gets swallowed silently

> Find every error that gets swallowed silently.

Credited to @Nikzaaaaad in the Drix10/awesome-prompts collection. https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise the whole repo. Report only.

Search first, then read. Look for:
- catch blocks that are empty, contain only a comment, or only log, with execution continuing past them.
- Error returns dropped: `_ = f()` or an unused error in Go, `let _ =` or `.ok()` on a Result in Rust, `except: pass` in Python, `.catch(() => {})` or a floating promise in TypeScript. Where a linter exists for this (errcheck, clippy unused_must_use, no-floating-promises), run it.
- Errors converted into a default: `catch { return [] }`, `catch { return null }`, `|| defaultValue` after an await.
- Error callbacks that set no state and show nothing.
- Logging at debug or info level for something that stops the operation.

For each, follow what the caller does next and what the user sees. The finding is the gap between what went wrong and what the system reported.

Not a finding: a catch that rethrows, wraps with context, or records the error where the caller can see it; an intentional best-effort call with no state depending on it and a note saying why.

## Report

One line per finding: file:line, what fails there, what the code does instead of reporting it, and what the user or operator sees. Tier Confirmed, Likely, or Smell. End with how many candidates you dropped. If the user asks for a fix: fix by class, one error boundary or one error reporter instead of twenty edited catch blocks, and let errors reach it.
