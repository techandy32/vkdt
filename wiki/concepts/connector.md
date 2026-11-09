---
title: Connector
type: concept
summary: The typed input and output plugs on modules and nodes, and the rules for wiring them.
sources:
  - src/pipe/connector.h
  - src/pipe/connector.c
  - src/pipe/connector.inc
  - src/pipe/cycles.h
  - src/pipe/modules/readme.md
updated: 2026-11-09
---
# Connector

A connector is a plug on a [module](module.md) or [node](node.md). An arrow in the graph
always runs from an output connector to an input connector. The connector carries the
buffer's type, pixel format and size, so the core can check that two plugs fit before it
wires them.

## The four fields

Each module directory has a `connectors` file with one line per plug:

```
name:type:channels:format
```

Example from `src/pipe/modules/llap/connectors`:

```
input:read:rgba:f16
output:write:rgba:f16
```

| field | values | meaning |
|-------|--------|---------|
| type | `read`, `write`, `source`, `sink`, `modify` | `source` is an output filled from the CPU (input modules); `sink` is an input read back to the CPU or shown on screen; `modify` is an input that may be written in place |
| channels | `r`, `rg`, `rgb`, `rgba`, `rggb`, `yuv`, `ssbo`, ... | `ssbo` means a storage buffer instead of an image |
| format | `f16`, `f32`, `ui8`, `ui16`, `ui32`, `atom`, `dspy`, `bc1`, `yuv` | `dspy` is the swap chain format for display sinks, `bc1` a compressed thumbnail |

Two wildcards exist. `*` means "take whatever is connected" (defaults to `rgba:f16` when
nothing is connected). `&input` means "same as the connector named input", which is how a
pass-through module keeps the format of its input.

## Flags

`dt_connector_flags_t` (`src/pipe/connector.h:62-71`):

| flag | value | effect |
|------|------:|--------|
| `s_conn_smooth` | 1 | sampled with bilinear filtering |
| `s_conn_clear` | 2 | cleared to zero before the node writes it |
| `s_conn_feedback` | 4 | written in frame n, read in frame n+1; see [feedback connectors](feedback-connectors.md) |
| `s_conn_dynamic_array` | 8 | array whose contents change during animation |
| `s_conn_protected` | 16 | never aliased with other buffers; see [memory aliasing](memory-aliasing.md) |
| `s_conn_double_buffer` | 32 | two copies so drawing and computing overlap |
| `s_conn_mipmap` | 64 | mip levels are generated |
| `s_conn_clear_once` | 128 | cleared only on frame 0 |
| `s_conn_concurrent` | 256 | shared between graphics and compute queues |

## What a connector stores at run time

`dt_connector_t` (`connector.h:105-150`) holds the four tokens, the flags, the
[region of interest](roi-region-of-interest.md), and bookkeeping:

- `connected`: for inputs, which output feeds it. Outputs do not know their readers
  (`connector.h:114-118`).
- `array_length`, `frames`: a connector can be an array of images and can have two frames
  (double buffering). The node consumes `array_length * frames` images.
- `mem_staging`, `offset_staging[2]`: staging memory for sources and sinks.
- `array_heap`, `array_dim`: the private allocator of a dynamic array connector.

## Wiring rules and errors

`dt_module_connect` and `dt_node_connect` (`src/pipe/connector.c` with the shared body in
`connector.inc`) check both ends and return a code. `dt_connector_error_str`
(`connector.h:181-200`) turns it into text:

| code | message |
|-----:|---------|
| 1, 2 | no such destination node / connector |
| 3 | destination does not read |
| 4, 5, 6 | destination inconsistent |
| 7, 8 | no such source node / connector |
| 9 | source does not write |
| 10 | channels do not match |
| 11 | format does not match |
| 12 | connection would be cyclic (`src/pipe/cycles.h`) |
| -100, -101 | named source / destination connector does not exist |

An output may fan out to any number of inputs. An input accepts exactly one output. There
are at most 30 connectors per module or node (`DT_MAX_CONNECTORS`, `connector.h:98`).

## Sources

- `src/pipe/connector.h:62-71` (flags), `:98` (limit), `:105-150` (struct), `:181-200` (errors)
- `src/pipe/connector.c`, `src/pipe/connector.inc` (connect functions)
- `src/pipe/cycles.h` (cycle test)
- `src/pipe/modules/llap/connectors` (example)

## Related

- [Module](module.md), [Node](node.md)
- [Recipe file format](cfg-recipe-format.md) (the `connect:` line)
- [Image parameters](image-params-metadata.md) (what travels along the arrow besides pixels)
