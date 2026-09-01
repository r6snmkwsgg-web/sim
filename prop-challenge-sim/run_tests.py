#!/usr/bin/env python3
"""Minimal pytest-compatible runner.

pytest is the intended way to run this suite (``pytest -q``).  This script
exists so the tests can also be run in an environment with no third-party
packages installed at all -- it discovers ``test_*`` functions in
``tests/test_*.py`` and runs them with plain asserts.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import time
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))


def load(path):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main(argv):
    pattern = argv[1] if len(argv) > 1 else ""
    tests_dir = os.path.join(ROOT, "tests")
    files = sorted(f for f in os.listdir(tests_dir)
                   if f.startswith("test_") and f.endswith(".py"))
    passed, failures = 0, []
    t0 = time.time()
    for fname in files:
        mod = load(os.path.join(tests_dir, fname))
        names = [n for n in dir(mod) if n.startswith("test_")]
        for name in sorted(names):
            if pattern and pattern not in name:
                continue
            fn = getattr(mod, name)
            if not callable(fn):
                continue
            try:
                fn()
            except Exception:
                failures.append((fname, name, traceback.format_exc()))
                sys.stdout.write("F")
            else:
                passed += 1
                sys.stdout.write(".")
            sys.stdout.flush()
    dt = time.time() - t0
    print()
    for fname, name, tb in failures:
        print(f"\n{'=' * 70}\nFAIL {fname}::{name}\n{'-' * 70}\n{tb}")
    print(f"\n{passed} passed, {len(failures)} failed in {dt:.2f}s")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
