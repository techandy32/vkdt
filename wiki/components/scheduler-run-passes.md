---
title: "Scheduler: the run passes"
type: component
summary: dt_graph_run step by step, from waiting on the previous frame to submitting the command buffer.
sources:
  - src/pipe/graph.c
  - src/pipe/graph-run-modules.h
  - src/pipe/graph-run-nodes-allocate.h
  - src/pipe/graph-run-nodes-upload.h
  - src/pipe/graph-run-nodes-record-cmd.h
  - src/pipe/graph-run-nodes-download.h
updated: 2026-11-09
---
# Scheduler: the run passes

`dt_graph_run(graph, run)` (`src/pipe/graph.c:770-1001`) turns the graph into GPU work.
`run` is the [run flags](../concepts/run-flags.md) mask. Below, line numbers are inside
`graph.c`.

## Step by step

```
 1 wait for the previous frame        vkWaitSemaphores            :792
 2 module passes                      dt_graph_run_modules         :801
     animate()                          per module
     pass 1  modify_roi_out             sources -> sinks
     pass 2  modify_roi_in              sinks -> sources
     propagate_roi_in, create_nodes     builds node[] from module[]
   stop here if only ROI was asked      :805
 3 sort nodes                          graph-traverse.inc, from sinks
 4 allocate                            dt_graph_run_nodes_allocate  :860
 5 upload sources                      dt_graph_run_nodes_upload    :863
 6 upload uniforms                     dt_graph_run_modules_upload_uniforms :870
 7 record command buffer               vkBeginCommandBuffer         :879
                                        dt_graph_run_nodes_record_cmd :881
                                        vkEndCommandBuffer           :904
 8 submit                              vkQueueSubmit                :930
   optionally wait                      vkWaitSemaphores             :939
 9 download sinks                      dt_graph_run_nodes_download  :943
10 read timings                        vkGetQueryPoolResults        :945-997
```

### 1. Wait

The graph has a timeline semaphore. Before touching any buffer the run waits until the
GPU finished the frame that used them. The GUI usually runs with `wait_done` cleared and
double buffers the display image, so this wait is short.

### 2. Module passes

`dt_graph_run_modules` (`src/pipe/graph-run-modules.h`) walks the module list in
topological order. If `s_graph_run_roi` is set it runs the two
[ROI](../concepts/roi-region-of-interest.md) passes. If `s_graph_run_create_nodes` is set
it empties `node[]`, calls every module's `create_nodes` and then repoints the module's
public connectors to the node connectors they stand for. Modules that are not reached from
a sink are skipped entirely.

### 3. Sort nodes

The same traversal macro sorts the fresh node list from the sinks backwards. `main`
display sinks are visited first. The result is `nodeid[]`, at most 2000 entries
(`graph.c:811`).

### 4. Allocate

`dt_graph_run_nodes_allocate` (`src/pipe/graph-run-nodes-allocate.h`) creates Vulkan
images and buffers for every output, plans memory with the last-reader trick, allocates
one block per arena, binds everything, and writes descriptor sets. See
[memory aliasing](../concepts/memory-aliasing.md). This only happens when
`s_graph_run_alloc` is set.

### 5. Upload sources

For every node with a `source` connector that requested a read, `read_source()` of its
module fills a mapped staging buffer (`src/pipe/graph-run-nodes-upload.h`). Decoding the
raw file happens here, on the CPU, inside the module. A copy command moves the data onto
the GPU. Thumbnails and dynamic arrays (for example texture atlases) use the same path.

### 6. Upload uniforms

`commit_params()` of every module runs (or the default byte copy), and the result is
written into the uniform buffer for the current frame
(`dt_graph_run_modules_upload_uniforms`). This is the only pass a slider move really
needs besides recording.

### 7. Record

`dt_graph_run_nodes_record_cmd` (`src/pipe/graph-run-nodes-record-cmd.h`) walks
`nodeid[]` in order. For each node it emits barriers for its inputs, clears outputs that
ask for it, binds pipeline and descriptor sets, pushes constants and dispatches, or runs a
render pass for a graphics node. Timestamp queries are written around each node when
performance logging is on.

### 8. Submit

One `vkQueueSubmit` on the compute queue, or the graphics queue if any graphics node
exists (`graph.h:111-113`). The submit signals the timeline semaphore. If `wait_done` is
set the run blocks here.

### 9. Download

`dt_graph_run_nodes_download` copies sink images from staging memory to the CPU and calls
`write_sink()` on output modules. Only when `s_graph_run_download_sink` is set. The GUI
display sink is not downloaded; the GUI samples the GPU image directly.

### 10. Timings

With `-d perf` the query pool results are printed per node and summed per module
(`graph.c:945-997`). See [debug the graph](../workflows/debugging-the-graph.md).

## Interactive versus batch

| caller | typical mask | why |
|--------|--------------|-----|
| GUI after a slider | `record_cmd_buf` | nodes and memory unchanged |
| GUI after opening an image | `all` without `wait_done` | everything rebuilt, display double-buffered |
| CLI export | `all` with `download_sink` | must write files, waits anyway |
| thumbnail thread | `all` with `download_sink` | small graph, writes `.bc1` |

## Sources

- `src/pipe/graph.c:770-1001`
- `src/pipe/graph-run-modules.h`, `graph-run-nodes-allocate.h`, `graph-run-nodes-upload.h`,
  `graph-run-nodes-record-cmd.h`, `graph-run-nodes-download.h`
- `src/pipe/graph-traverse.inc`

## Related

- [Run flags](../concepts/run-flags.md)
- [Memory aliasing](../concepts/memory-aliasing.md)
- [Data flow of an edit](../overview/data-flow-of-an-edit.md)
