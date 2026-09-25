"""The Departure Gate: a long, tall hall of joined seats facing a wall of glass, and beyond the glass
nothing but fog, lit from somewhere, and the pale shape of an aeroplane standing in it. The two jet
bridges are how you came in: they lead back to the library. A board lists the departures, all on
time, none boarding. Gate 0 has no number on its desk and its door is not quite shut: a short
bellows leads into the front of the aeroplane, which is a little reading room with its seats all
facing forward, going nowhere, the overhead lockers full of books."""
from kit_h9 import *

W, D = 32.0, 16.0
GY = 6.1                          # the glass line
FY0 = 1.25                        # the back of the fog
ZF = -1.8                         # the apron, down in the fog
BR = (8.0, 24.0)                  # the jet bridges, from the south doorways
BH = 2.8                          # their ceiling
PCY, PCZ, PR = 3.0, 1.2, 1.75     # the fuselage: centre line (y, z), radius
PX0, PX1 = 11.2, 21.0             # the cabin, inside the fuselage
DX0, DX1 = 15.4, 16.6             # gate 0's door, and the plane's
CY0, CY1 = PCY - 1.27, PCY + 1.27 # the cabin floor's edges (where the curved walls meet it)


def make():
    R = Room('airportgate', 2, 1, res=2048)
    R.sockets(floor='carpet', wall='ivory')
    hall(R)
    fog(R)
    for c in BR: bridge(R, c)
    plane(R)
    gate0(R)
    fx(R, 'fog', [T, FY0, ZF, W - T, GY - 0.1, TOP - 0.1], density=0.09)
    fx(R, 'dust', [T, GY, 0.5, W - T, D - T, 6.0])
    ids = navloop(R, [(2.0, 7.2), (16.0, 7.6), (30.0, 7.2), (30.0, 10.0), (16.5, 10.0), (2.0, 10.0)])
    for c in BR:
        a, b = R.navpt(c, 1.6), R.navpt(c, GY + 0.8)
        R.link(a, b)
    secret(R, 16.6, 3.0, 0.0, 'The Only Flight',
           'The door at gate 0 was not locked. The aeroplane is warm and lit and nobody is aboard; the overhead lockers are full of books, and every seat has its belt fastened, as if for take-off, but there are no engines, only fog.')
    return finish(R, 'The Departure Gate', weight=3, probe=(16, 10, 2.0), top=TOP - 0.1,
                  blurb='A departure lounge, joined seats in rows, a wall of glass onto fog. The board says every flight is on time. None of them is boarding.')


