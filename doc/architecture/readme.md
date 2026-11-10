# architecture guide

[index.html](index.html) in this directory is an illustrated, animated walk
through how vkdt is put together. it is one self-contained file: open it in a
browser. it needs no build step and makes no network requests.

what it covers, in order:

* one raw image followed through the default darkroom graph
* the three binaries (`vkdt`, `vkdt-cli`, `vkdt-fit`) and the code they share
* modules vs. nodes, connectors and tokens
* the stages of `dt_graph_run` and which of them are skipped on a parameter change
* how buffer memory is planned and reused
* the files that make up a module, using `exposure` as the example
* frames, keyframes and feedback connectors
* the gui main loop and how the graph output reaches the screen
* what vkdt reads and writes on disk
* a source map with good first files to read

the figures simplify on purpose. where a figure and the code disagree, the
code is right.
