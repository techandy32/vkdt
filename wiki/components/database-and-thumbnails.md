---
title: Database and thumbnails (src/db)
type: component
summary: Folder-based image list, vkdt.db ratings and labels, sidecar recipes and the bc1 thumbnail cache.
sources:
  - src/db/db.h
  - src/db/db.c
  - src/db/thumbnails.h
  - src/db/rc.h
  - src/db/readme.md
updated: 2026-11-09
---
# Database and thumbnails (src/db)

vkdt has no central catalog. The "database" is the folder you opened plus two kinds of
small text files next to the images. Nothing is lost if you move the folder.

## The image list

`dt_db_t` (`src/db/db.h:69`) holds the images of one folder as `dt_image_t` entries
(`db.h:24-30`): filename (in a string pool), thumbnail index, `rating` (0 to 5, or reject)
and `labels` bits (`db.h:12-20`: red, green, blue, yellow, purple, video, bracket, and bit
15 for "selected"). A *collection* is the filtered and sorted view of that list. Filters
(`dt_db_property_t`, `db.h:33-39`) are filename substring, minimum rating, label bits,
creation date and file type (the input module token).

## Files on disk

| file | content | written when |
|------|---------|--------------|
| `<folder>/vkdt.db` | `sort:<key>:`, `filter:<prop>:<value>` lines, a `time offset:` line, then one `<file>:rating:<n>` and `<file>:labels:<bits>` per image that has them (`src/db/db.c:494-552`) | folder changed or program exits |
| `<folder>/<image>.cfg` | the [recipe](../concepts/cfg-recipe-format.md) of one image | leaving darkroom mode |
| `~/.config/vkdt/config.rc` | settings as `type+key:value` lines (`intgui/lod:1`), read with `dt_rc_get_int`, `dt_rc_get_float`, `dt_rc_get` and written with `dt_rc_set_*` (`src/db/rc.h`) | on exit |
| `~/.config/vkdt/tags/<tag>/` | a folder of symlinks to images; tags are collections you can open like folders | tag assigned |
| `~/.cache/vkdt/<hash>.bc1` | thumbnail, hash is murmur3 of the full path | first time an image is seen |

When an image has no `.cfg` yet, `dt_db_...` copies `bin/default-darkroom.i-<input>` and
appends the `filename` parameter (`db.c:670-676`). The input module is chosen by file
extension via `src/pipe/graph-defaults.h`.

## Thumbnails

`dt_thumbnails_t` (`src/db/thumbnails.h`) owns:

- `DT_THUMBNAILS_THREADS` (2, `:37`) worker graphs, each a full `dt_graph_t` (`:40`) that
  runs the small default recipe `bin/default.i-<input>` with a `o-bc1` sink. Workers use
  the `s_queue_work0` and `s_queue_work1` Vulkan queues so they do not stall the darkroom.
- a GPU-side cache of decoded `.bc1` textures with an LRU list, so the lighttable can
  draw thousands of thumbnails with no CPU work after the first load.

API: `dt_thumbnails_cache_directory()` and `cache_collection()` schedule creation for a
folder or the current collection, `cache_one()` for a single image, `load_one()` and
`load_list()` bring finished files onto the GPU, `invalidate()` after an edit, and
`cache_abort()` when the user changes folder (`thumbnails.h`).

BC1 is a lossy GPU texture format at 4 bits per pixel. A thumbnail is tiny, uploads
without conversion and samples fast, which is why it was chosen over JPEG.

## Why no catalog

The author's stated goal (`src/db/readme.md`, `readme.md`) is that the file system is the
database: copy a folder to another machine and everything comes along. The price is that
cross-folder queries only exist through tags, and that ratings are per folder file.

## Sources

- `src/db/db.h:12-39, 69`, `src/db/db.c:494-552, 670-676`
- `src/db/thumbnails.h:37-41` and its function list
- `src/db/rc.h`, `src/db/readme.md`

## Related

- [Data flow of an edit](../overview/data-flow-of-an-edit.md)
- [GUI](gui.md)
- [Recipe file format](../concepts/cfg-recipe-format.md)