# ---------------------------------------------------------------------------
def hall(R):
    R.cut(box(T - 0.02, GY, 0, W - T + 0.02, D - T + 0.02, TOP - 0.1, 'ivory', bottom='carpet', top='plaster'))
    # the glass: mullions and transoms, and the invisible pane
    xs = [T + k * (W - 2 * T) / 18 for k in range(19)]
    opens = [(c - 1.5, c + 1.5) for c in BR] + [(DX0, DX1)]
    inopen = lambda x, e=0.1: any(a - e < x < b + e for (a, b) in opens)
    for x in xs:
        if not inopen(x): R.parts.add(box(x - 0.06, GY - 0.05, 0.0, x + 0.06, GY + 0.08, TOP - 0.1, 'iron'))
    for (a, b) in [(c - 1.7, c + 1.7) for c in BR] + [(DX0 - 0.15, DX1 + 0.15)]:
        R.parts.add(box(a, GY - 0.06, 0.0, a + 0.2 if a < b else a, GY + 0.1, TOP - 0.1, 'iron'))
        R.parts.add(box(b - 0.2, GY - 0.06, 0.0, b, GY + 0.1, TOP - 0.1, 'iron'))
    pts = sorted(set([T] + [q for o in opens for q in o] + [W - T]))
    x = T
    for (a, b) in sorted(opens) + [(W - T, W - T)]:
        if a - x > 0.05:
            R.parts.add(box(x, GY - 0.12, 0.0, a, GY + 0.12, 0.3, 'iron'))
            for z in (2.6, 5.0):
                R.nocol.add(box(x, GY - 0.03, z - 0.04, a, GY + 0.06, z + 0.04, 'iron'))
        x = b
    for z in (5.0,):
        R.nocol.add(box(T, GY - 0.03, z - 0.04, W - T, GY + 0.06, z + 0.04, 'iron'))
    x = T
    for (a, b) in sorted(opens) + [(W - T, W - T)]:
        if a - x > 0.05: R.col.add(box(x, GY - 0.04, 0.0, a, GY + 0.04, TOP - 0.1, 'tile'))
        x = b
    # the north wall: bookcases in bays between stone piers, a rolling ladder
    for (a, b) in ((0.6, 6.2), (9.8, 15.6), (16.4, 22.2), (25.8, W - 0.6)):
        sh(R, '-y', D - T, a, b, rows=15, frame='walnut')
    for c in BR:
        sh(R, '-y', D - T, c - 1.8, c + 1.8, z=4.4, rows=6, frame='walnut')
    for x in (0.55, 6.4, 9.6, 16.0, 22.4, 25.6, W - 0.55):
        R.parts.add(box(x - 0.25, D - T - 0.5, 0.0, x + 0.25, D - T, TOP - 0.1, 'tile'))
        R.nocol.add(cyl(x, D - T - 0.62, 3.1, 3.4, 0.06, 8, side='brass', top='brass', bottom='brass'))
        R.light(sphere(x, D - T - 0.62, 3.5, 0.12, 8, 4, 'e_lamp'))
    sh(R, '+x', T, 9.9, D - T - 0.6, rows=15, frame='walnut')
    sh(R, '-x', W - T, 9.9, D - T - 0.6, rows=15, frame='walnut')
    from kit_a import ladder
    R.nocol.add(ladder(19.0, D - T - 0.36, -math.pi / 2, h=5.8, lean=1.1))
    # reading tables along the books
    for (x0, x1) in ((2.0, 5.2), (10.6, 14.6), (17.4, 21.4), (26.8, 30.0)):
        R.parts.add(table(x0, 13.6, x1, 14.4, 0.78, 'walnut', top='leather'))
        for k in range(2):
            desk_lamp(R, x0 + (x1 - x0) * (k + 0.5) / 2, 14.0, 0.78)
        for k in range(3):
            xx = x0 + (x1 - x0) * (k + 0.5) / 3
            R.parts.add(chair(xx, 13.1, math.pi / 2)); R.spot('sit', xx, 13.1, 0.48, math.pi / 2)
    # the joined seats, in banks facing the glass (and back to back)
    for (x0, n) in ((3.0, 16), (18.6, 16)):
        for (y, f) in ((8.4, -1), (9.1, 1), (11.0, -1), (11.7, 1)):
            seat_bank(R, x0, y, n, f)
    # the departures board, hung over the glass
    board(R)
    # strip lights along the ceiling, and a few night lamps
    for y in (8.6, 12.0):
        R.light(box(1.0, y - 0.1, TOP - 0.16, W - 1.0, y + 0.1, TOP - 0.12, 'e_panel'))
    for x in (2.5, 16.0, 29.5):
        R.light(sphere(x, 7.0, 0.5, 0.08, 8, 4, 'e_amber'))
        R.nocol.add(cyl(x, 7.0, 0.0, 0.45, 0.03, 6, side='brass', caps=False))


def seat_bank(R, x0, y, n, f, pitch=0.62):
    """A row of joined seats on a chrome beam: f=-1 faces south (-y), +1 north."""
    L = n * pitch
    g = Geo()
    g.add(box(x0, y - 0.06, 0.34, x0 + L, y + 0.06, 0.4, 'chrome'))
    for xl in (x0 + 0.3, x0 + L / 2, x0 + L - 0.3):
        g.add(box(xl - 0.04, y - 0.3, 0.0, xl + 0.04, y + 0.3, 0.04, 'chrome'))
        g.add(box(xl - 0.03, y - 0.03, 0.04, xl + 0.03, y + 0.03, 0.34, 'chrome'))
    for i in range(n):
        xa = x0 + i * pitch + 0.03; xb = xa + pitch - 0.06
        ya, yb = sorted((y, y + 0.48 * f))
        g.add(box(xa, ya, 0.4, xb, yb, 0.47, 'seat'))
        yc, yd = sorted((y - 0.02 * f, y + 0.05 * f))
        g.add(box(xa, yc, 0.47, xb, yd, 1.0, 'seat'))
        R.spot('sit', (xa + xb) / 2, y + 0.26 * f, 0.47, math.pi / 2 * f)
        if i and i % 3 == 0:
            g.add(box(xa - 0.05, ya + 0.05, 0.47, xa + 0.01, yb - 0.05, 0.66, 'chrome'))
    R.parts.add(g)


