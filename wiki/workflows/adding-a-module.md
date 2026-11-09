---
title: Add a module
type: workflow
summary: Create a module directory, describe connectors and params, write kernels, optionally add main.c.
sources:
  - src/pipe/modules/readme.md
  - src/pipe/modules/api.h
  - src/pipe/modules/llap
  - src/Makefile
updated: 2026-11-09
---
# Add a module

Goal: a new box users can drop into the graph. The minimum is two files; the full form is
a `main.c` with callbacks. See [module anatomy](../modules/module-anatomy.md) for what
each file means.

## A one-kernel module in five steps

1. **Make the directory**, name at most 8 characters (it becomes a
   [token](../concepts/tokens.md)):

   ```
   mkdir src/pipe/modules/warmify
   ```

2. **Declare connectors** in `connectors`:

   ```
   input:read:rgba:f16
   output:write:rgba:f16
   ```

3. **Declare parameters** in `params` and widgets in `params.ui`:

   ```
   # params
   amount:float:1:0.5
   # params.ui
   amount:slider:0.0:1.0
   ```

4. **Write the kernel** `main.comp`:

   ```glsl
   #version 460
   #extension GL_GOOGLE_include_directive    : enable
   #extension GL_EXT_nonuniform_qualifier    : enable
   #include "shared.glsl"
   layout(local_size_x = DT_LOCAL_SIZE_X, local_size_y = DT_LOCAL_SIZE_Y, local_size_z = 1) in;
   layout(std140, set = 0, binding = 1) uniform params_t { float amount; } params;
   layout(set = 1, binding = 0) uniform sampler2D img_in;
   layout(set = 1, binding = 1) uniform writeonly image2D img_out;
   void main()
   {
     ivec2 ipos = ivec2(gl_GlobalInvocationID);
     if(any(greaterThanEqual(ipos, imageSize(img_out)))) return;
     vec3 rgb = texelFetch(img_in, ipos, 0).rgb;
     rgb *= mix(vec3(1.0), vec3(1.1, 1.0, 0.9), params.amount);
     imageStore(img_out, ipos, vec4(rgb, 1.0));
   }
   ```

   Copy the preamble from an existing small module (for example `exposure/main.comp`)
   rather than from memory; the include names and extensions must match the tree.

5. **Document** it in `readme.md` with a `## parameters` list. Tooltips are generated
   from it. Then `make` and add `module:warmify:01` plus two `connect:` lines to a recipe,
   or add it in the node editor.

No build file is needed: `src/Makefile` finds every module directory and compiles every
`.comp` to `.spv`. Without `main.c` the module gets the default callbacks: one node, same
size as the input, parameters as uniforms.

## When you need `main.c`

Add `main.c` and a `flat.mk` (copy one from a neighbour) when the module must:

- create more than one node or nodes of different sizes: implement `create_nodes` with
  `dt_node_add` and `dt_node_connect_named` (`src/pipe/modules/api.h:160, 212`); see the
  [llap example](../modules/llap-worked-example.md)
- change the output size or need a border: implement `modify_roi_out` and
  `modify_roi_in`; see [ROI](../concepts/roi-region-of-interest.md)
- derive uniforms from parameters (a matrix, a table): implement `commit_params`
- rebuild the graph when a combo changes: implement `check_params` and return
  `s_graph_run_all` for structural parameters, `s_graph_run_record_cmd_buf` otherwise
- read a file or device: it is an input module with a `source` connector and
  `read_source`; see [add a file format](adding-a-file-format.md)
- write a file: a `sink` connector and `write_sink`
- react to clicks or keys: `input` and `ui_callback`

The `flat.mk` sets `MOD_CFLAGS` and `MOD_LDFLAGS` if the module links a library, and
lists explicit dependencies so shaders rebuild when an include changes, for example
`pipe/modules/llap/curve.comp.spv: pipe/modules/llap/llap.glsl`
(`src/pipe/modules/llap/flat.mk`).

## Checklist before committing

- Names (module, connectors, params) are 8 characters or fewer.
- `readme.md` exists and is linked from `src/pipe/modules/readme.md` under a category.
- Run `vkdt-cli -g test.cfg --dump-nodes` to see the nodes and their sizes.
- Run with `-d perf` and check the kernel time is sane.
- Run `make debug` once; validation layers catch wrong bindings and missing barriers.
- If the module is meant for the default graph, add it to `bin/default-darkroom.i-raw`
  and friends, and maybe to `bin/darkroom.ui` so a panel appears.

## Sources

- `src/pipe/modules/readme.md` ("files to describe a module", widget list)
- `src/pipe/modules/api.h:160-245`
- `src/pipe/modules/llap/` and its `flat.mk` (multi-node example), `src/pipe/modules/exposure/main.comp` (one-kernel example, the preamble above)
- `src/Makefile` (module discovery)

## Related

- [Module anatomy](../modules/module-anatomy.md)
- [Parameters and UI](../concepts/parameters-and-ui.md)
- [Debug the graph](debugging-the-graph.md)
