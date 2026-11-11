---
title: README
type: meta
summary: What this wiki is and how to use it.
sources: []
updated: 2026-11-09
---
# vkdt wiki

This folder is an LLM-maintained knowledge base about the vkdt code base, built in the
style of Andrej Karpathy's "LLM wiki" pattern: raw sources stay untouched, a model compiles
them into a web of short, plain-language Markdown pages, and the same model keeps the pages
current as the code changes.

It is written so that a small model (or a new contributor) can answer questions about vkdt
by reading a handful of pages instead of the whole repository.

## Three layers

| layer | what it is | who edits it |
|-------|------------|--------------|
| raw | the source tree (`src/`, `bin/`, `doc/`) and the upstream `readme.md` files | developers, through normal commits |
| wiki | this folder: compiled pages with links and citations | the LLM, on ingest, query and lint |
| schema | [schema.md](schema.md): the rules the wiki follows | humans, rarely |

## How to use it

- **Human:** start at [index.md](index.md). Every page is listed there with a one-line summary.
- **LLM (Claude Code, Haiku, ...):** read `wiki/index.md` first, then open only the pages the
  question needs. Cite the `Sources` section of a page when you answer. If a question is not
  covered, follow the `sources` of the nearest page into the code, then write the answer back
  as a new page or a new section (see "query" in [schema.md](schema.md)).
- **Check the wiki:** `python3 wiki/tools/lint.py` verifies links, front matter and the index.

## Where to begin

1. [What vkdt is](overview/what-is-vkdt.md)
2. [Architecture in one picture](overview/architecture.md)
3. [The processing graph (DAG)](concepts/processing-graph-dag.md)
4. [How a run executes the graph](components/scheduler-run-passes.md)
5. [Why a DAG?](faq/why-a-dag.md)

## Operations

| operation | when | what happens |
|-----------|------|--------------|
| ingest | code or docs changed | read the diff, update affected pages, add a line to [log.md](log.md) |
| query | someone asks a question | answer from the pages; file durable answers as pages or sections |
| lint | periodically | run `tools/lint.py`, read for contradictions and stale facts, record them in [questions.md](questions.md) |

The wiki describes the checkout at commit `af70c5d` (2026-11-06) of `techandy32/vkdt`,
a fork of `hanatos/vkdt`. Line numbers in citations refer to that commit.