def board(R):
    x0, x1, z0, z1, y = 11.5, 20.5, 4.0, 6.6, GY + 0.9
    R.parts.add(box(x0, y - 0.08, z0, x1, y, z1, 'black'))
    for x in (x0 + 0.4, x1 - 0.4):
        R.nocol.add(box(x - 0.02, y - 0.06, z1, x + 0.02, y - 0.02, TOP - 0.1, 'iron'))
    rnd = random.Random(85)
    g = Geo()
    ys = y + 0.005
    # a header bar, then ten lines: a title in word blocks, and ON TIME on the right
    g.add(box(x0 + 0.2, y, z1 - 0.32, x0 + 2.2, ys, z1 - 0.12, 'e_board'))
    lh = (z1 - z0 - 0.5) / 10
    for i in range(10):
        z = z1 - 0.45 - (i + 0.5) * lh
        x = x0 + 0.25
        xe = x0 + (x1 - x0) * rnd.uniform(0.45, 0.68)
        while x < xe:
            wl = rnd.uniform(0.2, 0.7)
            n = max(1, int(wl / 0.07))
            for k in range(n):
                g.add(box(x + k * 0.07, y, z - 0.06, x + k * 0.07 + 0.05, ys, z + 0.06, 'e_board'))
            x += n * 0.07 + 0.12
        for k in range(7):
            if k == 2: continue
            xx = x1 - 1.4 + k * 0.17
            g.add(box(xx, y, z - 0.06, xx + 0.12, ys, z + 0.06, 'e_board'))
    R.light(g)


# ---------------------------------------------------------------------------
def fog(R):
    """Beyond the glass: an apron down in the fog, the fog lit from somewhere."""
    zt = TOP - 0.1
    x = T
    bands = [(c - 1.7, c + 1.7) for c in BR]
    for (a, b) in bands + [(W - T + 0.02, W - T + 0.02)]:
        if a > x: R.cut(box(x - (0.02 if x <= T else 0), FY0, ZF, a, GY + 0.02, zt, 'concrete', bottom='slate', top='plaster'))
        x = b
    for (a, b) in bands:
        R.cut(box(a, FY0, BH + 0.2, b, GY + 0.02, zt, 'concrete', bottom='concrete', top='plaster'))
        R.cut(box(a, FY0, ZF, b, GY + 0.02, -0.3, 'concrete', bottom='slate', top='concrete'))
    # the fog itself: glowing walls at the back and the ends
    R.light(panel_y(FY0 + 0.02, T, W - T, ZF, zt, 'e_fog', face=1))
    R.light(panel_x(T + 0.02, FY0, GY, ZF, zt, 'e_fog', face=1))
    R.light(panel_x(W - T - 0.02, FY0, GY, ZF, zt, 'e_fog', face=-1))
    # markings on the apron
    for y in (2.2, 4.6):
        R.nocol.add(box(T, y - 0.06, ZF, W - T, y + 0.06, ZF + 0.01, 'tactile'))
    for x in (4.0, 12.0, 20.0, 28.0):
        R.nocol.add(box(x - 0.06, FY0, ZF, x + 0.06, GY, ZF + 0.01, 'ivory'))


