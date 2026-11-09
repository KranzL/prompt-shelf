---
name: save-prompt
description: Save a good prompt as a new skill in the prompt-shelf collection. Take a prompt the user found (a tweet, a thread, a blog line, something they wrote), fetch the verbatim text, credit the author, write skills/<folder>/<name>/SKILL.md from the template, and commit. Use when the user pastes a prompt or a link to one and says save this, add this prompt, make this a skill, store this, or runs /save-prompt.
argument-hint: [prompt text or URL]
---

# Save a prompt as a skill

The input is $ARGUMENTS: a prompt in the user's words, or a URL to one.

## Run

1. Find the working copy of prompt-shelf. If the current directory is a clone (it has .claude-plugin/plugin.json naming prompt-shelf), use it. Otherwise look at the directory this skill loaded from; if it is a git checkout with a remote, use it. If it is an installed copy under a plugins cache, ask the user where their clone is, or offer to clone the repository named in plugin.json. Never write into the cache copy; the next update would erase it.
2. Get the verbatim text. For an x.com or twitter.com link, x.com itself refuses fetchers; use https://api.fxtwitter.com/<user>/status/<id> and read the tweet text from its JSON. For other pages, fetch and quote only the author's words. Never reword a quoted prompt.
3. Record the credit: author handle or name, date, and the URL. If the prompt reached you through a collection, name the collection too and keep its per-line credit.
4. Pick a name: lowercase, hyphens, two or three words that say what the prompt hunts or does, like swallowed-errors or half-the-code. Check every folder under skills/ for an existing skill that already covers it; if one does, add the quote to that skill instead of making a new one.
5. Pick the folder: the categories are the directories under skills/ (ui, state, errors, data, design, thinking, testing, performance, audit, shelf). If none fits, make a new one, such as writing, and add "./skills/<folder>/" to the skills list in .claude-plugin/plugin.json, because the plugin only loads the folders listed there.
6. Copy TEMPLATE.md from the repo root to skills/<folder>/<name>/SKILL.md and fill every section: the frontmatter name and description (what it does, then the words a user would say when they want it, then "or runs /<name>"), the quote, the credit, how to run it in a few lines, what is not a finding, and the report shape. Keep it under sixty lines. No emojis. No comments in any code.
7. Add a row to the folder's table in README.md.
8. Run `claude plugin validate .` from the repo root and fix anything it reports.
9. Commit with a one-line message naming the prompt and its author. Push only if the user asks.

## Report

The new skill's path, the quote with its credit, and the commit hash.
