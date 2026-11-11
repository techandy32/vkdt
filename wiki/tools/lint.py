#!/usr/bin/env python3
"""Lint the vkdt wiki.

Checks, for every Markdown page under the wiki directory:
  1. front matter exists and has title, type, summary, updated
  2. type is one of the allowed values
  3. every relative Markdown link resolves to a file
  4. every page is listed in index.md (except index.md itself)
  5. every page has a "## Sources" and a "## Related" section (meta pages exempt)
Also reports pages that no other page links to (orphans).

Usage: python3 wiki/tools/lint.py [wiki_dir]
Exit status 1 when a check fails, 0 otherwise. Orphans are warnings only.
"""
import os
import re
import sys

ALLOWED_TYPES = {"overview", "concept", "component", "module", "workflow", "faq", "meta"}
REQUIRED_KEYS = ("title", "type", "summary", "updated")
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")


def read_front_matter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    block = text[4:end]
    data = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..")
    root = os.path.abspath(root)
    pages = []
    for dirpath, _, files in os.walk(root):
        if os.path.basename(dirpath) == "tools":
            continue
        for f in sorted(files):
            if f.endswith(".md"):
                pages.append(os.path.join(dirpath, f))
    pages.sort()

    errors = []
    warnings = []
    inbound = {p: 0 for p in pages}
    index_path = os.path.join(root, "index.md")
    index_text = open(index_path, encoding="utf-8").read() if os.path.exists(index_path) else ""
    index_links = set()
    for m in LINK_RE.finditer(index_text):
        target = m.group(1).split("#")[0]
        if target.endswith(".md"):
            index_links.add(os.path.normpath(os.path.join(root, target)))

    for page in pages:
        rel = os.path.relpath(page, root)
        text = open(page, encoding="utf-8").read()
        fm = read_front_matter(text)
        if fm is None:
            errors.append(f"{rel}: missing front matter")
        else:
            for key in REQUIRED_KEYS:
                if not fm.get(key):
                    errors.append(f"{rel}: front matter lacks '{key}'")
            if fm.get("type") and fm["type"] not in ALLOWED_TYPES:
                errors.append(f"{rel}: unknown type '{fm['type']}'")
        is_meta = fm is not None and fm.get("type") == "meta"
        if not is_meta:
            if "## Sources" not in text:
                errors.append(f"{rel}: no '## Sources' section")
            if "## Related" not in text:
                errors.append(f"{rel}: no '## Related' section")
        for m in LINK_RE.finditer(text):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path = target.split("#")[0]
            if not path:
                continue
            full = os.path.normpath(os.path.join(os.path.dirname(page), path))
            if not os.path.exists(full):
                errors.append(f"{rel}: broken link '{target}'")
            elif full in inbound and full != page:
                inbound[full] += 1
        if page != index_path and page not in index_links:
            errors.append(f"{rel}: not listed in index.md")

    for page, count in inbound.items():
        if count == 0 and page != index_path:
            warnings.append(f"{os.path.relpath(page, root)}: orphan (no inbound links)")

    for e in errors:
        print("ERROR", e)
    for w in warnings:
        print("WARN ", w)
    print(f"{len(pages)} pages, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