def bridge(R, c):
    """A jet bridge on legs, from a doorway in the fog wall to the glass."""
    R.cut(box(c - 1.5, T - 0.02, 0.0, c + 1.5, GY + 0.05, BH, 'ivory', bottom='carpet', top='plaster'))
    # little windows on each side, looking into the fog
    for y in (2.2, 3.6, 5.0):
        for (xa, xb) in ((c - 1.75, c - 1.45), (c + 1.45, c + 1.75)):
            R.cut(box(xa, y - 0.4, 1.0, xb, y + 0.4, 2.0, 'iron', bottom='iron', top='iron'))
            R.col.add(box(xa, y - 0.4, 1.0, xb, y + 0.4, 2.0, 'tile'))
    for y in (2.4, 4.8):
        for x in (c - 1.2, c + 1.2):
            R.parts.add(box(x - 0.12, y - 0.12, ZF, x + 0.12, y + 0.12, -0.3, 'iron'))
    for y in (2.0, 3.6, 5.2):
        R.light(box(c - 0.5, y - 0.3, BH - 0.03, c + 0.5, y + 0.3, BH - 0.01, 'e_panel'))
    for k in range(6):
        y = FY0 + 0.3 + k * 0.8
        R.nocol.add(box(c - 1.5, y - 0.03, 0.0, c + 1.5, y + 0.03, 0.005, 'ivory'))


# ---------------------------------------------------------------------------
def fuselage(x0, x1, r, m, inner=False, segs=24, door=None):
    """A cylinder along x through (PCY, PCZ), with an optional hole (x range, z range) on its north side."""
    g = Geo()
    nx = max(1, int((x1 - x0) / 0.4))
    for i in range(nx):
        xa = x0 + (x1 - x0) * i / nx; xb = x0 + (x1 - x0) * (i + 1) / nx
        for k in range(segs):
            a0 = 2 * math.pi * k / segs; a1 = 2 * math.pi * (k + 1) / segs
            if door:
                am = (a0 + a1) / 2
                zm = PCZ + r * math.sin(am)
                if door[0] <= (xa + xb) / 2 <= door[1] and math.cos(am) > 0 and door[2] <= zm <= door[3]: continue
            P = [(xa, PCY + r * math.cos(a0), PCZ + r * math.sin(a0)), (xb, PCY + r * math.cos(a0), PCZ + r * math.sin(a0)),
                 (xb, PCY + r * math.cos(a1), PCZ + r * math.sin(a1)), (xa, PCY + r * math.cos(a1), PCZ + r * math.sin(a1))]
            ids = [g.vert(p) for p in P]
            if inner: ids = ids[::-1]
            g.face(ids, m, [(p[0], a0 * r) for p in P] if not inner else [(p[0], a0 * r) for p in P[::-1]])
    return g


def cone_x(x0, x1, r0, r1, m, segs=24, sharp=1.0):
    """A nose or tail: rings along x from radius r0 at x0 to r1 at x1 (bulging), closed at the small end."""
    g = Geo()
    n = 5
    rings = []
    for i in range(n + 1):
        t = i / n
        r = r0 + (r1 - r0) * (t ** sharp)
        rings.append([(x0 + (x1 - x0) * t, PCY + max(r, 0.01) * math.cos(2 * math.pi * k / segs), PCZ + max(r, 0.01) * math.sin(2 * math.pi * k / segs)) for k in range(segs)])
    for i in range(n):
        for k in range(segs):
            j = (k + 1) % segs
            P = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            ids = [g.vert(p) for p in P]
            g.face(ids if x1 > x0 else ids[::-1], m, [(p[0], k * 0.4) for p in P])
    return g


