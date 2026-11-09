---
title: Build and run
type: workflow
summary: Dependencies, make targets, running the GUI and CLI, first configuration.
sources:
  - readme.md
  - Makefile
  - bin/config.mk.defaults
  - src/db/rc.h
  - doc/howto/gui-basics/readme.md
updated: 2026-11-09
---
# Build and run

## 1. Dependencies

From `readme.md:111-118`:

- Vulkan loader and `glslangValidator` (`libvulkan-dev`, `glslang-tools`, or the LunarG SDK)
- GLFW 3.4 or newer for good Wayland support
- a raw decoder: rawspeed (C++, needs pugixml, zlib, jpeg, libomp, cmake; optional
  exiv2) **or** rawler (needs a Rust toolchain). Set `VKDT_USE_RAWINPUT` to 1 or 2, or 0
  to build without raw support.
- libjpeg
- build tools: make, pkg-config, clang, sed, xxd
- optional: libjxl, pipewire, ffmpeg 5 or newer, v4l2 headers

Clone with submodules (rawspeed and some third-party code are submodules):

```
git clone --recursive https://github.com/hanatos/vkdt.git
```

## 2. Configure

Nothing to run. To change a switch, create `bin/config.mk` and put the overriding lines
there, for example:

```
VKDT_USE_RAWINPUT=1
VKDT_USE_FFMPEG=0
```

See [build system](../components/build-system.md) for every switch.

## 3. Build

```
make -j8          # release build, everything
make debug        # -O0, validation layers, slow
make cli          # only vkdt-cli and the modules, no GLFW needed
make sanitize     # address sanitizer
```

Results land in `bin/`: `vkdt`, `vkdt-cli`, `vkdt-fit`, `modules/*/`. The first build
also compiles about 205 shaders and unpacks the LUT data (`make lut`).

## 4. Run

```
cd bin
./vkdt /path/to/folder/with/raws      # lighttable of the folder
./vkdt /path/to/IMG_0001.CR2          # straight into darkroom
./vkdt-cli -g IMG_0001.CR2.cfg        # export to IMG_0001.CR2.jpg next to it
```

Running from `bin/` matters while developing: the program finds modules and data relative
to the executable. After `make install` it uses the install prefix.

Navigation (`doc/howto/gui-basics/readme.md:8-30`): `enter` opens the focused folder or
image, `escape` goes back one view, `ctrl-n` opens the node editor from darkroom, `space`
and `backspace` step to the next and previous image. Darkroom hotkeys
(`src/gui/render_darkroom.c:96-135`): `ctrl-z` undo, `ctrl-shift-z` redo, `ctrl-h`
history panel, `ctrl-p` apply preset, `ctrl-o` create preset, `ctrl-k` insert keyframe,
`ctrl-d` dopesheet, `tab` hide panels, `0` to `5` rate, `F1` to `F5` colour labels,
`ctrl-c` and `ctrl-v` copy and paste history. All of them are editable in `bin/` hotkey
files. `ctrl-x` quits.

## 5. First configuration

`~/.config/vkdt/config.rc` is created on first exit. Lines are `type+key:value`
(`src/db/rc.h`). Useful ones:

| key | meaning |
|-----|---------|
| `strqvk/device_name:<name>` or `intqvk/device_id:<n>` | choose the GPU when there are several |
| `intgui/lod:<n>` | preview level of detail; higher is cheaper |
| `intgui/frame_limiter:<ms>` | cap the frame rate |
| `strsnd/alsa/pcm:pipewire` | audio device for video playback |

Delete the file to return to defaults.

## 6. Check it works

```
./vkdt-cli -g bin/examples/webcam-taa.cfg --dump-modules   # prints the graph, no GPU work
./vkdt-cli -g IMG.cfg -d perf                              # per-node timings
```

If the GUI shows a black image, start with `-d qvk` to see device selection and
`make debug` to enable validation layers.

## Sources

- `readme.md:60-200` (build, platform notes, FAQ)
- `Makefile:26-143`, `bin/config.mk.defaults`
- `src/db/rc.h`, `doc/howto/gui-basics/readme.md:8-30`, `src/gui/render_darkroom.c:96-135`

## Related

- [Build system](../components/build-system.md)
- [Export from the command line](export-from-cli.md)
- [Debug the graph](debugging-the-graph.md)
