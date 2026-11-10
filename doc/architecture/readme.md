# architecture guide

[index.html](index.html) in this directory is an illustrated, animated walk
through how vkdt is put together. it is one self-contained file: open it in a
browser. it needs no build step and makes no network requests.

[index.zh.html](index.zh.html) is the same guide in simplified chinese
(简体中文版).

what it covers, in order:

**the idea**

* one raw image followed through the default darkroom graph
* the three main binaries (`vkdt`, `vkdt-cli`, `vkdt-fit`) and the code they share
* what the pixel values mean at each stage, from sensor counts to the monitor

**the engine**

* modules vs. nodes, connectors, how `*` and `&input` are resolved, tokens
* the stages of `dt_graph_run`, which of them are skipped on a parameter
  change, and how the graph is sorted
* the vulkan commands recorded per node and what a shader finds in which
  descriptor set
* how buffer memory is planned and reused
* frames, keyframe easing and feedback connectors
* `vkdt-fit`: running the graph as a function to fit parameters

**modules**

* the files that make up a module, using `exposure` as the example
* writing your own module, shader-only and with `create_nodes`
* the formulas behind `filmcurv`, `llap`, `denoise` and `grade`, as live plots
* a browsable catalogue of all modules with their connectors and parameters

**the app**

* the gui main loop and how the graph output reaches the screen
* the edit history: undo as a replay of config lines
* threads and gpu queues: who submits where
* how lighttable thumbnails are rendered, cached and displayed
* what vkdt reads and writes on disk, and how a preset rewires a graph
* the build: what make produces and how the program finds it
* a source map with good first files to read, and a glossary

the figures simplify on purpose. where a figure and the code disagree, the
code is right. the module catalogue inside the page is a snapshot generated
from `src/pipe/modules/*/{connectors,params}`, the module list in
`src/pipe/modules/readme.md` and `doc/core.txt`.
