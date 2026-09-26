"""The Bridge over the Void: two landings high on the end walls of a vast dark gap, and between them one
narrow stone bridge, its parapets made of low bookcases, green lamps on posts along it. The walls of the
void are towering facades of books with lamps dotted up them; far below is a dark floor you would rather
not think about (you can reach it: under each landing is a hall, and a stair). Halfway across, one
bookcase in the north parapet is missing, and an iron ladder goes over the side: down onto the roof of a
little wooden room slung under the bridge on chains."""
from kit_h7 import *

W, D = 64.0, 32.0
UP = LH
PX0, PX1 = 10.5, 53.5          # the landings end here (the void between)
BY0, BY1 = 14.7, 17.3          # the bridge
BTH = 0.6                      # the landing slabs' thickness
RX0, RX1, RY0, RY1 = 28.0, 36.0, BY0, 19.8     # the room slung under the bridge
RZ = 4.6                       # its floor
LZ = 7.6                       # the roof ledge beside the bridge
GX0, GX1 = 27.93, 29.6        # the gap in the north parapet
LADY = 18.25                   # the ladder inside the room (climbs -x)
SEAL = [('S', 1, 1), ('S', 2, 1), ('N', 1, 1), ('N', 2, 1)]


def zu(x):
    """The bridge's underside: a shallow arch, thick at the landings, thin at mid-span."""
    t = (x - 32.0) / ((PX1 - PX0) / 2)
    return 7.42 - 3.6 * t ** 4


def make():
    R = Room('bridgevoid', 4, 2, levels=2, res=2048)
    seal(R, SEAL, floor='floor', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, R.hi - 0.1, 'tile', bottom='slate', top='plaster'))
    landings(R)
    bridge(R)
    facades(R)
    room(R)
    floor(R)
    fx(R, 'fog', [PX0, T, 0.0, PX1, D - T, 6.5], density=0.06)
    fx(R, 'dust', [PX0, BY0 - 3, UP, PX1, BY1 + 3, UP + 4])
    navloop(R, [(2.0, 2.0), (8.0, 2.0), (8.0, 29.9), (2.0, 29.9)])
    navloop(R, [(W - 2.0, 2.0), (W - 8.0, 2.0), (W - 8.0, 29.9), (W - 2.0, 29.9)])
    a, b = R.navpt(8.0, 16.0), R.navpt(W - 8.0, 16.0)
    R.link(a, R.navpt(32.0, 12.0), b)
    c, d = R.navpt(8.5, 16.0, UP), R.navpt(W - 8.5, 16.0, UP)
    m1, m2 = R.navpt(20.0, 16.0, UP), R.navpt(44.0, 16.0, UP)
    R.link(c, m1, m2, d)
    navloop(R, [(8.5, 3.0), (8.5, 29.0)], z=UP, close=False)
    return finish(R, 'The Bridge over the Void', weight=2, probe=(32.0, 11.0, UP + 1.5), top=R.hi,
                  blurb='One bridge, one person wide, across a gap in the library that goes down further than the lamps do. Its parapets are bookcases. People stop in the middle to browse, which seems brave.')


