---
title: Glossary
type: faq
summary: Short definitions of the words used across this wiki.
sources: []
updated: 2026-11-09
---
# Glossary

One or two sentences each. Follow the link for the full page.

- **Arena**: one large Vulkan memory allocation that the allocator carves into blocks.
  [Memory aliasing](../concepts/memory-aliasing.md)
- **Barrier**: a GPU command that makes one kernel wait for another's writes. Generated
  from graph edges. [Node](../concepts/node.md)
- **bc1**: a compressed GPU texture format used for thumbnails.
  [Database and thumbnails](../components/database-and-thumbnails.md)
- **Command buffer**: the list of GPU commands recorded per run and submitted once.
  [Scheduler](../components/scheduler-run-passes.md)
- **Connector**: a typed input or output plug on a module or node.
  [Connector](../concepts/connector.md)
- **DAG**: directed acyclic graph; boxes and one-way arrows with no loops.
  [Processing graph](../concepts/processing-graph-dag.md)
- **Darkroom**: the GUI view that edits one image. [GUI](../components/gui.md)
- **Default graph**: the recipe copied for a new image, `bin/default-darkroom.i-*`.
  [Default raw pipeline](../modules/default-raw-pipeline.md)
- **Descriptor set**: Vulkan's table of buffers and images a kernel can read.
  [Node](../concepts/node.md)
- **Display sink**: the `display` module that shows a buffer on screen.
  [GUI](../components/gui.md)
- **Dispatch**: launching a compute kernel over a grid of work groups. [Node](../concepts/node.md)
- **Feedback connector**: an edge that carries last frame's output into this frame.
  [Feedback connectors](../concepts/feedback-connectors.md)
- **Graph**: `dt_graph_t`, the whole set of modules and nodes for one image or job.
  [Pipeline core](../components/pipe-core.md)
- **History**: the undo list, stored as recipe lines.
  [History and keyframes](../concepts/history-and-keyframes.md)
- **Image parameters**: metadata (black point, white balance, matrix) travelling with the
  pixels. [Image parameters](../concepts/image-params-metadata.md)
- **Instance**: one occurrence of a module class in a graph, named by a token such as
  `main` or `01`. [Module](../concepts/module.md)
- **Kernel**: one GLSL compute shader, a `.comp` file compiled to SPIR-V.
  [Node](../concepts/node.md)
- **Keyframe**: a parameter value at an animation frame.
  [History and keyframes](../concepts/history-and-keyframes.md)
- **Lighttable**: the GUI view with thumbnails of a folder. [GUI](../components/gui.md)
- **Module**: the user-facing box: class plus instance, connectors, parameters.
  [Module](../concepts/module.md)
- **Node**: one kernel with a size and its connectors; modules expand into nodes.
  [Node](../concepts/node.md)
- **Preset**: a `.pst` file of recipe lines applied in one step.
  [Presets](../concepts/presets.md)
- **Push constant**: up to 256 bytes handed to a kernel per dispatch. [Node](../concepts/node.md)
- **Recipe**: the `.cfg` text file that describes a graph.
  [Recipe file format](../concepts/cfg-recipe-format.md)
- **ROI**: region of interest; full size and computed size of a buffer.
  [Region of interest](../concepts/roi-region-of-interest.md)
- **Run flags**: bits that select which passes a run performs.
  [Run flags](../concepts/run-flags.md)
- **Sidecar**: a file next to the image, such as `IMG.CR2.cfg`.
  [Database and thumbnails](../components/database-and-thumbnails.md)
- **Sink**: a connector or module that consumes a buffer for display or file output.
  [Connector](../concepts/connector.md)
- **Source**: a connector or module that produces a buffer from the CPU (file input).
  [Connector](../concepts/connector.md)
- **SPIR-V**: the binary shader format Vulkan loads, `.spv` files.
  [Build system](../components/build-system.md)
- **SSBO**: shader storage buffer object; a connector with channel `ssbo` is a buffer,
  not an image. [Connector](../concepts/connector.md)
- **Staging memory**: CPU-visible GPU memory used to upload sources and download sinks.
  [Scheduler](../components/scheduler-run-passes.md)
- **Timeline semaphore**: a Vulkan counter used to know when a frame finished.
  [Scheduler](../components/scheduler-run-passes.md)
- **Token**: an 8-character name stored in a 64-bit integer. [Tokens](../concepts/tokens.md)
- **Topological order**: an order of nodes where every producer comes before its
  consumers. [Processing graph](../concepts/processing-graph-dag.md)
- **Uniform**: a small read-only buffer of parameters visible to a kernel.
  [Parameters and UI](../concepts/parameters-and-ui.md)
- **Wildcard connector**: `*` or `&input` in a connector declaration; takes the format
  of whatever is connected. [Connector](../concepts/connector.md)

## Sources

- The definitions summarise the linked pages; each of those pages cites the code.

## Related

- [Index](../index.md)
