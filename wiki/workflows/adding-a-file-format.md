---
title: Add a file format
type: workflow
summary: Input and output modules for new formats and the default graphs that go with them.
sources:
  - doc/howto/file-support/readme.md
  - src/pipe/graph-defaults.h
  - src/pipe/modules/i-pfm
  - src/pipe/modules/o-pfm
  - bin/default.i-pfm
  - bin/default-darkroom.i-pfm
updated: 2026-11-09
---
# Add a file format

Formats are modules. An input format is a module whose name starts with `i-` and has a
`source` connector; an output format starts with `o-` and has a `sink` connector. The
core never looks inside a file.

## Output format (`o-new`)

1. Create `src/pipe/modules/o-new/` with `connectors`. `o-pfm` declares
   `input:sink:rgba:f32`; `o-jpg` asks for `ui8`. Pick the format you want to receive;
   the exporter inserts a conversion upstream if the declared format differs from what
   the graph produces.

2. `params` has the output name, `filename:string:256:output` in `o-pfm`, and often a
   `quality` value.

3. `main.c` implements `write_sink(module, buf, ...)`. The core calls it during the
   download pass with a pointer to the CPU copy of the image; the module writes the file.
   The `filename` parameter is set by the exporter.

4. That is all. The export dialog and `vkdt-cli --format o-new` list every module whose
   name starts with `o-` automatically (`doc/howto/file-support/readme.md`).

Look at `src/pipe/modules/o-pfm/` for the smallest real example.

## Input format (`i-new`)

1. Create `src/pipe/modules/i-new/` with `connectors`:

   ```
   output:source:rgba:f16
   ```

   Use `ui16` for mosaic data, `f16` or `f32` for floating point images, `ui8` for 8-bit.
   The channel field can be `*` and set at run time in `modify_roi_out`.

2. `params` must have `filename:string:...`. The database writes
   `param:i-new:main:filename:<file>` into every new recipe (`src/db/db.c:674`).

3. `main.c` implements at least:
   - `modify_roi_out`: open the file header, set `full_wd`, `full_ht` on the output,
     fill `module->img_param` (black, white, white balance, matrix, EXIF fields; see
     [image metadata](../concepts/image-params-metadata.md)).
   - `read_source`: decode the pixels into the mapped staging buffer the core hands you.
   Video inputs also implement `animate` (advance the frame) and `audio`.

4. **Register the extension** in `src/pipe/graph-defaults.h`:
   `dt_graph_default_input_module()` maps the file extension to the module token
   (`.mlv` to `i-mlv`, `.pfm` to `i-pfm`, ..., anything else to `i-raw`). Add a line for
   your extension.

5. **Add two default graphs** in `bin/`:
   - `default.i-new`: the thumbnail recipe, ending in `o-bc1:main`. Copy
     `bin/default.i-pfm` and change the input module.
   - `default-darkroom.i-new`: the darkroom recipe, ending in `display:main`. Copy
     `bin/default-darkroom.i-pfm`.
   The database picks `default*.i-<module>` by the token from step 4.

6. If the new format is raw mosaic data, keep the `denoise`, `hilite`, `demosaic` chain in
   the default graph; if it is already RGB, start at `colour` or `filmcurv` like the
   `i-jpg` defaults do.

## Testing

```
./vkdt-cli -g file.new.cfg --dump-modules       # recipe and defaults load
./vkdt-cli -g file.new.cfg --format o-pfm       # full export
./vkdt /folder/with/new/files                   # thumbnails appear
```

If the thumbnails are blank, run with `-d db -d pipe` to see which default graph was
chosen and which connection failed.

## Sources

- `doc/howto/file-support/readme.md`
- `src/pipe/graph-defaults.h:3-33`
- `src/pipe/modules/i-pfm/`, `src/pipe/modules/o-pfm/`
- `bin/default.i-pfm`, `bin/default-darkroom.i-pfm`, `src/db/db.c:670-676`

## Related

- [Add a module](adding-a-module.md)
- [Default raw pipeline](../modules/default-raw-pipeline.md)
- [Database and thumbnails](../components/database-and-thumbnails.md)
