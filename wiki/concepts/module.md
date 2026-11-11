---
title: Module
type: concept
summary: The user-facing processing box, its class, instance, callbacks and parameters.
sources:
  - src/pipe/module.h
  - src/pipe/global.h
  - src/pipe/global.c
  - src/pipe/modules/api.h
  - src/pipe/modules/readme.md
updated: 2026-11-09
---
# Module

A module is one box in the graph the user sees: `denoise`, `crop`, `llap`, `i-raw`,
`display`. It has typed plugs ([connectors](connector.md)), settings
([parameters](parameters-and-ui.md)) and, when the graph runs, it expands into one or more
[nodes](node.md).

## Class and instance

Two structs describe a module:

| struct | file | one per | holds |
|--------|------|---------|-------|
| `dt_module_so_t` | `src/pipe/global.h` | module *type* (`denoise`) | the loaded shared object, callback pointers, the parameter descriptions, connector template |
| `dt_module_t` | `src/pipe/module.h:127` | module *instance* in a graph (`denoise:main`) | pointer to its class, instance name, its 30 connector slots, parameter bytes, image metadata, keyframes |

Classes are discovered at start-up by `src/pipe/global.c`: for every directory under
`modules/` it loads `modules/<name>/lib<name>.so` with `dlopen` (if present) and reads the
`connectors`, `params` and `params.ui` files. A module without C code still works; it just
gets default behaviour for every callback.

A graph can hold several instances of the same class. Names are [tokens](tokens.md), so a
class or instance name has at most 8 characters. The default graphs name the input and the
display `main` and the processing modules `01` (`bin/default-darkroom.i-raw`). The
instance `main` is special: the
scheduler processes `main` sinks first, and the image metadata of the `main` input module
is the one most modules trust (`src/pipe/module.h:105`).

## Callbacks of a class

All are optional (`src/pipe/global.h:75-109`). When a callback is missing, the core uses a
default.

| callback | when it runs | default |
|----------|--------------|---------|
| `init` / `cleanup` | instance created or destroyed | nothing |
| `modify_roi_out` | run pass 1, sources to sinks | copy input size to outputs |
| `modify_roi_in` | run pass 2, sinks to sources | request from inputs what outputs need |
| `create_nodes` | run pass after sizes are known | one node with kernel `main` |
| `commit_params` | before command recording | copy raw parameter bytes as uniforms |
| `check_params` | GUI changed a parameter | return `s_graph_run_record_cmd_buf` |
| `animate` | start of a run while animating | nothing |
| `read_source` | upload pass, source modules | none (must exist for `i-*`) |
| `write_sink` | download pass, sink modules | none (must exist for `o-*`) |
| `input` | GUI event forwarded to the module | nothing |
| `ui_callback` | a `callback` widget was pressed | nothing |
| `audio` | the GUI asks for audio samples | nothing |
| `bs_init` | Windows-only startup hook | nothing |

`has_inout_chain` (`global.h:119`) marks a class whose first input and output pair can be
bypassed, so the GUI can disable the module for comparison.

## What an instance carries

From `src/pipe/module.h:127-167`:

- `connector[DT_MAX_CONNECTORS]`, `num_connectors`: the plugs and what they are wired to.
- `img_param`: the [image metadata](image-params-metadata.md) *as output by this module*.
- `param`, `param_size`: a byte block in the graph's parameter pool. Sliders write here.
- `keyframe`, `keyframe_cnt`, `param_keyframe[]`: animation data. See
  [history and keyframes](history-and-keyframes.md).
- `disabled`: GUI bypass switch, only valid when the class has an in/out chain.
- `version`: lets a module reinterpret old parameter layouts.

## Where a module lives on disk

```
src/pipe/modules/<name>/
  connectors     name:type:channels:format, one per line
  params         name:type:count:default values
  params.ui      widget per parameter (optional)
  readme.md      documentation; also the source of tooltips
  main.c         callbacks (optional)
  *.comp         GLSL compute kernels, compiled to .spv
```

See [module anatomy](../modules/module-anatomy.md) for the helper API that `main.c` uses to
build nodes, and [module catalog](../modules/module-catalog.md) for the list of modules.

## Sources

- `src/pipe/module.h:127-167` (`dt_module_t`), `:72-110` (`dt_image_params_t`)
- `src/pipe/global.h:75-121` (`dt_module_so_t` callbacks), `src/pipe/global.c` (dlopen)
- `src/pipe/modules/api.h` (helpers), `src/pipe/modules/readme.md` (categories)

## Related

- [Node](node.md), [Connector](connector.md), [Parameters and UI](parameters-and-ui.md)
- [Module anatomy](../modules/module-anatomy.md)
- [Add a module](../workflows/adding-a-module.md)
