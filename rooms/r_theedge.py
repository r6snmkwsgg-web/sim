"""The Edge: two floors of an ordinary library, and then the library stops. The upper hall's floor ends in a
clean cut at x = 20; past a low rail there is white nothing, bright, going down to a white floor and up to a
white ceiling. The vault's ribs are sliced off in mid-air, a chandelier is half a chandelier, and the last
bookcase along the edge is cut in half lengthwise. One bay of that bookcase is false: inside, a stair goes
down within the cut face, past slits full of white, to the floor of the nothing, where a chair is waiting.
A door from the lower hall opens onto the nothing too."""
from kit_h7 import *

W = D = 32.0
EX = 20.0                     # the cut
LX = 16.9                     # the lower hall's east wall (between it and the cut: the stair shaft)
UP = LH                       # upper hall floor
BX0, BX1, BY0, BY1 = 17.4, EX, 18.0, 28.4      # the cut bookcase (a hollow block)
SX0, SX1 = 17.42, 19.62       # the secret stair shaft (the whole inside of the cut bookcase)
N_, RISE, RUN = 40, 0.2, 0.3
SY_TOP = 26.4                 # the stair's top (z = 8), descending -y
SY_BOT = SY_TOP - N_ * RUN    # 14.4, z = 0
MX0, MX1, MY0, MY1 = 14.8, 16.85, 3.0, 15.0   # the main stair (lower -> upper), climbing +y
SEAL = [('E', 0, 0), ('E', 1, 0), ('E', 0, 1), ('E', 1, 1), ('S', 1, 0), ('N', 1, 0), ('S', 1, 1), ('N', 1, 1)]


def make():
    R = Room('theedge', 2, 2, levels=2, res=2048)
    seal(R, SEAL, floor='floor', wall='tile')
    hi = R.hi
    R.cut(box(T - 0.02, T - 0.02, 0, LX, D - T + 0.02, TOP, 'tile', bottom='floor', top='plaster'))        # lower hall
    R.cut(box(T - 0.02, T - 0.02, UP, EX, D - T + 0.02, hi - 0.1, 'tile', bottom='floor', top='plaster'))  # upper hall
    R.cut(box(EX, T - 0.02, 0, W - T + 0.02, D - T + 0.02, hi - 0.05, 'plaster', bottom='plaster', top='plaster'))  # nothing
    nothing(R)
    main_stair(R)
    ribs(R)
    upper(R)
    lower(R)
    secret_stair(R)
    fx(R, 'dust', [EX - 6, T, UP, EX + 2, D - T, UP + 6])
    navloop(R, [(3, 3), (13.5, 2.2), (13.5, 16.5), (13.5, 29.5), (3, 29.5), (2.2, 16)])
    navloop(R, [(2.5, 2.5), (13.2, 2.5), (19.0, 16.5), (16.5, 29.8), (2.5, 29.8), (2.5, 16)], z=UP)
    R.link(1, 2)
    return finish(R, 'The Edge', weight=2, probe=(15.0, 20.0, UP + 2.0), top=hi,
                  blurb='The library stops here, cleanly, as if someone had cut it with a very sharp knife. Past the rail there is nothing, and the nothing is very bright.')


def nothing(R):
    """White nothing: every face of the void glows (a cold, even white that stays on at night), and a clean section line."""
    hi = R.hi
    R.light(box(EX + 0.02, T, 0.0, W - T, D - T, 0.02, 'e_kiosk'))
    R.light(box(W - T - 0.03, T, 0.02, W - T - 0.01, D - T, hi - 0.06, 'e_kiosk'))
    R.light(box(EX, T + 0.01, 0.02, W - T - 0.03, T + 0.03, hi - 0.06, 'e_kiosk'))
    R.light(box(EX, D - T - 0.03, 0.02, W - T - 0.03, D - T - 0.01, hi - 0.06, 'e_kiosk'))
    R.light(box(EX, T, hi - 0.09, W - T, D - T, hi - 0.07, 'e_kiosk'))
    # the section through the upper floor: parquet, a dark joint, the slab
    R.nocol.add(box(EX - 0.01, T, UP - 0.04, EX + 0.004, D - T, UP, 'parquet'))
    R.nocol.add(box(EX - 0.01, T, UP - 0.12, EX + 0.004, D - T, UP - 0.1, 'walnut'))
    R.nocol.add(box(EX - 0.01, T, TOP - 0.02, EX + 0.004, D - T, TOP, 'slate'))
    # the low rail along the cut (not in front of the cut bookcase)
    for (a, b) in ((T + 0.1, BY0), (BY1, D - T - 0.1)):
        rail(R, EX - 0.06, a, EX - 0.06, b, UP, h=0.95)
    # a chair on the floor of the nothing, facing more nothing, and a lamp beside it
    c = chair(26.0, 13.0, 0.0, frame='walnut'); R.parts.add(c)
    R.spot('sit', 26.0, 13.0, 0.48, 0.0)
    R.parts.add(cyl(26.9, 13.6, 0, 0.6, 0.18, 12, side='walnut', top='walnut'))
    desk_lamp(R, 26.9, 13.6, 0.6)
    open_book(R, 26.85, 13.25, 0.6, 0.3)