def plane(R):
    """The aeroplane in the fog: its cabin is the small room at the end of gate 0."""
    door = (DX0 - 0.05, DX1 + 0.05, -0.05, 2.1)
    R.nocol.add(fuselage(PX0 - 0.2, PX1 + 0.2, PR, 'fuselage', door=door))
    R.nocol.add(fuselage(PX0, PX1, PR - 0.08, 'ivory', inner=True, door=door))
    # a band of livery, windows as dark squares outside and lit portholes inside
    for k in range(13):
        x = PX0 + 0.5 + k * 0.72
        if DX0 - 0.3 < x < DX1 + 0.3: continue
        for s in (-1, 1):
            y = PCY + s * (PR + 0.01) * math.cos(0.35)
            z = PCZ + (PR + 0.01) * math.sin(0.35)
            R.nocol.add(box(x - 0.12, min(y, y + 0.01 * s), z - 0.16, x + 0.12, max(y, y + 0.01 * s), z + 0.16, 'black'))
            yi = PCY + s * (PR - 0.1) * math.cos(0.35)
            R.light(box(x - 0.1, min(yi, yi - 0.01 * s), z - 0.14, x + 0.1, max(yi, yi - 0.01 * s), z + 0.14, 'e_fog'))
    # nose and tail cones, the fin, low wings with their engines
    R.nocol.add(cone_x(PX0 - 0.2, PX0 - 1.2, PR, 0.2, 'fuselage', sharp=2.2))
    R.nocol.add(cone_x(PX1 + 0.2, PX1 + 1.2, PR, 0.5, 'fuselage', sharp=1.0))
    fin = prism([(PX1 - 1.2, PCZ + PR - 0.1), (PX1 + 0.6, PCZ + PR - 0.1), (PX1 + 0.9, PCZ + PR + 2.4), (PX1 + 0.1, PCZ + PR + 2.4)], 'y', PCY - 0.07, PCY + 0.07, 'oxblood', cap='fuselage')
    R.nocol.add(fin)
    for s in (-1, 1):
        y0 = PCY + s * (PR - 0.2); y1 = GY - 0.4 if s > 0 else FY0 + 0.05
        w = prism([(13.2, -0.55), (17.4, -0.55), (17.6, -0.4), (13.6, -0.4)], 'y', min(y0, y1), max(y0, y1), 'fuselage', cap='fuselage')
        R.nocol.add(w)
    eng = cyl(0, 0, 0, 2.0, 0.42, 14, side='fuselage', top='black', bottom='black')
    rot(eng, 'y', math.pi / 2)
    R.nocol.add(eng.xform(0, 13.4, PCY + 2.2, -0.95))
    # the cabin: a floor, walls you cannot walk through, bulkheads at both ends
    R.parts.add(box(PX0, CY0 - 0.05, -0.25, PX1, CY1 + 0.05, 0.0, 'carpet', sides='fuselage', bottom='fuselage'))
    R.col.add(box(PX0, CY0 - 0.08, 0.0, PX1, CY0, 2.6, 'tile'))
    R.col.add(box(PX0, CY1, 0.0, DX0, CY1 + 0.08, 2.6, 'tile'))
    R.col.add(box(DX1, CY1, 0.0, PX1, CY1 + 0.08, 2.6, 'tile'))
    for x in (PX0, PX1):
        R.parts.add(box(x - 0.05, CY0 - 0.3, -0.25, x + 0.05, CY1 + 0.3, PCZ + PR - 0.1, 'ivory'))
    R.nocol.add(box(PX0 + 0.06, PCY - 0.45, 0.0, PX0 + 0.1, PCY + 0.45, 2.0, 'velvet'))      # the cockpit curtain
    # seats, two and one, all facing forward (west), belts done up; books in every overhead locker
    for k in range(9):
        x = PX0 + 1.3 + k * 0.85
        if DX0 - 0.4 < x < DX1 + 0.5: continue
        for (y0, y1) in ((CY0 + 0.1, CY0 + 1.1), (CY1 - 0.6, CY1 - 0.1)):
            R.parts.add(box(x - 0.25, y0, 0.0, x + 0.2, y1, 0.45, 'seat', top='velvet'))
            R.parts.add(box(x + 0.2, y0, 0.0, x + 0.3, y1, 1.15, 'seat'))
            n = int((y1 - y0) / 0.5 + 0.5)
            for i in range(n):
                yy = y0 + (y1 - y0) * (i + 0.5) / n
                R.spot('sit', x, yy, 0.45, math.pi)
                if (k + i) % 2 == 0:
                    R.nocol.add(book(x - 0.02, yy, 0.45, 0.3 * (i - 0.5), BOOKM[(k * 3 + i) % len(BOOKM)]))
    for (face, yb) in (('+y', CY0 + 0.3), ('-y', CY1 - 0.3)):
        if face == '+y':
            sh(R, '+y', yb, PX0 + 0.4, PX1 - 0.4, z=1.95, rows=1, frame='ivory', depth=0.4, row_h=0.4)
        else:
            sh(R, '-y', yb, PX0 + 0.4, DX0 - 0.2, z=1.95, rows=1, frame='ivory', depth=0.4, row_h=0.4)
            sh(R, '-y', yb, DX1 + 0.2, PX1 - 0.4, z=1.95, rows=1, frame='ivory', depth=0.4, row_h=0.4)
    for k in range(5):
        x = PX0 + 1.0 + k * 2.0
        R.light(box(x - 0.3, PCY - 0.15, 2.52, x + 0.3, PCY + 0.15, 2.55, 'e_lamp'))
    # at the back, the trolley with tea
    R.parts.add(box(PX1 - 0.9, PCY - 0.2, 0.0, PX1 - 0.3, PCY + 0.2, 1.0, 'chrome'))
    R.nocol.add(cyl(PX1 - 0.6, PCY, 1.0, 1.22, 0.1, 10, side='chrome', top='chrome', bottom='chrome'))
    for i in range(3):
        R.nocol.add(cyl(PX1 - 0.8 + i * 0.2, PCY + 0.12, 1.0, 1.08, 0.04, 8, side='ivory', top='ivory', bottom='ivory'))
    R.light(sphere(PX1 - 0.45, PCY - 0.1, 1.08, 0.03, 6, 3, 'e_candle'))


