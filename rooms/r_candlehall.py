"""The Hall of Candles: a vaulted nave where candles have burned so long the wax has grown into
stalagmites taller than a man and frozen waterfalls pouring off the bookcases. Behind the biggest
fall, on the west wall, a slot you only see side-on leads into a cave hollowed out of wax."""
from kit_h6 import *

W = D = 32.0
X0 = 3.2                        # the hall's west wall: the cave is in the thickness behind it
NX0, NX1 = 10.5, 21.5           # the nave, between two rows of piers
AH = 4.2                        # the aisles' ceiling
NJ, NR = 4.6, 2.8               # the nave vault: springing, rise
SY = (4.0, 12.0, 20.0, 28.0)    # stacks across the aisles
FALL = (13.6, 18.4)             # the great wax fall on the west wall
GAP = 0.85                      # the space behind it
CAVE_Y = (12.6, 19.6)


def make():
    R = Room('candlehall', 2, 2, res=2048)
    hall(R, x0=X0, h=AH, wall='tile', floor='terrazzo', ceil='plaster')
    R.cut(box(NX0, T - 0.02, 0, NX1, D - T + 0.02, NJ, 'tile', bottom='terrazzo', top='plaster'))
    pr = arch_profile(16, NX1 - NX0, 0, NJ, 28, rise=NR)
    R.cut(prism(pr, 'y', T - 0.02, D - T + 0.02, ['terrazzo'] + ['plaster'] * (len(pr) - 1), cap='plaster'))
    rs = rng(47)
    for k in range(8):
        y = 2.0 + k * 4.0
        R.nocol.add(prism(arc_band(16, NX1 - NX0, NJ, NR, 0.0, 0.3, 20), 'y', y - 0.18, y + 0.18, 'tile', cap='tile'))
    # piers down both sides of the nave, a wax heap at the foot of every other one
    for x in (NX0, NX1):
        R.parts.add(box(x - 0.4, T, AH - 0.3, x + 0.4, D - T, NJ + 0.1, 'tile'))
        for k in range(8):
            y = 2.0 + k * 4.0
            pier(R, x, y, 0, AH - 0.3, s=0.7)
            if k % 2 == 1:
                wax_mound(R, x + (0.75 if x < 16 else -0.75), y, 0.8, rs.uniform(1.6, 3.2), rs)
    walls(R, rs)
    stacks(R, rs)
    nave(R, rs)
    cave(R, rs)
    fx(R, 'dust', [NX0, T, 1.0, NX1, D - T, 7.2])
    fx(R, 'embers', [NX0 + 1, T + 1, 0.2, NX1 - 1, D - T - 1, 3.0], density=0.02)
    # walking graph: the nave, the walkways behind the piers, the cross aisles
    n = navloop(R, [(16, 1.6), (13.5, 8), (13.5, 16), (13.5, 24), (16, 30.4), (18.5, 24), (18.5, 16), (18.5, 8)])
    w = navloop(R, [(8, 1.6), (8, 8), (8, 16), (8, 24), (8, 30.4)], close=False)
    e = navloop(R, [(24, 1.6), (24, 8), (24, 16), (24, 24), (24, 30.4)], close=False)
    R.link(w[1], n[1]); R.link(w[3], n[3]); R.link(e[1], n[7]); R.link(e[3], n[5]); R.link(w[2], n[2]); R.link(e[2], n[6])
    a, b = R.navpt(4.6, 8), R.navpt(4.6, 24); R.link(a, w[1]); R.link(b, w[3])
    a, b = R.navpt(30.0, 8), R.navpt(30.0, 24); R.link(a, e[1]); R.link(b, e[3])
    return finish(R, 'The Hall of Candles', weight=3, probe=(16, 16, 2.6),
                  blurb='Candles on every shelf, every table, every ledge, all lit, and none of them ever burns down. The wax has had a long time to pile up.')


