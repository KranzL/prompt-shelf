# Pattern catalog

Each entry is one design habit that coding agents leave behind, written so it can be run as a search-and-fix pass. Every entry has the same six parts:

- **Looks like**: the shape in code, so you recognize it while reading.
- **Why it matters**: the failure it causes, so you can judge whether a given instance is worth fixing.
- **Who leaves it**: which models and tools are associated with it, with the evidence grade from `by-model.md`.
- **Discover**: the one-line prompt to run over the code (quoted lines are verbatim from their authors; credits in `prompts.md`).
- **Prove**: what makes a candidate Confirmed, Likely, or only a Smell, and what is not a finding at all.
- **Repair**: the fix at the authoritative boundary, the class-level move, and how to verify it.

The scanner in `scripts/scan.py` emits candidates for every pattern that has a grep signal. It never emits verdicts. Three patterns are semantic only and have no scanner signal.

Catalog last refreshed 2026-11-08. See `refresh.md` to update it.

## Contents

High severity
1. implicit-state-machine
2. swallowed-errors
3. silent-fallbacks
4. test-weakening
5. phantom-apis

Medium severity
6. defensive-overkill
7. type-escape-hatches
8. compat-shims
9. duplicate-helpers
10. over-abstraction
11. god-files
12. stringly-typed
13. boolean-params
14. react-smells
15. async-misuse
16. hardcoded-config
17. performance-waste

Low severity
18. stub-code
19. restating-comments
20. leftover-debug
21. dead-code
22. generic-naming
23. stray-files
24. emoji-and-hype

Semantic only
25. duplicated-truth
26. false-screens
27. scope-drift

---

## 1. implicit-state-machine (high)

**Looks like.** Three or more booleans (`isLoading`, `hasError`, `isSuccess`, `isDirty`) or nullable slots (`data: T | null`, `error: E | null`) whose combination is the real state. Conditions like `isSuccess && !hasError`. A retry counter plus flags. Status strings checked in scattered handlers. Every bug fix adds one more boolean.

**Why it matters.** Four booleans is sixteen states on paper and maybe five real ones. The bugs live in the other eleven: the UI shows loading and error at once, a canceled task is written back as success, a flag is never reset. There is no transition table, so the spec is whatever order the handlers happen to run in.

**Who leaves it.** Every model. It is the default output for any loading/error/success UI. No model-specific evidence; the Steve Ruiz thread (October 2026) made it visible, and one reporter claimed 212 hits in a mid-sized open-source codebase (unverified).

**Discover.** "Find all of the implicit state machines in my app." Then: "For each one, list: the states, how it moves between them, any impossible or conflicting combinations, and the risk level. Rank by risk. Don't change any code yet."

**Prove.** Confirmed: a reachable event sequence produces an impossible combination (show the sequence and the handlers). Likely: the combination is representable and nothing prevents it, but no sequence was found. Smell: the flags exist but are always set together. Not a finding: "A single loading flag, or framework-managed state with nothing layered on top, is not a finding." Two flags that are genuinely independent are also fine.

**Repair.** One discriminated union or enum with a transition function at the boundary that owns the state (a reducer, a service method, a column with a check constraint). Derive the booleans from it (`const isLoading = state.kind === 'loading'`) and delete the stored flags. Add a test that fails on any transition not in the table. Class-level move: if several components share the shape, one `AsyncState<T>` type or one hook, not one fix per component. Verify: the typechecker rejects the fourth flag; the transition test is red on the old code.

## 2. swallowed-errors (high)

**Looks like.** Empty `catch {}`. Catch that logs and continues. Catch that returns `[]`, `null`, `false`, or `0`. `.catch(() => {})`. Bare `except:` or `except Exception: pass`. Go `if err != nil { return nil }` or log-and-fall-through. Rust `.ok();` or `let _ = f()?`. A broad catch at a layer that cannot do anything about the error.

**Why it matters.** A failure turns into a success far from its cause. One documented case: an auth failure returned sample data for three days before anyone noticed. Models are, in Karpathy's phrase, "mortally terrified of exceptions", so they wrap everything.

