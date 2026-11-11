---
title: Repository map
type: overview
summary: What each directory in the source tree contains and how large it is.
sources:
  - Makefile
  - src/Makefile
  - readme.md
updated: 2026-11-09
---
# Repository map

Line counts were taken on 2026-11-09 at commit `af70c5d` with `wc -l` over `.c`, `.h` and
`.inc` files (GLSL counted separately).

| path | what is in it | size | wiki page |
|------|---------------|-----:|-----------|
| `src/pipe/` | the graph: `dt_graph_t`, modules, nodes, connectors, allocator, recipe I/O, export, history, ray tracing glue | 9.9k | [pipeline core](../components/pipe-core.md) |
| `src/pipe/modules/<name>/` | one folder per module: `connectors`, `params`, `params.ui`, `readme.md`, `*.comp` kernels, optional `main.c` | 43k C, 22k GLSL | [module anatomy](../modules/module-anatomy.md) |
| `src/pipe/modules/shared/` | kernels and GLSL includes shared by modules: blur, guided filter, resample, radix sort pieces, colour spaces | | [module anatomy](../modules/module-anatomy.md) |
| `src/gui/` | GLFW window, nuklear UI, the four views, widgets, hotkeys, display synchronisation | 17k (plus bundled `nuklear.h`) | [GUI](../components/gui.md) |
| `src/cli/` | `vkdt-cli` headless exporter | 159 | [CLI and export](../components/cli-and-export.md) |
| `src/fit/` | `vkdt-fit` parameter optimiser | 376 | [core utilities](../components/core-utilities.md) |
| `src/db/` | image list per folder, `vkdt.db`, thumbnails, `config.rc` handling, string pools | 3.0k | [database and thumbnails](../components/database-and-thumbnails.md) |
| `src/core/` | logging, threads, file system helpers, LUT loader, half floats, small math | 3.4k | [core utilities](../components/core-utilities.md) |
| `src/qvk/` | Vulkan instance, device, queues, swap chain helpers (from q2vkpt) | 1.4k | [Vulkan layer](../components/qvk-vulkan-layer.md) |
| `src/snd/` | audio output backends: alsa, pipewire, none | 311 | [core utilities](../components/core-utilities.md) |
| `src/tools/` | colour tooling: `clut` (input device transforms), `spec`, `read-icc` | | [core utilities](../components/core-utilities.md) |
| `src/*.lut.xz` | compressed data tables (film simulation, font metrics, font MSDF) unpacked into `bin/data/` at build time | | [build system](../components/build-system.md) |
| `bin/` | build output and runtime data: `default*.i-*` recipes, `presets/`, `keyaccel/`, `actionkeys/`, `dragkeys/`, `menus/`, `darkroom.ui`, `style.txt`, `examples/`, `config.mk.defaults` | | [build and run](../workflows/build-and-run.md) |
| `doc/` | howtos, `core.md` (compatibility promise), release notes | | |
| `.github/workflows/nightly.yml` | nightly AppImage (Linux) and Windows builds | | [build system](../components/build-system.md) |
| `flake.nix` | nix package and dev shell | | |

## Where the key mechanisms live

| mechanism | file |
|-----------|------|
| graph struct and run | `src/pipe/graph.h`, `src/pipe/graph.c` |
| traversal from sinks (topological sort) | `src/pipe/graph-traverse.inc` |
| ROI passes and node creation | `src/pipe/graph-run-modules.h` |
| memory allocation and aliasing | `src/pipe/graph-run-nodes-allocate.h`, `src/pipe/alloc.c` |
| command recording and barriers | `src/pipe/graph-run-nodes-record-cmd.h` |
| source upload and sink download | `src/pipe/graph-run-nodes-upload.h`, `src/pipe/graph-run-nodes-download.h` |
| recipe read and write | `src/pipe/graph-io.c` |
| connections and cycle check | `src/pipe/connector.c`, `src/pipe/connector.inc`, `src/pipe/cycles.h` |
| module registry (dlopen) | `src/pipe/global.c`, `src/pipe/global.h` |
| export (display to file sinks) | `src/pipe/graph-export.c`, `src/pipe/graph-export.h` |
| history and undo | `src/pipe/graph-history.h` |
| module helper API | `src/pipe/modules/api.h` |

## Sources

- `Makefile`, `src/Makefile` (what gets built from where)
- `readme.md` (dependencies, layout)
- directory listing on 2026-11-09

## Related

- [Architecture in one picture](architecture.md)
- [Pipeline core](../components/pipe-core.md)
