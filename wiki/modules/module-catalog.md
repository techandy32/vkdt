---
title: Module catalog
type: module
summary: The 101 modules grouped by category.
sources:
  - src/pipe/modules/readme.md
  - src/pipe/modules
updated: 2026-11-09
---
# Module catalog

At commit `af70c5d` there are 110 directories under `src/pipe/modules/`, of which 101
have a `connectors` file and are modules (the rest are `shared/` and work-in-progress
folders such as `const`, `dmlp-t`, `g-csolid`, `mipmap`, `nlr`, `o-csv`, `ocean`,
`svgf2`). The groups below follow `src/pipe/modules/readme.md`. Each module has a
`readme.md` in its directory.

## Input (`i-*`)

Source modules: they have a `source` connector and a `read_source` callback that fills a
staging buffer from a file or device.

`i-raw` (camera raw stills and timelapses, via rawspeed or rawler), `i-jpg`, `i-exr`,
`i-hdr` (Radiance RGBE), `i-pfm`, `i-lut` (half float tables), `i-bc1` (thumbnails),
`i-mlv` (Magic Lantern raw video), `i-mcraw` (MotionCam raw video), `i-vid` (ffmpeg
video), `i-v4l2` (webcam), `i-obj` (triangle meshes, listed under 3D geometry).

## Output (`o-*`) and loss

Sink modules with a `write_sink` callback.

`o-jpg`, `o-jxl`, `o-exr`, `o-pfm`, `o-lut`, `o-bc1` (thumbnails), `o-vid` (h264 or
ProRes), `o-web` (jpg plus mp4 for web pages), `o-copy` (copy the input file), `o-null`,
and `loss` (computes a scalar for `vkdt-fit`).

## Visualisation and inspection

`display` (the screen sink), `hist` (waveform), `rawhist` (raw histogram with noise
levels), `pick` (colour picker), `ciediag` (CIE vectorscope), `check` (gamut and clipping
warnings), `ab` (split screen compare), `vis` (false colour ramp), `coltgt` (render a
ColorChecker), `test10b` (banding test).

## Raw processing

`demosaic` (Bayer and X-Trans; methods gaussian splats, RCD, half size), `hilite`
(highlight reconstruction), `ca` (chromatic aberration), `jddcnn` (joint demosaic and
denoise network).

## Display transform and tone mapping

`filmcurv`, `filmsim` (spectral film simulation), `OpenDRT`, `reinhard`.

## Colour

`colour` (white balance, matrix, input device transform, gamut), `colenc` (encode for
output spaces), `curves`, `grade` (ASC CDL), `okgmtclp` (gamut clip in Oklab).

## Corrective

`denoise` (wavelets with noise profile), `hotpx`, `deconv`, `dehaze`, `usm`, `lens`,
`crop` (crop, rotate, perspective), `autoexp`, `negative`, `kpn` (kernel prediction
network), `oidn` (Open Image Denoise).

## Tone

`llap` (local Laplacian pyramid; see [worked example](llap-worked-example.md)), `contrast`
(guided filter), `eq`, `exposure`, `grad`, `zones`.

## Retouching and masks

`draw` (brush strokes), `guided` (refine masks), `inpaint`, `mask` (parametric), `segment`
(semantic segmentation network), `select` (click to select, network), `wavelet` (skin).

## Effects

`frame`, `grain`, `overlay` (text), `vignette`.

## Technical

`align`, `blend`, `format` (change channels or type), `resize`, `hdrmerge`, `mv2rot`,
`cnngenin` and `kpn-t` (training helpers).

## 3D and rendering

`rt` (real-time ray tracing), `quake`, `bvh`, `g-ocean`, `g-wobble`, `accum`, `svgf`,
`spheres`, `physarum`, `logo`.

## Internal

`nprof` (noise profiling), `thumb` (thumbnail display).

## Numbers

| | count |
|-|------:|
| module directories | 110 |
| modules with `connectors` | 101 |
| `.comp` compute kernels | 205 |
| modules with `main.c` | 80 |
| shipped presets | 62 |

## Sources

- `src/pipe/modules/readme.md` (categories and one-line descriptions)
- directory listing of `src/pipe/modules/` on 2026-11-09

## Related

- [Module anatomy](module-anatomy.md)
- [Default raw pipeline](default-raw-pipeline.md)
- [Add a module](../workflows/adding-a-module.md)
