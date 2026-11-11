---
title: Core utilities, sound, fit, tools
type: component
summary: Logging, threads, LUTs, audio backends, the parameter optimiser and colour tooling.
sources:
  - src/core/log.h
  - src/core/threads.h
  - src/core/lut.h
  - src/snd/readme.md
  - src/snd/snd.h
  - src/fit/readme.md
  - src/tools/clut/readme.md
updated: 2026-11-09
---
# Core utilities, sound, fit, tools

Small directories that the big ones lean on.

## `src/core/` (3.4k lines)

| file | provides |
|------|----------|
| `log.h`, `log.c` | `dt_log(category, fmt, ...)` with a bit mask of categories (`log.h:12-23`): `qvk`, `pipe`, `gui`, `db`, `cli`, `snd`, `perf`, `mem`, `ray`, `err`, `all`. Default is errors only (`log.h:59`); `-d <category>` on the command line adds one |
| `threads.h`, `threads.c` | a fixed thread pool: `threads_task()` queues work with a progress callback, `threads_num()`, `threads_id()`, mutex wrappers, `threads_shutting_down()`. Used by thumbnails and export |
| `fs.h` | file system helpers: `fs_basename`, `fs_copy_file`, `fs_mkdir_p`, home and cache directories, portable across Linux, macOS and Windows |
| `lut.h` | reader and writer for the `.lut` binary table format (header plus half or float data); modules load colour tables and film simulations through it |
| `half.h` | float to half conversion for `f16` buffers on the CPU side |
| `mat3.h`, `solve.h`, `gaussian_elimination.h` | small linear algebra for colour matrices and fitting |
| `colour.h` | colour space primaries and transfer function enums shared with GLSL |
| `sort.h`, `sort_r.h` | quicksort with a context pointer |
| `strexpand.h` | expands `${variable}` patterns, used for export file name templates |
| `xrand.h`, `clip.h`, `inpaint.h`, `sig.h`, `core.h`, `tools.h` | random numbers, clipping, CPU inpainting helper, signal handling, common macros |
| `version.h` | generated at build time from `git describe` |

## `src/snd/` (311 lines)

Audio output for video playback, selected at build time:

| backend | file | note |
|---------|------|------|
| alsa | `alsa.c` | default on Linux; the PCM device is `strsnd/alsa/pcm` in `config.rc` |
| pipewire | `pw.c` | built when `VKDT_USE_PIPEWIRE=1` (auto-detected) |
| none | `none.c` | stubs for macOS, Windows and headless builds |

`snd.h` declares `dt_snd_t` (handle, sample rate, channels, format, planar) with
`dt_snd_init` and `dt_snd_cleanup`; each backend adds its own play call. The GUI calls the
module's `audio()` callback to pull samples and hands them to the backend. (The
`src/snd/readme.md` only mentions alsa; see [open questions](../questions.md).)

## `src/fit/` (376 lines)

`vkdt-fit`, the parameter optimiser. See [CLI and export](cli-and-export.md).

## `src/tools/`

| tool | purpose |
|------|---------|
| `clut/` | builds input device transforms (camera to spectral to working space) from spectral sensitivity data; produces the `.lut` files used by the `colour` module. Ships CFA models (`cfa-gauss.h`, `cfa-legendre.h`, `cfa-pca.h`, ...) and a ColorChecker reference (`cc24.h`) |
| `spec/` | spectral upsampling tables |
| `read-icc/` | dumps matrices and curves from ICC profiles so they can be turned into recipes |
| `shared/` | code shared by the tools |

These produce data, not runtime code; the results are shipped as `src/*.lut.xz` and
unpacked by `make lut`. See [build system](build-system.md).

## Sources

- `src/core/log.h:12-23, 59`, `src/core/threads.h`, `src/core/*.h` listing
- `src/snd/snd.h`, `src/snd/readme.md`
- `src/fit/readme.md`, `src/tools/clut/readme.md`

## Related

- [Debug the graph](../workflows/debugging-the-graph.md) (log categories)
- [CLI and export](cli-and-export.md)
- [Build system](build-system.md)
