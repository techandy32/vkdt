---
title: Module anatomy
type: module
summary: The files that make up a module directory and the helper API modules use to build nodes.
sources:
  - src/pipe/modules/readme.md
  - src/pipe/modules/api.h
  - src/pipe/modules/llap
  - src/pipe/modules/shared
  - src/pipe/global.c
updated: 2026-11-09
---
# Module anatomy

Every module is a directory under `src/pipe/modules/`. The core discovers it at start-up
and reads its text files; nothing has to be registered anywhere else.

## Files

| file | required | purpose |
|------|----------|---------|
| `connectors` | yes | plugs: `name:type:channels:format` per line; see [connector](../concepts/connector.md) |
| `params` | no | settings: `name:type:count:default`; see [parameters and UI](../concepts/parameters-and-ui.md) |
| `params.ui` | no | widgets for the settings |
| `readme.md` | should | documentation; tooltips are generated from it; listed in the [module catalog](module-catalog.md) |
| `main.comp` | one of | the kernel of a one-node module |
| `*.comp`, `*.vert`, `*.frag`, `*.glsl` | | more kernels and includes for multi-node modules |
| `main.c` (or `main.cc`) | no | callbacks: `create_nodes`, `modify_roi_*`, `commit_params`, `check_params`, `read_source`, `write_sink`, ... |
| `flat.mk` | if `main.c` or extra includes | build dependencies and link flags |
| `config.h` | no | constants shared between C and GLSL |

A module with just `connectors` and `main.comp` already works: the default
`create_nodes` makes one node named after the module with the kernel `main`, the output
size equal to the input size, and all parameters passed as uniforms.

## The helper API (`src/pipe/modules/api.h`)

Used inside `main.c`. Line numbers refer to `api.h`.

| function | line | does |
|----------|-----:|------|
| `dt_node_add(graph, module, name, kernel, wd, ht, dp, pc_size, pc, nc, conn...)` | 160 | add a node: dispatch size, push constants, then `nc` connectors given as name, type, channels, format, roi pointer (`dt_no_roi` for inputs) |
| `dt_node_connect_named(graph, n0, "out", n1, "in")` | 212 | wire node output to node input by name; `dt_node_connect` by index |
| `dt_node_feedback_named(...)` | 231 | same, but as a [feedback edge](../concepts/feedback-connectors.md) |
| `dt_connector_copy(graph, module, mc, nid, nc)` | 88 | make module connector `mc` stand for node connector `nc`; this is how the module's public plugs reach the nodes |
| `dt_connector_copy_feedback(...)` | 124 | same, flagged as feedback |
| `dt_connector_bypass(graph, module, mi, mo)` | 142 | let the module pass its input straight to its output (used when disabled) |
| `dt_api_blur(...)`, `dt_api_blur_3x3`, `_5x5`, `_sub`, `_sep` | 583 | add a chain of blur nodes from `shared/blur*.comp` and return the output node |
| `dt_api_guided_filter(...)`, `_full` | 752 | add the guided filter nodes (`shared/guided1-3.comp`) |
| `dt_api_radix_sort(...)` | 949 | add a GPU radix sort (`shared/scan.comp`, `count.comp`, `scatter.comp`) |
| `dt_module_get(graph, name, inst)` | 808 | find a module id |
| `dt_module_set_param_string(module, param, str)` | 860 | set a string parameter (filenames) |
| `dt_module_get_input_img_param(graph, module, conn)` | 927 | follow the input connection to the upstream [image metadata](../concepts/image-params-metadata.md) |
| `dt_node_source`, `dt_node_sink`, `dt_connector_owner`, `dt_connector_find_owner`, `dt_connector_ssbo` | | small lookups |

`CONN(...)` wraps a connect call and prints the [connector](../concepts/connector.md)
error string if it fails (`src/pipe/connector.h:209`).

## Shared GLSL

`src/pipe/modules/shared/` holds kernels and includes any module may use: `blur*.comp`,
`guided*.comp`, `resample.comp`, `add.comp`, `scan.comp`, `count.comp`, `scatter.comp`
(radix sort), `coopmat.glsl` (cooperative matrix helpers for neural network modules),
`dtucs.glsl` and `munsell.glsl` (colour spaces), `oetf.glsl` (transfer curves),
`upsample.glsl`, `render3d.glsl`, `text.h`. Kernels include them with
`#include "shared/..."`; the shader compiler is run with `-Ipipe/modules`
(`src/Makefile:182`).

## Inside a kernel

A compute kernel declares an 8 by 8 local size, a `params` uniform block whose layout
matches the `params` file, optional push constants, and the connectors as
`layout(set = 1, binding = N)`. It reads `imageSize`-independent dimensions from the
`run` uniform block of the graph and returns early for threads outside the output size.
See [node](../concepts/node.md) for the binding layout.

## Convention for connector names

`input` and `output` have special meaning: the default ROI and metadata propagation
treats them as the main chain (`src/pipe/modules/readme.md`). A module with another
naming has to implement the callbacks itself.

## Sources

- `src/pipe/modules/readme.md` (file descriptions, widget list)
- `src/pipe/modules/api.h:88-949`
- `src/pipe/modules/shared/` listing, `src/Makefile:182`
- `src/pipe/connector.h:209` (`CONN`)

## Related

- [Module](../concepts/module.md), [Node](../concepts/node.md)
- [Add a module](../workflows/adding-a-module.md)
- [Worked example: llap](llap-worked-example.md)
