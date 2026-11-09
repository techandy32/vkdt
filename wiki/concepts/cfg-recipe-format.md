---
title: Recipe file format (.cfg)
type: concept
summary: The text format that stores a graph: module, connect, feedback, param, keyframe, frames, fps.
sources:
  - src/pipe/graph-io.c
  - bin/default-darkroom.i-raw
  - src/db/db.c
  - doc/howto/defgraph/readme.md
updated: 2026-11-09
---
# Recipe file format (.cfg)

A graph is saved as a plain text file. For an image `IMG_0001.CR2` the recipe is the
sidecar `IMG_0001.CR2.cfg` in the same folder. The same format is used for default graphs
(`bin/default.i-*`, `bin/default-darkroom.i-*`), for [presets](presets.md) (`.pst`) and
for the undo [history](history-and-keyframes.md).

## Grammar

One command per line, fields separated by `:`. Lines starting with `#` are comments.
The dispatch is in `src/pipe/graph-io.c:238-251`.

| line | meaning |
|------|---------|
| `module:<name>:<inst>[:<x>:<y>]` | add an instance of module `<name>` called `<inst>`; optional position for the node editor |
| `connect:<name>:<inst>:<conn>:<name>:<inst>:<conn>` | wire an output (first triple) to an input (second triple) |
| `feedback:<same as connect>` | like `connect`, but the edge carries last frame's buffer; see [feedback connectors](feedback-connectors.md) |
| `param:<name>:<inst>:<param>:<v0>[:<v1>...]` | set all values of a parameter |
| `paramsub:<name>:<inst>:<param>:<beg>:<end>:<values>` | set only elements `beg` to `end` of an array parameter |
| `paraminc:` / `paramdec:` | same range form, but add or subtract instead of set; used by key accelerators |
| `keyframe:<frame>:<name>:<inst>:<param>:<beg>:<end>:<values>` | parameter value at an animation frame, linear interpolation |
| `keyframE:` `Keyframe:` `KeyframE:` `keyFRAME:` | same with ease-out, ease-in, smooth, or step interpolation (`graph-io.c:243-247`) |
| `frames:<n>` | number of animation frames |
| `fps:<f>` | frame rate |

Names in the first three fields are [tokens](tokens.md): at most 8 characters. A module
name of `-1` in a `connect:` line disconnects the input (`graph-io.c:171-181`).

## Example

The default darkroom graph for raw files, `bin/default-darkroom.i-raw` (shortened; the
numbers after the instance are node editor positions, and the instance of most processing
modules is `01`, not `main`):

```
module:i-raw:main:43:400
module:denoise:01:218:400
module:hilite:01:393:400
module:demosaic:01:568:400
module:colour:01:931:400
module:filmcurv:01:1094:400
module:llap:01:1269:400
module:grade:01:1444:400
module:hist:01:1618:634
module:crop:01:743:400
module:display:hist:1800:634
module:display:main:1745:400
connect:i-raw:main:output:denoise:01:input
connect:denoise:01:output:hilite:01:input
connect:hilite:01:output:demosaic:01:input
connect:demosaic:01:output:crop:01:input
connect:crop:01:output:colour:01:input
connect:colour:01:output:filmcurv:01:input
# apply llap after curve
connect:filmcurv:01:output:llap:01:input
connect:llap:01:output:grade:01:input
connect:grade:01:output:display:main:input
connect:grade:01:output:hist:01:input
connect:hist:01:output:display:hist:input
param:llap:01:sigma:0.12
param:i-raw:main:filename:none.raw
```

When an image is opened for the first time, the database copies this file to
`<image>.cfg` and appends one line that points the input at the file, replacing the
placeholder `none.raw` (`src/db/db.c:674`):

```
param:i-raw:main:filename:IMG_0001.CR2
```

The full default graph is walked module by module in
[default raw pipeline](../modules/default-raw-pipeline.md).

## Reading and writing

- `dt_graph_read_config_ascii()` reads a whole file; `dt_graph_read_config_line()` reads
  one line. Both live in `src/pipe/graph-io.c`.
- `dt_graph_write_config_ascii()` writes a graph back. Parameters are written in the
  module's declared order, and keyframes are written with the case-coded command.
- A connection that fails is logged with the [connector](connector.md) error string and
  the rest of the file is still read (`graph-io.c:193`).
- Parameter values are parsed by type: `float`, `int` or `string` (`graph-io.c:77-97`).
  A string parameter takes the rest of the line.

## Design notes

The format is deliberately small so that a diff of two recipes is readable and so that
other tools (shell scripts, the CLI, the key accelerator files) can generate it. Because the
same lines are also the unit of undo, the GUI never needs a second serialisation.

## Sources

- `src/pipe/graph-io.c:77-97, 171-193, 238-251`
- `bin/default-darkroom.i-raw`
- `src/db/db.c:670-676` (first-open copy and filename line)
- `doc/howto/defgraph/readme.md` (how default graphs are chosen)

## Related

- [Connector](connector.md), [Parameters and UI](parameters-and-ui.md)
- [History and keyframes](history-and-keyframes.md), [Presets](presets.md)
- [Default raw pipeline](../modules/default-raw-pipeline.md)
