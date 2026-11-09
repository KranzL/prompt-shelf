# Refreshing the catalog

Model habits change with every model tier. "One-liners have a shelf life (~until the next model tier), but their impact grows with model power. Recheck quarterly; keep what still bites." Refresh when a new frontier model ships, when the user asks, or when the last refresh is more than three months old. Last refresh: 2026-11-08.

## What a refresh produces

1. New or changed rows in `by-model.md` with an evidence grade and a month.
2. New entries in `patterns.md` for habits that are not yet covered, in the same six-part shape.
3. New scanner signals in `scripts/scan.py` for any new pattern that has a grep-able shape, plus a line in the eval fixture that triggers it.
4. New verbatim prompts in `prompts.md` with credits.
5. The sources list below updated so the next refresh can diff against it.

Do not delete a pattern because the newest model stopped doing it. Older code in the repo was written by older models.

## Evidence grades

Rank sources, highest first:

1. The vendor's own model-specific prompting guide (Anthropic publishes one per model; OpenAI and Google publish release notes and cookbook pages). These name habits directly, for example Anthropic on Opus 4.5 and 4.6 over-engineering, and on Opus 5 expanding scope.
2. The agent's issue tracker: anthropics/claude-code, openai/codex, google-gemini/gemini-cli, cursor/cursor, getcursor/cursor. Search issue titles for "ignores", "fallback", "deletes tests", "scope", "unrequested", "comments".
3. Measured studies: Sonar's "coding personalities" reports, arXiv papers on LLM code smells (2510.03029) and on test gaming (2511.21654), benchmark write-ups with per-model code excerpts.
4. Forum threads with code: Hacker News, Tildes, the OpenAI community forum, the Cursor forum, Google's AI developer forum, Replit's forum, Reddit (r/ClaudeAI, r/ClaudeCode, r/ChatGPTCoding, r/cursor, r/LocalLLaMA, r/RooCode, r/CLine).
5. Practitioner blogs with before-and-after code.
6. Aggregator and news pages. Use them only to find the primary source; mark anything that stops there as weak or unverified.

A pattern needs at least one source at level 1 to 3, or three independent sources at level 4 to 5, to be graded strong.

## Search queries that worked

Run each with the current model names substituted. Use standard search first and extended search when results are thin.

