#!/bin/sh
# Full-quality bakes, one after another (they each use every core).
cd "$(dirname "$0")"
for r in "$@"; do
  echo "=== $r $(date +%H:%M:%S)"
  nice -n 10 python3 build.py "$r" 2>&1 | grep -v "^$" | grep -v "Fra:\|Info: Baking"
done
echo "=== all done $(date +%H:%M:%S)"