def landings(R):
    """The landings at each end (level 1), railed at the void; under each, a hall with a stair up."""
    for (x0, x1, ex) in ((T - 0.02, PX0, PX0), (PX1, W - T + 0.02, PX1)):
        if ex == PX0:     # the west landing has the stairwell in it
            for (a0, b0, a1, b1) in ((x0, T - 0.02, x1, 10.4), (x0, 16.55, x1, D - T + 0.02), (x0, 10.4, 2.5, 16.55), (4.7, 10.4, x1, 16.55)):
                R.parts.add(box(a0, b0, UP - BTH, a1, b1, UP, 'tile', top='floor', bottom='plaster'))
        else:
            R.parts.add(box(x0, T - 0.02, UP - BTH, x1, D - T + 0.02, UP, 'tile', top='floor', bottom='plaster'))
        s = 0.12 if ex == PX0 else -0.12
        brail(R, ex - s, T, ex - s, BY0, UP)
        brail(R, ex - s, BY1, ex - s, D - T, UP)
        # columns under the landing's edge
        for y in (4.0, 12.0, 20.0, 28.0):
            R.parts.add(box(ex - (0.7 if ex == PX0 else 0.0), y - 0.35, 0, ex + (0.0 if ex == PX0 else 0.7), y + 0.35, UP - BTH, 'tile', skip=('-z',)))
        # reading tables and benches facing the void
        xm = (x0 + x1) / 2
        reading_table(R, xm - 0.6, 20.5, xm + 0.6, 27.0, lamps=3, z=UP, axis='y')
        reading_table(R, xm - 0.6, 4.8, xm + 0.6, 11.0, lamps=3, z=UP, axis='y')
    # the stair from the west hall up to the west landing: two flights along the west wall
    n, rise, run = 20, 0.2, 0.3
    R.flight(0.4, 10.5, 0.0, 2.0, n, rise, run, '+y', m='tile', riser='tile', side='tile')
    R.parts.add(box(2.4, 10.5, 0.0, 4.6, 16.5, 4.0, 'tile', skip=('-z',)))
    R.parts.add(box(0.4, 16.5, 0.0, 4.6, 18.5, 4.0, 'tile', top='terrazzo', skip=('-z',)))
    R.flight(2.6, 16.5, 4.0, 2.0, n, rise, run, '-y', m='tile', riser='tile', side='tile')
    brail(R, 2.43, 11.6, 2.43, 16.6, UP)
    brail(R, 2.43, 16.62, 4.72, 16.62, UP)
    brail(R, 4.72, 11.6, 4.72, 16.62, UP)
    # books on every wall of the landings and the halls beneath
    for (z, rows) in ((0.0, 12), (UP, 11)):
        for (x0, x1) in ((0.6, 6.2), (9.8, PX0 - 0.2)):
            sh(R, '+y', T, x0, x1, z=z, rows=rows, frame='walnut')
            sh(R, '-y', D - T, x0, x1, z=z, rows=rows, frame='walnut')
        for (x0, x1) in ((PX1 + 0.2, 54.2), (57.8, W - 0.6)):
            sh(R, '+y', T, x0, x1, z=z, rows=rows, frame='walnut')
            sh(R, '-y', D - T, x0, x1, z=z, rows=rows, frame='walnut')
        for (y0, y1) in ((0.6, 6.2), (9.8, 22.2), (25.8, D - 0.6)):
            if not (z == 0.0 and y0 == 9.8):
                sh(R, '+x', T, y0, y1, z=z, rows=rows, frame='walnut')
            sh(R, '-x', W - T, y0, y1, z=z, rows=rows, frame='walnut')
    for (x, y) in ((5.5, 4.0), (5.5, 28.0), (W - 5.5, 4.0), (W - 5.5, 28.0), (W - 5.5, 16.0), (7.5, 21.5)):
        hanging(R, x, y, UP - BTH, 4.8, r=0.4, e='e_lamp', shade='green')
    for (x, y) in ((4.0, 16.0), (4.0, 3.0), (4.0, 29.0), (W - 4.0, 16.0), (W - 4.0, 3.0), (W - 4.0, 29.0)):
        hanging(R, x, y, R.hi - 0.1, UP + 3.6, r=0.45, e='e_lamp', shade='green')


def bridge(R):
    """The span: an arch-bellied stone deck, parapets of double-faced low bookcases between stone piers,
    lamp posts on every other pier, and the gap in the north parapet over the slung room."""
    prof = [(PX0 - 0.3, UP), (PX0 - 0.3, UP - BTH)]
    for k in range(25):
        x = PX0 + (PX1 - PX0) * k / 24
        prof.append((x, zu(x)))
    prof += [(PX1 + 0.3, UP - BTH), (PX1 + 0.3, UP)]
    prof = [prof[0]] + prof[1:]
    R.parts.add(prism(list(reversed(prof)), 'y', BY0, BY1, 'tile', cap='tile'))
    R.nocol.add(box(PX0, BY0 + 0.3, UP, PX1, BY1 - 0.3, UP + 0.004, 'carpet'))
    # piers every 4 m, parapet cases between
    piers = [PX0 + 4.3 * k for k in range(11)]
    piers[-1] = PX1
    ph = 2 * 0.42 + 0.035 + 0.08
    for side in (0, 1):
        yb = BY0 if side == 0 else BY1
        for k, x in enumerate(piers):
            y0, y1 = (BY0, BY0 + 0.4) if side == 0 else (BY1 - 0.4, BY1)
            R.parts.add(box(x - 0.22, y0, UP, x + 0.22, y1, UP + ph + 0.2, 'tile'))
            if k % 2 == 0 and 0 < k < len(piers) - 1:
                lamp_post(R, x, (y0 + y1) / 2, UP + ph + 0.2, h=1.2, m='e_lamp')
        for a, b in zip(piers, piers[1:]):
            spans = [(a + 0.22, b - 0.22)]
            if side == 1 and a < GX0 < b:
                spans = [(a + 0.22, GX0 - 0.02), (GX1 + 0.02, b - 0.22)]
            for (s0, s1) in spans:
                if s1 - s0 < 0.3: continue
                yc = BY0 + 0.2 if side == 0 else BY1 - 0.2
                stack(R, 'x', yc, s0, s1, UP, rows=2, depth=0.17, frame='walnut')
                R.parts.add(box(s0 - 0.02, yc - 0.23, UP + ph, s1 + 0.02, yc + 0.23, UP + ph + 0.12, 'tile'))
    # a small iron ladder hooked over the gap, down onto the room's roof
    for s in (GX0 + 0.1, GX1 - 0.1):
        R.nocol.add(box(s - 0.02, BY1 - 0.05, LZ, s + 0.02, BY1 + 0.25, UP + 0.9, 'iron'))
        R.nocol.add(box(s - 0.02, BY1 - 0.35, UP + 0.85, s + 0.02, BY1 + 0.05, UP + 0.9, 'iron'))
    for zz in (LZ + 0.15, LZ + 0.45, UP + 0.2, UP + 0.5):
        R.nocol.add(box(GX0 + 0.1, BY1 + 0.08, zz, GX1 - 0.1, BY1 + 0.12, zz + 0.03, 'iron'))