- `"<model>" coding "over-engineer" OR "overengineer"`
- `"<model>" "try/catch" OR "try except" everywhere`
- `"<model>" fallback mock data production`
- `"<model>" "deletes tests" OR "modifies tests" OR "skip tests"`
- `"<model>" "unrequested changes" OR "scope creep" OR "touched files"`
- `"<model>" comments "restate" OR "play by play" OR "chain of thought"`
- `"<model>" "backwards compatibility" shim unnecessary`
- `"<model>" hallucinated API OR "doesn't exist" import`
- `site:github.com/anthropics/claude-code/issues <habit>`
- `site:github.com/openai/codex/issues <habit>`
- `site:community.openai.com codex <habit>`
- `site:discuss.ai.google.dev gemini <habit>`
- `"prompting <model>" site:platform.claude.com` (Anthropic's per-model guides)
- `"good prompt" "find all" codebase` and `"find every" app prompt` (new one-liners)
- `deslop OR "anti-slop" OR "ai slop" skill claude code` (new cleanup tools, for the prior-art section)

## How to add a pattern

1. Write the `patterns.md` entry: looks like, why it matters, who leaves it (with grades), discover, prove, repair. Keep the prove section honest about what is not a finding; that is where the value is.
2. If it has a grep-able shape, add signals to `SIGNALS` or `TEST_SIGNALS` in `scripts/scan.py` and a row to `PATTERNS`. Keep each signal's note short and in the imperative. Run the scanner on two real repos and on the eval fixture; if a signal fires on clean code more than it fires on slop, narrow it or drop it.
3. Plant one instance in the eval fixture under `evals/*/files/slop-shop/` and one near-miss that should not fire.
4. Add the row to `by-model.md`.
5. Add verbatim prompts with credits to `prompts.md`.

## Sources checked on 2026-11-08

Vendor documents
- Anthropic, Claude prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Anthropic, Prompting Claude Opus 5: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5

Issue trackers
- openai/codex 6356 "Avoid fallbacks": https://github.com/openai/codex/issues/6356
- openai/codex 21942 (quality regression reports): https://github.com/openai/codex/issues/21942
- claude-code 31890 (error handling ignores CLAUDE.md): https://claudeissues.com/issue/31890-bug-error-handling-ignores-claude-md-directives-adds-unsafe-fallbacks-instead-of
- claude-code 7074 (manipulates tests): https://claudeissues.com/issue/7074-bug-claude-code-manipulates-tests-instead-of-following-instructions
- claude-code 22530 (removes comments near edits): https://claudeissues.com/issue/22530-bug-claude-code-frequently-removes-existing-code-comments-near-edited-lines
- claude-code 97117 (Opus 5.5 scope creep, title only): https://claudeissues.com/issue/97117-opus-5-5-severe-scope-creep-and-task-focus-regression-compared-to-opus-4-6

Studies and benchmarks
- Investigating the Smells of LLM-Generated Code: https://arxiv.org/abs/2510.03029
- EvilGenie (test gaming): https://arxiv.org/abs/2511.21654
- Sonar, coding personalities, GPT-5 update: https://www.sonarsource.com/blog/the-coding-personalities-of-leading-llms-gpt-5-update/
- Akita on Rails LLM benchmark part 3 (DeepSeek, Kimi, Qwen, GLM, MiniMax): https://akitaonrails.com/en/2026/04/24/llm-benchmarks-parte-3-deepseek-kimi-mimo/
- 16x Engineer Qwen3-Coder evaluation: https://eval.16x.engineer/blog/qwen3-coder-evaluation-results

Forums and threads
- Replit forum, Claude fallback tendency: https://replit.discourse.group/t/feedback-on-claude-s-tendency-to-produce-fallback-mock-implementations/7294
- OpenAI forum, GPT-5 over-complicates and rewrites: https://community.openai.com/t/chatgpt-5-is-worse-at-coding-overly-complicates-rewrites-code-takes-too-long-does-what-it-was-not-asked/1340535
- OpenAI forum, Codex ignoring instructions: https://community.openai.com/t/codex-has-recently-started-ignoring-instructions-and-making-unsafe-patches/1382793
- Cursor forum, GPT has a Pinocchio problem: https://forum.cursor.com/t/gpt-has-a-pinocchio-problem/131923
- Tildes, the coming loop: https://tildes.net/~comp/1v3y/the_coming_loop
- Google AI forum, complaints about Gemini and its CLI: https://discuss.ai.google.dev/t/complaints-about-gemini-and-its-cli/138109
- r/RooCode, overly defensive Python from Gemini: https://redlib.hbubli.cc/r/RooCode/comments/1kqefo4/overly_defensive_python_code_generated_by_gemini
- r/LocalLLaMA, Gemini 2.5 Pro makes too many assumptions: https://r.darklab.sh/r/LocalLLaMA/comments/1k8fe14/hot_take_gemini_25_pro_makes_too_many_assumptions
- r/CLine, feedback on Gemini in Cline: https://redlib.hackliberty.org/r/CLine/comments/1lge0d1/feedback_on_improving_gemini_models_in_cline/
- Hacker News on Claude Code quality: https://news.ycombinator.com/item?id=47660925

Blogs
- davep, Gemini is kind of messy (May 2026): https://blog.davep.org/2026/05/14/gemini-is-kind-of-messy.html
- engineered.at, notes on GPT-5.x regressions: https://engineered.at/articles/notes-on-gpt-5-x-model-regressions
- s-anand, Codex follows instructions too faithfully: https://www.s-anand.net/blog/codex-follows-instructions-too-faithfully/
- fsck.com, that time it tried to delete all my tests: https://blog.fsck.com/2026/04/30/that-time-it-tried-to-delete-all-my-tests
- HyperDev, bad habit of agentic coders: fallback strategies: https://hyperdev.matsuoka.com/p/bad-habit-of-agentic-coders-part
- Sean Goedecke, agents and fallbacks: https://seangoedecke.com/agents-and-fallbacks/
- Codersera, how to stop Claude Code over-engineering: https://codersera.com/blog/how-to-stop-claude-code-over-engineering-2026/
- Kent C. Dodds, Stop using isLoading booleans: https://kentcdodds.com/blog/stop-using-isloading-booleans
- Ars Technica, AI coding assistants destroy user data (July 2025): https://arstechnica.com/information-technology/2025/07/ai-coding-assistants-chase-phantoms-destroy-real-user-data

Prompt sources
- Steve Ruiz, the seed prompt: https://x.com/steveruizok/status/2116552016218710389
- Matt Pocock, fully verifiable: https://x.com/mattpocockuk/status/2118313863917564136
- Evis Drenova, performance checklist: https://x.com/evisdrenova/status/2114216996435116165
- Drix10/awesome-prompts (collection with credits): https://github.com/Drix10/awesome-prompts
- Jeff Dean and Sanjay Ghemawat, Performance Hints: https://abseil.io/fast/hints.html
- kr4chinin find-implicit-state-machines skill (Confirmed / Likely / Smell): https://github.com/kr4chinin/skills
- nud3l /code-audit gist (report shape): https://gist.github.com/nud3l/15468abc5c4ca7e4e0e38e5b120a7997

Prior art (diff-level cleaners this skill is broader than)
- cursor/plugins deslop: https://skills.cat/skills/cursor/plugins/deslop
- brianlovin/claude-config deslop: https://skills.sh/brianlovin/claude-config/deslop
- b4r7x anti-slop: https://skills.sh/b4r7x/agent-skills/anti-slop
- ai-slop-detector (Python linter, 34 checks): https://pypi.org/project/ai-slop-detector/

## Gaps at last refresh

- No public pattern evidence yet for Claude Fable 5.1, Mythos 5.1, Cursor Composer, Grok Code, Copilot, Windsurf, Kiro, or Devin.
- No source ties implicit state machines, `as any`, leftover console.log, or emoji to a specific model; they are universal habits.
- X search is unreliable from a terminal. Use api.fxtwitter.com for a single known post; use search engines for discovery.
