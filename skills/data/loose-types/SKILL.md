---
name: loose-types
description: Find every place where a type is looser than the data. String where a union is known, any or unknown left in place, optional fields that are always present, a plain number or string for an id, object where a shape is known, a Record where the keys are fixed. Use when the user asks about weak types, any, stringly-typed code, tightening types, or runs /loose-types.
argument-hint: [path]
---

# Find every place where a type is looser than the data

> Find every place where a type is looser than the data.

Credited to @Nikzaaaaad in the Drix10/awesome-prompts collection. https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise the whole repo. Report only.

Compare each declared type with the values that actually flow through it. Look for:
- `string` for a field that only ever holds a fixed set of values (status, kind, role, currency).
- `any`, `unknown`, `object`, `interface{}`, `dynamic`, or `Dict[str, Any]` where the shape is known at the boundary.
- `as` casts and non-null assertions that paper over a type the code could narrow.
- Optional fields that every writer sets, or required fields that are sometimes missing.
- Ids as plain number or string with no brand or newtype, so a user id can be passed where an order id goes.
- Functions that accept a whole object and read one field.
- A `Record<string, X>` or map whose keys are a known finite set.

For each, point at the evidence that the data is narrower: the writers, the switch statements, the validation.

Not a finding: genuinely open data (user-provided JSON, plugin payloads); a boundary that parses into a narrow type right after.

## Report

One line per finding: file:line, the declared type, the type the data supports, and the evidence. Tier Confirmed, Likely, or Smell. End with how many candidates you dropped. If the user asks for a fix: tighten at the source of the value and let the compiler find every consumer; do not add casts.
