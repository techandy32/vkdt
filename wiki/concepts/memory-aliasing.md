---
title: Memory aliasing
type: concept
summary: How the allocator reuses GPU memory for intermediate buffers using last-reader information.
sources:
  - src/pipe/graph-run-nodes-allocate.h
  - src/pipe/alloc.h
  - src/pipe/alloc.c
  - src/pipe/graph.h
  - src/pipe/connector.h
updated: 2026-11-09
---
# Memory aliasing

A graph with 100 nodes on a 50 megapixel image would need many gigabytes if every
intermediate image had its own memory. vkdt gives an intermediate image memory only for
the part of the schedule where it is alive, and reuses that memory afterwards. This is
possible because the whole schedule is known before the first kernel runs. See
[processing graph](processing-graph-dag.md).

## The idea in one picture

```
node order:    A    B    C    D    E
A.out alive:   [=========]            (last read by C)
B.out alive:        [====]            (last read by C)
C.out alive:             [=========]  (last read by E)
D.out alive:                  [====]

memory slot 1: A.out ........ C.out   (C.out takes A.out's slot after C ran)
memory slot 2: B.out ........ D.out
```

Two images share a slot when their live ranges do not overlap.

## How the code does it

All of this is in `src/pipe/graph-run-nodes-allocate.h` and runs during the
`s_graph_run_alloc` pass, walking the nodes in topological order twice.

1. **Mark last readers.** `alloc_outputs()` (`:951`) creates the Vulkan image or buffer
   object for every output and records, on each input, the node index that reads it last
   (`nid_last_ref`, `:980`).
2. **Allocate and free in order.** `alloc_alias_memory()` (`:524`) visits nodes in order.
   For each output it asks the arena for a block (`memory_alloc`, `:504`). For each input
   whose `nid_last_ref` is this node, it frees the block right after (`:618-621`). A block
   freed here is available to the very next node's outputs.
3. **One real allocation.** The arena (`dt_graph_memory_t`, `src/pipe/graph.h:42-44`) is
   a `dt_vkalloc_t` free-list allocator that only hands out offsets. After the planning
   walk, the graph knows the peak size and calls `vkAllocateMemory` once per arena, then
   `bind_buffers_to_memory()` (`:322`) binds every image to its offset.

The allocator itself (`src/pipe/alloc.c`) is a plain first-fit free list:
`dt_vkalloc_init`, `dt_vkalloc`, `dt_vkfree`, `dt_vkalloc_nuke` to clear everything,
`dt_vkalloc_check` for debugging (`alloc.c:12-216`).

## Arenas

Memory is split by use, because Vulkan needs different memory types:

| arena | holds | request |
|-------|-------|---------|
| device images | intermediate images | `memory_request_device()` (`:453`) |
| device buffers (SSBO) | storage buffers, ray tracing data | same with 32 bit offsets when needed |
| staging | CPU-visible copies for source upload and sink download | `memory_request_staging()` (`:463`) |
| uniform | parameters per node per frame | `vkmem_uniform`, `graph.h:126` |

## What is never aliased

`dt_vkalloc_protected()` (`alloc.c:52`) reserves a block that `nuke` and the live-range
logic do not touch. It is used for connectors flagged `s_conn_protected` and for anything
that must survive between runs:

- source and sink buffers (uploaded once, displayed later)
- [feedback connectors](feedback-connectors.md) (`frames == 2`, read next frame)
- dynamic array connectors with their own heap
- ray tracing acceleration structures

## Seeing it

Run with `-d mem` to print the arena sizes and peak use, and `-d perf` for per-node
timings. See [debug the graph](../workflows/debugging-the-graph.md). The node editor's
"vkdt.db" style statistics in the GUI show the same numbers.

## Why it matters

This is the main reason a 50 megapixel image with a deep graph fits into 4 to 8 GB of
video memory, and it is only possible because the graph is a DAG that is fully known
before it runs. A list-based pipeline could do the same for one buffer pair, but not for
graphs with fan-out and feedback.

## Sources

- `src/pipe/graph-run-nodes-allocate.h:322, 453-524, 618-621, 951-980`
- `src/pipe/alloc.h`, `src/pipe/alloc.c:12-216`
- `src/pipe/graph.h:42-44, 126` (arena struct, uniform memory)
- `src/pipe/connector.h:67` (`s_conn_protected`)

## Related

- [Scheduler: the run passes](../components/scheduler-run-passes.md)
- [Feedback connectors](feedback-connectors.md)
- [Why a DAG?](../faq/why-a-dag.md)
