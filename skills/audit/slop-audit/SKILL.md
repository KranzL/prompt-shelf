---
name: slop-audit
description: |
  Audit a whole repo or a branch for the design habits AI coding agents leave behind, all at once and keyed by which models wrote the code: implicit state machines, swallowed errors, fallbacks to mock data, tests weakened to pass, over-abstraction, compat shims, duplicate helpers, phantom imports, stringly-typed state, restating comments, stray summary files, and more. Runs a scanner, maps habits to Claude, GPT, Codex, Gemini, Cursor, and open-weight models, proves each finding against a real code path, and fixes by class. Use when the user says slop, deslop, AI smell, clean up after Claude Code or Codex or Cursor or Gemini, "what did the model do to my code", or asks for a repo-wide audit of agent habits. Also use to refresh or research what people complain about with current coding models. For a single named hunt, use the matching prompt-shelf skill instead.
argument-hint: [path or branch]
---

# slop-audit

Coding agents have habits. Each model has its own, and the habits change with every release. This skill carries a catalog of those habits, a scanner that finds candidates fast, a map from model to habit, and a procedure that proves each candidate before fixing it. Diff-level "deslop" skills remove noise from one branch; this one audits the whole system, including the habits that only show up across files.

Three moves, always in order: Discover, Prove, Repair. Then Verify. Never repair what you have not proved. "Read the so-called bugs before letting it fix anything; half of them are not real bugs."

## Files

