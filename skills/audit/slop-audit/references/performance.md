# Performance lens

Two checklists, one from application code and one from systems code. Run them over hot paths only: request handlers, per-item loops, startup of long-running processes, anything the profile points at. Estimate first, then measure, then optimize. Test code and setup code are not hot paths.

## Evis Drenova's low-hanging-fruit checklist

Verbatim from the post of 2026-10-25 (@evisdrenova):

> my low hanging fruit checklist for code performance optimizations:
>
> - is it sequential? can we parallelize/make it concurrent?
> - can we increase concurrency? what is the trade-off?
> - how many passes is it doing? can we do it in fewer?
> - how many allocations is it doing? can we do fewer?
> - is it batching? how big are the batches?
> - is it batching? can/should we stream it?
> - are we awaiting too long? can we do stuff in the await?
> - can we early exit?
> - how many threads are we spawning? too many? too few?
> - are we using the right DSA? how is data stored in-mem?
> - how many i/o calls are we making? can we make less?

How each question shows up in agent-written code, and what the scanner looks for:

| Question | Typical agent shape | Scanner signal |
|---|---|---|
| Sequential? | `for (...) { await f(item) }` over independent items | async-misuse: await inside a loop |
| Increase concurrency? | `Promise.all(items.map(fetch))` with no cap, or one at a time | performance-waste: unbounded concurrency |
| How many passes? | `.filter().map().filter()` over the same array; three loops that could be one | performance-waste: three passes |
| How many allocations? | string `+=` in a loop; `JSON.parse(JSON.stringify())`; a new regex per iteration | performance-waste: string concat, regex in loop; defensive-overkill: deep clone hack |
| Batching? | a query per item (N+1) | performance-waste: query inside a loop |
| Stream it? | `readFileSync` of a large file in a handler; loading a whole table to count it | performance-waste: sync IO in a handler; `SELECT *` |
| Awaiting too long? | sequential awaits where the second does not need the first | async-misuse |
| Early exit? | `.filter(...).length > 0` instead of `.some`; full scan after the answer is known | semantic |
| Threads? | unbounded worker spawn; one thread per request | semantic |
| Right data structure? | `.find()` or `.includes()` inside a loop (should be a Map or Set); `list.insert(0, x)` | performance-waste: linear search in loop, insert at front |
| How many I/O calls? | N+1 queries; a log line per item in a hot loop | performance-waste: query in loop, logging in loop |

## Jeff Dean and Sanjay Ghemawat, "Performance Hints"

From abseil.io/fast/hints (first published 2023-07-27, updated 2025-12-16). Written for C++ at Google scale, but most hints are language-neutral. Distilled, keeping their section names:

**Think about performance.** Choose the faster alternative when it does not significantly hurt readability or complexity.

**Estimation.** Decide whether the code is setup code or a hot path before spending effort. Do back-of-the-envelope calculations to discard alternatives before implementing them. Know rough costs of common operations.

**Measurement.** Measure or estimate benefits before optimizing. Use the profiler first. When profiles are flat, pursue many small wins, look at loops higher in the call stack, and replace overly general code with specialized code.

**API considerations.** Keep optimizations inside encapsulation boundaries. Add bulk APIs to amortize per-call overhead. Let callers pass pre-allocated or pre-computed data. Prefer view types for arguments unless ownership transfers.

**Algorithmic improvements.** Look for better complexity. Build structures in one shot instead of element by element. Use hash lookups where they replace ordered structures or sorted-list intersections.

**Better memory representation.** Use compact representations for frequently accessed data. Group fields accessed together; move cold data away from hot data. Prefer flat or chunked storage over one allocation per element. Replace maps with arrays when keys are small integers; replace sets with bit vectors.

**Reduce allocations.** Reserve when the size is known. Avoid growing containers one element at a time. Move instead of copy. Hoist temporaries out of loops and reuse them. Reuse serialization buffers.

**Avoid unnecessary work.** Add small fast paths for common cases. Order checks so cheap ones skip expensive work. Precompute expensive properties once. Check malformed input at module boundaries, not repeatedly inside. Move loop-invariant computation out of loops. Defer expensive computation until needed. Compute stats on demand; sample instead of counting everything; drop stats nobody reads.

**Make the compiler's job easier.** Only with profile evidence: avoid calls in hot functions, move slow paths out of line, copy small data into locals.

**Avoid logging on hot code paths.** Even disabled logs cost a check and can inhibit optimization. Compute whether logging is enabled once, outside nested loops.

**Code size.** Trim commonly inlined code; keep rarely used slow paths out of line; reduce template instantiations.

**Parallelization and synchronization.** Batch, then process in parallel, and measure, because saturated resources make it worse. Amortize lock acquisition over a whole tree of operations. Keep critical sections short; never do RPCs while holding a lock. Shard hot data to reduce contention. Process small work items inline instead of on a thread pool. Prefer higher-level abstractions over raw atomics.

**Protocol buffers.** Do not use them for data that is never serialized. Flatten single-field wrapper messages. Define smaller message types with only the fields you need. Reuse message objects.

## Prompts for this lens

- "Is this on a hot path? If not, stop."
- "Estimate the cost before and after. If the estimate is under a millisecond per request, file it and move on."
- "How many passes over the data does this make? Show each one."
- "How many I/O calls per request, in the worst case? Show the loop that multiplies them."
- "Where is the lookup inside a loop that should be a Map or Set built once?"
- "What is the biggest allocation in this loop, and can it move outside?"
- "What is logged inside the hottest loop?"
- "Establish baseline metrics (p50/p95/p99 latency, throughput) before optimizing; profile before proposing."
- "Add benchmark thresholds or monitoring hooks to prevent performance regressions."

## What not to do

- Do not micro-optimize without a profile. Dean and Ghemawat put "make the compiler's job easier" last and gate it on evidence.
- Do not trade readability for speed off the hot path. Their first hint is the readability test.
- Do not parallelize without measuring; a saturated database or disk gets slower, not faster.
- Do not report a speedup you did not measure.