**Who leaves it.** Claude Code (strong: Anthropic's own guide says not to add handling for cases that cannot happen; an issue reports CLAUDE.md rules against it being ignored). Gemini 2.5 Pro (strong: try/except around everything even when told not to, May 2025). GPT models (medium). Universal in practice.

**Discover.** "Find every error that gets swallowed silently." "Find every place that catches an error and returns a default instead of surfacing it." Where the language has a checker for unchecked results (errcheck or `go vet` for Go, `clippy::unused_must_use` for Rust, `no-floating-promises` for TypeScript), run it; the scanner only sees the `if err != nil` shape and misses a call whose error return is never assigned.

**Prove.** Confirmed: the catch can be entered by a real failure (network, parse, permission) and the caller then proceeds as if it succeeded; name the caller. Likely: reachable, but the caller's behavior is unclear. Smell: a catch around code that cannot throw. Not a finding: a catch that rethrows with context; a catch at a true boundary (request handler, CLI main, job runner) that reports and exits non-zero; a best-effort path that is documented and observable (warn-level log with the failure and a metric), where the caller knows the result may be partial.

**Repair.** Delete the try/catch and let it propagate, or handle it at the one boundary that can do something: retry, tell the user, exit non-zero. Use typed results where the language has them. Class-level move: one error boundary per layer, not one per call. Verify: a test that injects the failure and asserts the caller sees it (error surfaced, non-zero exit, UI error state).

## 3. silent-fallbacks (high)

**Looks like.** Mock data returned when the API fails. `value ?? 'unknown'`. `process.env.API_URL || 'http://localhost:3000'`. Try A, then B, then C. Logs that say "falling back to". A JSDoc `@fallback` tag. Generating an id when no match exists. An in-memory store when the database is unreachable.

**Why it matters.** The demo works and the product does not. From the Codex issue tracker: "Almost all fallbacks are hacks or workaround for various issues." From Replit's forum: the model "has a strong tendency to produce fallback implementations or mock code whenever it isn't sure about something."

**Who leaves it.** Claude through Replit's agent (strong, September 2025) and Claude Code (medium, several fake-success write-ups). gpt-5-high in Codex (medium, November 2025). GPT-5 in Cursor (medium, "Pinocchio problem" thread). Cross-model.

**Discover.** `grep -i fallback`, then for each hit say which failure it hides. "Find every place where the screen can show something false." "List every hard-coded sample, placeholder or mock value in non-test code."

**Prove.** Confirmed: the fallback is reached on a real failure and nothing downstream can tell. Likely: reachable, downstream might detect it. Smell: a default for a genuinely optional value. Not a finding: explicit resilience with a contract, such as feature detection, a documented provider failover, or a default for optional config with a sane value, as long as it is observable. HyperDev's split: legitimate fallbacks are explicit and at the edges; problematic ones are implicit and inside application logic.

**Repair.** Throw instead of falling back. Make absence explicit in the type and handle it in the caller. Move defaults into one config module that fails at startup when a required value is missing. Delete mock data from production paths. Verify: kill the dependency (API down, env unset) in a test and confirm the app fails loudly.

## 4. test-weakening (high)

**Looks like.** `it.skip`, `xit`, `.only` left in. `expect(true).toBe(true)`. Tests with no assertion. try/catch inside a test. Mocks of the module under test. Mocks of a class that does not exist. Assertions loosened in the same commit as the code they cover. `passWithNoTests`. Deleted tests. Production code that special-cases the test's inputs.

**Why it matters.** The suite stays green while the behavior is wrong. "Tests the same agent wrote will pass by design." The EvilGenie paper documents agents hard-coding test expectations and editing test files to pass.

**Who leaves it.** Claude Code (medium: issue "manipulates tests instead of following instructions"; a 2026 write-up titled "that time it tried to delete all my tests"; Anthropic's guide: "Do not hard-code values or create solutions that only work for specific test inputs"). Codex (medium: reports PASS without real verification; one case deleted all tests when two rules conflicted). Gemini CLI (medium: EvilGenie runs). Kimi, Qwen, Grok in a 2026 Rails benchmark (medium: `rescue => e; assert true`). Cross-model.

**Discover.** "Find every test that can pass when the feature is broken." "Diff tests against main and list assertions that got weaker or removed." "Find tests that assert less than their name claims."

**Prove.** Confirmed: break the code under test and the test still passes. Likely: no assertion on the behavior the test name promises. Smell: a skip with a tracked reason. Not a finding: a skip with a linked issue and a reason; a snapshot test on stable output; an integration test skipped without credentials.

**Repair.** Restore the assertion the name promises. Delete tests that only test their mocks. Un-skip or delete with the reason in the commit message. For a bug fix, write the regression test first and watch it fail on the old code. Never special-case test inputs in production code. "If a test fails, fix the cause rather than the test. If the test itself is wrong, say why." Verify: run the suite with the fix reverted and confirm red.

## 5. phantom-apis (high)

**Looks like.** Imports of packages not in the manifest. Calls to methods that do not exist on the installed version. Invented fluent DSLs (`c.user()`, `client.chat(messages: [...])`). Tests that mock the invented class so everything passes. API shapes from an older major version.

**Why it matters.** It fails only at runtime, or never fails because the mock hides it.

**Who leaves it.** DeepSeek V3.2, Qwen 3 Coder Next, MiniMax M2.7, GLM 5.1 (medium: one detailed Rails benchmark, April 2026). Gemini (weak). Any model on a library that changed after its training data.

**Discover.** "Check every imported symbol and method call against the installed dependency version and list the ones that don't exist." Run the scanner's phantom-apis check first (manifest level), then the typechecker or compiler, then an import smoke test (symbol level).

**Prove.** Confirmed: install and call it; ImportError, TS2305, or "undefined is not a function". Likely: declared, but the symbol is not in the pinned version. Smell: the manifest lacks it but a parent workspace provides it.

**Repair.** Read the installed package's types or docs, not memory. Pin the dependency. Delete the mock of the nonexistent class and test the real integration behind a boundary. Verify: typecheck, compile, and one real call in a smoke test.

## 6. defensive-overkill (medium)

**Looks like.** Null checks on values the type guarantees. `typeof x !== 'undefined'`. `x ? x : []`. Optional chaining three deep. `Array.isArray(x) ? x : []`. try/catch around code that cannot throw. isinstance sniffing in typed Python. "Just in case" comments. The same validation repeated in every layer instead of once at the boundary.

**Why it matters.** It hides invalid states instead of making them impossible, and it buries the real logic. One reviewer cut a 1000-line class to 300 lines by removing single-use abstractions and this. Anthropic's guide: "Don't add error handling, fallbacks, or validation for scenarios that can't happen."

**Who leaves it.** GPT models (strong: Tildes thread, 2026, "I've ever had a situation where I didn't have to first remove a bunch of useless defensive checks"). Gemini 2.5 Pro (strong). Claude Code (medium: the deslop skills all target "defensive checks unusual for trusted paths").

**Discover.** "Find defensive checks on values that cannot be null by construction." "Find validation repeated inside a module that is already checked at its boundary."

**Prove.** Confirmed: the type or the single call site proves the guarded case impossible. Likely: all current callers rule it out but the type allows it. Not a finding: checks at module boundaries on untrusted input; checks the type system cannot express.

**Repair.** Tighten the type so the check is unnecessary, then delete the check. Parse once at the boundary instead of validating everywhere. Early returns instead of nested guards. Verify: typecheck passes with the check removed; one boundary test covers the malformed input.

## 7. type-escape-hatches (medium)

**Looks like.** `as any`, `as unknown as`, `@ts-ignore`, `eslint-disable`, `!` non-null assertions, `# type: ignore`, `Any`, `interface{}`, `#[allow(...)]`, dense `.unwrap()`, `@SuppressWarnings`.

**Why it matters.** The compiler found a real mismatch and was told to be quiet. The casts travel with copy-paste.

**Who leaves it.** Universal (medium). Cleanup skills name "any casts that only bypass type errors" as a standard target.

**Discover.** "Find every place where a type is looser than the data." "List every cast or ignore and say what type error it hides."

**Prove.** Confirmed: removing the escape produces a type error that points at a real bug or a wrong type. Likely: removing it produces an error that a better type would fix. Not a finding: an escape with a written reason at a real library boundary (`@ts-expect-error` with an explanation, `# type: ignore[code]` with a comment).

**Repair.** Fix the type at the source: narrow with a type guard, parse with a schema, correct the signature. Keep escapes only at boundaries, each with a reason. Verify: typecheck with the escape removed.

## 8. compat-shims (medium)

**Looks like.** `export const oldName = newName`. `export * from './moved'`. A deprecated wrapper beside its replacement. `_v2` functions. "Kept for backwards compatibility" in a repo with no external consumers. Renamed re-exports.

**Why it matters.** Nobody asked for compatibility. Two names for one thing, and the old one is what the next agent finds first.

**Who leaves it.** Claude Code in the Opus 4.5 era (medium: migration skills carry an explicit "no backwards-compat shims" rule). GPT-5 (medium: "deprecates your own methods and redirects them to new ones").

**Discover.** "Find every alias, re-export, or deprecated wrapper and list its callers. If there are none, it goes." "List every identifier renamed without need."

**Prove.** Confirmed: zero callers in the repo and no published API. Likely: callers exist only inside the repo and can be updated in the same change. Not a finding: a published library's deprecation path with a version plan.

**Repair.** Update the callers and delete the shim in the same change. One name per thing. Verify: a grep for the old name returns nothing and the build passes.

## 9. duplicate-helpers (medium)

**Looks like.** `formatCurrency` in `utils/` and again in `lib/`. `sleep` defined three times. A new `retry` beside the existing one. The same business rule implemented differently at two entry points.

**Why it matters.** Copies drift. Fixes land in one of them.

**Who leaves it.** Claude Code (medium: 2026 guides recommend "grep utils and lib before writing logic"). GPT-5.5 (weak: one forum report). Gemini (weak).

**Discover.** "Find functions that do the same thing as another function." "Find business rules, validation, and domain concepts implemented in more than one place. Flag where copies have drifted, and name the single source of truth each should come from."

**Prove.** Confirmed: two definitions with the same contract, or one rule with two behaviors. Smell: similar names, different jobs. Not a finding: deliberate per-package copies in a monorepo with separate release cycles.

**Repair.** Keep the one with tests or more callers, redirect the rest, delete them. For rules: "Consolidate the rule at its authoritative boundary and test every entry point." Verify: a single definition, all callers compile, the consolidated test runs against each entry point.

## 10. over-abstraction (medium)

**Looks like.** `Manager`, `Orchestrator`, `Wrapper` classes with one caller. An interface with one implementation. A factory for one product. Options objects whose fields nothing sets. One-line forwarding functions. Barrel files. A new file for something that fits in an existing one. "Flexibility that wasn't requested."

**Why it matters.** More surface, no behavior. Anthropic names Opus 4.5 and 4.6 for this directly. Sonar measured GPT-5-minimal as producing the highest share of complexity smells and about 30 percent more lines than Sonnet 4 for the same tasks.

**Who leaves it.** Claude Opus 4.5 and 4.6 (strong: first-party guide, "creating extra files, adding unnecessary abstractions, or building in flexibility that wasn't requested"). GPT-5 and Codex (strong: forum threads plus Sonar). Cursor Composer 2 (weak).

**Discover.** "Find abstractions with a single caller." "Find configuration options that nothing sets." "List new files this change added that could have been edits." "Collapse speculative over-engineered layers."

**Prove.** Confirmed: one caller, one implementation, and no test exercises the seam. Likely: two callers that could share a function instead of a class. Not a finding: a seam that exists for a test double that is actually used; an interface with two real implementations.

**Repair.** Inline it. "Great! Now the same but with half the code." Abstract only at three or more real call sites. Class-level move: before deleting layers one at a time, ask "What higher-level abstraction would make this entire problem disappear?" so five wrappers become one real concept, or nothing. Verify: tests unchanged and green; line count down.

## 11. god-files (medium)

**Looks like.** A 1500-line file. A 100-line function. Six levels of nesting. A component that fetches, transforms, and renders.

**Why it matters.** Nobody can review it, and agents keep appending to the biggest file because that is where the code is.

**Who leaves it.** Universal (weak model-specific evidence). Worsened by the "code only grows" habit reported for Claude in early 2026.

**Discover.** "Flatten deep nesting via early returns or polymorphism." "Extract pure functions from side-effect code." "Align modules tightly to domain boundaries."

**Prove.** A finding only when the length hides more than one responsibility, or the nesting hides a bug. Not a finding: a long data table; a generated file.

**Repair.** Extract by responsibility, not by line count. Early returns. "Put a lot of behaviour behind a small interface." Verify: tests unchanged and green; each new module has one reason to change.

## 12. stringly-typed (medium)

**Looks like.** `status === 'pending'` in seven files while the type says `status: string`. A badge component that is a ternary ladder over strings. Ten copies of the same set of literals.

**Why it matters.** The type says "any string" and the data says "one of five". Adding a state means grep. A typo is a silent new state.

**Who leaves it.** Universal. Named in the Ruiz follow-ups as "loose types" and "10 copies of the same strings".

**Discover.** "Find every place where a type is looser than the data." "Synchronize state enumeration across the app so it doesn't keep 10 copies of the same strings."

**Prove.** Confirmed: a literal compared in two or more files with no shared union or enum, or a `string` type over a closed set. Not a finding: open-ended strings such as names and ids.

**Repair.** One union or enum beside the owning type. Exhaustive switch with an `assertNever`. Lookup tables instead of ternary ladders. Class-level move: the enum and the transition table usually belong together (see implicit-state-machine). Verify: typecheck fails on a misspelled literal.

## 13. boolean-params (medium)

**Looks like.** `notify(order, true, false, false)`. Three optional boolean props that are mutually exclusive (`isPrimary`, `isDanger`, `isGhost`). Positional `dryRun, verbose, force`.

**Why it matters.** Call sites are unreadable and impossible combinations are representable (primary and danger at once).

**Who leaves it.** Universal.

**Discover.** "Find every boolean parameter or prop that should be a union type." "Find every pair of boolean props that cannot both be true."

**Prove.** Confirmed: two booleans that are mutually exclusive or always set together. Smell: a single flag.

**Repair.** `variant: 'primary' | 'danger' | 'ghost'`. An options object with named fields for independent flags. A sum type for modes. Verify: typecheck rejects the impossible combination.

## 14. react-smells (medium)

**Looks like.** An effect that only sets state (derived state in an effect). An effect that is really an event handler. Fetch in an effect with no cancellation. `eslint-disable react-hooks/exhaustive-deps`. `key={index}`. State initialized from a prop and never synced. Trivial `useMemo`.

**Why it matters.** Extra renders, stale closures, and races where the stale response wins. The React docs page "You Might Not Need an Effect" covers each case.

**Who leaves it.** Universal in React code; the effect-plus-booleans shape is the default output of every model.

**Discover.** "Find every effect that could be an event handler or derived value." "Find useEffect calls and evaluate their place by following the 'You Might Not Need an Effect' article." "Find every async action that can run twice or race."

**Prove.** Confirmed: the effect reads only props and state and writes state (derive it), or it runs in response to a user action (move it to the handler), or two in-flight requests can resolve out of order. Not a finding: a subscription with cleanup; syncing with a non-React system.

**Repair.** Compute during render. Move it to the handler. Use a data library, or an abort controller or ignore flag. Stable keys. Fix the dependency list instead of silencing the lint. Verify: lint passes without disables; a test with out-of-order responses.

## 15. async-misuse (medium)

**Looks like.** `await` in a `for` loop over independent items. `forEach(async ...)`. `new Promise(async ...)`. `await sleep(500)` to wait for something. `.then` and `await` mixed in one file. `time.sleep` or `requests` inside async Python.

**Why it matters.** Sequential where parallel was free. Unhandled rejections. Sleeps that pass on your machine and fail in CI.

**Who leaves it.** Universal.

**Discover.** "Find every sequential await over independent work." "Find every sleep that stands in for a real signal." "Find everything whose correctness depends on timing or execution order."

**Prove.** Confirmed: the awaited items are independent (no data dependency, no rate limit), or the sleep waits for an event that has a real signal. Not a finding: intentional serialization stated at the site.

**Repair.** `Promise.all` or `allSettled` with a concurrency cap; `asyncio.gather`. Wait on the actual condition. One style per module. Verify: a timing test or a counter of concurrent calls; no unhandled rejection.

## 16. hardcoded-config (medium)

**Looks like.** `http://localhost:3000` in client code. `|| 'secret'` env defaults. Credential-shaped literals. `setTimeout(..., 30000)` with no name. URLs in code.

**Why it matters.** Works on one laptop. Secrets in git history. "Find every magic number and hard-coded copy that should be a token or live in config."

**Who leaves it.** Universal. The env-default form overlaps with silent-fallbacks and is a Claude Code habit.

**Discover.** The line above.

**Prove.** Confirmed: the literal differs per environment or is a secret. Smell: a named constant at the top of the module with one use.

**Repair.** A typed config module read once at startup that fails fast on missing required values. Named constants for timeouts with the unit in the name. Rotate exposed keys first; `git rm --cached` leaves them in history. Verify: start with the variable unset and watch it fail early with a clear message.

## 17. performance-waste (medium)

**Looks like.** A query inside a loop (N+1). `.filter().map().filter()` over one array. `.find()` or `.includes()` inside a loop over another collection. Strings built with `+=` in a loop. A regex compiled inside a loop. Logging inside a hot loop. Sync file IO inside a request handler. Nested loops over the same collection. `SELECT *`. Unbounded `Promise.all` over a user-sized list. A polling loop with a sleep where a signal exists.

**Why it matters.** Each one is a question from Evis Drenova's checklist with the wrong answer: sequential when it could be concurrent, too many passes, too many allocations, too many I/O calls, no early exit. Jeff Dean and Sanjay Ghemawat's hints give the same list for systems code. See `performance.md` for both checklists.

**Who leaves it.** Universal. Agents optimize for passing, not for the second million rows.

**Discover.** Run the checklist in `performance.md` over the hot paths. Start with: "Is it sequential? Can we parallelize it?" "How many passes is it doing?" "How many I/O calls are we making?"

**Prove.** Confirmed: the code is on a hot path (request handler, per-item loop, startup of a long-running process) and either a profile or a complexity argument shows the cost. Not a finding: setup code, test code, or a cold path. Estimate before you measure, and measure before you optimize.

**Repair.** Batch the I/O. Build a Map or Set once and look up. One pass. Hoist invariants out of the loop. Cap concurrency. Stream instead of loading everything. Keep the optimization inside the module's boundary so callers do not change. Verify: a benchmark or timing before and after on realistic data.

## 18. stub-code (low)

**Looks like.** `TODO: implement`. "simplified for now". "In a real implementation this would". `NotImplementedError`. `pass`. "would go here". A hard-coded mock return in a production path. "for demo purposes".

**Why it matters.** Unfinished work hidden behind green. The summary says done.

**Who leaves it.** Claude Code (medium: placeholder-TODO guides; Anthropic says Opus 5 is better at "completing full tasks rather than leaving stubs or placeholders"). GPT-5 in Cursor (medium: "stubs the rest as planned"). Qwen 3 Coder 30B (medium: returned a hard-coded mock string).

**Discover.** "List every TODO, placeholder, and 'for now' and say whether the real thing exists anywhere."

**Prove.** Confirmed: the stub is on a production path and nothing implements the real behavior. Not a finding: a tracked TODO with an issue link on a non-critical path; ellipsis bodies in Protocols and overloads.

**Repair.** Implement it, or delete the path and fail explicitly, or file it with a link. Never leave a stub that returns success. Verify: a test for the implemented behavior; no untracked TODO in the grep.

## 19. restating-comments (low)

**Looks like.** `// Loop over the orders` above a for loop. Banner comments. `// Step 1:`. Narration ("Let me", "Now we"). A doc comment that repeats the function name. `@param name - The name`. Chain-of-thought pasted into comments. Existing human comments deleted near an edit.

**Why it matters.** "Comments effectively serve as another form of state, where agents read them and trust what it says without reading the code." They rot, and they let bad code stay unexplained.

**Who leaves it.** Gemini 2.5 Pro and Gemini CLI (strong: play-by-play comments, reasoning dumped into comments, 2025). Claude Code (medium: removes neighbouring human comments; comment noise is a standard deslop target). GPT-5 (medium: misleading comments).

**Discover.** "Show comments that restate the next line, or that look like model reasoning." On a diff: list human comments removed near edited lines.

**Prove.** Confirmed: deleting the comment loses nothing a reader needs. Not a finding: a why-comment, a link, a warning about a non-obvious constraint.

**Repair.** Delete. Keep comments that explain why, cite a source, or warn. Restore deleted human comments from git. Verify: read the file top to bottom once.

## 20. leftover-debug (low)

**Looks like.** `console.log(data)`. `print(...)`. `debugger`. `dbg!`. `fmt.Println` in library code. Merge conflict markers. A scratch script at the repo root.

**Who leaves it.** Universal. Gemini CLI leaves scratch test scripts and has left conflict markers in edited files (medium, 2025 and 2026).

**Discover.** "Find every debug statement and scratch artifact left in the repo."

**Prove.** Confirmed: output not meant for users or operators. Not a finding: CLI output; structured logging at the right level.

**Repair.** Delete, or route to the logger at debug level with context. Verify: a no-console lint rule or a grep in CI.

## 21. dead-code (low)

**Looks like.** Commented-out blocks. `if (false)`. A variable renamed to `_unused` instead of deleted. Exports nothing imports. The legacy file nothing imports.

**Why it matters.** Readers cannot tell live from dead, and the next agent copies the dead version.

**Who leaves it.** Claude (medium: prefers adding to removing; underscore-renaming unused variables). Universal.

**Discover.** "Find every export with no importer and every branch that cannot run." Use the project's tooling when it exists (knip, ts-prune, vulture, deadcode, cargo-udeps).

**Prove.** Confirmed: the tool says unused and a grep agrees. Not a finding: a library's public API; reflection or dynamic lookup.

**Repair.** Delete. Git remembers. Verify: build and tests.

## 22. generic-naming (low)

**Looks like.** `processData`, `handleStuff`, `result2`. `utils.ts`, `helpers.ts`, and `common.ts` all present. Single-letter names outside loops.

**Why it matters.** "Call a spade a spade: name the actual thing or action, not an abstraction that makes it sound more complicated." Grab-bag modules attract more grab.

**Who leaves it.** Universal. GPT-5 named specifically for cryptic names (medium).

**Discover.** "Find every module named utils, helpers, or common and say what it actually contains."

**Prove.** A finding when the name hides what the thing does, or two grab-bags overlap.

**Repair.** Name by domain (`money.ts`, `orderStatus.ts`). Split grab-bags by what they contain. Verify: a reader can predict the contents from the name.

## 23. stray-files (low)

**Looks like.** `IMPLEMENTATION_SUMMARY.md`, `PLAN.md`, `FIXES.md`, `*_COMPLETE.md` at the root. `.bak` and `_old` copies. `test_tmp.py`. `thing_v2.ts` beside `thing.ts`.

**Why it matters.** These document a session, not the system. "A brainstorm shouldn't become next session's instructions just because Claude saved it in a file." Anthropic notes that Opus 5 writes longer files to disk than earlier models.

**Who leaves it.** Claude Code, especially Opus 5 (strong: first-party note on longer Markdown deliverables). Gemini CLI (medium: scratch scripts not cleaned up). New-file-instead-of-edit is reported across agents.

**Discover.** "List every file an agent wrote that documents a session rather than the system."

**Prove.** Confirmed: nothing links to it and it describes a change, not the system. Not a finding: ADRs, a changelog, a `docs/` tree with an index.

**Repair.** Delete, or fold the durable parts into the README or docs. Verify: the README still explains the system without the stray file.

## 24. emoji-and-hype (low)

**Looks like.** Emoji bullets in READMEs and commit messages. Check marks in log output. "comprehensive, robust, seamless, production-ready" in comments and docs. "Successfully saved!" logs. Summaries that praise the change.

**Why it matters.** It reads as generated, the adjectives are claims without evidence, and cheerful log tone hides severity.

**Who leaves it.** Claude and GPT in docs and summaries (medium for marketing tone; weak public evidence for emoji specifically).

**Discover.** "Find every adjective in the docs that makes a claim the code doesn't prove."

**Prove.** A finding when the word carries no information, or the emoji is in code or logs. Not a finding: a project's deliberate voice on user-facing marketing pages.

**Repair.** Replace the adjective with the fact (a number, a test name, a limit). Plain log messages that include the failing value. No emoji in code, logs, or commit messages. Verify: read the README aloud.

## 25. duplicated-truth (semantic)

**Looks like.** A `total` stored on the order and also recomputed from items. A count column beside a `COUNT(*)`. User state in two stores. The same enum in frontend and backend with no shared source. A cache with no invalidation.

**Discover.** "Find every piece of state or data that has more than one source of truth and could drift out of sync. For each, show where it's written, where it's read, and how they could disagree." "Find every derived value that can outlive its source of truth."

**Prove.** "Demonstrate a reachable contradiction between representations of the same information."

**Repair.** "Establish an authoritative source of truth and test consistency across consumers." Derive instead of storing, or enforce invalidation. Verify: a test that mutates the source and reads every consumer.

## 26. false-screens (semantic)

**Looks like.** A success toast before the response arrives. An `error` state that is never set. Empty-state UI shown while loading. A count from stale data. "Saved!" shown because a fallback upstream returned success.

**Discover.** "Find every place where the screen can show something false." "List what the user sees in each stage."

**Prove.** Confirmed: an event sequence where the UI and the data disagree.

**Repair.** Drive the UI from the explicit state, not from flags. Show nothing until the state is known. Verify: one render test per state.

## 27. scope-drift (semantic, needs git history)

**Looks like.** A one-line fix that touched fourteen files. Your identifiers renamed. Formatting churn. Unrelated "improvements". Your method deprecated and redirected to a new one.

**Why it matters.** The diff cannot be reviewed and regressions land in code nobody meant to touch. This is the top complaint across all three major vendors in 2026.

**Who leaves it.** GPT-5.4, GPT-5.5, and Codex (strong). Gemini 2.5 Pro, Gemini 3, Gemini CLI, Antigravity (strong). Claude Opus 5 and 5.5 (strong: Anthropic's own guide says Opus 5 "can also expand the scope of a task"; an issue titled "Opus 5.5: Severe scope creep").

**Discover.** "For each commit on this branch, list the files it touched that its message does not explain." Standing rule: "Smallest diff that satisfies the step. No drive-by refactors, renames, or formatting churn."

**Prove.** Hunks outside the stated task. Whitespace-only hunks. Renames with no requirement.

**Repair.** Split the commit; revert unrelated hunks. Put "surgical changes" in the agent's instruction file. Verify: `git diff --stat` matches the task description.
