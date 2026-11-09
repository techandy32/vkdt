---
title: Wiki schema
type: meta
summary: The rules every page in this wiki follows, and the three operations that maintain it.
sources: []
updated: 2026-11-09
---
# Wiki schema

## Layers

1. **Raw** is the repository itself. The wiki never edits raw files and never copies long
   passages from them. It cites them by path and, where useful, by line number.
2. **Wiki** is this folder. Every page is Markdown with YAML front matter.
3. **Schema** is this file. Change it only when the conventions change.

## Page types

| type | folder | answers the question |
|------|--------|----------------------|
| overview | `overview/` | what is this thing and how do its parts fit together |
| concept | `concepts/` | what does this word mean in vkdt and how does it work |
| component | `components/` | what does this part of the source tree do |
| module | `modules/` | how do processing modules work, with worked examples |
| workflow | `workflows/` | how do I do X, step by step |
| faq | `faq/` | questions people actually ask, with the reasoning |
| meta | top level | how the wiki itself works |

## Front matter

Every page starts with:

```yaml
---
title: Human readable title
type: overview | concept | component | module | workflow | faq | meta
summary: One sentence. Appears in index.md.
sources:
  - src/pipe/graph.c
  - src/pipe/readme.md
updated: YYYY-MM-DD
---
```

`sources` lists the raw files the page was compiled from. A page with an empty list is
either meta or synthesis; synthesis pages say so in their first paragraph.

## Writing rules

- Write for a reader who knows programming but not vkdt. Define a term the first time it
  appears on a page, or link to its concept page.
- Short sentences. One idea per paragraph. Prefer a table to a long list of facts.
- State what the code does, not what it should do. When the code and a readme disagree,
  describe the code and record the disagreement in [questions.md](questions.md).
- Numbers come with their origin: a file, a command, or "counted on YYYY-MM-DD".
- Anything not verified in the repository is marked "(general knowledge)" or "(external)".
- Every page ends with a `## Sources` section (paths, optionally `path:line`) and a
  `## Related` section with links to other wiki pages.

## Links

- Use relative Markdown links, for example `[module](concepts/module.md)` from the root (prefix `../` from a subfolder). They render on
  GitHub and in Obsidian alike.
- Every page must be listed in [index.md](index.md) with its summary.
- A page that nothing but the index links to is an orphan. The lint tool reports orphans;
  fix them by linking from the pages that should mention them.

## Names

File names are lower-case, hyphen-separated, and name the thing, not the question
(`memory-aliasing.md`, not `how-does-memory-work.md`). FAQ pages are the exception and may
be phrased as questions.

## Operations

### Ingest

Trigger: a commit, pull request, or upstream merge changed raw files.

1. Read the diff. List the wiki pages whose `sources` include a changed file.
2. Update those pages. Keep the page's shape; change the facts.
3. If a changed file has no page, decide whether it needs one. New modules get a row in
   `modules/module-catalog.md`; new subsystems get a component page.
4. Update `updated:` on every touched page and the commit hash in `README.md`.
5. Append one line to `log.md`: date, operation, what changed, which pages.

### Query

Trigger: someone asks a question about vkdt.

1. Read `index.md`. Open the two or three pages whose summaries match.
2. Answer from the pages. Quote the `Sources` so the asker can verify.
3. If the pages did not contain the answer and you had to read code, write the answer back:
   a new section on the closest page, or a new FAQ page. Log it.

### Lint

Trigger: periodically, or after a large ingest.

1. Run `python3 wiki/tools/lint.py`. Fix broken links, missing front matter, pages missing
   from the index.
2. Read pages that share sources and look for contradictions, numbers that drifted, and
   claims the current code no longer supports.
3. Record each finding in `questions.md` with the pages involved. Resolve what can be
   resolved from the code; leave the rest as open questions for a human.

## Sources

- The pattern this wiki follows is Andrej Karpathy's "LLM wiki" note (external).

## Related

- [index](index.md)
- [log](log.md)
- [open questions](questions.md)
