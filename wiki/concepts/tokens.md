---
title: Tokens
type: concept
summary: Eight-byte names used for modules, instances, parameters and connectors.
sources:
  - src/pipe/token.h
  - src/pipe/tests/token.c
updated: 2026-11-09
---
# Tokens

Almost every name in vkdt is a **token**: a string of at most 8 characters stored in one
64-bit integer (`dt_token_t`, `src/pipe/token.h:15`). Module names (`denoise`), instance
names (`main`), connector names (`output`), parameter names (`sigma`) and widget types
(`slider`) are all tokens.

## Why

- Comparing two names is one integer compare. The graph does thousands of lookups per run
  (find the module called X, find its connector called Y) and never calls `strcmp`.
- Names can be switched on in C with `if(cmd == dt_token("module"))`, as the recipe
  reader does (`src/pipe/graph-io.c:238`).
- A token is its own storage. No string pool, no allocation, no lifetime questions.

## How

- `dt_token("abc")` (`token.h:39`) packs the characters little-endian into the integer. It
  is a macro so it works in constant expressions and switch-like chains.
- `dt_token_str(t)` (`token.h:35`) reinterprets the integer's bytes as a `char *`. The
  result is **not** zero-terminated when the name has exactly 8 characters, so printing
  uses the format `%" PRItkn "` which is `.8s` (`token.h:59`).
- Shorter names are zero-padded, so `main` and `main\0\0\0\0` are the same token.

## Consequences you will meet

- A module, instance, parameter or connector name longer than 8 characters is cut. Choose
  short names: `filmcurv`, `demosaic`, `hilite`.
- Instance names in a recipe are tokens too, so `connect:i-raw:main:output:...` can be
  parsed without any string table.
- The unit test `src/pipe/tests/token.c` checks round-tripping.

## Sources

- `src/pipe/token.h:15, 35-59`
- `src/pipe/tests/token.c`
- `src/pipe/graph-io.c:238` (use in the recipe reader)

## Related

- [Recipe file format](cfg-recipe-format.md)
- [Module](module.md), [Connector](connector.md)
