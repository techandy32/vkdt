---
title: CLI and export
type: component
summary: vkdt-cli, vkdt-fit and the export mechanism that swaps display sinks for file outputs.
sources:
  - src/cli/main.c
  - src/cli/readme.md
  - src/pipe/graph-export.h
  - src/pipe/graph-export.c
  - src/fit/fit.c
  - src/fit/readme.md
updated: 2026-11-09
---
# CLI and export

Export does not have its own pipeline. It takes the graph as the GUI would run it, unplugs
the `display` sinks, plugs output modules into their place, and runs once with
`s_graph_run_download_sink` set. The GUI export dialog and the command line both call the
same function.

## `dt_graph_export`

`src/pipe/graph-export.h`:

- `dt_graph_export_output_t` (`:11-25`): one requested output. Fields: the sink instance
  to replace (default `main`), the output module to use (`o-jpg`, `o-pfm`, `o-exr`,
  `o-bc1`, `o-vid`, ...), the filename, `max_width` and `max_height` to scale the
  [ROI](../concepts/roi-region-of-interest.md) request, `quality`, requested
  `colour_primaries` and transfer curve.
- `dt_graph_export_t` (`:28-48`): up to 20 outputs (`output[20]`, `:39`), the recipe to
  load, extra config lines, `last_frame_only` (`:42`) for animations, and dump flags.
- `dt_graph_export()` (`:51`): loads the recipe, calls
  `dt_graph_disconnect_display_modules()`, adds the output modules, wires each to the
  module that fed the display sink, applies keyframes per frame
  (`src/pipe/graph-export.c:261, 302`), runs the graph for every frame and lets each output
  module's `write_sink()` write the file.

Because the display sink is replaced and nothing else changes, what you export is what you
saw, at full size if no limit is given.

## `vkdt-cli`

`src/cli/main.c` (159 lines) parses arguments into a `dt_graph_export_t` and calls
`dt_graph_export`. Options (`main.c:64-96`):

| option | meaning |
|--------|---------|
| `-g <file.cfg>` | the recipe to render (required) |
| `-d <category>` | log category, see [debug the graph](../workflows/debugging-the-graph.md) |
| `--filename <base>` | output file name without extension |
| `--format <o-module>` | output module, default `o-jpg` |
| `--quality <q>`, `--width <w>`, `--height <h>` | quality and size limits |
| `--output <inst>` | which display instance to replace; repeat for several outputs |
| `--colour-prim`, `--colour-trc` | request a colour space |
| `--last-frame-only` | render all animation frames but write only the last |
| `--audio <file>` | write the audio track of a video |
| `--dump-modules`, `--dump-nodes` | print the graph instead of rendering |
| `--progress` | print per-frame progress |
| `--device <name>`, `--device-id <n>` | pick the GPU |
| `--config <line>...` | extra recipe lines appended before running |
| `--version` | print the version and exit |

Example: render a recipe to a 1920 pixel wide JPEG:

```
vkdt-cli -g IMG_0001.CR2.cfg --format o-jpg --width 1920 --filename out
```

The GUI's lighttable export does the same for many images, in a background thread, and
writes files with a pattern.

## `vkdt-fit`

`src/fit/fit.c` is a parameter optimiser built on the same export path. Given a recipe, a
parameter to vary (`--param module:inst:param`) and a target to minimise
(`--target module:inst:param`, usually the output of a loss module), it runs the graph
repeatedly and adjusts the parameter with Adam, Nelder-Mead or a random search
(`fit.c:222-236`). It can also fit keyframes (`--keyframe`). Typical use is fitting a
vignetting or colour model to a reference (`src/fit/readme.md`).

## Other command line tools in `bin/`

`vkdt-gallery` (static web gallery from exports), `vkdt-noise-profile` (fits `noise_a`
and `noise_b` for a camera), `vkdt-mkclut` and `vkdt-mkssf` (input device transforms and
spectral sensitivity from `src/tools/clut`), `vkdt-read-icc`, `vkdt-lutinfo`,
`vkdt-eval-profile`. They are shell scripts or small C programs around `vkdt-cli`.

## Sources

- `src/pipe/graph-export.h:11-51`, `src/pipe/graph-export.c:261, 302`
- `src/cli/main.c:39-96`, `src/cli/readme.md`
- `src/fit/fit.c:222-236`, `src/fit/readme.md`

## Related

- [Export from the command line](../workflows/export-from-cli.md)
- [Scheduler: the run passes](scheduler-run-passes.md)
- [Add a file format](../workflows/adding-a-file-format.md)