def facades(R):
    """The walls of the void: two tiers of towering cases between pilasters, stone cornices, lamps
    dotted all the way up, and more books round the ends of the landings."""
    for (yw, face) in ((T, '+y'), (D - T, '-y')):
        sg = 1 if face == '+y' else -1
        PIL = [10.8, 15.2, 19.6, 28.0, 32.0, 36.0, 44.4, 48.8, 53.2]
        for x in PIL:
            R.parts.add(box(x - 0.35, yw - 0.02 if sg > 0 else yw - 0.45, 0, x + 0.35, yw + 0.45 if sg > 0 else yw + 0.02, R.hi - 0.1, 'tile', skip=('-z',)))
        for (pa, pb) in zip(PIL, PIL[1:]):
            a, b = pa + 0.4, pb - 0.4
            doors = [24.0, 40.0]
            for (z, rows) in ((0.0, 15), (UP - 0.3, 14)):
                segs = [(a, b)]
                if z == 0.0:
                    for dc in doors:
                        if a < dc < b: segs = [(a, dc - 1.9), (dc + 1.9, b)]
                for (s0, s1) in segs:
                    if s1 - s0 > 0.6: sh(R, face, yw, s0, s1, z=z, rows=rows, frame='walnut')
        for z in (UP - 0.55, R.hi - 1.3):
            y0, y1 = (yw, yw + 0.6) if sg > 0 else (yw - 0.6, yw)
            R.nocol.add(box(PX0, y0, z, PX1, y1, z + 0.25, 'tile'))
        # lamps up the facade
        for x in PIL:
            for (z, m) in ((3.2, 'e_dim'), (UP + 2.5, 'e_amber'), (UP + 5.6, 'e_dim')):
                R.light(sphere(x, yw + sg * 0.62, z, 0.1, 8, 4, m))


