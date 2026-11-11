---
title: Wiki log
type: meta
summary: Chronological record of every ingest, query and lint operation on this wiki.
sources: []
updated: 2026-11-09
---
# Wiki log

One line per operation, newest last. Format: `date · operation · what · pages`.

- 2026-11-09 · bootstrap · Compiled the wiki from the checkout at `af70c5d` (2026-11-06). Read
  `readme.md`, `src/pipe/readme.md`, `src/pipe/*.h`, `src/pipe/graph*.c|h|inc`,
  `src/pipe/modules/readme.md`, the `main.c` and `connectors` of the default pipeline modules,
  `src/gui/gui.h`, `src/gui/main.c`, `src/db/*.h`, `src/qvk/qvk.h`, `src/cli/`, `src/fit/`,
  `Makefile`, `bin/config.mk.defaults`, `src/Makefile`, `doc/howto/*`. · all pages
- 2026-11-09 · query · "Why a DAG, and is it the modern trend?" answered and filed. ·
  `faq/why-a-dag.md`, `faq/comparison-with-other-tools.md`
- 2026-11-09 · lint · First pass. Found stale docs (gui readme says imgui, code uses nuklear;
  snd readme says alsa only, pipewire backend exists), an apparently unused run flag, and
  unverified node counts (no GPU in the build container). · `questions.md`

## Sources

- none (this page is a record)

## Related

- [schema](schema.md)
- [open questions](questions.md)

## 2026-11-09 ingest: all planned pages written

- Wrote the 14 concept pages, 8 component pages, 4 module pages, 5 workflow pages and 3
  FAQ pages listed in `index.md`.
- Verified line citations against commit `af70c5d` while writing. Corrections made on
  the way: the fixed arrays are at `graph.c:795, 811` (not 787, 803); the slider path is
  `render_darkroom.h:299-303` (gui `api.h:45` is the animation seek); the default graphs
  use instance `01` for processing modules, `main` only for input and display;
  `dt_roi_t` has no x/y offset, only full and scaled sizes plus a marker; `NUM_GAMMA` in
  llap is 10; shaders target `vulkan1.4`; 80 modules have a `main.c`.
- Added `tools/lint.py` and ran it: 43 pages, 0 errors after fixing README front matter,
  the glossary sources section and one example link in `schema.md`.

