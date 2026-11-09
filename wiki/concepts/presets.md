---
title: Presets
type: concept
summary: Recipe fragments that add modules, wires and parameters to a graph in one step.
sources:
  - bin/presets
  - src/gui/api.h
  - src/gui/render_darkroom.c
  - src/gui/menu.h
  - bin/keyaccel
updated: 2026-11-09
---
# Presets

A preset is a file of [recipe lines](cfg-recipe-format.md) with the extension `.pst`.
Applying it reads the lines into the current graph one by one, as if the user had typed
them, and records each line in the [history](history-and-keyframes.md).

## Where they live

- Shipped: `bin/presets/*.pst`, 62 files at commit `af70c5d` (for example `burn.pst`,
  `clut.pst`, `ColorChecker.pst`).
- User: `~/.config/vkdt/presets/`. Files there are listed together with the shipped ones.

## Using them

| action | key | code |
|--------|-----|------|
| apply a preset | ctrl-p opens a filtered list | `src/gui/render_darkroom.c:100`, `src/gui/api.h:450` |
| create a preset from the current image | ctrl-o | `src/gui/render_darkroom.c:99, 271-272` (`dt_gui_dr_preset_create`) |
| preset menu (chord) | p | `render_darkroom.c:129` |
| apply from the lighttable to many images | lighttable "presets" list | `src/gui/render_lighttable.c:1513` |

Creating a preset writes the selected modules' `module:`, `connect:` and `param:` lines to
a new `.pst` file. Because the lines name module instances, a preset usually works on any
image whose graph has the same instances (`01` for the processing modules of the default
graphs, `main` for the input and display).

## Menus and key accelerators

The menu system (`src/gui/menu.h`) can list presets as menu entries (`scan_presets`
provider, `menu.h:144`) and binds a key chord to a preset file (`menu.h:248`). The
`bin/keyaccel/` scripts are small preset-like files that use `paraminc:` and `paramdec:`
lines to nudge a parameter, which is how single-key exposure or contrast steps work
without a slider.

## Pitfalls

- A preset that adds a module with an instance name that already exists silently reuses
  that instance.
- Presets store absolute parameter values. Applying a preset twice is idempotent for
  `param:` lines but not for `paraminc:` lines.
- Presets are text; they can be edited and shared like recipes.

## Sources

- `bin/presets/` (62 files), `bin/keyaccel/`
- `src/gui/render_darkroom.c:99-100, 129, 271-272`, `src/gui/api.h:450`
- `src/gui/menu.h:133-144, 248`, `src/gui/render_lighttable.c:1513`

## Related

- [Recipe file format](cfg-recipe-format.md)
- [History and keyframes](history-and-keyframes.md)
- [GUI](../components/gui.md)
