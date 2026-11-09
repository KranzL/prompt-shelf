---
name: half-the-code
description: Take working code and do the same thing with half the code. Collapse speculative layers, inline single-use abstractions, flatten nesting with early returns, extract pure functions from side-effect code, name things for what they are. Use when the user says simplify this, too much code, autosimplify, make it smaller, half the code, or runs /half-the-code.
argument-hint: [path]
---

# Now the same but with half the code

> Great! Now the same but with half the code.

> Autosimplify.

> Put a lot of behaviour behind a small interface.

> Call a spade a spade: name the actual thing or action, not an abstraction that makes it sound more complicated.

From the Drix10/awesome-prompts collection, which credits the small-interface line to Matt Pocock's skills repo. https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise the code written or changed in this session. This skill changes code, so run the tests before you start and again after.

In this order:
1. Delete what nothing calls. Search before each deletion.
2. Inline every abstraction with one caller, every layer that forwards without changing anything, every option every caller sets the same way.
3. Flatten nesting with early returns, or with polymorphism when the branches are on a type.
4. Extract the pure part of side-effect code into a function with inputs and outputs, and leave the side effects thin.
5. Rename anything whose name is grander than what it does.
6. Remove comments that restate the line below them.

Keep behavior identical. No new abstractions, no new files, no new dependencies. If the halving needs a behavior change, stop and say so.

## Report

Lines before and after, what was deleted, inlined, flattened, extracted, and renamed, and the test run output. If a step would have changed behavior, name it and leave it undone.
