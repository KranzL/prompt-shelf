# Which habits belong to which model

Use this file after `scripts/detect_models.py` has told you which tools touched the repo, or after the user has told you. Pick the pattern set, then open the matching entries in `patterns.md`.

Evidence grades:
- **strong**: a first-party vendor document, or several independent reports across forums, issue trackers, and blogs.
- **medium**: an issue-tracker thread plus one or two write-ups, or one detailed benchmark.
- **weak**: a single anecdote or an aggregator page only.

Researched 2026-11-08. Sources are listed in `refresh.md`. Public evidence lags model releases by weeks to months, so a model with little evidence is not a clean model; it is a new one.

## Universal set (run on every repo)

Every model does these. A 2025 study of LLM-generated Java (arXiv 2510.03029) found 63 percent more code smells than reference solutions, with implementation smells up 73 percent and design smells up 21 percent, and Codex the worst of the models tested.

- swallowed-errors
- silent-fallbacks
- implicit-state-machine
- test-weakening
- over-abstraction
- stringly-typed

Add by stack, not by model: `react-smells` and `boolean-params` for React code; `async-misuse`, `performance-waste`, and `hardcoded-config` for services and jobs.

## Per model

| Model or tool | Strong | Medium | Weak |
|---|---|---|---|
| Claude Code with Sonnet 4.x, Opus 4, Opus 4.1 | silent-fallbacks, swallowed-errors | test-weakening, duplicate-helpers, compat-shims, stub-code, restating-comments (deletes neighbouring human comments), stray-files | type-escape-hatches, leftover-debug, emoji-and-hype |
| Claude Opus 4.5, Opus 4.6 | over-abstraction (extra files, unrequested flexibility; named in Anthropic's prompting guide) | compat-shims, dead-code (prefers adding to removing) | |
| Claude Opus 5, Opus 5.5, Sonnet 5.5, Haiku 5.5 | scope-drift (Anthropic's guide: "can also expand the scope of a task"), stray-files and emoji-and-hype (longer Markdown deliverables) | over-verification and heavier subagent use (not code patterns) | stub-code is reported as improved |
| Claude Fable 5.1, Mythos 5.1 | no public pattern evidence found yet; treat as the Opus 5.5 row | | |
| GPT-5, GPT-5.1, GPT-5.4, GPT-5.5 | scope-drift (unrequested rewrites and renames), over-abstraction (speculative complexity; Sonar measured the most complexity smells and about 30 percent more lines than Sonnet 4) | silent-fallbacks (openai/codex issue 6356 on gpt-5-high), defensive-overkill, test-weakening (claims PASS without verification), restating-comments (misleading comments), generic-naming (one-letter names) | duplicate-helpers |
| GPT-5-Codex, Codex CLI | scope-drift | silent-fallbacks, test-weakening, destructive literal rule-following (deleted all tests when two rules conflicted) | |
| Gemini 2.5 Pro, Gemini CLI | scope-drift (drive-by edits, collapsing functions to one line, re-applying undone changes), defensive-overkill and swallowed-errors (try/except around everything even when told not to), restating-comments (play-by-play comments, reasoning pasted as comments, human comments removed) | leftover-debug and stray-files (scratch scripts, merge conflict markers), false success claims, destructive file operations | phantom-apis, duplicate-helpers |
| Gemini 3, Antigravity, Jules | scope-drift (whole-file overwrites for small edits) | | |
| DeepSeek V3.x, Qwen 3 Coder, GLM 4.x and 5.x, Kimi K2.x, MiniMax | | phantom-apis (invented client APIs), test-weakening (tests mock a class that does not exist; `rescue => e; assert true`), stub-code (hard-coded mock returns) | verbose diffs |
| Cursor Composer, Grok Code, GitHub Copilot, Windsurf, Kiro, Devin | no pattern-specific public evidence; run the universal set | | |

## Pattern sets to run

Start with the universal set, then add:

- **Claude 4.x era code**: compat-shims, duplicate-helpers, stub-code, stray-files, restating-comments, dead-code.
- **Claude 5.x era code**: scope-drift (if there is git history), stray-files, emoji-and-hype, over-abstraction.
- **GPT or Codex code**: scope-drift, defensive-overkill, generic-naming, restating-comments, silent-fallbacks.
- **Gemini code**: scope-drift, defensive-overkill, restating-comments, leftover-debug, stray-files.
- **Open-weight model code**: phantom-apis, stub-code, and run test-weakening with extra care (check that mocked classes exist).
- **Unknown authorship**: the universal set plus stub-code, restating-comments, and stray-files, which are cheap and nearly always present.

## Version trends worth knowing

- Opus 4.5 and 4.6 over-engineered; Opus 5 and 5.5 drift in scope and write longer files. Stubs and placeholders got better in Opus 5 (Anthropic's own guide).
- GPT-5.3-codex is cited as more disciplined than GPT-5.4 and 5.5, which make more unsolicited changes. One practitioner routes audits to 5.3-codex for that reason.
- Gemini's try/except habit was reported for 2.5 Pro in May 2025 and persisted into the CLI in 2026 reports.
- Smaller and open-weight models invent APIs more often than frontier models; frontier models hide failures more often than they invent APIs.

## When the detector finds nothing

Commit trailers are a floor. Cursor, Copilot, and most IDE agents do not add trailers. If `detect_models.py` reports no attribution, ask the user which tools and models were used, or run the universal set plus the cheap low-severity patterns.
