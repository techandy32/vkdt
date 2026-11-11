---
title: History and keyframes
type: concept
summary: Undo history stored as recipe lines, and keyframed animation of parameters.
sources:
  - src/pipe/graph-history.h
  - src/pipe/graph.h
  - src/pipe/module.h
  - src/pipe/anim.h
  - src/pipe/graph-io.c
  - src/gui/widget_dopesheet.h
updated: 2026-11-09
---
# History and keyframes

Both features reuse the [recipe format](cfg-recipe-format.md). Undo is a list of recipe
lines; animation is a set of `keyframe:` lines.

## History (undo)

The graph keeps a text pool of recipe lines (`history_pool`, `history_item[]`,
`history_time[]`, `src/pipe/graph.h:85-89`). Every edit appends one line, exactly as it
would be written to the `.cfg` file.

| function (`src/pipe/graph-history.h`) | appends |
|----------------------------------------|---------|
| `dt_graph_history_append` (`:90`) | `param:` line for one parameter; a `throttle` argument merges rapid slider moves into one entry |
| `dt_graph_history_module` (`:140`) | `module:` line |
| `dt_graph_history_connection` (`:152`) | `connect:` or `feedback:` line |
| `dt_graph_history_keyframe` (`:164`) | `keyframe:` line |
| `dt_graph_history_global` (`:181`) | `frames:` and `fps:` |
| `dt_graph_history_line` (`:194`) | any raw line (presets use this) |
| `dt_graph_history_set` (`:209`) | move the current position (undo and redo) |
| `dt_graph_history_reset` (`:19`) | start over, from the recipe as loaded |

Two indices mark the state: `history_item_cur` is where the user is, `history_item_end`
is the newest entry. Undo moves `cur` back and replays the lines from the start up to
`cur` into a fresh graph. Redo moves it forward. A new edit after an undo drops the
entries past `cur`.

The history panel in darkroom mode lists the lines; clicking one calls
`dt_graph_history_set`. When leaving darkroom mode the current graph is written to the
`.cfg` file, so only the final state is saved, not the undo list.

## Keyframes (animation)

A graph has `frame_cnt` frames at `frame_rate` fps (`frames:` and `fps:` lines). A
keyframe says what a parameter is at a given frame.

`dt_keyframe_t` (`src/pipe/module.h:113-124`): the parameter token, the frame, byte range
`beg` to `end` inside the parameter, a pointer to the data, the interpolation mode, and a
`next` pointer. Per module, `param_keyframe[]` indexes the first keyframe of each
parameter, and the keyframes of one parameter form a list sorted by frame.

Interpolation modes (`src/pipe/anim.h:5-9`) and how they are spelled in the recipe
(`src/pipe/graph-io.c:243-247`):

| mode | recipe command | curve |
|------|----------------|-------|
| `s_anim_lerp` | `keyframe:` | straight line |
| `s_anim_ease_out` | `keyframE:` | fast start, slow end |
| `s_anim_ease_in` | `Keyframe:` | slow start, fast end |
| `s_anim_smooth` | `KeyframE:` | smooth step |
| `s_anim_step` | `keyFRAME:` | jump at the half-way point |

Before a frame runs, `dt_graph_apply_keyframes()` (`src/pipe/graph.h:225`) walks every
module's keyframes, finds the two around the current frame, and writes the interpolated
bytes into the parameter block. Then the run needs only `s_graph_run_record_cmd_buf`
(`src/gui/render_darkroom.c:696`). String parameters, such as a filename, step rather
than blend.

The GUI edits keyframes in the dopesheet (`src/gui/widget_dopesheet.h`): one row per
animated parameter, one marker per keyframe, drag to move. The export code applies
keyframes for every frame when writing video (`src/pipe/graph-export.c:261, 302`).

## Sources

- `src/pipe/graph-history.h:6-209`, `src/pipe/graph.h:85-89, 225`
- `src/pipe/module.h:113-124, 161-165`, `src/pipe/anim.h:5-9`
- `src/pipe/graph-io.c:243-247`, `src/gui/render_darkroom.c:696`, `src/pipe/graph-export.c:261, 302`
- `src/gui/widget_dopesheet.h`

## Related

- [Recipe file format](cfg-recipe-format.md), [Run flags](run-flags.md)
- [Feedback connectors](feedback-connectors.md) (frame to frame state)
- [GUI](../components/gui.md)
