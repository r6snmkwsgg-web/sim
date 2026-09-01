#!/usr/bin/env python3
"""
build.py -- assemble web/index.html from the template and the JS engine.

The engine has exactly one source of truth: web/propsim.js, which node runs
directly for web/verify.js.  Inlining it here (with the ES module `export`
keywords stripped) means the published page and the verified module are the
same code, rather than two copies that drift.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def build() -> str:
    engine = open(os.path.join(HERE, "propsim.js"), encoding="utf-8").read()
    # Strip module syntax: the page loads it as a classic script.
    engine = re.sub(r"^import\s+\{[^}]*\}\s+from\s+'[^']*';?\s*$", "",
                    engine, flags=re.M)
    engine = re.sub(r"^export\s+(const|function|let|var|class)\b",
                    r"\1", engine, flags=re.M)
    if "export " in engine:
        raise SystemExit("build: unhandled `export` left in propsim.js")

    bars = open(os.path.join(HERE, "realbars.js"), encoding="utf-8").read()
    ui = open(os.path.join(HERE, "ui.js"), encoding="utf-8").read()

    template = open(os.path.join(HERE, "artifact.template.html"),
                    encoding="utf-8").read()
    for marker, payload in (("/*__ENGINE__*/", engine), ("/*__BARS__*/", bars),
                            ("/*__UI__*/", ui)):
        if marker not in template:
            raise SystemExit(f"build: template is missing the {marker} marker")
        template = template.replace(marker, payload)
    return template


if __name__ == "__main__":
    out = os.path.join(HERE, "index.html")
    html = build()
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"{out}  {len(html):,} bytes")
