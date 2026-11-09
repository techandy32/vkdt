---
title: Comparison with other tools
type: faq
summary: darktable, DaVinci Resolve, compositors, render graphs and ML frameworks next to vkdt.
sources:
  - readme.md
  - doc/howto/dt/readme.md
  - src/pipe/readme.md
updated: 2026-11-09
---
# Comparison with other tools

Most facts about other programs on this page are general knowledge, checked against
public documentation in November 2026. They are not in the vkdt repository. Where a
statement comes from the repository it is cited.

## Photo editors

| tool | pipeline model | relation to vkdt |
|------|----------------|------------------|
| darktable | an ordered list of modules (the pixelpipe), order editable but linear | same author; `doc/howto/dt/readme.md` maps darktable modules to vkdt modules. vkdt's graph removes the single-chain limit |
| RawTherapee | fixed-order pipeline | vkdt is more general and GPU only |
| GIMP 3.0 (2025) | non-destructive layer stack on GEGL, which is itself a graph library | GEGL is a CPU graph with lazy evaluation; vkdt is a GPU graph compiled to one command list |
| Lightroom, Capture One | fixed pipelines behind sliders, GPU accelerated | no user-visible graph |

## Video and compositing

| tool | model | relation |
|------|-------|----------|
| DaVinci Resolve (colour page) | node graph: serial, parallel, layer mixer, outside nodes | closest in spirit. Resolve's nodes are colour operations on one clip; vkdt's modules can be any kernel and can have many inputs and outputs. Both chose a graph for the same reason: operations that combine results |
| Nuke, Fusion, Natron, Blender compositor | full node compositors | general DAGs like vkdt. Blender's GPU compositor (since 3.5, default by 2024) also compiles the node tree to GPU work |
| FFmpeg filtergraph | text-described filter graph | like vkdt's recipe, a graph in plain text; CPU and GPU filters mixed |

## Game and graphics engines

| system | model | relation |
|--------|-------|----------|
| Frostbite FrameGraph (GDC 2017), Unity render graph (default in Unity 6), Unreal RDG | a DAG of render passes declared per frame; the engine allocates transient memory by live range and inserts barriers | this is the same technique as vkdt's [memory aliasing](../concepts/memory-aliasing.md) and barrier generation. vkdt applies it to photo processing and keeps the graph persistent between frames |
| q2vkpt | Quake 2 path tracer | vkdt's Vulkan bootstrap code comes from it (`src/qvk/readme.md`) |

## Compilers and ML

| system | model | relation |
|--------|-------|----------|
| Halide | separates algorithm from schedule, fuses stages | vkdt does not fuse kernels; each node is a dispatch. Halide optimises inside a stage chain, vkdt optimises memory across the whole graph |
| PyTorch, TensorFlow, ONNX | computation graphs | vkdt consumes ONNX networks compiled to SPIR-V by the separate `denox` project (`readme.md`), so a network becomes nodes in the same graph |
| OpenCL and Vulkan compute by hand | explicit kernels and buffers | what a module author would otherwise write; vkdt generates the glue |

## Is a DAG the modern trend?

Yes, for anything that runs on a GPU and combines operations: compositors have always
been graphs, colour grading moved to nodes with Resolve, real-time engines moved to render
graphs around 2017, ML frameworks are graphs, and GIMP moved onto a graph library. Raw
photo editors are the exception, mostly because their users want a list of sliders. vkdt
is a raw editor that took the graph route and hides the graph behind default recipes.

## Sources

- `readme.md` (features, denox), `doc/howto/dt/readme.md`, `src/qvk/readme.md`
- general knowledge about the other tools, checked against their public documentation in
  November 2026

## Related

- [Why a DAG?](why-a-dag.md)
- [What vkdt is](../overview/what-is-vkdt.md)