- `references/patterns.md`: the catalog. One entry per habit with looks-like, why, who, discover, prove, repair. Read the entries for the patterns you are running.
- `references/by-model.md`: which habits belong to which model, with evidence grades, and which pattern sets to run.
- `references/prompts.md`: the one-line prompts, verbatim with credits, by phase.
- `references/performance.md`: the performance lens (Drenova's checklist, the Abseil hints).
- `references/refresh.md`: how to re-research the catalog, with sources and queries.
- `scripts/scan.py`: grep-level candidate finder. `python3 scripts/scan.py <path> [--only a,b] [--exclude a,b] [--files -] [--json] [--list]`.
- `scripts/detect_models.py`: reads commit trailers and config files to say which agents touched the repo.

## Step 0: Scope

Decide three things before reading code.

1. **Where.** The whole repo, one directory, or a diff. For a branch: `git diff --name-only main...HEAD | python3 scripts/scan.py . --files -`. For a diff, also run the scope-drift check from `patterns.md`.
2. **Which patterns.** If the user gave one prompt ("find all of the implicit state machines"), run only that pattern and stop after the report; they asked a question, not for a cleanup. Otherwise pick the set in Step 1.
3. **Report or fix.** Read-only unless the user asked for fixes. "Audit", "find", "what's wrong", "report" mean read-only. "Fix", "clean up", "deslop" mean fix after proving.

## Step 1: Who wrote it

Run `python3 scripts/detect_models.py <path>`. It reads commit trailers (Claude Code, Codex, Copilot, Cursor, Gemini, Jules, Devin, Aider and others leave them) and lists agent config files. Trailers are a floor, not a census; Cursor and most IDE agents leave none. If it finds nothing, ask the user which tools and models wrote the code, or run the universal set.

Open `references/by-model.md`, take the universal set, and add the sets for the models found. Add `react-smells` for React code, `async-misuse`, `performance-waste`, and `hardcoded-config` for services and jobs.

## Step 2: Discover

Run the scanner first:

```
python3 scripts/scan.py <path> --only <chosen pattern ids>
```

It prints a summary table and candidates with file:line and a one-line note. It is a grep. It finds shapes, not problems, and it misses anything that needs reading. Its job is to point you at files.

Then the semantic pass. For each chosen pattern, read its entry in `patterns.md` and run its Discover prompt over the code, starting from the scanner's files and then widening. The three semantic-only patterns (duplicated-truth, false-screens, scope-drift) have no scanner signal and need this pass.

On a repo over a few hundred files, split the semantic pass across read-only search agents, one per pattern group. Give each one the pattern entries it owns, the scanner's candidates for those patterns, and the instruction to return file:line, the evidence (the reachable path or the type), and a tier. Keep the main thread narrow; short prompts get a fresh context window's full attention.

## Step 3: Prove

Tier every candidate with the pattern's Prove rule:

- **Confirmed**: a reachable code path or a type-level argument shows the problem. Quote file and line.
- **Likely**: the shape is there and nothing prevents the problem, but you did not find the path.
- **Smell**: the shape is there and the problem is not.

Drop everything below Smell and say how many you dropped. Then rate what is left: "Rate each bug from 1 to 10 on how often it would happen and how bad it would be. If the two scores multiplied are below 5, just file it as an issue and leave the code alone."

Deduplicate by root cause. A mock fallback, the catch that returns it, and the success toast it triggers are one finding with three symptoms, not three findings. The repair is at the root.

Respect the repo's conventions. If every service is a `Manager` class with an interface, that is a style, not slop. "A single loading flag, or framework-managed state with nothing layered on top, is not a finding."

## Step 4: Report

Use this shape, in plain words:

```
# Slop audit: <repo or path>

Scope: <whole repo | path | branch diff>. Written by: <tools and models, from trailers or the user>.
Scanned N files. M candidates, K kept (C confirmed, L likely, S smell), D dropped.

| pattern | confirmed | likely | smell | fix by class? |

## <pattern id>: <one-line summary of what is going on here>
- file:line  what is wrong  (tier)  evidence: <the path or the type>
  fix: <one line>
...

## Not findings
<things the scanner flagged that are fine, and why, so the user can trust the rest>

## Suggested order
1. <class-level fix that removes the most findings at once>
2. ...
```

Put the report in the reply unless the user asked for a file. Then stop if the mode is read-only. If the mode is fix, confirm the set to fix: recommend the class-level fixes first, and anything Confirmed and high severity, and use AskUserQuestion when it is available. The user decides scope; you do not widen it.

## Step 5: Repair

Fix by class, not by instance. Before touching the first instance of a pattern, "Exercise abstract thinking when considering this task." and ask "What higher-level abstraction would make this entire problem disappear?" Seven components with the same five booleans want one `AsyncState<T>` type, not seven edits. Ten string comparisons want one union and one exhaustive switch. Five wrappers want zero wrappers.

Then:

- One pattern per change set, so the diff is reviewable and revertible. If the user wants commits, one commit per pattern.
- "Smallest diff that satisfies the step. No drive-by refactors, renames, or formatting churn."
- Preserve behavior unless the finding is a bug. If it is a bug, write the regression test first and watch it fail.
- Repair at the authoritative boundary: the type that owns the state, the module that owns the rule, the one error boundary per layer.
- Do not introduce the habits you are removing. After each change set, scan your own diff: no new comments that restate code, no new TODO, no new `as any`, no new fallback, no new file where an edit would do, no deleted test.
- Run the project's typecheck, lint, and tests after each change set. "If a test fails, fix the cause rather than the test. If the test itself is wrong, say why."

## Step 6: Verify

Ask, for the whole change: "How do we make this change fully verifiable?" Then do it. For each pattern fixed, the proof is in its Repair section:

- The typechecker rejects the state or value that used to be possible.
- The regression test is red on the old code and green on the new.
- The dependency is killed (API down, env unset) and the app fails loudly where it used to fall back.
- The benchmark number moved, for performance fixes.

Report what actually ran, with the key output lines. "Don't claim a test passed unless it actually ran." If something could not be verified, say so first.

## Step 7: Prevent (when asked)

Offer standing rules from `references/prompts.md` for the user's CLAUDE.md or AGENTS.md, and a lint rule or type wherever one can replace a sentence. "Turn architectural rules into deterministic lint rules or construct the types so there's only one way to do something." Keep the rules file short; every rule competes with the ones already there.

## Refresh mode

When the user asks to refresh the catalog, research what people complain about with a model, or update the habits for a new release, follow `references/refresh.md`. It lists sources by evidence grade, the search queries that worked, and how to add a pattern to the catalog, the scanner, the fixture, and the model map.

## Guardrails

- Never delete or skip a test to go green. Never widen a type to silence an error. Never add a fallback to make a failure disappear.
- The scanner emits candidates. Never report a scanner hit as a finding without the Prove step.
- Read-only by default. Fixing is opt-in, and the set of fixes is the user's call.
- Do not flag trivial booleans, framework-managed state, boundary validation on untrusted input, or a project's deliberate conventions.
- Quote file and line for every claim. "For every number or claim, quote the file and line. If you can't, delete it."
