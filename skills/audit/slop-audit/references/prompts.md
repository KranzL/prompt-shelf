# Prompt library

Each prompt that stands on its own is also a skill of its own in this repo's `skills/` folder, with the credit and a short procedure. This file is the full list grouped by phase, for the audit procedure to draw on.

One-line prompts to run over a codebase, grouped by the phase they serve. Quoted lines are verbatim from their authors; do not reword them when reusing. Lines without a named author come from the Drix10/awesome-prompts collection (MIT), which harvested them from the Steve Ruiz thread and related threads; its README holds the per-line credits.

The structure Discover, Prove, Repair comes from that collection's "unicorn hunt" framing: "Discover what the code implies. Prove where those implications fail. Repair the underlying system." Never authorize a repair until the breakage is demonstrated.

## Discover

The seed, Steve Ruiz (tldraw), 2026-10-31:

- "find all of the implicit state machines in my app"

The nine follow-ups (credited to @Nikzaaaaad in the awesome-prompts README). Run the seed first, then these:

- "Find every place where the screen can show something false."
- "Find every bit of business logic sitting in UI components that belongs in the domain layer."
- "Find every place a value is stored twice and can drift apart."
- "Find every database rule the code assumes but Postgres doesn't enforce."
- "Find every async action that can run twice or race."
- "Find every error that gets swallowed silently."
- "Find every magic number and hard-coded copy that should be a token or live in config."
- "Find every place where a type is looser than the data."
- "Find every effect that could be an event handler or derived value."

Expanded one-file audit (credited to @trevin):

- "Find the app's explicit and implicit state machines and document their states, invariants, and transition tables in one file. Identify invalid states or transitions the code can actually reach, with evidence, including through retries and concurrency. Prioritize confirmed bugs by impact, group related fixes into issues, then fix them with regression tests and keep the document updated."

More hunts from the same family:

- "Find every invariant my application relies on but does not enforce."
- "Find every impossible state my data model permits."
- "Find every operation that is unsafe to retry."
- "Find everything whose correctness depends on timing or execution order."
- "Find every business rule implemented differently across entry points."
- "Find every piece of state or data that has more than one source of truth and could drift out of sync. For each, show where it's written, where it's read, and how they could disagree."
- "Find every workflow that can become permanently stuck."
- "Find every successful operation that can leave the system inconsistent."
- "Find useEffect calls and evaluate their place by following the 'You Might Not Need an Effect' article."
- "Find the pile of booleans that secretly means step 3."
- "Hunt over-engineering, unnecessary text, unnecessary abstractions, implicit state machines, duplication, and tests with no useful coverage."

From practitioners outside the thread:

