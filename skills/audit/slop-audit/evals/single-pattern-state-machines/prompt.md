---
tags: [slop-audit]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Bash]
---

find all of the implicit state machines in the slop-shop app in this folder. for each one list the states, how it moves between them, which combinations are impossible but still reachable, and how you'd make it explicit. don't change any code yet. put the answer in STATE_MACHINES.md at the repo root

Input files: slop-shop