def main_stair(R):
    """A plain stone flight up the lower hall's east wall into the upper hall, railed."""
    n = N_
    gflight(R, MX0, MY0, 0, MX1 - MX0, n, RISE, RUN, '+y', m='terrazzo', riser='tile', side='tile')
    gflight_rail(R, MX0, MY0, 0, MX1 - MX0, n, RISE, RUN, '+y', which=(0,), m='tile', cap='brass')
    # the slot in the upper floor over it, railed on three sides
    R.cut(box(MX0 - 0.2, MY0, TOP - 0.1, MX1 + 0.05, MY1, UP + 0.1, 'tile', bottom='floor'))
    brail(R, MX0 - 0.27, MY0 - 0.07, MX0 - 0.27, MY1 - 1.2, UP)
    brail(R, MX0 - 0.34, MY0 - 0.07, MX1 + 0.12, MY0 - 0.07, UP)
    brail(R, MX1 + 0.12, MY0 - 0.07, MX1 + 0.12, MY1, UP)


def rib_profile(y, zs=11.0, R0=20.0, rise=4.0, depth=0.55, x0=T, xcut=EX):
    """A segmental arch springing from the west wall, sliced at the cut. Returns (x, z) closed profile."""
    half = math.sqrt(R0 * R0 - (R0 - rise) ** 2)
    xc = x0 + half
    zc = zs + rise - R0
    pts_o, pts_i = [], []
    n = 16
    for k in range(n + 1):
        x = x0 + (xcut - x0) * k / n
        pts_i.append((x, zc + math.sqrt(max(0.0, R0 * R0 - (x - xc) ** 2))))
        pts_o.append((x, zc + math.sqrt(max(0.0, (R0 + depth) ** 2 - (x - xc) ** 2))))
    return pts_i, pts_o


def ribs(R):
    """Transverse ribs over the upper hall, springing from pilasters on the west wall and sliced off in the
    air at the cut, their sections showing clean and pale."""
    top = R.hi - 0.12
    for y in (2.0, 6.0, 10.0, 14.0, 18.0, 22.0, 26.0, 30.0):
        pi_, po = rib_profile(y)
        prof = [(x, min(z, top)) for (x, z) in pi_] + [(x, min(z, top)) for (x, z) in reversed(po)]
        # extrude along y: prism takes (p, q) = (x, z) when axis is 'y'
        R.nocol.add(prism(prof, 'y', y - 0.25, y + 0.25, 'tile', cap='tile'))
        R.nocol.add(box(EX - 0.004, y - 0.25, pi_[-1][1], EX + 0.002, y + 0.25, min(po[-1][1], top), 'plaster'))
        # the pilaster under it
        R.parts.add(box(T - 0.02, y - 0.3, UP, T + 0.35, y + 0.3, 11.0, 'tile', skip=('-z',)))
        R.parts.add(box(T - 0.02, y - 0.38, 10.7, T + 0.45, y + 0.38, 11.0, 'tile'))


