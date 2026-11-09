---
title: Why a DAG?
type: faq
summary: The reasons the pipeline is a graph instead of an ordered list, and what that costs.
sources:
  - src/pipe/readme.md
  - src/pipe/modules/readme.md
  - src/pipe/graph-run-nodes-allocate.h
  - src/pipe/graph-run-nodes-record-cmd.h
  - readme.md
updated: 2026-11-09
---
# Why a DAG?

darktable, which the same author started, processes an image through an ordered list of
modules. vkdt replaced the list with a directed acyclic graph. This page gives the
reasons found in the code and its documentation, and the costs.

## What a list cannot do

1. **Two inputs into one operation.** HDR merge, blending a drawn mask, aligning a burst,
   using a colour lookup table as a second image. In a list every module has one input
   and one output. In the graph `blend` has `back`, `input`, `mask` and `output`
   (`src/pipe/modules/readme.md`).
2. **Two outputs out of one operation.** The main image and the histogram
   (`grade` feeds `display:main` and `hist`), a curve preview (`filmcurv`'s `dspy`),
   a mask and the image.
3. **State from the previous frame.** Temporal anti-aliasing, accumulation, simulations.
   [Feedback connectors](../concepts/feedback-connectors.md) make this a one-line recipe
   entry.
4. **Skipping work that nobody needs.** Only modules reachable from a sink are scheduled.
   A disconnected module costs nothing.

## What a graph gives the scheduler

5. **Synchronisation for free.** Each edge becomes a Vulkan barrier between the producer
   and the consumer (`src/pipe/graph-run-nodes-record-cmd.h`). Module authors never write
   synchronisation code.
6. **Memory reuse.** Because all producers and consumers are known before the run, each
   intermediate buffer gets memory only for its live range
   (`src/pipe/graph-run-nodes-allocate.h`). This is why large images fit in GPU memory.
   See [memory aliasing](../concepts/memory-aliasing.md).
7. **Size negotiation.** Requests flow backwards from the sink, so a preview computes a
   fraction of the pixels and an export computes all of them, with the same graph. See
   [ROI](../concepts/roi-region-of-interest.md).
8. **Incremental re-runs.** The graph is persistent between frames. A slider move only
   re-records the command list ([run flags](../concepts/run-flags.md)).
9. **Modules as macros.** A module expands into a sub-graph of nodes
   ([llap](../modules/llap-worked-example.md) becomes 24). Complex algorithms are built
   from small kernels without the module author managing temporaries.
10. **One description for everything.** The GUI, the command line exporter, thumbnails,
    presets and undo all use the same text format. Only the sink changes.

## What it costs

- **Users see a graph.** Wiring boxes is harder than dragging a module up or down a list.
  vkdt hides this behind default graphs and presets, and most users never open the node
  editor, but the complexity is there.
- **Every module negotiates.** ROI in two directions, metadata propagation, connector
  formats. Defaults cover the common case, but a module that does anything unusual has
  more to get right than a darktable module.
- **Fixed limits.** 100 modules, 2000 nodes, 30 connectors, 8-character names
  (`src/pipe/graph.c:795, 811`, `connector.h:98`, `token.h`). They are generous for
  photo editing and tight for generative work.
- **No kernel fusion.** Each node is a separate dispatch with a full write and read of
  its buffers in between. A compiler-based system (Halide, for example) could fuse
  neighbouring stages. vkdt pays memory bandwidth for simplicity.
- **Feedback memory is permanent.** Buffers that cross frames cannot be aliased.
- **A serial schedule.** Nodes are recorded in one topological order on one queue. Two
  independent branches do not run concurrently on the GPU beyond what the driver overlaps
  on its own.

## Verdict

For a GPU-only tool that wants real-time previews on large raws, video, and unusual
compositions, the graph is the natural fit: it is exactly the information the GPU
scheduler needs. The costs are mostly on the module author and the GUI designer, not on
the GPU.

## Sources

- `src/pipe/readme.md`, `src/pipe/modules/readme.md`
- `src/pipe/graph-run-nodes-allocate.h`, `src/pipe/graph-run-nodes-record-cmd.h`
- `src/pipe/graph.c:795, 811`, `src/pipe/connector.h:98`
- `readme.md` (feature list)

## Related

- [Processing graph](../concepts/processing-graph-dag.md)
- [Comparison with other tools](comparison-with-other-tools.md)
- [Architecture in one picture](../overview/architecture.md)
