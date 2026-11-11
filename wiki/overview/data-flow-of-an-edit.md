---
title: Data flow of an edit
type: overview
summary: What happens between opening an image, moving a slider, and exporting.
sources:
  - src/gui/render_darkroom.c
  - src/gui/api.h
  - src/db/db.c
  - src/pipe/graph-export.h
  - doc/howto/gui-basics/readme.md
  - doc/howto/defgraph/readme.md
updated: 2026-11-09
---
# Data flow of an edit

This page follows one image through the program. Each step names the code that does it.

## 1. Opening a folder

The GUI starts in the lighttable view (or the file manager if the folder has no images,
`src/gui/main.c:247-249`). The [database](../components/database-and-thumbnails.md) lists
the image files in the folder. For every image a thumbnail is rendered through the small
default recipe `bin/default.i-<input module>` and cached as a compressed `.bc1` file.

## 2. Entering darkroom mode

Pressing enter on an image opens it. `src/gui/render_darkroom.c:544-560`:

1. `dt_graph_repurpose` resets the graph object but keeps its Vulkan objects.
2. `dt_graph_read_config_ascii` reads the image's recipe. If the image has no `.cfg` yet, the
   database copies `bin/default-darkroom.i-<input>` and appends one line that sets the
   input module's `filename` parameter (`src/db/db.c:674`).
3. The search path is set to the image's folder so modules can find side files.
4. History is reset and `runflags = s_graph_run_all`: the next frame rebuilds everything.

## 3. The first run

The render loop calls `dt_graph_run(&vkdt.graph_dev, runflags)` once per frame that needs it
(`src/gui/render_darkroom.c:1249`). With all flags set the run does every pass: traverse,
sizes forward, requests backward, create nodes, allocate memory, upload the decoded raw,
record the command buffer, submit. See [scheduler run passes](../components/scheduler-run-passes.md).

The `display:main` sink's buffer is handed to the GUI as a Vulkan image; the GUI draws it as
a texture. The `display:hist` sink becomes the waveform in the panel. Nothing is copied back
to the CPU.

## 4. Moving a slider

A slider edits bytes in the module's parameter block. The GUI asks the module's
`check_params()` whether more than a re-record is needed, then ORs
`s_graph_run_record_cmd_buf` and that answer into `runflags`
(`src/gui/render_darkroom.h:299-301`). On the next frame the run skips
the structural passes: it re-uploads parameters as uniforms, re-records the command buffer
and submits. The nodes and their memory are untouched. See [run flags](../concepts/run-flags.md).

If `check_params()` says the graph shape changed (for example a different demosaic method,
`src/pipe/modules/demosaic/main.c:50-54`), the GUI sets `s_graph_run_all` instead.

Every change is also appended to the history as a recipe line
(`dt_graph_history_append`, `render_darkroom.h:303`), which is what undo and the history
panel use. See
[history and keyframes](../concepts/history-and-keyframes.md).

## 5. Leaving darkroom mode

The recipe is written back to `<image>.cfg` when leaving darkroom mode or switching to the
next image (`doc/howto/gui-basics/readme.md`). Ratings and labels go to `vkdt.db` when the
folder changes or the program exits.

## 6. Exporting

Export builds a `dt_graph_export_t` (`src/pipe/graph-export.h`): for each requested output it
names a sink instance to replace (`main` by default), an output module (`o-jpg`, `o-pfm`,
`o-exr`, `o-vid`, ...), a filename, quality, and optional size limits. `dt_graph_export`
disconnects the display modules, wires the output modules in their place, runs the graph
with `download_sink` set, and the output module's `write_sink()` writes the file. The CLI
uses the same function (`src/cli/main.c:139`).

## Sources

- `src/gui/render_darkroom.c:544-560, 1249`
- `src/gui/render_darkroom.h:299-303` (slider path), `src/gui/api.h:45` (animation seek)
- `src/db/db.c:670-674`
- `src/pipe/graph-export.h`
- `doc/howto/gui-basics/readme.md`, `doc/howto/defgraph/readme.md`

## Related

- [Architecture in one picture](architecture.md)
- [Run flags](../concepts/run-flags.md)
- [CLI and export](../components/cli-and-export.md)
