---
name: abstract-thinking
description: Exercise abstract thinking before touching code. What higher-level abstraction makes the whole problem disappear, what are the irreducible constraints, what would a principal architect rewrite first, what single test breaks the design on day one. Use when a task feels tangled, before a refactor or a large fix, when the user says think abstractly, step back, zoom out, first principles, or runs /abstract-thinking.
argument-hint: [task or problem]
---

# Exercise abstract thinking

Five prompts, credited to @Wyrmfalls in the Drix10/awesome-prompts collection, and the one-line note from that collection's references folder. https://github.com/Drix10/awesome-prompts

> Exercise abstract thinking when considering this task.

> What higher-level abstraction would make this entire problem disappear?

> Reduce this problem to its irreducible constraints and rebuild it from zero.

> What would a principal architect immediately rewrite before even starting this?

> Design the single test that breaks this design on day one.

## Run

The task is $ARGUMENTS, or the problem the user has been describing. Do not write code yet.

Answer the five questions in order, in writing, briefly:
1. State the task one level up from how it was given. What is it an instance of?
2. Name the abstraction that would make the problem disappear. If the answer is a state machine, a single source of truth, an event log, or a type, say which and where it goes.
3. List the constraints that cannot be removed. Everything else is a choice. Rebuild the minimal design from the constraints alone.
4. Name what a principal architect would rewrite first, and why that first.
5. Write the one test that would break the current design on day one. If you cannot write it, the design may be fine.

Then compare: does the rebuilt design change the fix you were about to make? Say so, and propose the smallest diff that moves toward it. Stop and let the user choose before editing.

## Report

The five answers, each a few sentences, then the proposed diff in a sentence or two. No code until the user agrees.
