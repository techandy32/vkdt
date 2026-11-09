---
title: Export from the command line
type: workflow
summary: Render a recipe to jpg, pfm, exr or video without the GUI.
sources:
  - src/cli/main.c
  - src/cli/readme.md
  - src/pipe/graph-export.h
  - doc/howto/timelapse/readme.md
updated: 2026-11-09
---
# Export from the command line

`vkdt-cli` loads a recipe, replaces its display sinks with output modules and runs the
graph once (or once per animation frame). See [CLI and export](../components/cli-and-export.md)
for how that works inside.

## One image

```
vkdt-cli -g IMG_0001.CR2.cfg
```

writes `IMG_0001.CR2.jpg` using `o-jpg` with default quality, at full size. The `.cfg`
must exist; open the image once in the GUI, or copy `bin/default-darkroom.i-raw` and
append `param:i-raw:main:filename:IMG_0001.CR2`.

Common variations:

```
vkdt-cli -g in.cfg --format o-pfm --filename out            # 32-bit float, out.pfm
vkdt-cli -g in.cfg --format o-exr --filename out            # OpenEXR
vkdt-cli -g in.cfg --format o-jpg --quality 90 --width 2048 # size limit
vkdt-cli -g in.cfg --output hist --filename wave             # export the histogram sink instead of main
vkdt-cli -g in.cfg --config "param:llap:01:clarity:0.5"      # override a parameter for this run
```

`--width` and `--height` scale the ROI request; the image is rendered at that size, not
rendered large and downscaled. `--output` names the display instance to replace and can
be repeated to export several sinks in one run.

## Many images

A shell loop is the intended tool:

```
for f in *.CR2; do vkdt-cli -g "$f.cfg" --format o-jpg --filename "${f%.CR2}"; done
```

Each run initialises Vulkan, which costs a fraction of a second. The GUI's lighttable
export batches this in one process when speed matters.

## Video and timelapse

A recipe with `frames:<n>` and `fps:<f>` lines is an animation. With `--format o-vid` the
CLI renders every frame and the output module encodes h264 or ProRes. `--audio file`
muxes an audio track. `--last-frame-only` renders all frames but writes just the last,
which is what you want for feedback-based accumulation (see
[feedback connectors](../concepts/feedback-connectors.md)). `doc/howto/timelapse/readme.md`
describes building a timelapse from a folder of raws with `i-raw` in sequence mode.

## Colour management

`--colour-prim` and `--colour-trc` request output primaries and transfer curve, which
the exporter passes to the output module through
`dt_graph_export_output_t.colour_primaries` (`src/pipe/graph-export.h:22`). Defaults are
sRGB for `o-jpg` and linear rec2020 for `o-pfm` and `o-exr`.

## Checking what will happen

```
vkdt-cli -g in.cfg --dump-modules   # which modules and connections, no rendering
vkdt-cli -g in.cfg -d perf          # render and print GPU time per node
vkdt-cli -g in.cfg --progress       # frame counter for long animations
```

## Picking the GPU

`--device <name substring>` or `--device-id <n>`; the same keys exist in `config.rc`
(`strqvk/device_name`, `intqvk/device_id`).

## Sources

- `src/cli/main.c:39-96`, `src/cli/readme.md`
- `src/pipe/graph-export.h:11-51`
- `doc/howto/timelapse/readme.md`

## Related

- [CLI and export](../components/cli-and-export.md)
- [Recipe file format](../concepts/cfg-recipe-format.md)
- [Build and run](build-and-run.md)
