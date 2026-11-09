---
title: Debug the graph
type: workflow
summary: Log categories, graphviz dumps, per-kernel timings, memory statistics, common errors.
sources:
  - src/core/log.h
  - src/pipe/graph-print.h
  - src/pipe/graph.c
  - src/cli/main.c
  - src/pipe/connector.h
  - Makefile
updated: 2026-11-09
---
# Debug the graph

## Turn on logging

Both `vkdt` and `vkdt-cli` take `-d <category>`, repeatable. Categories
(`src/core/log.h:12-23`):

| category | prints |
|----------|--------|
| `err` | errors (always on) |
| `pipe` | graph construction, connection failures, ROI decisions |
| `qvk` | Vulkan device selection, extensions, swap chain |
| `gui` | view switches, input |
| `db` | folder scan, which default graph was used, `vkdt.db` reads and writes |
| `cli` | export progress |
| `snd` | audio |
| `perf` | per-node GPU timings after every run |
| `mem` | memory arena sizes and peak use |
| `ray` | ray tracing acceleration structures |
| `all` | everything |

## Print the graph

```
vkdt-cli -g image.cfg --dump-modules     # module list with instance names and connections
vkdt-cli -g image.cfg --dump-nodes       # every node with kernel, size, connectors
```

These call `dt_graph_print_modules()` and `dt_graph_print_nodes()`
(`src/pipe/graph-print.h:22, 76`), which write graphviz `dot` syntax. Pipe into
`dot -Tpdf > graph.pdf` to get a picture of the DAG. The node dump is the fastest way to
see what `create_nodes` of a module really built and which ROI each node got.

## Timings

`-d perf` makes the scheduler write timestamp queries around every node and print, after
each run, one line per node and a sum per module, then `total time`
(`src/pipe/graph.c:945-997`). Numbers are GPU time in milliseconds. Use it to find the
module that dominates a frame. In the GUI the same numbers can be shown in the node
editor.

## Memory

`-d mem` prints what the allocator planned: the size of each arena, how many bytes were
aliased, and the peak. If a run fails with an out-of-memory error from Vulkan, look here
first, then reduce the preview size (`intgui/lod`) or export size. See
[memory aliasing](../concepts/memory-aliasing.md).

## Validation layers

`make debug` builds with `-DQVK_ENABLE_VALIDATION` and `-DDEBUG_MARKERS`
(`Makefile:119`). The Vulkan validation layer then reports wrong descriptor bindings,
missing barriers, out-of-range image accesses and format mismatches, with the node name
as a debug marker. It is slow; use it only to find the bug.

## Common errors and what they mean

| message | cause | fix |
|---------|-------|-----|
| `connection failed: error 10: channels do not match` | connector channels differ (`rggb` into `rgba`) | insert `demosaic` or `format`, or use `*` |
| `error 11: format does not match` | `f16` output into `ui8` input | add a `format` module or change the declaration |
| `error 12: connection would be cyclic` | the wire closes a loop | use `feedback:` if a one-frame delay is intended |
| `error 3: destination does not read` | wired into an output | swap the two triples in the `connect:` line |
| `error 1`/`7: no such ... node` | instance name typo, or module failed to load | check `-d pipe` for `dlopen` errors, check 8-char names |
| black image, no error | a module not reached from a sink, or ROI of size 0 | `--dump-nodes` and look at `wd`, `ht` |
| `too many modules`/`nodes` | over 100 modules or 2000 nodes | split the graph |
| shader not found | `.spv` missing | `make reload-shaders`, check the kernel name in `dt_node_add` |

Error codes are from `src/pipe/connector.h:181-200`. See [connector](../concepts/connector.md).

## Tests

`src/pipe/tests/` holds unit tests for the allocator, graph construction and tokens
(`make -C src/pipe/tests` style builds, see the files). Image regression tests are in the
separate `vkdt-test` repository and compare CLI exports against references.

## Sources

- `src/core/log.h:12-23`, `src/pipe/graph-print.h:22, 76`
- `src/pipe/graph.c:945-997` (perf output), `src/cli/main.c:84-86` (dump flags)
- `src/pipe/connector.h:181-200`, `Makefile:119-130`

## Related

- [Scheduler: the run passes](../components/scheduler-run-passes.md)
- [Connector](../concepts/connector.md)
- [Build and run](build-and-run.md)
