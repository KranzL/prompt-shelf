---
name: unenforced-db-rules
description: Find every database rule the code assumes but the database does not enforce. Uniqueness checked only in code, foreign keys without constraints, required fields that are nullable, enums held as free text, invariants guarded only by the application. Use when the user asks about missing constraints, schema integrity, rules the database should enforce, or runs /unenforced-db-rules.
argument-hint: [path or schema]
---

# Find every database rule the code assumes but the database does not enforce

> Find every database rule the code assumes but Postgres doesn't enforce.

Credited to @Nikzaaaaad in the Drix10/awesome-prompts collection. Written for Postgres; it applies to any database with constraints. https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise the schema or migrations plus every module that writes to the database. Report only.

Read the schema first and list what it enforces: primary keys, unique constraints, foreign keys, not null, check constraints, enum types, triggers. Then read the code that writes and look for assumptions the schema does not back:
- A lookup by a column with no unique index, then an insert if nothing was found.
- An id column referring to another table with no foreign key.
- A field the code never writes as null, stored in a nullable column.
- A status or kind column of free text with a fixed set of values in code.
- A check in code (quantity above zero, end after start, one active row per user) with no constraint.
- A multi-row invariant kept by the application in a transaction that is not actually one.

For each, ask what happens on a race, a second code path, a manual fix in production, or a migration script. If any of them can write a row the code considers impossible, it is a finding.

## Report

One line per finding: the table and column, the rule the code assumes, where the code assumes it, and the path that can violate it. Tier Confirmed, Likely, or Smell. End with how many candidates you dropped. If the user asks for a fix: add the constraint, backfill or clean the rows that already break it, and keep the code check only where it gives a better error message.
