---
title: GUI (src/gui)
type: component
summary: Views, the nuklear immediate-mode UI, display synchronisation and the hotkey files.
sources:
  - src/gui/gui.h
  - src/gui/main.c
  - src/gui/view.h
  - src/gui/render_darkroom.c
  - src/gui/graph-display.h
  - src/gui/api.h
  - src/gui/readme.md
updated: 2026-11-09
---
# GUI (src/gui)

The GUI is a GLFW window with a Vulkan swap chain, drawn with the **nuklear**
immediate-mode UI library (the bundled `nuklear.h`). Immediate mode means the whole
interface is re-described every frame from the program state; there is no widget tree to
keep in sync. (`src/gui/readme.md` still says imgui; the code is nuklear. See
[open questions](../questions.md).)

## One global struct

`vkdt` (`dt_gui_t`, `src/gui/gui.h:184-208`) holds everything the GUI needs:
`graph_dev` (the darkroom graph), `db` (the image list), `thumbnails` and
`thumbnail_gen`, `view_mode`, `snd` (audio), window and swap chain state, and the current
style.

## Views

| view | file | shows |
|------|------|-------|
| files | `render_files.c` | folder browser, used to pick a folder |
| lighttable | `render_lighttable.c` | thumbnails of the current folder, ratings, labels, collections, export |
| darkroom | `render_darkroom.c` | the image, module panels, history, metadata, dopesheet |
| nodes | `render_nodes.c` | the graph editor: modules as boxes, connectors as wires |

`dt_view_switch()` changes `view_mode`; `main.c` starts in lighttable, or in files when
the folder has no images (`src/gui/main.c:247-249`). Each view has `enter`, `leave`,
`render`, and input callbacks.

## Drawing the image without copying

The display sink of `graph_dev` writes into a GPU image. `src/gui/graph-display.h` keeps
a small ring of such images (`dt_graph_display_images_t`) with timeline semaphore values:

- `dt_graph_display_acquire_for_processing()` gives the graph a free image to render into.
- `dt_graph_display_acquire_for_display()` gives the GUI the newest finished one.
- `dt_graph_display_get_dset()` returns a descriptor set so nuklear can draw it as a
  texture.
- `dt_graph_display_have_free_process()` tells the render loop whether another graph run
  may start.

So processing and drawing overlap, and no pixel ever travels back to the CPU for display.

## The render loop in darkroom

Per frame (`render_darkroom.c:1238-1250`): if `runflags` is non-zero and a display image
is free, call `dt_graph_run` with `wait_done` cleared, then clear the flags. Sliders set
the flags through `src/gui/render_darkroom.h:299-303`; `src/gui/api.h` collects
helper functions such as `dt_gui_dr_anim_seek` (`:40-46`), preset application (`:450`)
and module add or remove with history.

## Keys and menus are data files

Runtime behaviour is configured by text files in `bin/`, copied from the source tree at
build time:

| file or folder | defines |
|----------------|---------|
| `darkroom.ui` | which module panels appear and in which tab, favourites |
| `actionkeys/` | key to action bindings per view |
| `dragkeys/` | key plus mouse drag bindings (`src/gui/dragkey.h` evaluates them and calls `check_params`) |
| `keyaccel/` | one-key parameter nudges written as `paraminc:`/`paramdec:` lines |
| `menus/` | radial and chord menus (`src/gui/menu.h`) |
| `style.txt` | colours and sizes |

Settings live in `~/.config/vkdt/config.rc`, read through `src/db/rc.h`. Keys that
matter for the GUI: `intgui/lod` (preview level of detail), `intgui/frame_limiter`,
`strqvk/device_name`, `intqvk/device_id`.

## Other pieces

- `widget_*.h`: dopesheet, draw (masks), export dialog, file browser, filtered list,
  image view with zoom, node editor canvas, radial menu, thumbnails, tooltips.
- `screencast.c`: records the window to video through the graph.
- `hotkey.h`, `actionkey.h`: key tables and the dispatcher; the darkroom table lists
  about 40 actions including create preset (ctrl-o) and apply preset (ctrl-p)
  (`render_darkroom.c:96-135`).

## Sources

- `src/gui/gui.h:184-208`, `src/gui/main.c:247-249`
- `src/gui/graph-display.h:68-109`
- `src/gui/render_darkroom.c:49-129, 1238-1250`, `src/gui/render_darkroom.h:299-303`
- `src/gui/api.h:40-46, 450`
- `src/gui/readme.md`

## Related

- [Data flow of an edit](../overview/data-flow-of-an-edit.md)
- [Run flags](../concepts/run-flags.md), [Presets](../concepts/presets.md)
- [Database and thumbnails](database-and-thumbnails.md)
