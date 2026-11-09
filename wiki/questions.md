---
title: Open questions and lint findings
type: meta
summary: Contradictions, stale documentation and unverified claims found while compiling the wiki.
sources: []
updated: 2026-11-09
---
# Open questions and lint findings

Each entry says what was found, where, and what would resolve it. Resolved entries move
to the bottom with the resolution.

## Open

1. **GUI toolkit named wrongly in its readme.** `src/gui/readme.md` says the GUI is written
   with imgui and has a C++ part. The code uses nuklear (`src/gui/nuklear.h`, `nk_*` calls
   in `src/gui/render_darkroom.c`) and is C. Resolve by updating the readme upstream.
   Pages: [gui](components/gui.md).
2. **Sound readme is stale.** `src/snd/readme.md` says alsa is the only backend. The folder
   has `alsa.c`, `pw.c` (pipewire) and `none.c`, and `bin/config.mk.defaults` has a
   `VKDT_USE_PIPEWIRE` switch. Pages: [core utilities](components/core-utilities.md).
3. **Run flag with no consumer.** `s_graph_run_before_active` is defined in
   `src/pipe/modules/api.h:35` and printed in `src/pipe/graph.c:757`, but no code in
   `src/pipe` reads it to skip nodes. The `active_module` field is set by the GUI. Either the
   flag is a planned feature or the consumer lives somewhere not yet read. Pages:
   [run flags](concepts/run-flags.md).
4. **Kernel counts are read, not measured.** The build container has no GPU, so the numbers
   of nodes per module in [default raw pipeline](modules/default-raw-pipeline.md) come from
   counting `dt_node_add` calls, not from `vkdt-cli --dump-nodes`. Resolve by running the
   dump on a machine with Vulkan and recording the real counts.
5. **Module count differs by definition.** `src/pipe/modules/` has 110 entries, 101 of which
   have a `connectors` file. The rest are shared code (`shared/`, `api.h`, `bs.h`,
   `localsize.h`, `matrices.h`, `colourspaces.glsl`, `shared.glsl`) or folders without
   connectors. The wiki uses 101 as the module count.
6. **Which modules are "core"?** `doc/core.md` promises backward compatibility for modules
   tagged core, but the tag list was not found in this pass. Resolve by locating where the
   tag is stored (module readme front matter or a list in `doc/`).
7. **Howto index lists pages that do not exist.** `doc/howto/howto.md` ends with topics
   marked "do not exist yet" (feedback, gallery, fit, align, crash). Not a bug, but the wiki
   should not link to them.
8. **ROI is scale, region or both?** The display's backward ROI request certainly carries the
   scale (level of detail, zoom). Whether darkroom zoom also crops the computed region to the
   visible part was not confirmed. Pages: [region of interest](concepts/roi-region-of-interest.md).

## Resolved

- none yet

## Sources

- none (this page is a record)

## Related

- [schema](schema.md)
- [log](log.md)
