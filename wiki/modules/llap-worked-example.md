---
title: "Worked example: llap"
type: module
summary: How one local-contrast module expands into a pyramid of about 24 kernels.
sources:
  - src/pipe/modules/llap/main.c
  - src/pipe/modules/llap/config.h
  - src/pipe/modules/llap/connectors
  - src/pipe/modules/llap/params
  - src/pipe/modules/llap/readme.md
updated: 2026-11-09
---
# Worked example: llap

`llap` is the local contrast, shadows and highlights module. To the user it is one box
with two plugs and four sliders. To the GPU it is a pyramid of about 24 kernels. It is
the clearest example of why vkdt has two graph layers.

## What the user sees

- `connectors`: `input:read:rgba:f16`, `output:write:rgba:f16`
- `params`: `sigma`, `shadows`, `hilights`, `clarity` (all `float`)
- `readme.md`: explains the sliders; the "technical" section says it works on luminance
  with a local Laplacian pyramid and recolours with the method of Mantiuk 2009.

## What `create_nodes` builds

`src/pipe/modules/llap/main.c`, with `NUM_GAMMA` 10 (`config.h:2`):

```
input (rgba)
  |
  v
curve  ----> array of 11 luminance images (one per gamma level, plus gray)
  |
  v
reduce (level 1) -> reduce (level 2) -> ... -> reduce (level nl-1)     each halves the size
  |                   |                            |
  v                   v                            v
assemble(1) <----- assemble(2) <----- ... <----- assemble(nl-1)        each builds one finer level
  |
  v
colour (recolour the new luminance with the original rgba)
  |
  v
output (rgba)
```

Step by step:

1. **`curve`** (`main.c:31-35`): one node, full size, output `array_length = 11`. Each
   array slice is the luminance pushed through a different tone curve (the gamma levels).
   The push constant carries `num_gamma`.
2. **`reduce`** (`main.c:51-55`): for each level `l` from 1, a node at half the previous
   size, dispatch depth 11 so all slices reduce at once. Its input is the previous
   level's output (`main.c:57`). The loop stops at `max_nl = 12` levels (`main.c:44`) or when
   the image gets smaller than 2 pixels (`main.c:84-88`).
3. **`assemble`** (`main.c:67-77`): for each level, a node at the *finer* size with
   inputs `coarse` (the next coarser assembled result), `currlo` and `currhi` (the reduce
   outputs around this level) and output `fine`. Levels are chained coarse to fine
   (`main.c:77`). The coarsest `assemble` gets the gray slice of `curve` as its `coarse`
   input and a push constant that says so (`main.c:92-93`).
4. **`colour`** (`main.c:96-100`): takes the finest assembled luminance (`lum`) and the
   original `input`, writes the final `output`.
5. **Wiring to the module** (`main.c:103-105`): `dt_connector_copy` maps the module's
   `input` to both `curve.input` and `colour.input`, and the module's `output` to
   `colour.output`.

Node count: 1 curve + (nl-1) reduce + (nl-1) assemble + 1 colour. For a 24 megapixel
image `nl` reaches the cap of 12, giving 24 nodes. For a small preview `nl` is smaller,
so fewer nodes exist.

## What the core does with that

- The [ROI](../concepts/roi-region-of-interest.md) of every node is computed from the
  module's input ROI, halved per level (`main.c:39-42, 79-83`), so the dispatch sizes are
  right at any preview scale.
- [Memory aliasing](../concepts/memory-aliasing.md) frees each `reduce` output after the
  two `assemble` nodes that read it, so the pyramid costs far less than 11 full-size
  images times 12 levels.
- Barriers between `reduce` and `assemble` nodes come from the connections; the module
  author wrote none.
- Changing a slider only re-uploads the four floats; the 24 nodes and their memory stay.
  Resizing the window changes the ROI and rebuilds them.

## Why this is good

The module author wrote about 120 lines of C and four kernels and got a full multi-scale
algorithm that previews at interactive speed and exports at full resolution. In a
list-based pipeline the same module would have to manage its own temporaries and
synchronisation.

## Sources

- `src/pipe/modules/llap/main.c:31-105`, `config.h:2`
- `src/pipe/modules/llap/connectors`, `params`, `readme.md`

## Related

- [Module anatomy](module-anatomy.md)
- [Node](../concepts/node.md), [Region of interest](../concepts/roi-region-of-interest.md)
- [Default raw pipeline](default-raw-pipeline.md)