- `grep -i fallback`, then judge each hit. From openai/codex issue 6356: "Almost all fallbacks are hacks or workaround for various issues."
- "Review this diff only for over-engineering. Flag every unrequested abstraction, fallback, new file, and dependency. Propose the minimal version." (Codersera, 2026)
- "Find defensive checks on values that cannot be null by construction." (paraphrase of the Tildes thread "the coming loop")
- "Find abstractions with a single caller." and "Find configuration options that nothing sets." (phrasings that follow from Anthropic's over-engineering note on Opus 4.5 and 4.6)
- "Find every test that can pass when the feature is broken." (phrasing that follows from the EvilGenie paper, arXiv 2511.21654)

Performance lens: see `performance.md` for Evis Drenova's checklist and the Abseil hints.

## Prove

- "Order findings Confirmed, then Likely, then Smell; report how many candidates you dropped."
- "Don't modify any code. List the states, allowed transitions, and conflicting combinations, with line numbers."
- "For every number or claim, quote the file and line. If you can't, delete it."
- "Read the so-called bugs before letting it fix anything; half of them are not real bugs."
- "A single loading flag, or framework-managed state with nothing layered on top, is not a finding."
- "Demonstrate a reachable counterexample for each unenforced invariant."
- "Construct each invalid state through a reachable execution path."
- "Reproduce an operation that reports success while leaving inconsistent state."
- "Rate each bug from 1 to 10 on how often it would happen and how bad it would be. If the two scores multiplied are below 5, just file it as an issue and leave the code alone."
- "Prioritize evidence over speculation. Don't claim a test passed unless it actually ran."

The Confirmed / Likely / Smell tiers come from the kr4chinin find-implicit-state-machines skill, which labels each finding by how far it was traced through the code. The HIGH / MEDIUM / LOW plus Quick Wins / Medium / Complex report shape comes from the nud3l /code-audit gist.

## Repair

Think in classes of problem, not instances. The five abstraction prompts (credited to @Wyrmfalls):

- "Exercise abstract thinking when considering this task."
- "What higher-level abstraction would make this entire problem disappear?"
- "Reduce this problem to its irreducible constraints and rebuild it from zero."
- "What would a principal architect immediately rewrite before even starting this?"
- "Design the single test that breaks this design on day one."

Then the repair moves:

- "Turn each one into an explicit status enum with an allowed-transitions table, and add a test that fails on any transition not in the table."
- "Minimize the state space and make illegal states unrepresentable."
- "Prevent invalid states structurally and test that they remain unreachable."
- "Enforce each invariant at its authoritative boundary and add regression tests."
- "Establish an authoritative source of truth and test consistency across consumers."
- "Consolidate the rule at its authoritative boundary and test every entry point."
- "Make retries safe through idempotency or deduplication and test concurrent execution."
- "Collapse speculative over-engineered layers."
- "Put a lot of behaviour behind a small interface."
- "Great! Now the same but with half the code."
- "Autosimplify."
- "Call a spade a spade: name the actual thing or action, not an abstraction that makes it sound more complicated."
- "Flatten deep nesting via early returns or polymorphism."
- "Extract pure functions from side-effect code."
- "Smallest diff that satisfies the step. No drive-by refactors, renames, or formatting churn."
- "If a test fails, fix the cause rather than the test. If the test itself is wrong, say why."
- "Prove findings against actual code paths before repairing them. Preserve intended behavior, prefer the smallest systemic fix, and reject unverified assumptions."

Anthropic's own guidance, from the Claude prompting best-practices page:

- "Don't add error handling, fallbacks, or validation for scenarios that can't happen."
- "Do not hard-code values or create solutions that only work for specific test inputs."

## Verify

Matt Pocock, 2026-11-05:

- "How do we make this change fully verifiable?"

He reports it "Makes the agent bend over backwards to verify all its changes. Signing up for real services, clicking through the frontend."

- "Give me irrefutable proof this works now."
- "Check every acceptance criterion: PASS / FAIL / UNTESTED, with evidence."
- "Run the checks and report pass/fail with the key output lines."
- "For bug fixes, ask for one extra artifact: the new regression test failing on the old code, then passing on the fix."
- "Does the new test fail on the commit before the change?"
- "'Looks done' is not done."
- "Green tests are just the agent grading its own homework."

## Standing rules for CLAUDE.md or AGENTS.md

Offer these when the user wants the habit prevented, not just removed. Prefer a lint rule or a type over a sentence whenever one exists: "Turn architectural rules into deterministic lint rules or construct the types so there's only one way to do something."

- "Add to the global rules: never create implicit state machines; make state explicit when you write code."
- "Do not design for rare or future cases nobody asked about."
- "Ban comments unless the code is unusual for very good reason."
- "Do not add error handling, fallbacks, or validation for scenarios that can't happen." (Anthropic)
- No fallbacks policy, from openai/codex issue 6356: the reporter notes "Adding a no-fallbacks policy to AGENTS.md helps."
- Karpathy's four rules as summarized in 2026 posts: think before coding, simplicity first (no abstractions for single-use code), surgical changes (do not improve adjacent code), goal-driven execution.
- Codersera's threshold: abstract only when there are three or more real call sites; do not create new files unless strictly required.
- "Every rule added to CLAUDE.md competes with the forty already there." Keep the file short.

## Principles behind the prompts

From the awesome-prompts notes file, useful when deciding what to flag:

- "Every flag added to fix one bug quietly becomes a state."
- "Demand concrete evidence and deduplicate overlapping findings before authorizing any repair."
- "Walk the unhappy paths: retries and concurrency are where invalid states hide; a happy-path walkthrough never shows them."
- "State machines you never designed are design debt, not a tooling win."
- "Adding a risk score makes the reviewer stop chasing ghosts."
- "Comprehension debt: the code looks clean, the tests pass, and nobody understands it anymore."
- "One-liners have a shelf life (~until the next model tier), but their impact grows with model power. Recheck quarterly; keep what still bites."
