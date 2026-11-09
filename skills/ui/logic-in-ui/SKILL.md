---
name: logic-in-ui
description: Find every bit of business logic sitting in UI components that belongs in the domain layer. Pricing, permissions, validation rules, status derivation, date math inside render code. Use when the user asks about fat components, logic in the view, separating domain from UI, or runs /logic-in-ui.
argument-hint: [path]
---

# Find every bit of business logic sitting in UI components

> Find every bit of business logic sitting in UI components that belongs in the domain layer.

Credited to @Nikzaaaaad in the Drix10/awesome-prompts collection. https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise every component, page, view, and template. Report only.

Business logic is any rule that would still be true if the UI were deleted: how a price is computed, who may do what, what makes a record valid, which status a record is in, what counts as overdue. Look for it in render functions, event handlers, hooks that exist for one component, and template expressions. Signs:
- The same rule written in two components with slightly different wording.
- A rule the server also applies, written again on the client.
- Conditionals on role, plan, status, or money inside JSX, templates, or view controllers.
- Tests that mount a component to test a calculation.

Not a finding: presentation logic (formatting, layout, which icon to show), or a one-line call into a domain function.

## Report

One line per finding: file:line, the rule, and where it should live (an existing domain module if there is one). Group findings by rule, since the fix is one function per rule with the components calling it. Tier Confirmed, Likely, or Smell. End with how many candidates you dropped.
