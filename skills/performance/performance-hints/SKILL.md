---
name: performance-hints
description: Review code against Jeff Dean and Sanjay Ghemawat's Performance Hints from abseil.io. Estimate before optimizing, measure, keep optimizations inside API boundaries, better algorithms, compact memory layout, fewer allocations, avoid unnecessary work, no logging on hot paths, batch then parallelize, short critical sections. Use when the user asks for a deeper performance review of systems code, memory layout, allocation pressure, lock contention, or runs /performance-hints.
argument-hint: [path or function]
---

# Performance Hints, applied

Jeff Dean and Sanjay Ghemawat, "Performance Hints", first published 2023-07-27 and updated 2025-12-16. Written for C++ at Google scale; most of it is language-neutral. https://abseil.io/fast/hints.html

Read references/hints.md in this skill's folder before reviewing, and the original page for the sections that apply.

## Run

Scope: $ARGUMENTS when given, otherwise ask which code is hot. Their first two hints decide whether to go on at all: choose the faster alternative only when it does not significantly hurt readability, and decide whether this is setup code or a hot path before spending effort. Do a back-of-the-envelope estimate; if the code is not hot, stop and say so.

For a hot path, walk the sections in their order and note what applies:
- Measurement: is there a profile? If not, get one before proposing anything beyond the obvious.
- API: can a bulk call replace per-item calls? Can callers pass pre-allocated or pre-computed data?
- Algorithm: is there a better complexity? Is a structure built element by element that could be built once?
- Memory: are hot and cold fields mixed? One allocation per element where a flat or chunked store would do? A map keyed by small integers?
- Allocations: containers grown one at a time, temporaries inside loops, copies where moves would do, buffers not reused.
- Unnecessary work: no fast path for the common case, expensive checks before cheap ones, loop-invariant work inside the loop, stats computed that nobody reads.
- Logging on hot paths, even disabled logging.
- Parallelism: batching before threading, a lock held across RPC or I/O, long critical sections, hot shared data that could be sharded, tiny work items sent to a thread pool.

"Make the compiler's job easier" comes last in their list and is gated on profile evidence; leave it there.

## Report

Per section that applies: file:line, the hint, the estimated gain, the readability cost. Ordered by estimated gain. Say which findings need a profile before acting. Do not report a speedup you did not measure.
