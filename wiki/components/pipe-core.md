---
title: Pipeline core (src/pipe)
type: component
summary: The files that implement the graph, modules, connectors, allocator and I/O.
sources:
  - src/pipe/graph.h
  - src/pipe/graph.c
  - src/pipe/readme.md
  - src/pipe/tests
updated: 2026-11-09
---
# Pipeline core (src/pipe)

About 9.9k lines of C that know nothing about windows, files on disk, or image formats.
They know how to turn a graph description into Vulkan work. Everything else (GUI, CLI,
thumbnails) sits on top of this directory.

## File by file

| file | what it does | wiki page |
|------|--------------|-----------|
| `graph.h`, `graph.c` | `dt_graph_t`; init, cleanup, `dt_graph_run`, pipeline and shader module creation | [scheduler](scheduler-run-passes.md) |
| `graph-fwd.h` | forward declarations, `DT_GRAPH_MAX_FRAMES` 2 | |
| `graph-traverse.inc` | depth-first traversal from sinks, reused for modules and nodes | [processing graph](../concepts/processing-graph-dag.md) |
| `graph-run-modules.h` | the module passes: animate, `modify_roi_out`, `modify_roi_in`, `create_nodes`, uniform upload | [ROI](../concepts/roi-region-of-interest.md) |
| `graph-run-nodes-allocate.h` | image and buffer creation, descriptor sets, memory planning | [memory aliasing](../concepts/memory-aliasing.md) |
| `graph-run-nodes-upload.h` | copy source data into staging memory and onto the GPU | |
| `graph-run-nodes-record-cmd.h` | barriers, binds, push constants, dispatches, draws | [node](../concepts/node.md) |
| `graph-run-nodes-download.h` | copy sink images back and call `write_sink` | [CLI and export](cli-and-export.md) |
| `graph-io.h`, `graph-io.c` | read and write recipes | [recipe format](../concepts/cfg-recipe-format.md) |
| `graph-history.h` | undo history | [history and keyframes](../concepts/history-and-keyframes.md) |
| `graph-export.h`, `graph-export.c` | swap display sinks for output modules, run, write files | [CLI and export](cli-and-export.md) |
| `graph-defaults.h` | which default recipe belongs to which input module | [add a file format](../workflows/adding-a-file-format.md) |
| `graph-print.h` | dump the graph as text or graphviz | [debug the graph](../workflows/debugging-the-graph.md) |
| `module.h`, `module.c` | `dt_module_t`, `dt_image_params_t`, `dt_keyframe_t`, add and remove modules | [module](../concepts/module.md) |
| `node.h` | `dt_node_t` | [node](../concepts/node.md) |
| `connector.h`, `connector.c`, `connector.inc` | `dt_connector_t`, `dt_roi_t`, connect functions, error strings | [connector](../concepts/connector.md) |
| `cycles.h` | cycle detection for module and node graphs | [processing graph](../concepts/processing-graph-dag.md) |
| `global.h`, `global.c` | module class registry, `dlopen` of `lib<name>.so`, parsing of `connectors`, `params`, `params.ui` | [module](../concepts/module.md) |
| `params.h` | `dt_ui_param_t` | [parameters and UI](../concepts/parameters-and-ui.md) |
| `anim.h` | interpolation curves for keyframes | [history and keyframes](../concepts/history-and-keyframes.md) |
| `token.h` | 8-byte names | [tokens](../concepts/tokens.md) |
| `alloc.h`, `alloc.c` | free-list allocator over a Vulkan memory block | [memory aliasing](../concepts/memory-aliasing.md) |
| `raytrace.h`, `raytrace.c` | acceleration structure build for ray tracing modules | |
| `buffer.h`, `buffer.c`, `res.h`, `res.c` | small buffer helpers and resource lookups (search paths for module files) | |
| `asciiio.h` | parse numbers and tokens from text | |
| `dlist.h` | intrusive doubly linked list | |
| `geo.h`, `draw.h` | geometry and drawing helpers for graphics nodes | |
| `dng_opcode.h`, `metadata.h`, `icc-profiles.h` | raw metadata helpers shared by input modules | |
| `pipe.h` | umbrella include | |
| `modules/` | the modules themselves | [module anatomy](../modules/module-anatomy.md) |

## The central struct

`dt_graph_t` (`src/pipe/graph.h`) owns:

- `module[]`, `num_modules`; `node[]`, `num_nodes`
- the parameter pool every module's `param` pointer points into
- memory arenas (`dt_graph_memory_t` with a `dt_vkalloc_t` heap and a `VkDeviceMemory`),
  uniform memory, staging memory
- command buffers and pools for two frames, a timeline semaphore, query pools for timings
- `runflags`, `frame`, `frame_cnt`, `frame_rate`
- history pool and indices
- `searchpath` and `basedir` for finding module files and side files
- GUI hooks (`gui_attached`, `active_module`)

Two graphs are usually alive in the GUI: `vkdt.graph_dev` for the darkroom and one per
thumbnail thread (`src/db/thumbnails.h:40`).

## Tests

`src/pipe/tests/` has small programs for the allocator (`alloc.c`), graph construction
(`graph.c`), a pipe run (`pipe.c` with `pipe.cfg`) and tokens (`token.c`). The larger
regression suite lives in the separate `vkdt-test` repository.

## Sources

- `src/pipe/*.h`, `src/pipe/*.c` (listing at commit `af70c5d`)
- `src/pipe/readme.md`
- `src/db/thumbnails.h:40`

## Related

- [Architecture in one picture](../overview/architecture.md)
- [Scheduler: the run passes](scheduler-run-passes.md)
- [Repository map](../overview/repository-map.md)