def upper(R):
    """Stacks running in from the west wall, a long table by the edge, lamps, and the half chandelier."""
    for y in (4.2, 12.0, 20.2, 28.0):
        stack(R, 'x', y, 1.0, 10.5, UP, rows=9, frame='walnut')
    # books on the south and north walls between the stacks' ends and the cut
    sh(R, '+y', T, 11.0, EX - 0.3, z=UP, rows=9, frame='walnut')
    sh(R, '-y', D - T, 11.0, EX - 0.3, z=UP, rows=9, frame='walnut')
    # the reading tables
    reading_table(R, 12.2, 17.0, 13.4, 27.0, lamps=4, z=UP, axis='y')
    reading_table(R, 11.3, 2.4, 12.5, 9.5, lamps=2, z=UP, axis='y')
    # lamps down the hall, and a chandelier hanging exactly on the cut: its eastern half is not there
    for y in (8.0, 16.0, 24.0):
        for x in (6.0, 13.5):
            hanging(R, x, y, R.hi - 0.12, UP + 3.4, r=0.5, e='e_lamp', shade='green', segs=16)
    for y in (8.0, 24.0):
        half_chandelier(R, EX, y, UP + 4.2, R.hi - 0.1)
    # a rug sliced by the edge, and a book face down on the last board of floor
    rug(R, 15.0, 5.0, EX - 0.001, 11.0, UP, m='carpet')
    open_book(R, 19.4, 13.0, UP, 0.6)
    for (x, y) in ((1.6, 1.6), (1.6, D - 1.6)):
        R.light(sphere(x, y, UP + 1.4, 0.1, 10, 5, 'e_amber'))
        R.nocol.add(cyl(x, y, UP, UP + 1.3, 0.02, 6, side='brass', caps=False))


def half_chandelier(R, x, y, z, top, r=1.1, n=10):
    R.nocol.add(cyl(x - 0.01, y, z + 0.3, top, 0.015, 4, side='iron', caps=False))
    R.nocol.add(ring(x, y, z - 0.03, z + 0.03, r - 0.05, r + 0.05, n, top='brass', bottom='brass', inner='brass', outer='brass', a0=math.pi / 2, a1=3 * math.pi / 2))
    for k in range(n + 1):
        a = math.pi / 2 + math.pi * k / n
        px, py = x + r * math.cos(a), y + r * math.sin(a)
        R.nocol.add(beam((x, y, z + 0.3), (px, py, z), 0.02, 'brass'))
        if 0 < k < n:
            R.light(sphere(px, py, z + 0.12, 0.07, 8, 4, 'e_lamp'))
    R.nocol.add(box(x - 0.12, y - 0.12, z - 0.2, x, y + 0.12, z + 0.35, 'brass'))


def lower(R):
    """An ordinary lower hall: cases on the walls, stacks, tables. On its east wall a door onto the nothing."""
    for y in (4.0, 12.0, 20.0, 28.0):
        stack(R, 'x', y, 2.4, 9.6, 0.0, rows=11, frame='walnut')
    sh(R, '+y', T, 0.8, 6.2, rows=12, frame='walnut')
    sh(R, '+y', T, 9.8, MX0 - 0.3, rows=12, frame='walnut')
    sh(R, '-y', D - T, 0.8, 6.2, rows=12, frame='walnut')
    sh(R, '-y', D - T, 9.8, LX - 0.3, rows=12, frame='walnut')
    sh(R, '+x', T, 0.8, 6.2, rows=12, frame='walnut')
    sh(R, '+x', T, 9.8, 22.2, rows=12, frame='walnut')
    sh(R, '+x', T, 25.8, D - 0.8, rows=12, frame='walnut')
    sh(R, '-x', LX, MY1 + 1.5, 25.8, rows=12, frame='walnut')
    reading_table(R, 11.6, 17.0, 12.8, 29.0, lamps=4, axis='y')
    reading_table(R, 11.6, 4.0, 12.8, 13.0, lamps=3, axis='y')
    for y in (8.0, 16.0, 24.0):
        for x in (6.0, 12.2):
            hanging(R, x, y, TOP - 0.1, 3.4, r=0.45, e='e_lamp', shade='green', segs=16)
    for y in (4.0, 12.0, 20.0, 28.0):
        for x in (6.0, 12.2):
            R.light(box(x - 1.2, y - 0.5, TOP - 0.14, x + 1.2, y + 0.5, TOP - 0.11, 'e_panel'))
    # the door onto the nothing
    dy0, dy1 = 26.6, 28.0
    R.cut(box(LX - 0.05, dy0, 0, EX + 0.05, dy1, 2.3, 'tile', bottom='floor', top='tile'))
    for s in (dy0 - 0.1, dy1):
        R.parts.add(box(LX - 0.12, s, 0, LX, s + 0.1, 2.4, 'walnut'))
    R.parts.add(box(LX - 0.12, dy0 - 0.1, 2.3, LX, dy1 + 0.1, 2.45, 'walnut'))
    door = box(0, 0, 0, 0.05, dy1 - dy0 - 0.04, 2.26, 'oak')
    door.add(box(0.05, 0.12, 0.2, 0.07, dy1 - dy0 - 0.16, 1.0, 'walnut'))
    door.add(box(0.05, 0.12, 1.2, 0.07, dy1 - dy0 - 0.16, 2.05, 'walnut'))
    door.xform(-1.2, LX + 0.02, dy0 + 0.02, 0)
    R.nocol.add(door)
    R.parts.add(box(LX - 0.1, dy0 + 0.25, 2.55, LX - 0.02, dy1 - 0.25, 2.8, 'black'))
    R.light(box(LX - 0.12, dy0 + 0.3, 2.58, LX - 0.1, dy1 - 0.3, 2.77, 'e_exit'))


