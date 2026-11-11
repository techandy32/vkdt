---
title: Processing graph (DAG)
type: concept
summary: The directed acyclic graph of modules and nodes, its rules, limits and traversal.
sources:
  - src/pipe/graph.h
  - src/pipe/graph.c
  - src/pipe/graph-traverse.inc
  - src/pipe/cycles.h
  - src/pipe/connector.h
  - src/pipe/readme.md
updated: 2026-11-09
---
# Processing graph (DAG)

A **DAG** is a directed acyclic graph: boxes joined by arrows, where arrows have a
direction and you can never follow arrows back to where you started. In vkdt the boxes are
image operations and the arrows carry image buffers. Everything the program does to pixels
is described by one such graph, the `dt_graph_t` struct in `src/pipe/graph.h`.

## Two layers

| layer | element | what it is | array in `dt_graph_t` |
|-------|---------|------------|------------------------|
| module graph | [module](module.md) | the box a user sees and edits, e.g. `denoise:main` | `module[]`, `num_modules` |
| node graph | [node](node.md) | one GPU kernel with a fixed size | `node[]`, `num_nodes` |

Every run, each module expands into its nodes (`create_nodes` callback). A simple module
makes one node. A big one, like `llap`, makes about 24. See
[worked example: llap](../modules/llap-worked-example.md).

## Rules

1. **Arrows point forward only.** When a connection is made, `dt_connection_is_cyclic`
   (`src/pipe/cycles.h:51`) walks the graph from the destination and refuses the edge if it
   could reach the source again. The error is code 12, "connection would be cyclic"
   (`src/pipe/connector.h:196`).
2. **Feedback edges are the one exception.** They carry last frame's result into this
   frame and are skipped by the cycle check. See [feedback connectors](feedback-connectors.md).
3. **An output can feed many inputs. An input takes exactly one output.** The graph only
   stores, on each input, which output it is connected to (`connector.h:114-118`).
4. **Only what leads to a sink runs.** Traversal starts at the sinks and walks backwards.
   A module that is in the recipe but not wired to a sink is never scheduled.
5. **Sizes are negotiated before anything runs.** See [region of interest](roi-region-of-interest.md).

## Traversal

`src/pipe/graph-traverse.inc` is a piece of code that is included several times and works
on any array whose elements have a `connector[]` member, so the same code sorts modules and
nodes. It does a depth-first search:

- Start at every sink. Sinks whose instance is named `main` are pushed first
  (`graph-traverse.inc:28-45`), so the main display is processed before helpers like the
  histogram.
- Follow each input connector back to the module or node that writes it.
- Emit an element after all of its inputs have been emitted (post-order). The resulting
  list is a valid topological order: every producer comes before its consumers.

That ordered list is what the scheduler loops over in every pass. See
[scheduler run passes](../components/scheduler-run-passes.md).

## Limits

| limit | value | where |
|-------|------:|-------|
| modules per graph | 100 | `modid[100]`, `src/pipe/graph.c:795` |
| nodes per graph | 2000 | `nodeid[2000]`, `src/pipe/graph.c:811` |
| traversal work stack | 1000 | `stack[1000]`, `graph-traverse.inc:13` |
| feedback stack | 100 | `feedback_stack[100]`, `graph-traverse.inc:14` |
| visited marks | 4000 | `mark[4000]`, `graph-traverse.inc:16` |
| connectors per module or node | 30 | `DT_MAX_CONNECTORS`, `src/pipe/connector.h:98` |
| parameters per module | 100 | `DT_MAX_PARAMS_PER_MODULE`, `src/pipe/global.h:9` |

The run aborts with an error when a graph has more modules or nodes than the fixed arrays
hold (`graph.c:796, 812`).

## Why a graph and not a list

A list (darktable's pixelpipe is one) cannot express two inputs into one box, two outputs
out of one box, or a result that feeds back into the next frame. A graph can, and it also
tells the scheduler which buffers are dead so their memory can be reused. The trade-offs
are listed in [why a DAG?](../faq/why-a-dag.md).

## Sources

- `src/pipe/graph.h` (the struct), `src/pipe/graph.c:795-812` (fixed arrays)
- `src/pipe/graph-traverse.inc` (DFS, `main` first)
- `src/pipe/cycles.h:51` (cycle check), `src/pipe/connector.h:114-118, 181-200` (fan-out rule, error strings)
- `src/pipe/readme.md` (design notes)

## Related

- [Module](module.md), [Node](node.md), [Connector](connector.md)
- [Scheduler: the run passes](../components/scheduler-run-passes.md)
- [Memory aliasing](memory-aliasing.md)