def walls(R, rs):
    rows = 9
    runs_w = ((0.7, 6.3), (9.7, FALL[0] - 0.6), (FALL[1] + 0.6, 22.3), (25.7, D - 0.7))
    for (a, b) in runs_w:
        sh(R, '+x', X0, a, b, rows=rows, frame='walnut')
        ledge(R, '+x', X0, a, b, rows, rs)
    for (a, b) in ((0.7, 6.3), (9.7, 22.3), (25.7, D - 0.7)):
        sh(R, '-x', W - T, a, b, rows=rows, frame='walnut')
        ledge(R, '-x', W - T, a, b, rows, rs)
    for (a, b) in ((X0 + 0.4, 6.3), (25.7, W - 0.7)):
        sh(R, '+y', T, a, b, rows=rows, frame='walnut'); ledge(R, '+y', T, a, b, rows, rs)
        sh(R, '-y', D - T, a, b, rows=rows, frame='walnut'); ledge(R, '-y', D - T, a, b, rows, rs)
    # wax falls pouring off the wall cases in the aisles
    wax_fall(R, 26.6, 29.4, W - T - 0.36, 3.9, rs, depth=0.3, bulge=0.4, foot=0.7, face=-1)
    wax_fall(R, 1.4, 4.2, W - T - 0.36, 3.9, rs, depth=0.3, bulge=0.35, foot=0.6, face=-1)
    wax_fall(R, 13.4, 18.6, W - T, AH - 0.05, rs, depth=0.4, bulge=0.8, foot=1.1, face=-1)
    R.parts.add(box(W - T - 0.5, 13.2, AH - 0.4, W - T, 18.8, AH, 'tallow'))
    for (x, y, r, h) in ((29.2, 12.9, 0.6, 2.2), (29.4, 19.1, 0.7, 3.1), (9.2, 17.2, 0.55, 1.9), (22.8, 10.4, 0.5, 1.6), (4.6, 30.6, 0.6, 2.6)):
        wax_mound(R, x, y, r, h, rs)
    # the great fall on the west wall, standing off it: the way into the cave is behind it
    wax_fall(R, FALL[0], FALL[1], X0 + GAP, AH - 0.05, rs, depth=0.5, bulge=0.9, foot=1.0, face=1)
    R.parts.add(box(X0, FALL[0] - 0.2, AH - 0.5, X0 + GAP + 0.3, FALL[1] + 0.2, AH, 'tallow'))
    candles_on(R, X0 + GAP + 1.3, FALL[0] + 0.6, X0 + GAP + 1.8, FALL[1] - 0.6, 0.12, 14, rs, 0.1, 0.45)
    candles_on(R, W - T - 1.9, 14.0, W - T - 1.4, 18.0, 0.12, 12, rs, 0.1, 0.45)
    drips(R, X0 + 0.1, FALL[0], X0 + GAP, FALL[0], AH - 0.5, 5, rs, 0.1, 0.8)
    drips(R, X0 + 0.1, FALL[1], X0 + GAP, FALL[1], AH - 0.5, 5, rs, 0.1, 0.8)
    # the wall behind it is wax-coated
    R.nocol.add(box(X0 - 0.01, FALL[0] - 0.2, 0, X0 + 0.04, 15.3, AH - 0.5, 'tallow'))
    R.nocol.add(box(X0 - 0.01, 16.9, 0, X0 + 0.04, FALL[1] + 0.2, AH - 0.5, 'tallow'))


def ledge(R, facing, bk, a, b, rows, rs, dens=2.2):
    """Candles along a bookcase's crown and a couple of its rows, wax hanging off the edges."""
    top = rows * 0.42 + 0.035 + 0.08 + 0.06
    L = b - a
    for (z, n, hmax) in ((top, int(L * dens * 0.7), 0.45), (2 * 0.42 + 0.035, int(L * dens * 0.22), 0.2), (5 * 0.42 + 0.035, int(L * dens * 0.18), 0.2)):
        for _ in range(n):
            t = rs.uniform(0.03, 0.97); dd = rs.uniform(0.08, 0.3)
            if facing == '+x': x, y = bk + dd, a + L * t
            elif facing == '-x': x, y = bk - dd, a + L * t
            elif facing == '+y': x, y = a + L * t, bk + dd
            else: x, y = a + L * t, bk - dd
            h, r = rs.uniform(0.08, hmax), rs.uniform(0.022, 0.04)
            R.nocol.add(taper(x, y, z, z + h, r, r * 0.9, 4))
            flame(R, x, y, z + h + 0.004)
    # drips off the crown edge and a row
    f = 0.36
    for (z, n, Lm) in ((top - 0.06, int(L * 2.4), 1.2), (2 * 0.42, int(L * 0.6), 0.25)):
        if facing == '+x': drips(R, bk + f, a, bk + f, b, z, n, rs, 0.06, Lm)
        elif facing == '-x': drips(R, bk - f, a, bk - f, b, z, n, rs, 0.06, Lm)
        elif facing == '+y': drips(R, a, bk + f, b, bk + f, z, n, rs, 0.06, Lm)
        else: drips(R, a, bk - f, b, bk - f, z, n, rs, 0.06, Lm)


