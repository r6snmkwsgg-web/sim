# The Deep Stacks: building the 100 concept rooms

The concept gallery (100 rooms, 10 wings) is being built into the game. Each room below has a slug
(the room name and `r_<slug>.py`), a size (w x d x levels, kind), the concept, build notes, and at
least one **secret**. Concept art: `$CONCEPT_IMG/<n>.jpg` (n is the number in brackets; look at it
with the Read tool before you start a room).

Read `AUTHORING.md` first (the kit, the rules, the checker), including the **Additions for the Deep
Stacks** section at its end: water, secrets, effects, relaxed size budgets.

The aim is not a copy of the picture: it is a room that gives the same jolt when you walk into it,
built in stone, oak, brass and books, that is fun to explore, with somewhere hidden that rewards
people who poke around. Make it big and strange; keep it walkable and connected (`"ok":true`).

Rooms marked **engine** need portals, moving parts or gravity changes that the game does not have
yet; they are built later, after the engine work. Everything else is buildable now.

## Batch 1: scale gone wrong (giants)
- **giantdesk** [10] 4x4x2 giant. You come out onto the top of a writing desk the size of a city
  block: the desk top is the floor of the upper level, the room's lower level is the dark underside
  (legs like towers, drawers like buildings). A fountain pen lies across it like a fallen column (walk
  along it), an inkwell is a black lake (water, `bot` a few metres down, ink-dark tile), books stacked
  like skyscrapers you can climb by their overhanging covers. Doorways on the lower level lead up
  through a stair inside a hollow desk leg. Secret: a drawer standing open a crack; squeeze in, and it
  is a long dark wooden hall of giant pencils and a single lit candle.
- **chairmountain** [13] 4x4x2 giant. Every lost chair, piled into a mountain; a path winds up it
  (chairs as steps, a ramp collider under it). At the summit a single chair faces the view. Secret: a
  hollow inside the pile, a cave of chair legs reached through a gap on the far side, with a bed of
  cushions.
- **pencilforest** [19] 4x4x2 giant. Sharpened yellow pencils 12-15 m tall standing like pines (hex
  prisms with cones), a floor of cedar shavings (curled nocol pieces over a walkable floor). Secret: a
  hollowed pencil with a spiral stair up inside it to a lookout platform on its point, among the tips.
- **titanlamp** [17] 4x4x2 giant. A green banker's lamp as tall as a cathedral, shade glowing, over a
  colossal table with one enormous page. Climb the base plinth by stairs cut into it; a stair winds up
  the brass stem. Secret: inside the shade, a warm green-lit room hung with the chain (reached from
  the top of the stem).

## Batch 2: scale gone wrong (smaller)
- **onebook** [11] 2x2x2 tall. One open book fills the hall: the pages are hills you walk over (slope
  colliders), lines of text are shallow trenches; a ladder leans on the page edge. Secret: under the
  front cover, a low cave between the pages.
- **dollhouse** [12] 2x1x1 long. A normal hall with a one-tenth-scale library built into one side:
  knee-high doors, sugar-cube books; its main corridor is crawl height (crouch, 1.3 m). Secret: crawl
  deep enough and it opens into a full-size hidden room behind, where the dollhouse is the size of a
  real room again.
- **antgalleries** [14] 1x1x1 single. A wall honeycombed with hundreds of matchbox-sized lit
  libraries (instanced small cubes with tiny lamps). Secret: one niche among them is person-sized; it
  leads to a narrow room behind the wall.
- **cardcatalogue** [15] 4x2x2 giant. A card catalogue cabinet 14 m tall and 60 m long, brass pulls
  like doors, library ladders on rails. One drawer is open at floor level like a room: walk in among
  index cards the size of doors. Secret: that drawer runs back much further than it should, into a
  tunnel of cards to a small reading room at the far end.
- **keyhole** [16] 2x2x2 tall. An ornate brass keyhole-shaped opening in a wall on the upper level;
  beyond it a keyhole-shaped canyon lined with books steps down eight metres to the lower level.
  Secret: a ledge room halfway down, behind a false bookcase.
