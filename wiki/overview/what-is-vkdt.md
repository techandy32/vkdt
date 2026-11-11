---
title: What vkdt is
type: overview
summary: A GPU-only raw photo and video editor built around a processing graph.
sources:
  - readme.md
  - src/pipe/readme.md
  - doc/release-1.0/readme.md
updated: 2026-11-09
---
# What vkdt is

vkdt is a workflow tool for raw still photos and raw video. It reads camera raw files,
video, and a few other formats, processes them, shows them on screen, and exports them.
Every pixel operation runs on the graphics card through the Vulkan API, written as GLSL
compute shaders. There is no CPU pixel path.

The one idea that shapes the whole program: processing is a **graph**. Boxes (modules) are
connected by arrows (connectors). The graph can have many inputs and many outputs. See
[architecture in one picture](architecture.md) and [processing graph](../concepts/processing-graph-dag.md).

The author also started darktable, and `doc/howto/dt/readme.md` maps darktable modules to
vkdt modules for people switching over (general knowledge plus that file).

## What it can do

From `readme.md`:

- fast GPU-only processing of raw stills
- a general graph of operations with multiple inputs and outputs and feedback connectors for
  animation and iteration
- full-window colour management, 10-bit display output
- noise profiling and profiled denoising
- a folder-based image database with no central catalog (sidecar text files only)
- a command line tool that runs the same graphs headless
- real-time raw video: Magic Lantern `.mlv`, MotionCam `.mcraw`, and ffmpeg-decoded video
- automatic parameter optimisation (`vkdt-fit`), for example to fit vignetting
- neural network modules (u-net denoising, joint demosaicing and denoising, segmentation),
  compiled from ONNX to SPIR-V by the external `denox` project

## Platforms and licence

- Linux is native (Wayland works better than X11). macOS builds with brew and the LunarG SDK.
  Windows builds under msys2. An Android port is unfinished.
- Needs a Vulkan-capable GPU; 4 GB of video memory is the comfortable minimum, 8 GB for very
  large graphs or 50 MP images.
- Licence is 2-clause BSD for most code, with some GPLv3 parts (`i-mlv`), and LGPL libraries
  (rawspeed, ffmpeg).

## Size of the code base

Counted on 2026-11-09 at commit `af70c5d`:

| part | lines | note |
|------|------:|------|
| `src/pipe` (graph core) | 9.9k C | graph, modules, connectors, allocator |
| `src/pipe/modules` | 43k C + 22k GLSL | 101 modules, 205 `.comp` kernels |
| `src/gui` | 17k C | excluding the bundled `nuklear.h` |
| `src/db`, `src/core`, `src/qvk` | 3.0k, 3.4k, 1.4k | database, utilities, Vulkan wrapper |
| `src/cli` | 159 | the command line front-end |

## Ecosystem

Separate repositories hold camera spectral data (`vkdt-camconst`), neural network weights
(`vkdt-nn`), unit tests (`vkdt-test`), the web site, and the `denox` ONNX compiler.

## Sources

- `readme.md` (features, dependencies, FAQ, licence)
- `src/pipe/readme.md` (design of the graph)
- `doc/release-1.0/readme.md` (1.0 release notes)

## Related

- [Architecture in one picture](architecture.md)
- [Repository map](repository-map.md)
- [Why a DAG?](../faq/why-a-dag.md)
