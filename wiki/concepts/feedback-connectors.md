---
title: Feedback connectors
type: concept
summary: Edges that carry last frame's output into this frame, double-buffered, without making the graph cyclic.
sources:
  - src/pipe/connector.h
  - src/pipe/modules/api.h
  - src/pipe/graph-io.c
  - src/pipe/cycles.h
  - bin/examples/webcam-taa.cfg
  - bin/examples/ad.cfg
updated: 2026-11-09
---
# Feedback connectors

Some effects need the result of the *previous* frame: temporal anti-aliasing, iterative
solvers, accumulation of samples, particle systems. In a strict DAG that is a cycle. vkdt
allows it with a special edge type, the feedback connector.

## What it is

A feedback edge is a normal connection whose input connector has the flag `s_conn_feedback`
(`src/pipe/connector.h:65`). In a recipe it is written with `feedback:` instead of
`connect:` (`src/pipe/graph-io.c:249`). In `main.c` a module uses `dt_node_feedback_named()`
(`src/pipe/modules/api.h:231`) or marks a copied connector with
`dt_connector_copy_feedback()` (`api.h:124-132`).

The rule: a feedback edge is written in frame n and read in frame n+1. In frame 0 the
reader sees cleared memory (or the data from `s_conn_clear_once`).

## How it stays a DAG

- The cycle check (`src/pipe/cycles.h`) skips feedback edges, so the connection is
  accepted even though it closes a loop.
- The traversal (`graph-traverse.inc`) does not follow feedback edges backwards either.
  It collects them on a separate `feedback_stack` and visits their sources as if they were
  independent roots. The schedule for one frame is therefore still acyclic.

## Double buffering

The connector gets `frames = 2` (`api.h:106`). Memory for both copies is allocated as
protected, so [memory aliasing](memory-aliasing.md) never reuses it inside a frame. On
each frame the writer uses buffer `dbuf` and the reader uses buffer `1 - dbuf`; the
descriptor sets for both frames are prepared once (`dset[2]` on the [node](node.md)), so
switching is free. Think of it as two wires crossed: what one frame writes, the next frame
reads.

## Examples in the repository

- `bin/examples/webcam-taa.cfg`: temporal anti-aliasing of a webcam stream. The blended
  output is fed back into the blend module as "history".
- `bin/examples/ad.cfg`: a solver that iterates over frames and feeds its state back.

## Pitfalls

- A feedback input is one frame late by definition. For still images this is harmless
  only if the graph is run for at least two frames (the CLI `--last-frame-only` flag
  renders all frames but writes just the last one).
- Memory for feedback buffers is permanent for the life of the graph; large feedback
  images cost real video memory.
- The flag is on the *input* connector. The writer does not know that its buffer is read
  late.

## Sources

- `src/pipe/connector.h:65` (flag), `src/pipe/modules/api.h:106, 124-132, 231-245`
- `src/pipe/graph-io.c:249` (`feedback:` line), `src/pipe/cycles.h`, `src/pipe/graph-traverse.inc:14`
- `bin/examples/webcam-taa.cfg`, `bin/examples/ad.cfg`

## Related

- [Processing graph](processing-graph-dag.md), [Connector](connector.md)
- [Memory aliasing](memory-aliasing.md)
- [History and keyframes](history-and-keyframes.md) (animation frames)