def gate0(R):
    """Gate 0: a desk with no number, a door not quite shut, a bellows out to the aeroplane."""
    # the bellows: a floor, pleated walls and roof (drawn), walls you cannot pass
    R.parts.add(box(DX0 - 0.1, CY1 - 0.05, -0.25, DX1 + 0.1, GY + 0.05, 0.0, 'carpet', sides='iron', bottom='iron'))
    for k in range(8):
        y = CY1 + 0.1 + k * (GY - CY1 - 0.1) / 8
        for x in (DX0 - 0.1, DX1 + 0.1):
            R.nocol.add(box(x - 0.06, y - 0.05, 0.0, x + 0.06, y + 0.05, 2.3, 'black' if k % 2 else 'slate'))
        R.nocol.add(box(DX0 - 0.1, y - 0.05, 2.25, DX1 + 0.1, y + 0.05, 2.35, 'black' if k % 2 else 'slate'))
    for x in (DX0 - 0.16, DX1 + 0.16):
        R.col.add(box(x - 0.04, CY1, 0.0, x + 0.04, GY, 2.4, 'tile'))
    R.light(box(15.9, 5.2, 2.2, 16.1, 5.4, 2.24, 'e_dim'))
    # the door in the glass, ajar
    R.nocol.add(door_leaf(DX1 - DX0 - 0.04, 2.3, 'iron', 'slate', 'chrome', t=0.04).xform(math.pi / 2 + 1.0, DX0 + 0.02, GY + 0.06, 0))
    R.parts.add(box(DX0 - 0.12, GY - 0.06, 2.3, DX1 + 0.12, GY + 0.1, 2.45, 'iron'))
    # the desk and its sign
    R.parts.add(box(13.0, GY + 0.8, 0.0, 14.6, GY + 1.4, 1.05, 'walnut', top='leather'))
    desk_lamp(R, 13.4, GY + 1.1, 1.05)
    R.parts.add(box(12.9, GY + 0.35, 2.7, 15.1, GY + 0.45, 3.3, 'black'))
    R.light(box(13.1, GY + 0.46, 2.85, 13.9, GY + 0.47, 3.15, 'e_board'))
    g = Geo()   # a nought, in lamps
    for k in range(10):
        a = 2 * math.pi * k / 10
        g.add(box(14.45 + 0.1 * math.cos(a) - 0.025, GY + 0.46, 3.0 + 0.12 * math.sin(a) - 0.025, 14.45 + 0.1 * math.cos(a) + 0.025, GY + 0.47, 3.0 + 0.12 * math.sin(a) + 0.025, 'e_board'))
    R.light(g)
    # a rope line in front of it, as if boarding had been cancelled
    for x in (14.9, 17.4):
        R.parts.add(cyl(x, GY + 1.2, 0.0, 0.95, 0.03, 8, side='brass', top='brass', bottom='brass'))
        R.parts.add(cyl(x, GY + 1.2, 0.0, 0.04, 0.16, 10, side='brass', top='brass', bottom='brass'))
    R.nocol.add(tube(curve((14.9, GY + 1.2, 0.9), (17.4, GY + 1.2, 0.9), (0, 0, 0), 7, 0.25), 0.025, 6, 'velvet'))
