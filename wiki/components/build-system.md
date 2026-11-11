---
title: Build system
type: component
summary: Flat makefiles, config.mk switches, shader compilation to SPIR-V, module shared objects and CI.
sources:
  - Makefile
  - src/Makefile
  - bin/config.mk.defaults
  - src/pipe/modules/llap/flat.mk
  - .github/workflows/nightly.yml
  - readme.md
updated: 2026-11-09
---
# Build system

Plain GNU make, no configure step, no CMake. Run `make` in the root directory or in
`bin/` (`bin/Makefile` forwards to the root).

## The makefiles

| file | role |
|------|------|
| `Makefile` (root) | targets, includes `bin/config.mk.defaults` and then `sinclude bin/config.mk` for local overrides; `.osx` and `.w64` variants of the defaults for macOS and Windows |
| `src/Makefile` | builds the two executables and all modules; includes every `flat.mk` |
| `src/*/flat.mk` | one per directory (core, pipe, gui, db, qvk, snd, cli, fit, tools): lists sources and flags in a flat, non-recursive way |
| `src/pipe/modules/*/flat.mk` | per module: extra sources, link flags (for example `-lrawspeed` for `i-raw`) |

Targets (`Makefile:26-143`): `all` (default, builds `src`, `bin` and `lut`), `debug`
(`-O0 -g`, Vulkan validation layers on, debug markers), `sanitize` and `sanitize-thread`,
`cli` (only `vkdt-cli` and modules), `lib`, `lut` (unpacks `src/*.lut.xz` into
`bin/data/`), `reload-shaders` (recompile only `.spv`), `install`, `install-bin`,
`install-mod`, `release`.

## Switches in `config.mk`

`bin/config.mk.defaults` auto-detects most of them with `pkg-config` and sets:

| variable | values | effect |
|----------|--------|--------|
| `VKDT_USE_RAWINPUT` | 0 none, 1 rawspeed (C++), 2 rawler (Rust) | which raw decoder `i-raw` uses; defaults to 2 if `rustc` exists (`:24`) |
| `VKDT_USE_JXL` | 0 or 1 | JPEG XL input and output (`:46`) |
| `VKDT_USE_V4L2` | 1 | webcam input on Linux (`:54`) |
| `VKDT_USE_MLV` | 1 | Magic Lantern raw video (`:60`) |
| `VKDT_USE_PIPEWIRE` | 0 or 1 | pipewire audio backend (`:65`) |
| `VKDT_USE_MCRAW` | 1 | MotionCam raw video (`:73`) |
| `VKDT_USE_FFMPEG` | 0 or 1 | video decode through ffmpeg 5 or newer (`:80`) |
| `VKDT_USE_QUAKE`, `VKDT_USE_EXIV2` | 0 or 1 | the Quake input module, exiv2 metadata |

Copy the lines you want to change into `bin/config.mk`; that file is not tracked.

## What gets built

1. **Shaders.** Every `.comp`, `.vert`, `.tesc`, `.tese`, `.geom`, `.frag` under
   `src/pipe/modules/` is compiled with `glslangValidator` (variable `GLSLC`) to a `.spv`
   next to it with `--target-env vulkan1.4` (`bin/config.mk.defaults:115-116`). Modules include shared GLSL from
   `src/pipe/modules/shared/`.
2. **Module shared objects.** A module with `main.c` becomes `lib<name>.so` (variable
   `MODULES`); one with `main.cc` is C++ (`MODULESXX`). Modules without C code produce no
   library.
3. **Tooltips.** `ptooltips` is generated from each module's `readme.md`.
4. **Executables.** `vkdt` (GUI), `vkdt-cli`, `vkdt-fit`, plus the tools.
5. **Data.** `make lut` unpacks `filmsim.lut`, `font_metrics.lut`, `font_msdf.lut` into
   `bin/data/` (`Makefile:58`).
6. **Runtime files.** `bin/` already contains `default*.i-*`, `presets/`, `keyaccel/`,
   `actionkeys/`, `dragkeys/`, `menus/`, `darkroom.ui`, `style.txt`, `examples/`.

Install (`install-mod`) copies per module: `params`, `params.ui`, `connectors`,
`*tooltips`, `readme.md`, `*.spv`, `*.so`. That list is the complete runtime contract of a
module.

## Where the program finds its files

`vkdt` looks for modules and data relative to the executable (`bin/` when run from the
tree, `$(prefix)/lib/vkdt` after install). The search path logic is in `src/pipe/res.c`
and `src/core/fs.h`.

## CI

`.github/workflows/nightly.yml` builds on every push:

- **AppImage** on Ubuntu x86-64 and arm64 (`ubuntu-26.04-arm`), with both raw back-ends
  tried (rawler and rawspeed), a patched GLFW for pen tablet support, and the LunarG
  Vulkan SDK. The artefact is a nightly AppImage.
- **WindowsRawler**: msys2 build with the rawler back-end.

There is no test job in CI; tests are in `src/pipe/tests`, `src/db/tests` and the
external `vkdt-test` repository.

## Sources

- `Makefile:26-143`, `src/Makefile`, `bin/config.mk.defaults:24-80`
- `src/pipe/modules/llap/flat.mk` (a module makefile)
- `.github/workflows/nightly.yml:15-214`
- `readme.md` (dependency list)

## Related

- [Build and run](../workflows/build-and-run.md)
- [Module anatomy](../modules/module-anatomy.md)
- [Repository map](../overview/repository-map.md)
