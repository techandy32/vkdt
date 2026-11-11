---
title: Node
type: concept
summary: One GPU kernel with its dispatch size, push constants and descriptor sets.
sources:
  - src/pipe/node.h
  - src/pipe/modules/localsize.h
  - src/pipe/graph-run-nodes-record-cmd.h
  - src/pipe/graph-run-nodes-allocate.h
  - src/pipe/modules/api.h
updated: 2026-11-09
---
# Node

A node is the smallest unit the GPU runs: one compute shader (or, rarely, one draw call)
over a buffer of a known size. Users never see nodes directly; [modules](module.md) create
them each time the graph is rebuilt. The node graph is the second layer of the
[processing graph](processing-graph-dag.md).

## The struct

`dt_node_t` in `src/pipe/node.h:22-55`:

| field | meaning |
|-------|---------|
| `name`, `kernel` | the shader file is `modules/<module name>/<kernel>.comp`, compiled to `.spv` at build time |
| `module` | back pointer to the module instance that created it |
| `connector[30]`, `num_connectors` | inputs and outputs, same struct as on modules |
| `wd`, `ht`, `dp` | size of the dispatch in pixels (and depth for arrays or 3D) |
| `push_constant[64]`, `push_constant_size` | up to 256 bytes handed to the kernel per dispatch |
| `pipeline`, `pipeline_layout`, `dset_layout` | Vulkan objects built once per graph rebuild |
| `uniform_dset[2]`, `dset[2]` | descriptor sets, one per frame for double buffering (`DT_GRAPH_MAX_FRAMES` is 2, `src/pipe/graph-fwd.h:3`) |
| `type` | `s_node_compute` 0, `s_node_graphics` 1, `s_node_geometry` 2, `s_node_vid_dec` 16 (`node.h:11-16`) |
| `rt` | ray tracing acceleration structure data, if used |
| `vtx_cnt` | vertex count for graphics nodes |

## How a kernel is launched

The command recorder (`src/pipe/graph-run-nodes-record-cmd.h`) binds the pipeline and two
descriptor sets, pushes the constants and calls

```
vkCmdDispatch(ceil(wd / 8), ceil(ht / 8), dp)
```

Work group size is 8 by 8 (`DT_LOCAL_SIZE_X`, `DT_LOCAL_SIZE_Y` in
`src/pipe/modules/localsize.h`). A kernel therefore sees one thread per pixel of its output
and must check that it is inside `wd` by `ht`.

Descriptor set 0 holds uniforms: the graph's global block plus the module's committed
parameters. Set 1 holds the connectors in order: an input appears as `sampler2D`, an output
as `image2D`, and array connectors as arrays of them. Module kernels declare them like
`layout(set = 1, binding = 0) uniform sampler2D img_in;`
(`src/pipe/modules/llap/colour.comp:14`).

Before the dispatch the recorder inserts pipeline barriers for every input, so a node only
starts after the nodes that wrote its inputs have finished. The barriers come straight
from the edges of the graph; no module writes synchronisation code.

## Graphics and other node types

A module directory can hold `main.vert` and `main.frag` instead of `main.comp`. The default
`create_nodes` checks for `main.vert.spv` and makes a graphics node, which is recorded as a
draw into the output image with dynamic rendering. If any graphics node exists, the whole
command buffer is submitted on the graphics queue instead of the asynchronous compute queue
(`src/pipe/graph.h:111-113`). Video decode nodes (`s_node_vid_dec`) are used by the
ffmpeg-based input module.

## Creating nodes from a module

In `main.c` a module calls `dt_node_add()` with the kernel name, size, push constants and
connector list, then wires nodes with `dt_node_connect_named()` and links the module's
public connectors to node connectors with `dt_connector_copy()`
(`src/pipe/modules/api.h`). See [module anatomy](../modules/module-anatomy.md).

## Sources

- `src/pipe/node.h:11-16, 22-55`
- `src/pipe/modules/localsize.h` (8 by 8 work groups)
- `src/pipe/graph-run-nodes-record-cmd.h` (barriers, bind, dispatch)
- `src/pipe/graph-run-nodes-allocate.h` (descriptor set writes)
- `src/pipe/graph.h:111-113` (graphics queue fallback)

## Related

- [Module](module.md), [Connector](connector.md)
- [Scheduler: the run passes](../components/scheduler-run-passes.md)
- [Worked example: llap](../modules/llap-worked-example.md)
