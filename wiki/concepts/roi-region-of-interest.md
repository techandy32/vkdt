---
title: Region of interest (ROI)
type: concept
summary: How sizes flow forward and requests flow backward so kernels compute only what a sink needs.
sources:
  - src/pipe/connector.h
  - src/pipe/graph-run-modules.h
  - src/pipe/modules/api.h
  - src/pipe/modules/llap/main.c
updated: 2026-11-09
---
# Region of interest (ROI)

Every [connector](connector.md) carries a `dt_roi_t` (`src/pipe/connector.h:26-32`):

| field | meaning |
|-------|---------|
| `full_wd`, `full_ht` | the size of the whole image at this point in the graph |
| `wd`, `ht` | the size that will actually be computed and stored |
| `marker` | who decided this size and how firmly (`s_roi_mark_*`, `connector.h:13-20`) |

The ratio `wd / full_wd` is the scale. A darkroom preview on a small window may compute
a 1500 pixel wide version of a 6000 pixel wide raw. The nodes then run on 16 times fewer
pixels, which is why previews are fast. There is no x/y offset in the struct: the ROI is a
scaled version of the full image, not a crop window. Cropping is done by the `crop` module
itself, which changes `full_wd` and `full_ht` of its output.

## Two passes

Sizes are negotiated at the start of every run that has `s_graph_run_roi` set
(`src/pipe/graph-run-modules.h`), before any node exists.

1. **Forward: `modify_roi_out`.** Modules are visited from sources to sinks. A source
   module (`i-raw`) sets `full_wd` and `full_ht` of its output from the file. The default
   for every other module copies the input ROI to all outputs. A module that changes size
   overrides this: `crop` shrinks, a resampler may grow.
2. **Backward: `modify_roi_in`.** Modules are visited from sinks to sources. The sink says
   what it wants: a `display` sink asks for the window size (clamped by `max_wd`,
   `max_ht`, `connector.h:124`), an output module asks for full size or an export limit.
   The default copies the request from the output to every input. A module that needs
   more than its output (a blur with a border, a pyramid) asks for more.

After the backward pass, `propagate_roi_in` makes outputs agree with the inputs they are
wired to, and the markers resolve conflicts: a `hard` request wins over a `soft` one, and a
backward (`bck`) decision wins over a forward one (`dt_roi_stronger`, `connector.h:34`).

Only then does `create_nodes` run, so a module knows its final sizes when it makes nodes
and can compute pyramid levels or dispatch sizes from them.

## Example

`llap` builds a Laplacian pyramid. In `modify_roi_in` it rounds the requested size up so
that every pyramid level divides cleanly, and in `create_nodes` it creates one node per
level with `wd` and `ht` halved each step (`src/pipe/modules/llap/main.c`). The number of
levels depends on the size, so a smaller preview makes fewer nodes.

## Why it is done this way

- Computing only the requested size makes the interactive preview fast and export exact
  with the same graph.
- Because the request walks backwards, a module never has to know who reads it.
- Sizes are known before memory is given out, so the allocator can plan the whole run.
  See [memory aliasing](memory-aliasing.md).

The cost is that every module author must think about two directions. Most modules take
the defaults and are fine.

## Sources

- `src/pipe/connector.h:13-36` (`dt_roi_t`, markers, `dt_roi_stronger`), `:124` (`max_wd`)
- `src/pipe/graph-run-modules.h` (the two passes and `propagate_roi_in`)
- `src/pipe/modules/llap/main.c` (a module with its own ROI callbacks)

## Related

- [Run flags](run-flags.md) (`s_graph_run_roi`)
- [Scheduler: the run passes](../components/scheduler-run-passes.md)
- [Worked example: llap](../modules/llap-worked-example.md)