- **shrinkcorridor** [18] 2x1x1 long. A corridor that shrinks as you walk: doors, shelves and lamps
  all scale down with it, until you crouch, then crawl. Secret: at the very end a tiny door opens into
  a normal-sized, warm, hidden room (the joke is that it's bigger than the corridor was).
- **biggerinside** [2] 4x4x2 giant. A plain little room with a plain wooden door; behind the door, a
  hall so big the far end is blue with distance: skydome (e_skydome) strips in the coffered ceiling
  for clouds, reading tables in rows, bookcases to the horizon. Secret: a ladder up a far bookcase to
  a high catwalk that leads to a door in the "sky".
- **stairforest** [9] 4x4x2 giant. Hundreds of freestanding staircases rising from a parquet floor
  into fog, some upside down, some spiralling around each other. A few actually arrive at platforms.
  fx fog. Secret: one stair reaches a hidden reading platform in the fog with a desk and a lamp.

## Batch 3: weather indoors
- **rainroom** [20] 2x2x1 quad. A grand reading room where it always rains (fx rain), marble with
  puddles (shallow water 5 cm), books under glass bells. Secret: behind a curtain of water from a
  broken gutter, a dry room.
- **snowstacks** [21] 2x2x1 quad. Snow falling between tall shelves (fx snow), drifts against the
  bookcases (smooth white slopes, walkable), a lit fireplace far off. Secret: a snow cave dug into the
  biggest drift, with a candle.
- **tidelibrary** [22] 2x1x1 long. Half-flooded: sea water 0.6-1.2 m deep over the lower aisles
  (wading), barnacled lower shelves, arched windows. Secret: an underwater passage (swim) to an air
  pocket room.
- **cloudfloor** [23] 2x2x1 quad. The floor is cloud (soft white lumpy geometry, walkable), shelves
  float on it like ships. Secret: a gap in the clouds with a ladder down into a hidden room below the
  cloud (use the -2 m below-floor space).
- **thunderatrium** [24] 2x2x2 tall. A domed atrium with a black storm cloud trapped in the dome
  (dark lumpy geometry), a brass lightning rod on a reading desk (fx lightning). Secret: a ring
  gallery behind the dome's drum.
- **desertroom** [25] 2x2x1 quad. Dunes bury the reading room up to the table tops (smooth slopes),
  green lamps stick out of the sand, harsh sunlight through tall windows. Secret: a door half-buried
  at the foot of a dune into a sand-filled room below.
- **fogmaze** [26] 2x2x1 quad. A maze of tall bookcases in dense fog (fx fog). Secret: a false
  bookcase in a dead end leads to a lit room at the centre.
- **aurorastacks** [27] 2x2x1 quad. No ceiling: a night sky (e_skydome, fx aurora), snowy ground,
  stacks like standing stones. Secret: a shelter built of books, like an igloo, with a lamp.

## Batch 4: water, ice and growth
- **waterfallstair** [28] 2x2x2 tall. A grand staircase with a river running down it (stepped water
  volumes in a channel beside the treads), moss on the stone. Secret: a grotto behind the fall at the
  top.
- **frozenwave** [29] 2x2x2 tall. A breaking wave of turquoise ice frozen over a reading room; walk
  through the tunnel under its curl. Secret: ice steps up the back to a cave inside the crest.
- **breathinghall** [30] 2x1x1 long. Walls that bulge and curve like ribs of something breathing,
  shelves warped with them. fx breathe (later). Secret: a narrow gap between two bulges into an alcove.
- **rootcellar** [31] 2x2x1 quad. Huge pale roots through stone walls, books held in their tangles.
  Secret: a root tunnel (crawl) to a hollow.
- **orchard** [32] 2x2x1 quad. Trees in rows under a glass roof, books hanging like fruit, some
  fallen in the grass. Secret: a reading platform in the biggest tree, reached by a hidden ladder.
- **coralarchive** [33] 2x2x1 quad. Shelves turned to pink and white branching coral with book
  spines in it, blue light. Secret: a grotto inside the largest coral.
- **mosscathedral** [34] 2x2x2 tall. A cathedral nave overgrown with thick moss over pews and
  shelves, stained glass. Secret: a crypt under the altar.
- **hive** [35] 2x2x1 quad. Hexagonal wax cells, each a reading carrel with a chair and lamp, honey
  dripping down golden walls. Secret: the queen's chamber behind a wax wall.

## Batch 5: living library II, time I
- **mushroomstacks** [36] 2x2x1 quad. Dark aisles with glowing blue mushrooms (e_blue) growing out
  of damp shelves. Secret: a ring of giant mushrooms hiding a hollow under their caps.
- **growingstair** [37] 1x1x1 column (repeat=True). A spiral stair made of one living tree's
  branches climbing a tower through every floor (like the tower column; must line up at z=0 and z=8).
  Secret: a hollow in the trunk with a bed (one per copy is fine).
- **whaleribs** [38] 2x1x1 long. A corridor inside a whale's ribcage, bone ribs arching overhead,
  shelves between them, dim red light. Secret: the heart chamber.
- **flowerindex** [39] 2x2x1 quad. A glasshouse of flowers whose petals carry printed text. Secret: a
  potting shed behind vines.
- **frozenexplosion** [40] 2x2x1 quad. A reading room frozen a split second after something went
  off: books, chairs, glass hanging still in the air. Some debris is solid and makes stepping stones.
  Secret: climb the debris to the still centre of the blast, a small ring of calm high up.
- **daynight** [41] 2x1x1 long. One half of the hall is noon (sunlit windows), the other midnight
  (stars through windows, e_candle and e_amber only): split the light sources sharply. Secret: exactly
  on the line, a door into a room of permanent dusk.
- **ruinwing** [42] 2x1x1 long. Rooms in a row, each a thousand years older: pristine, worn,
  cracked, collapsed, a tree growing through the last. Secret: under the rubble of the last, a stair
  to a crypt.
- **clockroom2** [43] 2x2x1 quad. Thousands of clocks on every wall, pendulums (fx pendulums later).
  Secret: through the case of the tallest grandfather clock, a passage.

## Batch 6: time II, machines
- **hourglass** [44] 2x2x2 tall. Walk inside the upper bulb of a church-sized hourglass: books pour
  (sloped heap) toward the neck; go down through the neck into the lower bulb. Secret: a chamber in
  the base plinth.
- **candlehall** [47] 2x2x1 quad. Thousands of candles, wax built up into stalagmites and frozen
  waterfalls. Secret: a wax cave.
- **unfinished** [48] 2x2x1 quad. A room under construction: scaffolding (climbable), half-laid
  stone, empty shelves, tools. Secret: the scaffolding reaches a gap into an unfinished room above,
  still bare concrete.
- **seasons** [49] 2x1x1 long. A corridor of arches, each bay a season: snow, autumn leaves,
  blossom, summer haze. Secret: a fifth season behind the last arch.
- **pneumatic** [51] 2x2x1 quad. Brass pneumatic tubes in every direction, glass sections with
  books; one tube is big enough to walk through. Secret: that tube leads to a hidden sorting office.
- **presses** [52] 2x2x2 tall. Printing presses the size of locomotives, rivers of paper down the
  aisles (paper ribbons, walkable). Secret: the ink room under the biggest press.
- **sortingengine** [53] 2x2x1 quad. A sorting machine: conveyor belts (walkable), brass arms,
  shelves. Secret: the control booth up a service ladder.
- **typewriters** [57] 2x2x1 quad. A plain of typewriters on desks in rows to the walls. Secret: an
  alcove with one typewriter and one page (a plaque spot with its text).

## Batch 7: machines II, voids I
- **lighthouse** [58] 4x4x2 giant. A lighthouse tower rising out of a dark sea of shelves (fx beam
  later); climb the spiral stair inside. Secret: the lamp room at the top, and a keeper's room below it.
- **bridgevoid** [60] 4x2x2 giant. A narrow railed stone bridge with bookshelf parapets across a dark
  void. Secret: a ladder over the side to a room slung under the bridge.
- **hanginglib** [61] 4x4x2 giant. Bookcases hung on chains in the dark at different heights;
  planks and short jumps (gaps under 1 m) between them; railed where it matters, deliberate falls
  allowed past rails. Secret: the top of the tallest hanging case, a reading nook.
- **wellofstairs** [62] 1x1x1 column (repeat). A wide well with a spiral stair round the inside
  wall, landings with chairs every so often, the bottom a point of light. Secret: a landing with a
  small door into the wall (a cell with a bed).
- **floatislands** [63] 4x4x2 giant. Chunks of parquet floor, each with a desk and a lamp, floating
  in the dark; some close enough to step or jump between. Secret: the underside of the biggest island,
  a room hanging below it reached by a ladder through a hatch.
- **theedge** [64] 2x2x2 tall. The library just stops: the floor ends in a clean cut and past it is
  white nothing (e_sky wall, bright) and a drop behind a low rail. The last bookcase is sliced in
  half. Secret: step into the cut bookcase and find a stair going down the cut face.
- **starfloor** [65] 2x2x1 quad. A glass floor over a starfield (an e_skydome surface below the glass
  shows the night sky; fx starfloor later), tables and lamps calmly on it. Secret: a hatch in the
  glass to a platform below.
- **drain** [66] 2x2x1 quad. A circular room whose floor tilts toward a hole in the middle (railed);
  rugs and chairs sliding toward it. Secret: a ladder inside the drain to a ring room below.

## Batch 8: voids II, inversions
- **stairblack** [67] 2x2x2 tall. A grand stair descending into total darkness (no lights below
  halfway; faint e_dim at the bottom). Secret: a door halfway down.
- **catwalks** [68] 4x4x2 giant. A grid of iron catwalks over a deep drop, shelves hung under them.
  Secret: a maintenance room in the grid.
- **singlechair** [69] 2x2x1 quad. A huge black room, walls lost in dark, one chair under one lamp.
  Secret: a door in the far black wall that only shows when you are close (lit by an e_dim).
- **upsidedown** [70] 2x2x2 tall. Furniture, shelves and tables on the ceiling; chandeliers stand up
  from the floor. Secret: a chandelier's stem is a ladder up to a hidden niche on the "ceiling".
- **insideout** [73] 2x2x1 quad. A room turned inside out: a closed box in a dim hall with the backs
  of shelves facing out. Secret: the way into the box, where the room is the right way round.
- **ceilinggarden** [76] 2x2x2 tall. A garden growing from the ceiling: trees hanging down, a
  fountain pouring upward (a column of water material), benches on the ceiling. Secret: a stair to a
  balcony among the hanging roots.
- **symmetry** [77] 2x1x1 long. A perfectly symmetrical hall, mirrored down to the spines. One
  asymmetry is a secret door.
- **waterceiling** [78] 2x2x1 quad. A lake hangs overhead (a water volume from ~4.2 m to 7.2 m,
  surface facing down, fish shapes in it), a rope ladder up into it: you can swim up into the lake.
  Secret: an air pocket room at the top of the lake.

## Batch 9: wrong places
- **behindroom** [79] 2x1x1 long. A normal room; the narrow dusty world behind its bookcases (pipes,
  cables, a makeshift bed) is the secret.
- **beach** [80] 2x2x1 quad. A library door opens onto a grey beach under an overcast sky (e_skydome),
  a sea (water) and bookcases along the tide line. Secret: a beach hut.
- **subway** [81] 2x1x1 long. An empty tiled platform, shelves where the adverts are, a tunnel.
  Secret: a service door into a maintenance room in the tunnel.
- **motel** [82] 2x1x1 long. A motel corridor, patterned carpet, numbered doors, rooms each with a
  bed and one shelf. Secret: through one room's closet.
- **stadium** [83] 4x4x2 giant. An empty stadium at night, floodlights on, a book on every seat.
  Secret: the players' tunnel to a locker room.
- **wheatfield** [84] 2x2x1 quad. A golden wheat field inside four library walls (nocol wheat over a
  walkable floor), a desk in the middle, low sun (e_sky strip). Secret: a cellar hatch under the desk.
- **airportgate** [85] 2x1x1 long. Joined seats facing windows onto fog, a departures board.
  Secret: the jet bridge to a small room.
- **drainedpool** [86] 2x2x1 quad. A drained public pool, white tiles, shelves on the pool bottom,
  a very tall diving tower (climbable, railed). Secret: the pump room under the pool.

## Batch 10: wrong places II, traces of others
- **deadmall** [87] 4x4x2 giant. A dead mall atrium: escalators (static stairs), a fountain (water),
  every shop full of shelves, skylights. Secret: a back corridor behind a shop.
- **bigbedroom** [88] 2x2x1 quad. A child's bedroom at enormous scale, a kilometre-long bookcase.
  Secret: under the bed.
- **highway** [89] 2x1x1 long. Empty motorway lanes through a library hall, sodium lamps, shelves on
  the central reservation. Secret: a maintenance tunnel.
- **banquet** [90] 2x1x1 long. A table the length of the hall, fully laid, candles lit, chairs
  pushed back. Secret: the kitchen behind a service door.
- **waitingroom2** [91] 2x2x1 quad. Hundreds of chairs facing one door with a number display.
  Secret: what's behind the door.
- **classroom** [92] 2x2x1 quad. Desks for a thousand, a giant blackboard. Secret: the teacher's
  store room.
- **coatroom** [93] 2x1x1 long. Coats on hooks as far as you can see (walk through the coats: nocol).
  Secret: a passage behind the coats.
- **ballroom** [94] 2x2x1 quad. A ballroom mid-party, glasses, streamers. Secret: the musicians'
  gallery.
- **lostshrine** [95] 1x1x1 single. A stepped altar of candles and lost things. Secret: under the
  altar.
- **dormitory2** [96] 2x1x1 long. Rows of made beds, one unmade. Secret: a trapdoor under it.
- **bigtheatre** [97] 2x2x2 tall. A red velvet theatre; the stage set is an exact replica of a
  library room. Secret: backstage and the fly loft.
- **graffitistair** [98] 2x2x2 tall. A long stone stair between two levels, every surface covered in
  handwriting (dense line-marks texture: use many thin nocol strips). Secret: a landing room.
- **lastreader** [99] 2x2x1 quad. One lamp on, one chair out, an open book, tea steaming. Secret: a
  door behind the reader's shelf.

## Batch 11: engine rooms I (portals)
Read AUTHORING.md's "Engine features" section first: portals, mirrors, moving parts.
- **mobius** [0] 2x1x1 long. A long reading hall whose floor, walls and ceiling visibly twist along its
  length (a twisted ribbon of shelves overhead, lamps hanging at angles); the far end is a portal back
  onto the near end, so the hall never ends. The walkable floor stays level; the twist is architecture
  around you. Secret: behind the twist's tightest point, a gap into a still, level reading nook.
- **escherloop** [1] 2x2x2 tall. Four flights of stairs climbing round a square courtyard of shelves;
  the top of the fourth flight is a portal onto the bottom of the first (b is 8 m lower), so you can
  climb forever. Doorways on both levels connect by ordinary walking too. Secret: a door on a landing
  that only exists on the "second lap" side (reached by a short spur off a landing).
- **recursion** [3] 1x1x1 single. A gallery whose gilded frames are portals looking back into this same
  room from other angles (small portals, too high or small to walk through), one large low frame empty
  and dark: that one you can climb into (a real portal) and it leads to the secret, a small room hung
  with frames of its own. Keep to 3-4 portals.
- **klein** [4] 2x2x2 tall. A glass-and-brass bottle-shaped atrium sculpture you walk into; its neck
  curves up and back and "passes through its own wall": a portal at the top of the neck brings you out
  inside the bulb's base. Shelves line the inner surface. Secret: a brass capsule reading room in the base.
- **folded** [5] 2x1x1 long. A corridor folded like paper: sharp angled planes of wall and shelving at
  odd angles overhead, doors set sideways; at each fold a portal turns you 90° into the next leg (b turned),
  so the corridor folds back on itself more often than the room could hold. Secret: a door in a fold.
- **penrose** [6] 2x2x2 tall. A triangular balcony round a deep book-lined well, rising on all three
  sides; the end of the third side is a portal onto the start of the first (lower), so it rises forever.
  Railed. Secret: a hatch in the well wall below the balcony.
- **tesseract** [7] 1x1x1 single. A cubic study with a door on every wall; each door opens (portal) into
  the same study turned 90°/180°/270°, so walking through a door brings you into the study from another
  side. A hatch in the ceiling and floor are sealed (painted doors). Secret: the fifth door, behind a
  bookcase, leads to a normal corridor to a small room with the only window.
- **rotunda5** [8] 2x2x1 quad. A circular domed rotunda with an ambulatory ring corridor; walking round
  one way takes far longer than the other (a portal pair in the ring shortcuts one direction), and the
  floor pattern warps. Secret: under the central floor medallion, a stair to a crypt.
- **loopcorridor** [46] 2x1x1 long. An identical doorway repeats down a corridor; the last opens onto
  the first a few metres back (portal), so through it you see endless copies, a single book on the floor
  in each. Secret: one side door in the corridor leads out of the loop to a quiet reading room.
- **reflectstair** [75] 2x2x2 tall. A grand stair rising to a tall ornate mirror (a real mirror); beside
  it an identical frame is a portal onto a second stair that descends to the lower level. Secret: a
  landing halfway down with a small room.

## Batch 12: engine rooms II (motion, mirrors, effects)
- **clockwork** [50] 2x2x2 tall. A clockwork nave: huge brass gears in the walls turning (movers:
  swing/spin about horizontal axes, nocol, behind rails), and a great rotating floor disc (spin 'z',
  slow, collided: it carries you round). Secret: an engine room under the disc, reached by a stair.
- **elevator** [54] 2x2x2 tall. An ornate open brass lift cage (slide mover, delta 8 m, pause) in a
  shaft lined with shelves on every side, joining the two levels; stairs also connect them (checker).
  Secret: a door at mid-shaft reachable only from the cage roof? No: from a ledge the cage passes, a
  short jump from a rail gap on the stair.
- **orrery** [55] 2x2x1 quad. A domed hall with a great orrery: planets made of bound books on long
  arms turning about a brass sun (spin 'z' movers at different speeds); low arms are wide walkways you
  can step onto from a ring platform and ride. Secret: inside the sun.
- **waterwheel** [56] 2x2x1 quad. A water channel through the hall (water volume) turning a great wheel
  whose paddles are bookcases (spin about horizontal axis, nocol, railed off). Secret: the mill room
  behind the wheel.
- **dumbwaiters** [59] 1x1x1 single. A wall of small dumbwaiter hatches; several are lifts (slide
  movers) big enough to crouch in, rising 4 m to an upper gallery; stairs also go up. Secret: one hatch
  goes to a hidden room.
- **afterimage** [45] 2x1x1 long. A long plain gallery with fx afterimage over the whole floor (pale
  copies of you trail behind; one pale figure walks its own loop). Secret: the end of the other figure's
  loop is a door.
- **mirrorlake** [71] 2x2x1 quad. The floor of the hall is a still black mirror (a floor mirror) with a
  raised stone walkway grid across it; shelves and arches reflected. Secret: a door visible only in
  the reflection? Make it real: a door in a place you only notice via the reflection (under the walkway).
- **mirrorhall** [72] 2x1x1 long. A corridor of mirrors (2-3 large mirrors facing each other) with
  bookcases and lamps. Secret: one "mirror" is a portal instead, into a mirror-image room.
- **negative** [74] 2x2x1 quad. A library with fx negative over it: the picture inverts. Build it with
  strong contrast so the negative reads well: white shelves, black-glowing lamps (use dark emitters
  sparingly). Secret: a small room at its heart where the effect stops (the box excludes it).