def secret_stair(R):
    """The cut bookcase: a hollow block standing on the edge, its west face full of books, its east half
    sliced away (the books there face the nothing). One bay on the west is false. Inside, a stair goes
    down within the cut face to the floor of the nothing."""
    z = UP
    rows = 10
    Hh = rows * 0.42 + 0.035 + 0.08
    top = z + Hh
    # the west face (facing the hall), with a false bay at the north end
    fy0, fy1 = 26.55, 27.85
    sh(R, '-x', BX0, BY0 + 0.1, fy0, z=z, rows=rows, frame='walnut')
    sh(R, '-x', BX0, fy0, fy1, z=z, rows=rows, frame='walnut', solid=False)
    sh(R, '-x', BX0, fy1, BY1 - 0.1, z=z, rows=rows, frame='walnut')
    # the east face: books facing the nothing, the section of the bookcase
    sh(R, '+x', EX - 0.36, BY0 + 0.1, BY1 - 0.1, z=z, rows=rows, frame='walnut')
    # the block's ends (with books on them) and its roof
    sh(R, '-y', BY0, BX0 - 0.34, EX - 0.02, z=z, rows=rows, frame='walnut')
    sh(R, '+y', BY1, BX0 - 0.34, EX - 0.02, z=z, rows=rows, frame='walnut')
    R.parts.add(box(BX0 - 0.38, BY0 - 0.38, top, EX, BY1 + 0.38, top + 0.12, 'walnut'))
    R.parts.add(box(BX0 - 0.02, BY0 - 0.02, z, BX0 + 0.02, fy0, top, 'walnut', skip=('-z',)))
    R.parts.add(box(BX0 - 0.02, fy1, z, BX0 + 0.02, BY1 + 0.02, top, 'walnut', skip=('-z',)))
    # the shaft: under the block it opens up into it; south of it, under the upper floor
    R.cut(box(SX0, SY_BOT - 1.8, 0, SX1, SY_TOP + 0.02, TOP - 0.6, 'plaster', bottom='oak', top='plaster'))
    R.cut(box(SX0, BY0 + 0.02, TOP - 0.7, SX1, SY_TOP + 0.02, UP + 0.05, 'plaster', bottom='oak', top='plaster'))
    R.flight(SX0, SY_BOT, 0.0, SX1 - SX0, N_, RISE, RUN, '+y', m='oak', riser='walnut', side='walnut')
    # slits in the skin between the shaft and the nothing, one every few steps, at eye height
    for k in range(4, N_, 5):
        yy = SY_TOP - (k + 0.5) * RUN
        zz = UP - (k + 1) * RISE
        R.cut(box(SX1 - 0.05, yy - 0.08, zz + 1.1, EX + 0.05, yy + 0.08, zz + 2.0, 'plaster'))
    # the way out at the bottom, east onto the floor of the nothing
    R.cut(box(SX0, SY_BOT - 1.8, 0, EX + 0.05, SY_BOT - 0.4, 2.3, 'plaster', bottom='oak', top='plaster'))
    # a candle on the landing, a lamp halfway, and a plaque at the foot
    R.light(sphere(SX0 + 0.25, fy1 - 0.2, UP + 2.2, 0.07, 8, 4, 'e_candle'))
    for k in (12, 28):
        yy = SY_TOP - k * RUN
        bulb(R, (SX0 + SX1) / 2, yy, UP - k * RISE + 2.4, r=0.09, m='e_dim', top=min(UP - k * RISE + 3.6, TOP - 0.6) if yy < BY0 + 0.4 else UP - k * RISE + 3.6)
    R.spot('plaque', SX0 + 0.02, SY_BOT - 1.0, 1.5, 0.0, text='THE LIBRARY REGRETS THAT IT DOES NOT CONTINUE.')
    secret(R, (SX0 + SX1) / 2, fy0 + 0.6, UP, 'The Cut Bookcase',
           'The last bookcase is hollow, and inside it a stair goes down the face of the cut. Through the slits there is only white. At the bottom someone has put out a chair, facing nothing.', r=1.3)
