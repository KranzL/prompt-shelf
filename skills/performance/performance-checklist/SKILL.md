---
name: performance-checklist
description: Run Evis Drenova's low-hanging-fruit performance checklist over a hot path. Sequential work that could be concurrent, too many passes, too many allocations, batching and streaming, long awaits, early exits, thread counts, the right data structure, too many I/O calls. Use when the user asks why something is slow, wants a quick performance pass, mentions latency or throughput on a handler or loop, or runs /performance-checklist.
argument-hint: [path or function]
---

# Low-hanging-fruit performance checklist

Verbatim from Evis Drenova, 2026-10-25. https://x.com/evisdrenova/status/2114216996435116165

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

## Run

Scope: $ARGUMENTS when given, otherwise ask which path is hot. The checklist is for hot paths: request handlers, per-item loops, startup of long-running processes, whatever a profile points at. Test code and setup code are not hot paths. If there is no profile and no measurement, estimate the cost first; if the estimate is under a millisecond per request, file it and move on.

Go through the eleven questions in order against the code and answer each with evidence from the code: the loop that awaits one item at a time, the three passes over the same array, the allocation inside the loop, the query inside the loop, the `.find` inside a loop that should be a Map built once, the log line in the hottest loop. Where a question does not apply, say so in a word.

For each yes, estimate the gain before proposing the change, and name the trade-off (memory for concurrency, complexity for fewer passes).

## Report

The eleven questions with a one-line answer each and file:line evidence. Then the changes worth making in order of estimated gain, each with its trade-off. Do not report a speedup you did not measure; if the user asks for the change, measure before and after.