def room(R):
    """The room slung under the bridge: a plank box on chains, its roof a ledge beside the bridge (railed),
    a hatch in the ledge and a steep ladder down inside. A hammock-bed, a desk with a lamp, maps, books,
    windows onto the dark."""
    x0, x1, y0, y1 = RX0, RX1, RY0, RY1
    R.parts.add(box(x0, y0, RZ - 0.25, x1, y1, RZ, 'walnut', top='oak'))
    wt = 0.12
    # walls, with windows (sills at 1 m so nobody steps out)
    def wall(ax0, ay0, ax1, ay1, wins):
        along_x = abs(ax1 - ax0) > abs(ay1 - ay0)
        a, b = (ax0, ax1) if along_x else (ay0, ay1)
        cuts = sorted(wins)
        p = a
        for (c, hw) in cuts + [(None, 0)]:
            q = b if c is None else c - hw
            if q - p > 0.01:
                if along_x: R.parts.add(box(p, ay0, RZ, q, ay1, 7.42, 'walnut'))
                else: R.parts.add(box(ax0, p, RZ, ax1, q, 7.42, 'walnut'))
            if c is not None:
                if along_x:
                    R.parts.add(box(c - hw, ay0, RZ, c + hw, ay1, RZ + 1.0, 'walnut'))
                    R.parts.add(box(c - hw, ay0, RZ + 2.0, c + hw, ay1, 7.42, 'walnut'))
                else:
                    R.parts.add(box(ax0, c - hw, RZ, ax1, c + hw, RZ + 1.0, 'walnut'))
                    R.parts.add(box(ax0, c - hw, RZ + 2.0, ax1, c + hw, 7.42, 'walnut'))
                p = c + hw
    wall(x0, y0, x1, y0 + wt, [(30.0, 0.5), (34.0, 0.5)])
    wall(x0, y1 - wt, x1, y1, [(33.0, 0.6)])
    wall(x0, y0 + wt, x0 + wt, y1 - wt, [(16.5, 0.5)])
    wall(x1 - wt, y0 + wt, x1, y1 - wt, [(16.2, 0.5)])
    # the roof beside the bridge: the ledge you step down onto, with a rail round it and a hatch
    hx0, hx1, hy0, hy1 = 30.4, 32.2, LADY - 0.55, LADY + 0.6
    for (a0, b0, a1, b1) in ((x0, BY1, x1, hy0), (x0, hy1, x1, y1), (x0, hy0, hx0, hy1), (hx1, hy0, x1, hy1)):
        R.parts.add(box(a0, b0, 7.42, a1, b1, LZ, 'oak', bottom='walnut', sides='walnut'))
    rail_line(R, [(x0 + 0.05, BY1 + 0.05), (x0 + 0.05, y1 - 0.05), (x1 - 0.05, y1 - 0.05), (x1 - 0.05, BY1 + 0.05)], LZ, m='iron')
    rail_line(R, [(hx0, hy1 + 0.05), (hx1 + 0.05, hy1 + 0.05), (hx1 + 0.05, hy0 - 0.05), (hx0, hy0 - 0.05)], LZ, m='iron')
    ladder_up(R, 33.4, LADY, RZ, LZ, '-x', w=1.0, m='oak', rail='iron', ang=math.radians(45))
    # chains from the bridge's piers down to the room's corners
    for (x, y, px) in ((x0 + 0.1, y1 - 0.1, 27.7), (x1 - 0.1, y1 - 0.1, 36.3)):
        R.nocol.add(beam((x, y, LZ), (px, BY1 - 0.2, UP + 1.15), 0.05, 'iron'))
    # inside: a bed hung like a hammock, a desk and lamp, books, maps on the wall, a candle
    R.parts.add(box(34.0, 14.9, RZ + 0.35, 35.8, 15.85, RZ + 0.55, 'bed', sides='velvet'))
    for x in (34.05, 35.75):
        R.nocol.add(box(x - 0.02, 15.35, RZ + 0.55, x + 0.02, 15.4, 7.42, 'iron'))
    R.spot('bed', 34.9, 15.4, RZ + 0.55, 0.0)
    desk(R, 29.4, 15.3, 0.0, z=RZ, w=1.5, d=0.7)
    desk_lamp(R, 29.0, 15.3, RZ + 0.78)
    open_book(R, 29.7, 15.35, RZ + 0.78, 0.2)
    R.parts.add(chair(29.4, 16.1, -math.pi / 2).xform(0, 0, 0, RZ))
    R.spot('sit', 29.4, 16.1, RZ + 0.48, -math.pi / 2)
    sh(R, '-x', x1 - wt, 17.4, 19.6, z=RZ, rows=5, frame='walnut', depth=0.26)
    for (x, y) in ((31.0, 14.83), (32.8, 14.83)):
        R.nocol.add(box(x - 0.4, y, RZ + 1.3, x + 0.4, y + 0.01, RZ + 1.9, 'ivory'))
    candle(R, 33.3, 16.8, RZ, h=0.2)
    book_pile(R, 33.8, 17.2, RZ, 7, seed=2)
    hanging(R, 32.0, 16.4, 7.4, 6.5, r=0.35, e='e_lamp', shade='green')
    hanging(R, 29.6, 18.9, 7.4, 6.6, r=0.2, e='e_candle')
    R.light(sphere(x0 + 0.4, y1 - 0.4, LZ + 1.2, 0.08, 8, 4, 'e_amber'))
    R.spot('plaque', 30.6, 14.83, RZ + 1.6, math.pi / 2, text='IN CASE OF FALLING, YOU ARE ALREADY HALFWAY.')
    secret(R, 32.0, 16.5, RZ, 'The Room Under the Bridge',
           'Over the side, down an iron ladder and through a hatch: a plank room hung under the span on chains, swaying very slightly. Someone slept here, with the void on every side and a lamp for company.', r=2.2)


def floor(R):
    """The bottom of the void: dark slate, and what has fallen from the bridge over the years."""
    rnd = rng(60)
    g = Geo()
    for k in range(500):
        x, y = rnd.uniform(PX0 + 1, PX1 - 1), rnd.uniform(1.5, D - 1.5)
        if abs(y - 16) < 5 and rnd.random() < 0.3: continue
        book_scatter(g, x, y, 0.0, rnd, 1, spread=0.0, tilt=0.2)
    R.nocol.add(g)
    for (x, y) in ((20.0, 12.0), (44.0, 20.0), (32.0, 6.0), (31.0, 26.0)):
        lamppost(R, x, y, h=2.8, e='e_candle', r=0.12)
    # an open book face down under the middle of the span, where things tend to land
    open_book(R, 32.0, 16.0, 0.0, 0.4)
