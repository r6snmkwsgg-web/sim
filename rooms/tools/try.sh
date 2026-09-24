#!/bin/sh
# Build a room and look at it:  rooms/tools/try.sh <name> [--nobake|--quick] [cams-json]
#   --nobake  geometry only, flat light (seconds): for layout and the walkability check
#   --quick   a fast low-sample bake (a minute or two): to judge the look
# Then: packs it (not into the catalogue), runs the walkability check, and takes screenshots.
# Output: rooms/out/check/<name>.png (walk map), rooms/out/shots/<name>.jpg (contact sheet)
cd "$(dirname "$0")/.." || exit 1
name=$1; mode=${2:---nobake}; cams=$3
python3 build.py "$name" $mode 2>&1 | grep -v "^$" | grep -v "Fra:\|Info: Baking" | tail -4 || exit 1
python3 pack.py "$name" --noindex || exit 1
node tools/check.mjs "$name" | grep -v '"unreachable\|"x":\|"z":\|"h":\|"n":\|"area":' 
node tools/shots.mjs "$name" $cams
