# Authoring rooms for the Dreaming Library

The game is a first-person walk through the endless library of *A Short Stay in Hell*, built like the
TikTok "poolrooms" (liminal, dreamlike, strange architecture) but made of **library materials**:
limestone, oak, polished marble, brass, velvet, and books everywhere. Rooms are generated here in
Python with Blender, their light is baked with Cycles, and the game streams them in as you walk.

Read these existing rooms first to see the kit in use: `r_courtyard.py` (simple, recent),
`r_crossing.py` (vaults, niches, stepped pit), `r_grand.py` (two levels, stairs, rails, gallery),
`r_backrooms.py` (maze), `r_tower.py` / `r_well.py` (shafts that repeat through every floor).
The kit itself is `lib.py`. **Do not edit `lib.py`, `pack.py`, `tools/`, or anything in `game/`.**
If you need a helper, put it in your room script (or in `kit_<yourbatch>.py` next to them).

## The world

- Space is a grid of **cells 16 m square** (`C`) and **levels 8 m tall** (`LH`). A room fills
  `w x d` cells and `levels` levels. Inside one level you have from the floor (z=0) to `TOP = 7.6`
  (the next level's floor slab sits above that).
- Blender axes: x east, y north, **z up**. A room occupies x 0..w*16, y 0..d*16, z -2..levels*8.
  Everything starts as solid; you carve space out with `R.cut(...)` and add things with `R.parts`.
- Walls: the room's shell is `T = 0.35` thick inside its boundary. **Every boundary cell edge on every
  level has a doorway** (3 m wide, arched, centred on the cell edge: at x = i*16+8 on the south/north
  walls, y = j*16+8 on the west/east walls). `R.sockets()` cuts them. Any room can sit next to any
  other, so these doorways must stay where they are.
- Kinds (derived from the size): `single` 1x1x1, `long` 2x1x1, `quad` 2x2x1, `tall` 2x2x2,
  `column` 1x1x1 with `repeat=True` (stacked through every level, like the well), `giant`
  (w and d even, up to 8; levels 2 or 4).
- The player: radius 0.3 m, eye height 1.62, standing height 1.78, crouching 1.15. Steps up to
  0.55 m are walked; higher needs stairs. A drop over 4.2 m starts a fall, and landing faster than
  11 m/s kills (about 6 m). Jumping clears about 1 m.

## Building a room

```python
from lib import *

def make():
    R = Room('myroom', 1, 1, res=1024)          # name, w, d, levels=1, repeat=False, res (lightmap px)
    R.sockets(floor='floor', wall='tile')         # the doorways (skip=((side, i, level), ...) to seal one)
    R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, C - T + 0.02, TOP, 'tile', bottom='floor', top='plaster'))
    ...
    R.spot('probe', 8, 8, 1.7)                    # REQUIRED: where the reflection probe sits (open space)
    R.meta.update(label='The Something', weight=8, blurb='One or two sentences, second person.')
    R.meta['box'] = [[T, 0, T], [C - T, TOP, C - T]]   # interior bounds, GAME axes: [x, height, y]
    return R
```

Save it as `rooms/r_<name>.py` with `Room('<name>', ...)` matching.

### Tools (run from anywhere; the game server on :8812 is already running)

```
rooms/tools/try.sh <name> --nobake      # geometry + flat light, ~10-40 s: iterate layout with this
rooms/tools/try.sh <name> --quick       # fast low-sample light bake, 1-4 min: judge the look
rooms/tools/try.sh <name> --quick '[[x,y,z,yaw,pitch],...]'   # your own camera views
```

It builds, packs (not into the catalogue), runs the **walkability check** and takes screenshots:
- `rooms/out/check/<name>.png`: a top-down map per level. Green = reachable (brighter = higher),
  red = **trap** (you can get in but not out), grey = unreachable (often just the inside of a solid
  block or the top of a bookcase: fine), yellow = a fall of more than 4.2 m, blue squares = doorways.
- `rooms/out/shots/<name>.jpg`: a contact sheet of views (from each corner and one high up).
  Camera: game axes x east, **y up**, z = Blender y; yaw 0 looks toward -z, pitch + looks up.
- The JSON report must end `"ok":true`: no `door_problems`, no `traps`, no `bad_nav`. `falls` must
  be null unless the room is meant for falling (columns, some giants) and the drop is behind a rail.

Never run a full bake (no flag): the orchestrator does all final bakes. Look at your screenshots
with the Read tool and iterate until the room is **striking**.

### The kit (lib.py)

Geometry is built from `Geo` pieces; all take metres, Blender axes.
- `box(x0,y0,z0,x1,y1,z1, m, top=, bottom=, sides=, skip=('-z',...))`
- `prism(profile, 'x'|'y', a0, a1, edge_mats, cap=)`: extrude a (p, z) profile along x or y
- `arch_profile(c, w, z0, jamb, segs, rise=None)` + `arch_mats(n, floor, wall)`: arched openings
- `cyl(cx,cy,z0,z1,r,segs, side=,top=,bottom=,caps=, a0=,a1=)`, `sphere(cx,cy,cz,r,segs,rings,m,lower=)`
- `ring(cx,cy,z0,z1,r0,r1,segs, top=,bottom=,inner=,outer=, a0=,a1=)`: annulus / sector slab
- `helix(cx,cy,r0,r1,z0,rise_per_turn,a0,a1,thick,segs, top=,side=,bottom=)`: spiral ramp band
- `poly_prism(pts, z0, z1, side=,top=,bottom=)`: vertical prism from a 2D polygon
- `slope_box(x0,x1,y0,y1, bot0,bot1, top0,top1, m)`: a box along x whose bottom/top slope
- `stairs(x0,y0,z0,width,n,rise,run,axis, m, riser, side)`: solid steps (visual)
- `balustrade(x0,y0,x1,y1, z, h=1.0, m='tile', cap='brass')`: a solid rail with a brass top
- `.xform(angle, tx, ty, tz)` rotates a piece about Z then moves it; `Geo().add(g)` merges.

Room methods:
- `R.cut(g)`: carve space (boolean difference from the solid). Surfaces take the cutter's materials.
- `R.parts.add(g)`: solid additions (collided). `R.nocol.add(g)`: drawn, not collided.
  `R.col.add(g)`: invisible colliders (ramps, invisible walls).
- `R.flight(x0,y0,z0,width,n,rise,run,axis, m, riser, side)`: **use this for stairs**: visible steps plus
  an invisible ramp so walking up is smooth. `axis` is the climb direction; (x0,y0) is the foot's
  corner. Risers 0.15-0.25, run 0.28-0.32. Its sides are open: add walls or balustrades.
- `R.shelf(x, y, z, length, dirn, rows, row_h=0.42, depth=0.34, frame='wood', back=, sides=, crown=, solid=True)`:
  a bookcase facing dirn ('+x','-x','+y','-y' or radians); (x, y) is its back-left corner as seen from
  the front. The game fills every row with real, readable books. `solid=False` = a **false bookcase**
  you can walk straight through (for secret passages).
- `R.light(g)`: an emitter (lights the bake and glows in the game). Use emitter materials below.
- `R.pool(x0,y0,x1,y1, depth, m=, steps=True)` / `R.round_pool(cx,cy,r,depth, m=)`: sunken floors /
  pits, stepped 0.3 m down per 0.45 m (no water in this library).
- `R.spot(kind, x, y, z, face)`: `probe` (required), `sit` (seat top, facing), `read`, `bed`, `kiosk`
  (a food kiosk, rest areas only), `plaque`.
- `R.navpt(x, y, z=0)` + `R.link(a, b, ...)`: a walking graph for the people who wander the library.
  Give every room a loop or two through its open floor (points at least 0.6 m from walls, straight
  links that don't cross walls, rails or furniture).
- `R.meta`: `label` ('The X'), `blurb` (shown once, first time you enter: one or two sentences,
  second person, present tense, eerie or wry), `weight` (how common: common 8-12, uncommon 3-6,
  rare 1-2), `box` (see above), `sealed` (list of `(side, i, level)` doorways you deliberately
  skipped in `sockets`, e.g. `[('N', 0, 0)]`; the checker then ignores them), `secret` (True).

### Materials

Surfaces: `tile` (becomes warm limestone in courses), `floor` (oak parquet), `terrazzo` / `mosaic`
(polished checkered marble), `plaster` (cream), `wood` / `oak` / `walnut` (bookcases, furniture),
`brass`, `bronze`, `gilt`, `iron` (dark metal), `velvet` (deep red cloth), `carpet` (deep red),
`damask` (dark green wallpaper), `green` (library green paint), `oxblood`, `ivory` (cream paint),
`slate` (dark stone), `blackboard`, `leather`, `black`, `bed`, `kiosk`, `chrome`.

Emitters (lights): `e_sky` (warm skylight), `e_panel` (ceiling panel), `e_lamp` (warm bulb),
`e_dim` (weak bulb, for dark rooms), `e_fluor` (low warm lamps), `e_candle` (candles, stay lit
after lights-out), `e_amber` (night lamps), `e_exit` (little green signs), `e_red` / `e_blue` /
`e_green` (stained glass), `e_skydome` (a painted sky: the game draws a real-looking sky with
clouds on it, so a big plane of it overhead reads as open air), `e_pool` (warm step lights).

Light size matters: a 2x2 m panel is bright, a 0.15 m sphere is a small point. Rooms should have
real contrast: pools of light and shadow, not flat brightness, but nothing pitch black where you
walk. Every room needs a few lights that stay on after lights-out (`e_candle`, `e_amber`, `e_exit`,
`e_pool`) if it is meant to be walked at night; not required.

## Rules

1. **Doorways all connect** (checker `ok:true`). Every live doorway reaches every other one.
2. **No traps**: nowhere you can walk or fall into that you cannot walk out of.
3. **Rails on every edge with a drop over 1 m** (balustrades ~1.0 m tall, or brass rails at 0.95 m
   with posts at most 1.2 m apart). Deliberate falls only in columns/giants, and only past a rail.
4. **Headroom 2.1 m** on walkways; crawl spaces (1.3 m) only in secret rooms.
5. Keep the doorways' approaches clear: nothing within 2 m inside each doorway.
6. **Size budget** (printed by pack): single <= 350 KB, long/quad <= 700 KB, tall <= 1100 KB,
   giant <= 2500 KB. Keep segment counts sensible (cyl 12-32 for small things), avoid thousands of
   tiny parts. `res`: 1024 for singles, long, columns; 2048 for quad, tall, giant.
7. Books everywhere it makes sense: this is the library. But not every wall: variety.
8. Upper-level doorways in multi-level rooms must be reachable (galleries, stairs) or sealed.
9. Columns (`repeat=True`) must line up with the copy above and below (z=0 and z=8 match).
10. Name, label and blurb in keeping with the book's tone: quiet, uncanny, occasionally funny.

## The aesthetic

Think: the poolrooms' smooth, too-regular, too-quiet spaces; architecture that doesn't quite make
sense (stairs to nowhere, doors in walls too high to reach, rooms at the wrong scale, endless
repetition, a room that is only slightly wrong); but in a library of stone, wood and brass, warmly
lit, with books on everything. Strong silhouettes and depth: arches receding, rows of columns,
long sightlines, big voids, pools of light. Every room should make a player stop and look.

## Additions for the Deep Stacks (the concept rooms, see CONCEPTS.md)

**Size budgets are relaxed** (the game is hosted without the old size cap): single <= 700 KB,
long/quad <= 1400 KB, tall <= 2200 KB, giant <= 5000 KB. `res` 1024 for singles and columns, 2048 for
everything else. Still keep geometry sensible: instance-like repetition (hundreds of clocks,
typewriters, chairs) should be simple boxes, a few dozen faces each.

**Water** (wade in it, swim in it; the game draws the surface and handles swimming):
```python
R.water.append(dict(x0=..., y0=..., x1=..., y1=..., top=0.0, bot=-1.2))   # a box of water, Blender axes
R.water.append(dict(cx=..., cy=..., r=..., top=..., bot=...))                # a round one
```
Carve the basin with `R.cut` so there is a floor at `bot`. Water may hang in the air (a lake overhead)
if you give it a basin's worth of walls; you swim up into it. Water deeper than 1.4 m is swimming.

**Secrets**: every concept room has at least one hidden place. Build it for real (a false bookcase
`solid=False`, a crawlspace at crouch height 1.15-1.3 m, a hatch and ladder, a gap you only see from
one angle, a drawer that goes too far). It must be reachable and walkable: the checker's `"ok":true`
still applies, and nothing in it may be a trap. Register it so the game can notice when someone finds it:
```python
R.meta.setdefault('secrets', []).append({'at': [x, y, z], 'r': 1.5, 'name': 'The Snow Cave',
    'text': 'One or two sentences, second person, for when you find it.'})
```
`at` is a point inside the secret space (Blender axes, z = floor height there), `r` how close counts.
Put something in it worth finding: a lamp, a bed, a view, a desk with an open book, a `plaque` spot.

**Effects**: things the lightmap can't do (falling rain and snow, fog, drifting dust, lightning, an
aurora, a sweeping beam) are drawn by the game from a list in the room's metadata; the game is
getting support for these, so declare them now:
```python
R.meta.setdefault('fx', []).append({'type': 'rain', 'box': [x0, y0, z0, x1, y1, z1]})
```
Types: `rain`, `snow`, `fog` (add `'density': 0.02-0.12`), `dust` (motes in light), `embers`,
`lightning` (add `'at': [x, y, z]`, where it strikes), `aurora` (put the box where the sky is),
`beam` (a lighthouse beam: `'at'`, `'r'` radius), `breathe` (walls that swell), `pendulums`, `starfloor`.
Build the room so it already works and looks right without them.

**Names**: new room names must not clash with existing ones (`ls rooms/r_*.py`). Use the slug given
in CONCEPTS.md. Helpers go in `kit_<batch>.py` (e.g. `kit_h1.py` for batch 1).

## Engine features: moving parts, portals, mirrors

These exist in the game now; use them for the engine rooms (and anywhere they make a room better).

**Moving parts** (lib.py `R.mover`): geometry that moves in the game. It is baked where it stands.
```python
M = R.mover('spin', pivot=(8, 8, 0), axis='z', speed=0.3)            # turns about a vertical axis, rad/s
M = R.mover('swing', pivot=(8, 8, 6), axis='x', amp=0.4, period=6)   # rocks back and forth (a pendulum)
M = R.mover('slide', delta=(0, 0, 8.0), period=20, pause=4)          # there and back: lifts, drawers, rails
M.parts.add(...)   # collided: you can stand on it and it carries you (only level movers: spin about 'z', slide)
M.nocol.add(...)   # drawn only
M.col.add(...)     # invisible colliders that move with it
```
`phase` (0..1) offsets its timing. Movers that tilt (spin/swing about 'x' or 'y') are drawn but never
collided: keep people out of their way with rails. A lift must have somewhere safe at both ends, and the
room must pass the checker with every mover in its rest position (the checker does not animate them).

**Portals**: a rectangle that shows, and leads to, another rectangle in the same room. Walk through
and you come out of the other one, moving the same way relative to it.
```python
R.meta['portals'] = [{'a': {'c': [26, 8, 0], 'n': [1, 0, 0], 'w': 3.2, 'h': 3.5},
                      'b': {'c': [6.4, 8, 0], 'n': [1, 0, 0], 'w': 3.2, 'h': 3.5}}]
```
`c` is the middle of the rectangle's bottom edge (Blender axes), `n` the direction you walk when you go
in at `a` and the direction you come out at `b`, `w`/`h` its size. Pairs work both ways. The rectangles
must stand in an opening with at least 0.8 m of free, walkable floor behind them (the recess the player
steps into while crossing), and nothing may block the far side of `b`. `b` may be higher or lower than
`a` (stairs that climb forever), or turned (a door that brings you back in sideways). Only the nearest
two portals in view are rendered at a time; keep a room to a handful. Portals are extras: the checker
does not know about them, so the room must still pass without them (every doorway connected by
ordinary walking; a portal can be a shortcut or a loop, not the only way).

**Mirrors**: a rectangle showing the room reflected.
```python
R.meta['mirrors'] = [{'c': [9, 15.3, 0], 'n': [0, -1, 0], 'w': 4.0, 'h': 3.6}]   # n faces the viewer
```
Put a solid surface (a wall, a frame's back) at the mirror plane; the image is drawn just in front of it.
A floor mirror (`n` = [0, 0, 1], `c` on the floor, `w` along x, `h` along y) makes a still, black-glass floor.

**More effects** for `R.meta['fx']`: `negative` (inside the box the picture inverts, like a photographic
negative), `afterimage` (inside the box, pale copies of you trail a few seconds behind, and one pale figure
that is not you walks its own loop).
