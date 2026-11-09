---
name: useless-tests
description: Find every test that can pass when the feature is broken. Tests with no assertion, tests that assert the mock, tests weakened to pass, snapshots nobody reads, skipped tests, tests that catch and swallow the failure. Use when the user asks about test quality, tests that always pass, weakened or gamed tests, fake coverage, or runs /useless-tests.
argument-hint: [path]
---

# Find every test that can pass when the feature is broken

> Find every test that can pass when the feature is broken.

Phrasing that follows from the EvilGenie paper on test gaming (arXiv 2511.21654), which measured how often coding agents make tests pass without making the feature work. https://arxiv.org/abs/2511.21654

## Run

Scope: $ARGUMENTS when given, otherwise every test file. Report only.

For each test, ask what change to the production code would make it fail. If you cannot name one, it is a finding. Look for:
- No assertion, or an assertion on a constant, or `expect(true)`.
- The function under test mocked, so the test asserts the mock.
- `assert.ok(result)` or `toBeDefined()` where the shape or value matters.
- Try/catch around the body with the failure swallowed, or `assert true` in a rescue.
- `skip`, `only`, `xit`, `todo`, and commented-out assertions.
- Snapshot tests of large output that get updated without review.
- Expected values changed in the git history to match new output rather than the other way round. Check `git log -p` on tests that changed alongside the feature.
- Tests that pass only in a fixed order or with shared state.

Where it is cheap, prove it: break the feature on a scratch copy and run the test. A test that stays green is Confirmed.

## Report

One line per finding: file:line, the test, why no change to production would fail it. Tier Confirmed (you ran it broken), Likely, or Smell. End with how many candidates you dropped. If the user asks for a fix: fix the cause, never the test; write the assertion that fails on the broken feature, and show it failing before it passes.
