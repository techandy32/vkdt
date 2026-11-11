---
title: Vulkan layer (src/qvk)
type: component
summary: Device, queues and feature detection wrapped in C helpers inherited from q2vkpt.
sources:
  - src/qvk/qvk.h
  - src/qvk/qvk.c
  - src/qvk/readme.md
updated: 2026-11-09
---
# Vulkan layer (src/qvk)

`src/qvk/` (about 1.4k lines) is the only place that creates the Vulkan instance and
device. The name comes from q2vkpt, the Quake 2 path tracer whose Vulkan bootstrap code
was reused (`src/qvk/readme.md`). The rest of vkdt calls Vulkan directly but always
through the handles stored in the global `qvk` struct.

## The `qvk` struct

`qvk_t` in `src/qvk/qvk.h`:

- `instance`, `physical_device`, `device`, debug messenger when validation is on
- `queue[s_queue_cnt]` and `qid[s_queue_cnt]`: queue handles and the mapping from role
  to actual queue family. Roles (`qvk.h:79-84`):

| role | index | used for |
|------|------:|----------|
| `s_queue_graphics` | 0 | the window swap chain, draws of graphics nodes |
| `s_queue_compute` | 1 | the processing graph (asynchronous compute when the GPU has a separate family) |
| `s_queue_work0`, `s_queue_work1` | 2, 3 | thumbnail threads |
| `s_queue_vid_dec` | 4 | video decode |

  Two roles may map to the same family on GPUs with few queues; `qid[]` handles that.
- `raytracing_supported`, `float_atomics_supported` (`qvk.h:139-140`): feature flags that
  modules check before using ray queries or atomic float adds.
- device limits used by the allocator and pipeline builder, `ticks_to_nanoseconds` for
  timestamp queries
- swap chain state for the GUI (format, images, image views)

## What it does

1. `qvk_init()` creates the instance with the extensions GLFW asks for, picks a physical
   device (by name `strqvk/device_name` or id `intqvk/device_id` from `config.rc` if set),
   and creates the logical device with the queues above.
2. Enables features the graph relies on: 16-bit storage and shader float16, descriptor
   indexing for connector arrays, timeline semaphores, dynamic rendering, buffer device
   address, and ray query when available.
3. Offers small helpers: command pool creation, one-shot command buffers, image layout
   transitions, shader module creation from `.spv` bytes.
4. For the GUI, creates and recreates the swap chain and chooses a 10-bit format when the
   display supports it.

## Why a separate layer

Everything that is boilerplate in Vulkan lives here once. Modules never see an instance or
a device; they only declare kernels and connectors. The CLI and the GUI call the same
`qvk_init()`, the CLI just skips the swap chain.

## Sources

- `src/qvk/qvk.h:79-84, 104-105, 139-140`
- `src/qvk/qvk.c`
- `src/qvk/readme.md`

## Related

- [Scheduler: the run passes](scheduler-run-passes.md)
- [GUI](gui.md)
- [Build and run](../workflows/build-and-run.md) (device selection in `config.rc`)
