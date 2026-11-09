# prompt-shelf

Good prompts for coding agents, stored as Claude Code skills so you can run any one of them whenever you want.

Someone posts a prompt that works, like Steve Ruiz's "find all of the implicit state machines in my app". You want to keep it, credit them, and run it on your own repo next month with one command. That is what this repo is. Each prompt is its own small skill: the prompt verbatim, who wrote it, a few lines on how to run it well, and what the report should look like. Add a prompt by adding a folder.

## Install

In Claude Code:

```
/plugin marketplace add KranzL/prompt-shelf
/plugin install prompt-shelf@prompt-shelf
```

From a local clone: `claude plugin marketplace add ~/path/to/prompt-shelf`, then the same install line. After new prompts land: `claude plugin update prompt-shelf`.

Each skill is a plain folder with a SKILL.md, so you can also copy a single one into `~/.claude/skills/` and ignore the rest.

## Use

Type the skill name as a slash command, with an optional path or branch:

```
/implicit-state-machines src/orders
/swallowed-errors
/over-engineering feature/checkout
/fully-verifiable
```

Use `/prompt-shelf:implicit-state-machines` if another plugin has a skill with the same name. Claude also picks them up when you ask in plain words ("find every error that gets swallowed silently").

Every hunt reports first and changes nothing until you ask. Findings are tiered Confirmed, Likely, or Smell, and each report ends with how many candidates were dropped, so you can tell how much was filtered.

## The prompts

Skills sit in folders by what they are about. A folder is only a shelf label; the slash command is the skill name alone.

### ui

| Skill | Prompt | Credit |
|---|---|---|
| `/false-screens` | Find every place where the screen can show something false. | @Nikzaaaaad |
| `/logic-in-ui` | Find every bit of business logic sitting in UI components that belongs in the domain layer. | @Nikzaaaaad |
| `/needless-effects` | Find every effect that could be an event handler or derived value. | @Nikzaaaaad |

### state

| Skill | Prompt | Credit |
|---|---|---|
| `/implicit-state-machines` | find all of the implicit state machines in my app | Steve Ruiz |
| `/state-machine-audit` | Find the app's explicit and implicit state machines and document their states, invariants, and transition tables in one file... | @trevin |
| `/unenforced-invariants` | Find every invariant my application relies on but does not enforce. | awesome-prompts |
| `/duplicated-truth` | Find every place a value is stored twice and can drift apart. | @Nikzaaaaad |
| `/stuck-workflows` | Find every workflow that can become permanently stuck. | awesome-prompts |

### errors

| Skill | Prompt | Credit |
|---|---|---|
| `/swallowed-errors` | Find every error that gets swallowed silently. | @Nikzaaaaad |
| `/fallbacks` | grep -i fallback | openai/codex issue 6356 |
| `/racing-async` | Find every async action that can run twice or race. | @Nikzaaaaad |

### data

| Skill | Prompt | Credit |
|---|---|---|
| `/unenforced-db-rules` | Find every database rule the code assumes but Postgres doesn't enforce. | @Nikzaaaaad |
| `/loose-types` | Find every place where a type is looser than the data. | @Nikzaaaaad |
| `/magic-values` | Find every magic number and hard-coded copy that should be a token or live in config. | @Nikzaaaaad |
| `/inconsistent-rules` | Find every business rule implemented differently across entry points. | awesome-prompts |

### design

| Skill | Prompt | Credit |
|---|---|---|
| `/over-engineering` | Review this diff only for over-engineering. Flag every unrequested abstraction, fallback, new file, and dependency. Propose the minimal version. | Codersera |
| `/half-the-code` | Great! Now the same but with half the code. | awesome-prompts |

### thinking

| Skill | Prompt | Credit |
|---|---|---|
| `/abstract-thinking` | Exercise abstract thinking when considering this task. And four more. | @Wyrmfalls |

### testing

| Skill | Prompt | Credit |
|---|---|---|
| `/useless-tests` | Find every test that can pass when the feature is broken. | after the EvilGenie paper |
| `/fully-verifiable` | How do we make this change fully verifiable? | Matt Pocock |

### performance

| Skill | Prompt | Credit |
|---|---|---|
| `/performance-checklist` | my low hanging fruit checklist for code performance optimizations | Evis Drenova |
| `/performance-hints` | Performance Hints, applied as a review | Jeff Dean and Sanjay Ghemawat |

### audit

| Skill | What it does | Credit |
|---|---|---|
| `/slop-audit` | Runs the full catalog of agent habits over a repo, keyed by which models wrote the code, with a scanner, a model map, and a Discover, Prove, Repair, Verify procedure. The one big skill here. | many, listed inside |
| `/agent-rules` | Standing rules for CLAUDE.md or AGENTS.md that stop a habit from coming back, preferring a lint rule or type over a sentence. | several, listed inside |

### shelf

| Skill | What it does |
|---|---|
| `/save-prompt` | Paste a prompt or a link and it becomes a new skill folder with the quote, the credit, and a README row. |

## Add a prompt

Say "save this prompt" with the link or text and `/save-prompt` does the steps below. By hand:

1. Copy `TEMPLATE.md` to `skills/<folder>/<name>/SKILL.md`. A new folder also needs a line in the `skills` list in `.claude-plugin/plugin.json`, because the plugin loads only the folders listed there.
2. Quote the prompt verbatim with author, date, and link. Never reword a quote.
3. Fill in how to run it, what is not a finding, and the report shape. Keep it under sixty lines.
4. Add a row to the folder's table above and run `claude plugin validate .`.

## Credits

The seed is Steve Ruiz's "find all of the implicit state machines in my app" (October 2026). The follow-up hunts, the one-file audit, and the five abstraction prompts were collected with per-author credits in [Drix10/awesome-prompts](https://github.com/Drix10/awesome-prompts) (MIT); this repo quotes them verbatim and keeps the credits. "How do we make this change fully verifiable?" is Matt Pocock's. The performance checklist is Evis Drenova's. The performance hints are Jeff Dean and Sanjay Ghemawat's, from abseil.io. The Confirmed, Likely, Smell tiers follow kr4chinin's find-implicit-state-machines skill. The over-engineering review is Codersera's. The fallback hunt comes from openai/codex issue 6356.

## License

MIT
