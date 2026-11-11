---
title: Parameters and UI
type: concept
summary: The params, params.ui and readme files that define a module's settings, widgets and uniforms.
sources:
  - src/pipe/params.h
  - src/gui/widget_descriptor.h
  - src/pipe/global.h
  - src/pipe/modules/llap/params
  - src/pipe/modules/llap/params.ui
  - src/pipe/modules/OpenDRT/params.ui
  - src/gui/render_darkroom.h
updated: 2026-11-09
---
# Parameters and UI

A module's settings are declared in text files next to its kernels. The same declaration
drives three things: the bytes a slider edits, the uniform block the kernel reads, and the
widget the GUI draws. There is no per-module GUI code for ordinary parameters.

## `params`: what exists

One line per parameter: `name:type:count:default values`. From
`src/pipe/modules/llap/params`:

```
sigma:float:1:0.12
shadows:float:1:1.0
hilights:float:1:1.0
clarity:float:1:0.0
```

Types are `float`, `int` and `string` (`src/pipe/params.h:28-30`). `count` makes an array;
a string's count is its buffer length. At most 100 parameters per module
(`DT_MAX_PARAMS_PER_MODULE`, `src/pipe/global.h:9`).

Each line becomes a `dt_ui_param_t` (`params.h:5-24`) on the module class: name and type
as [tokens](tokens.md), `cnt`, `offset` into the uniform block, the widget descriptor, a
tooltip and a long name. The default values are stored after the struct.

## `params.ui`: how it is shown

One line per parameter that has a widget: `name:widget:args`. From
`src/pipe/modules/llap/params.ui`:

```
shadows:slider:0.0:10.0
hilights:slider:0.0:10.0
clarity:slider:-1.0:3.0
```

A parameter without a line is not shown. The parsed form is `dt_widget_descriptor_t`
(`src/gui/widget_descriptor.h:7-14`): widget type, soft min and max, group binding and an
optional count parameter.

Widget types in use at commit `af70c5d`, counted over all `params.ui` files:

| widget | count | draws |
|--------|------:|-------|
| `slider` | 244 | float slider with soft range; `vslider` is the vertical variant |
| `combo` | 90 | drop-down of named choices for an `int` |
| `hidden` | 60 | parameter exists but no widget (set by presets, code or the graph) |
| `filename` | 23 | file picker |
| `tabs` | 19 | begins a tab group that later widgets fall into |
| `rgbknobs`, `colwheel`, `rgb`, `colour` | 6, 5, 3, 3 | colour controls |
| `callback` | 5 | a button that calls the module's `ui_callback` |
| `text`, `grab`, `draw`, `bitmask`, `pick`, `crop`, `straight`, `pers`, `rbmap`, `print`, `click`, `btngrid` | few | text entry, mouse grab, mask drawing, bit toggles, colour picker, crop frame, horizon tool, perspective, radial basis map, read-only print, click position, button grid |

The directive `group:<param>:<value>` makes the following widgets visible only when the
integer parameter has that value; `group:-1:-1` ends the group
(`src/pipe/modules/OpenDRT/params.ui:22-29`).

## `readme.md`: tooltips

At build time `ptooltips` is generated from the module's `readme.md`: the paragraph that
describes `## parameters` and each `* name:` bullet becomes the tooltip of that parameter
(`dt_ui_param_t.tooltip`, `params.h:13`). An optional `params.en` file gives longer display
names (`long_name`).

## From slider to kernel

1. The widget code (`src/gui/render_darkroom.h:299-303`) writes the new value into the
   module instance's parameter bytes (`dt_module_t.param`).
2. It calls the module's `check_params()` to learn if the graph shape changed, sets the
   [run flags](run-flags.md) and appends a history line.
3. On the next run, `commit_params()` (or the default copy) writes the bytes into the
   module's uniform block at `uniform_offset`.
4. The kernel reads them from descriptor set 0 as a uniform struct with the same field
   order as the `params` file.

A module whose kernel needs derived values (a matrix from three sliders, a lookup table)
implements `commit_params()` and writes to `committed_param` instead.

## Sources

- `src/pipe/params.h:5-30`, `src/pipe/global.h:9`
- `src/gui/widget_descriptor.h:7-14`
- `src/pipe/modules/llap/params`, `params.ui`; `src/pipe/modules/OpenDRT/params.ui:22-29`
- `src/gui/render_darkroom.h:299-303` (slider path)
- `src/Makefile` (`ptooltips` generation)

## Related

- [Module](module.md), [Run flags](run-flags.md)
- [Recipe file format](cfg-recipe-format.md) (`param:` lines)
- [GUI](../components/gui.md)
