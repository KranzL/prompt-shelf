# Performance Hints, distilled

Jeff Dean and Sanjay Ghemawat, https://abseil.io/fast/hints.html (first published 2023-07-27, updated 2025-12-16). Section names are theirs; the one-line summaries are ours. Read the original for the examples.

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

## What not to do

- Do not micro-optimize without a profile. They put "make the compiler's job easier" last and gate it on evidence.
- Do not trade readability for speed off the hot path. Their first hint is the readability test.
- Do not parallelize without measuring; a saturated database or disk gets slower, not faster.
- Do not report a speedup you did not measure.