def stacks(R, rs):
    """Short double-sided stacks across the aisles, each overgrown with wax and candles."""
    rows = 8
    for y in SY:
        for (a, b) in ((X0 + 0.1, 6.2), (25.8, W - T - 0.1)):
            stack(R, 'x', y, a, b, rows=rows, frame='walnut')
            ledge(R, '+y', y + 0.01, a, b, rows, rs, 1.6)
            ledge(R, '-y', y - 0.01, a, b, rows, rs, 1.6)
            # a great wax heap at the end facing the walkway
            xe = b + 0.5 if a < 10 else a - 0.5
            wax_mound(R, xe, y, 0.7, rs.uniform(2.4, 4.4), rs)


def nave(R, rs):
    """Reading tables down the nave, candles crowding the lamps, chandeliers of candles overhead."""
    for (y0, y1) in ((3.0, 6.8), (9.2, 14.8), (17.2, 22.8), (25.2, 29.0)):
        reading_table(R, 15.3, y0, 16.7, y1, lamps=2, chairs=True)
        candles_on(R, 15.4, y0 + 0.1, 16.6, y1 - 0.1, 0.78, int((y1 - y0) * 5), rs, 0.08, 0.35)
        drips(R, 15.28, y0, 15.28, y1, 0.76, int((y1 - y0) * 2), rs, 0.05, 0.35)
        drips(R, 16.72, y0, 16.72, y1, 0.76, int((y1 - y0) * 2), rs, 0.05, 0.35)
    # tall standing candelabra between tables
    for y in (8.0, 16.0, 24.0):
        for x in (12.6, 19.4):
            candelabrum(R, x, y, rs)
    for y in (4.9, 12.0, 20.0, 27.1):
        chandelier(R, 16, y, 5.2, 1.3, rs)
    # the biggest heaps, in the nave's corners
    for (x, y, h) in ((12.4, 2.4, 4.2), (19.6, 29.6, 5.0), (12.2, 29.4, 3.4), (19.8, 2.6, 3.0)):
        wax_mound(R, x, y, 1.1, h, rs)


def candelabrum(R, x, y, rs):
    R.parts.add(cyl(x, y, 0, 0.1, 0.35, 12, side='brass', top='brass'))
    R.parts.add(cyl(x, y, 0.1, 1.9, 0.04, 8, side='brass', caps=False))
    for (r, z, n) in ((0.45, 1.5, 6), (0.28, 1.9, 4)):
        R.nocol.add(ring(x, y, z, z + 0.04, r - 0.03, r + 0.03, 16, top='brass', bottom='brass', inner='brass', outer='brass'))
        for k in range(n):
            a = 2 * math.pi * k / n
            wax_spire(R, x + math.cos(a) * r, y + math.sin(a) * r, z + 0.04, rs.uniform(0.15, 0.4), 0.035, rs, col=False, segs=6)
    wax_spire(R, x, y, 1.9, 0.5, 0.05, rs, col=False, flame_m='e_flame')
    drips(R, x - 0.3, y, x + 0.3, y, 1.5, 6, rs, 0.1, 0.6)


