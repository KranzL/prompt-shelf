---
name: fully-verifiable
description: Make a change fully verifiable. A type that rejects the old state, a regression test that fails on the old code and passes on the new, a dependency killed to show the app fails loudly, the frontend actually clicked through, every acceptance criterion marked PASS, FAIL, or UNTESTED with evidence. Use before claiming a change is done, when the user asks for proof it works, how do we verify this, is this really fixed, or runs /fully-verifiable.
argument-hint: [change or branch]
---

# How do we make this change fully verifiable?

> How do we make this change fully verifiable?

Matt Pocock, 2026-11-05. He reports it "Makes the agent bend over backwards to verify all its changes. Signing up for real services, clicking through the frontend." https://x.com/mattpocockuk/status/2118313863917564136

Companions from the Drix10/awesome-prompts collection:

> Give me irrefutable proof this works now.

> Check every acceptance criterion: PASS / FAIL / UNTESTED, with evidence.

> Does the new test fail on the commit before the change?

## Run

The change is $ARGUMENTS, or the diff of the current branch against main, or the work done in this session.

1. Write down every claim the change makes: the bug is fixed, the feature works, nothing else broke, the migration is safe.
2. For each claim, choose the strongest verification available, in this order: a type or constraint that makes the old state impossible to express; a regression test that fails on the old code and passes on the new; the real system exercised end to end (start the app, click through, call the real service, kill a dependency and watch it fail loudly); a reproduction run by hand with output captured.
3. Do it. Run the test on the old commit and on the new one. Start the app. Capture output. Do not describe a verification you did not run.
4. Mark each claim PASS, FAIL, or UNTESTED. UNTESTED needs a reason you could not test it, not a hope.

Looks done is not done, and green tests written by the same agent are that agent grading its own homework, so prefer the kinds of evidence a reviewer can rerun.

## Report

A table of claims with PASS, FAIL, or UNTESTED and the evidence for each: the command, the key output lines, the commit the test failed on. Then what remains unverified and what it would take.
