---
name: needless-effects
description: Find every effect that could be an event handler or derived value. useEffect that syncs state from props, that sets state from other state, that runs on mount to do what the event already knew, or that duplicates what a framework hook or the server already does. Use when the user asks about useEffect misuse, derived state, effects that should be handlers, re-render chains, or runs /needless-effects.
argument-hint: [path]
---

# Find every effect that could be an event handler or derived value

> Find every effect that could be an event handler or derived value.

Credited to @Nikzaaaaad in the Drix10/awesome-prompts collection. A companion from the same collection:

> Find useEffect calls and evaluate their place by following the 'You Might Not Need an Effect' article.

The article is at https://react.dev/learn/you-might-not-need-an-effect. The collection is at https://github.com/Drix10/awesome-prompts

## Run

Scope: $ARGUMENTS when given, otherwise every React, Vue, Svelte, or Solid component with effects or watchers. Report only.

For each effect ask: what does it react to, and could the code that caused that change have done this directly? Look for:
- An effect that computes a value from props or state and stores it in state. That is a derived value; compute it during render or memoize it.
- An effect that resets or copies state when a prop changes. Usually a key on the component or a handler.
- An effect that responds to a flag set by a handler, doing work the handler could have done.
- Chains: effect A sets state, effect B fires on it, effect C fires on that.
- Effects that fetch with no cancellation, racing on fast input.
- Effects that subscribe to something a framework hook already provides.

Not a finding: synchronizing with something outside the framework (a DOM API, a socket, a third-party widget); an effect that is the documented pattern in the framework used.

## Report

One line per finding: file:line, what the effect does, what it should be instead (derived value, event handler, key, framework hook). Tier Confirmed, Likely, or Smell. End with how many candidates you dropped.
