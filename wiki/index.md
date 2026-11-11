---
title: Index
type: meta
summary: Catalog of every page in the vkdt wiki with a one-line summary.
sources: []
updated: 2026-11-09
---
# Index

Read this page first. Each entry is a page with its one-line summary. New pages must be
added here (the lint tool checks).

## Start here

- [What vkdt is](overview/what-is-vkdt.md): A GPU-only raw photo and video editor built around a processing graph.
- [Architecture in one picture](overview/architecture.md): The whole app as one graph: recipe file, module graph, node graph, scheduler, GPU, screen or file.
- [Repository map](overview/repository-map.md): What each directory in the source tree contains and how large it is.
- [Data flow of an edit](overview/data-flow-of-an-edit.md): What happens between opening an image, moving a slider, and exporting.

## Concepts

- [Processing graph (DAG)](concepts/processing-graph-dag.md): The directed acyclic graph of modules and nodes, its rules, limits and traversal.
- [Module](concepts/module.md): The user-facing processing box, its class, instance, callbacks and parameters.
- [Node](concepts/node.md): One GPU kernel with its dispatch size, push constants and descriptor sets.
- [Connector](concepts/connector.md): The typed input and output plugs on modules and nodes, and the rules for wiring them.
- [Recipe file format (.cfg)](concepts/cfg-recipe-format.md): The text format that stores a graph: module, connect, feedback, param, keyframe, frames, fps.
- [Region of interest (ROI)](concepts/roi-region-of-interest.md): How sizes flow forward and requests flow backward so kernels compute only what a sink needs.
- [Run flags](concepts/run-flags.md): The bit flags that choose which passes a graph run repeats after an edit.
- [Memory aliasing](concepts/memory-aliasing.md): How the allocator reuses GPU memory for intermediate buffers using last-reader information.
- [Feedback connectors](concepts/feedback-connectors.md): Edges that carry last frame's output into this frame, double-buffered, without making the graph cyclic.
- [Tokens](concepts/tokens.md): Eight-byte names used for modules, instances, parameters and connectors.
- [Image parameters (metadata)](concepts/image-params-metadata.md): The black point, white balance, matrix and colour description that travel along the graph edges.
- [Parameters and UI](concepts/parameters-and-ui.md): The params, params.ui and readme files that define a module's settings, widgets and uniforms.
- [History and keyframes](concepts/history-and-keyframes.md): Undo history stored as recipe lines, and keyframed animation of parameters.
- [Presets](concepts/presets.md): Recipe fragments that add modules, wires and parameters to a graph in one step.

## Components

- [Pipeline core (src/pipe)](components/pipe-core.md): The files that implement the graph, modules, connectors, allocator and I/O.
- [Scheduler: the run passes](components/scheduler-run-passes.md): dt_graph_run step by step, from waiting on the previous frame to submitting the command buffer.
- [Vulkan layer (src/qvk)](components/qvk-vulkan-layer.md): Device, queues and feature detection wrapped in C helpers inherited from q2vkpt.
- [GUI (src/gui)](components/gui.md): Views, the nuklear immediate-mode UI, display synchronisation and the hotkey files.
- [CLI and export](components/cli-and-export.md): vkdt-cli, vkdt-fit and the export mechanism that swaps display sinks for file outputs.
- [Database and thumbnails (src/db)](components/database-and-thumbnails.md): Folder-based image list, vkdt.db ratings and labels, sidecar recipes and the bc1 thumbnail cache.
- [Core utilities, sound, fit, tools](components/core-utilities.md): Logging, threads, LUTs, audio backends, the parameter optimiser and colour tooling.
- [Build system](components/build-system.md): Flat makefiles, config.mk switches, shader compilation to SPIR-V, module shared objects and CI.

## Modules

- [Module anatomy](modules/module-anatomy.md): The files that make up a module directory and the helper API modules use to build nodes.
- [Module catalog](modules/module-catalog.md): The 101 modules grouped by category.
- [Default raw pipeline](modules/default-raw-pipeline.md): The graph a raw file gets by default, module by module, with its two sinks.
- [Worked example: llap](modules/llap-worked-example.md): How one local-contrast module expands into a pyramid of about 24 kernels.

## Workflows

- [Build and run](workflows/build-and-run.md): Dependencies, make targets, running the GUI and CLI, first configuration.
- [Add a module](workflows/adding-a-module.md): Create a module directory, describe connectors and params, write kernels, optionally add main.c.
- [Add a file format](workflows/adding-a-file-format.md): Input and output modules for new formats and the default graphs that go with them.
- [Debug the graph](workflows/debugging-the-graph.md): Log categories, graphviz dumps, per-kernel timings, memory statistics, common errors.
- [Export from the command line](workflows/export-from-cli.md): Render a recipe to jpg, pfm, exr or video without the GUI.

## FAQ

- [Why a DAG?](faq/why-a-dag.md): The reasons the pipeline is a graph instead of an ordered list, and what that costs.
- [Comparison with other tools](faq/comparison-with-other-tools.md): darktable, DaVinci Resolve, compositors, render graphs and ML frameworks next to vkdt.
- [Glossary](faq/glossary.md): Short definitions of the words used across this wiki.

## Meta

- [README](README.md): What this wiki is and how to use it.
- [Schema](schema.md): The rules every page follows and the ingest, query and lint operations.
- [Log](log.md): Chronological record of wiki operations.
- [Open questions](questions.md): Contradictions, stale documentation and unverified claims.