def chandelier(R, x, y, z, r, rs):
    R.nocol.add(cyl(x, y, z + 0.1, NJ + NR - 0.05, 0.02, 6, side='iron', caps=False))
    for (rr, dz, n) in ((r, 0.0, 14), (r * 0.6, 0.45, 8)):
        R.nocol.add(ring(x, y, z + dz, z + dz + 0.06, rr - 0.04, rr + 0.04, 24, top='iron', bottom='iron', inner='iron', outer='iron'))
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * dz) / n
            cx, cy = x + math.cos(a) * rr, y + math.sin(a) * rr
            R.nocol.add(taper(cx, cy, z + dz + 0.06, z + dz + 0.36, 0.03, 0.028, 5))
            R.light(box(cx - 0.02, cy - 0.02, z + dz + 0.38, cx + 0.02, cy + 0.02, z + dz + 0.46, 'e_flame'))
        drips(R, x - rr, y, x + rr, y, z + dz, n // 2, rs, 0.1, 0.9)
    for k in range(4):
        a = k * math.pi / 2
        R.nocol.add(beam((x, y, z + 1.2), (x + math.cos(a) * r, y + math.sin(a) * r, z + 0.05), 0.03, 'iron'))


def cave(R, rs):
    """Hollowed out of the wax in the thickness of the west wall: a low warm cave, candles on every
    ledge, a bed of cushions, a book left open."""
    y0, y1 = CAVE_Y
    # the slot in the wall behind the fall
    R.cut(box(0.9, 15.3, 0, X0 + 0.05, 16.9, 2.2, 'tallow', bottom='tallow', top='tallow'))
    # the cave: overlapping round chambers
    for (cx, cy, r, h) in ((1.75, 14.2, 1.35, 2.5), (1.8, 16.1, 1.3, 2.7), (1.75, 18.0, 1.35, 2.4)):
        R.cut(cyl(cx, cy, 0, h, r, 14, side='tallow', top='tallow', bottom='tallow'))
    R.cut(cyl(1.85, 16.1, 2.6, 3.4, 0.9, 12, side='tallow', top='tallow', bottom='tallow'))
    # stalactites from the roof, stalagmites round the edge, candles on them
    for _ in range(26):
        a = rs.uniform(0, 2 * math.pi); d = rs.uniform(0.2, 1.0)
        cy = rs.choice((14.2, 16.1, 18.0))
        x, y = 1.9 + math.cos(a) * d, cy + math.sin(a) * d
        L = rs.uniform(0.1, 0.6)
        R.nocol.add(cone(x, y, 2.35 - L, 2.42, 0.005, rs.uniform(0.03, 0.08), 5, side='tallow'))
    for (cx, cy) in ((1.9, 14.2), (1.9, 18.0)):
        for k in range(9):
            a = 2 * math.pi * k / 9 + rs.uniform(-0.2, 0.2)
            x, y = cx + math.cos(a) * 1.15, cy + math.sin(a) * 1.15
            if x > 2.9: continue
            wax_spire(R, x, y, 0, rs.uniform(0.3, 1.2), rs.uniform(0.08, 0.14), rs, col=False, segs=7)
    # a bed of cushions and a blanket in the north chamber, a reading stand in the south one
    R.parts.add(box(0.9, 17.4, 0, 2.6, 18.9, 0.3, 'velvet'))
    R.nocol.add(box(1.0, 17.5, 0.3, 2.5, 18.2, 0.38, 'bed'))
    R.nocol.add(box(0.95, 18.4, 0.3, 1.6, 18.85, 0.45, 'oxblood'))
    R.spot('bed', 1.75, 18.1, 0.3, math.pi / 2)
    R.parts.add(box(1.6, 13.6, 0, 2.2, 14.2, 0.9, 'tallow'))
    open_book(R, 1.9, 13.9, 0.9, 0.3)
    candles_on(R, 1.65, 13.62, 2.15, 13.72, 0.9, 3, rs, 0.1, 0.3)
    book_pile(R, 1.2, 14.8, 0.0, n=7, seed=3, col=False)
    book_pile(R, 2.5, 13.3, 0.0, n=5, seed=4, col=False)
    candles_on(R, 0.8, 15.4, 1.5, 16.8, 0.0, 12, rs, 0.1, 0.6)
    secret(R, 1.9, 16.1, 0.0, 'The Wax Cave',
           'Behind the frozen fall the wax is hollow. Somebody has lived in here a long time, warm, in the smell of it, reading by a thousand small lights.')
