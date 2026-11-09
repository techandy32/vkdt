---
title: Image parameters (metadata)
type: concept
summary: The black point, white balance, matrix and colour description that travel along the graph edges.
sources:
  - src/pipe/module.h
  - src/pipe/modules/api.h
  - src/pipe/graph-run-modules.h
updated: 2026-11-09
---
# Image parameters (metadata)

Pixels are not the only thing that flows through the graph. Each module also publishes a
small struct about the image it outputs: `dt_image_params_t` (`src/pipe/module.h:72-110`).
Downstream modules read it to know how to interpret the pixels.

## Fields

| group | fields | set by |
|-------|--------|--------|
| raw data | `black[4]`, `white[4]`, `whitebalance[4]`, `filters` (0 full colour, 9 X-Trans, else Bayer pattern bits), `crop_aabb[4]` | input module from the raw file |
| camera | `cam_to_rec2020[9]` matrix, `orientation`, `datetime`, `maker`, `model`, `exposure`, `aperture`, `iso`, `focal_length` | input module from EXIF or DNG |
| colour state | `colour_primaries`, `colour_trc` (transfer curve) | changes as data moves: `colour` sets rec2020 linear, `o-jpg` expects sRGB |
| audio | `snd_format`, `snd_channels`, `snd_samplerate`, `snd_planar` | video and game inputs |
| noise | `noise_a`, `noise_b` (Gaussian and Poisson part of the raw noise model) | `i-raw` from the camera's noise profile |
| identity | `input_name` (the instance, `main` has special rights), `meta` (extra metadata list owned by the input module) | input module |

## How it travels

The struct on a module describes the module's **output** (`module.h:138-148`). To learn
about its input, a module follows the connection backwards with
`dt_module_get_input_img_param()` (`src/pipe/modules/api.h`). The default behaviour, done
by the core during the forward ROI pass in `src/pipe/graph-run-modules.h`, copies the
input's struct to the output. So `black` and `whitebalance` set by `i-raw` are visible to
`denoise`, `hilite` and `demosaic` without any extra wiring, and a module that changes the
meaning of the pixels (`colour` after the matrix, `filmcurv` after the curve) overwrites
the relevant fields.

Because the data follows edges, two raw files merged in one graph each carry their own
black level and white balance up to the module that merges them, which is the reason the
struct is per module and not per graph (`module.h:138-147`).

## Uses

- `demosaic` reads `filters` to pick Bayer or X-Trans kernels.
- `colour` reads `cam_to_rec2020` and `whitebalance`.
- `denoise` reads `noise_a`, `noise_b` for the profiled noise model.
- Output modules read `colour_primaries` and `colour_trc` to tag the file.
- The GUI shows `maker`, `model`, `exposure`, `aperture`, `iso`, `focal_length` in the
  metadata panel.

## Sources

- `src/pipe/module.h:72-110` (struct), `:138-148` (why it is per module output)
- `src/pipe/modules/api.h` (`dt_module_get_input_img_param`)
- `src/pipe/graph-run-modules.h` (default propagation)

## Related

- [Connector](connector.md), [Module](module.md)
- [Default raw pipeline](../modules/default-raw-pipeline.md)
