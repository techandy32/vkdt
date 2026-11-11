---
title: Run flags
type: concept
summary: The bit flags that choose which passes a graph run repeats after an edit.
sources:
  - src/pipe/modules/api.h
  - src/pipe/graph.c
  - src/gui/render_darkroom.h
  - src/gui/render_darkroom.c
  - src/gui/api.h
  - src/pipe/modules/demosaic/main.c
updated: 2026-11-09
---
# Run flags

`dt_graph_run()` does not always do everything. The caller passes a bit mask that says
which passes are needed. The GUI keeps the mask in `vkdt.graph_dev.runflags`, ORs bits
into it when something changes, and the render loop runs the graph once per frame with
that mask (`src/gui/render_darkroom.c:1249`).

## The bits

From `src/pipe/modules/api.h:27-36`:

| flag | value | pass it enables |
|------|------:|-----------------|
| `s_graph_run_roi` | 1 | recompute [regions of interest](roi-region-of-interest.md) |
| `s_graph_run_create_nodes` | 2 | expand modules into [nodes](node.md), rebuild pipelines |
| `s_graph_run_alloc` | 4 | plan and allocate GPU memory; see [memory aliasing](memory-aliasing.md) |
| `s_graph_run_record_cmd_buf` | 8 | upload uniforms and record the command buffer |
| `s_graph_run_upload_source` | 16 | upload source images (decoded raw) through staging memory |
| `s_graph_run_download_sink` | 32 | copy sink images back to the CPU (export, colour picker) |
| `s_graph_run_wait_done` | 64 | block on the fence until the GPU finished |
| `s_graph_run_before_active` | 128 | run modules before the active module too (no consumer in the code at `af70c5d`, see [open questions](../questions.md)) |
| `s_graph_run_all` | all bits | everything |

The passes are ordered. If nodes are recreated, memory must be reallocated and the command
buffer re-recorded, so `dt_graph_run` treats the mask as a chain: a bit implies the bits
that depend on it.

## Who sets which bits

| event | mask | where |
|-------|------|-------|
| open an image | `s_graph_run_all` | `src/gui/render_darkroom.c:560` |
| move a slider | `record_cmd_buf` plus whatever `check_params()` returns | `src/gui/render_darkroom.h:299-301` |
| `demosaic` method changed | `s_graph_run_all` (graph shape changed) | `src/pipe/modules/demosaic/main.c:50-54` |
| seek in an animation | `record_cmd_buf | wait_done` after applying keyframes | `src/gui/api.h:45` |
| next animation frame | `record_cmd_buf` | `src/gui/render_darkroom.c:696` |
| colour picker or export needs CPU data | `download_sink` | `src/gui/render_darkroom.c:875` |
| CLI export | `s_graph_run_all` with `download_sink` | `src/cli/main.c` |

`check_params()` is the module's chance to say "this parameter changes the graph shape".
The default (in `api.h:254-255`, for the blur radius helper) returns `s_graph_run_all` when
the radius changed and `s_graph_run_record_cmd_buf` otherwise.

## Why it matters

A slider move with only `record_cmd_buf` costs: copy a few hundred bytes of uniforms,
re-record one command buffer, submit. No node is created, no memory moves, no raw file is
read again. That is what makes vkdt feel instant on big images. A change that needs
`create_nodes` costs noticeably more, and `upload_source` means decoding the raw again.

The GUI strips `wait_done` from the mask for interactive frames
(`render_darkroom.c:1249`) and instead uses timeline semaphores to know when a display
image is ready. See [GUI](../components/gui.md).

## Sources

- `src/pipe/modules/api.h:27-36, 254-255`
- `src/pipe/graph.c:770-1001` (`dt_graph_run`, which pass checks which bit)
- `src/gui/render_darkroom.h:299-303`, `src/gui/render_darkroom.c:560, 696, 875, 1249`, `src/gui/api.h:45`
- `src/pipe/modules/demosaic/main.c:50-54`

## Related

- [Scheduler: the run passes](../components/scheduler-run-passes.md)
- [Data flow of an edit](../overview/data-flow-of-an-edit.md)
- [Parameters and UI](parameters-and-ui.md)
