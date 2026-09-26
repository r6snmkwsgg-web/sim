#!/bin/sh
# Full-quality bakes, one after another, at low priority, each checked and packed (not into the catalogue).
#   rooms/tools/bake_queue.sh name [name...]      log: rooms/out/bake_queue.log
# A bake that crashes or comes out black is retried once.
cd "$(dirname "$0")/.." || exit 1
LOG=out/bake_queue.log
for r in "$@"; do
  for try in 1 2; do
    echo "=== $r try $try $(date +%H:%M:%S)" >> $LOG
    touch out/.bakestart
    nice -n 15 python3 build.py "$r" > out/$r.bakelog 2>&1
    [ out/$r.json -nt out/.bakestart ] || { echo "FAILED $r (no fresh output): $(tail -2 out/$r.bakelog | tr '\n' ' ')" >> $LOG; continue; }
    ok=$(python3 -c "
import json,sys
try:
    m=json.load(open('out/$r.json')); a=m['avg']; print('ok' if a.get('day',0)>0.002 and 'night' in a else 'bad %s'%a)
except Exception as e: print('bad',e)")
    if grep -q "built in" out/$r.bakelog && [ "$ok" = ok ]; then
      python3 pack.py "$r" --noindex >> $LOG 2>&1; echo "done $r" >> $LOG; break
    fi
    echo "FAILED $r ($ok): $(tail -2 out/$r.bakelog | tr '\n' ' ')" >> $LOG
  done
done
echo "=== queue finished $(date +%H:%M:%S)" >> $LOG
