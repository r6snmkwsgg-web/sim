"""The Drain: a round reading room inside a ring of columns, raised on a stepped plinth, whose floor tilts
gently toward a black hole in the middle. The rugs have slid, the armchairs lean, a table has gone half
over, books lie strewn toward the lip where a brass rail stops the rest. Inside the drain an iron ladder
goes down to the grating at the bottom, and a low door off it opens into a ring room under the tilted
floor, where everything the drain has swallowed has been put away."""
from kit_h7 import *

W = D = 32.0
CX = CY = 16.0
RH = 4.6                       # the hole
RF = 11.0                      # where the tilt begins (the flat rim runs out to the plinth)
RP = 12.3                      # the plinth's top edge; steps down to RP + 0.9
ZR, ZH = 1.0, -0.5             # rim and lip heights
ZB = -2.15                     # the drain's floor (and the ring room's)
RR0, RR1 = 5.0, 10.4           # the ring room
RC = 13.9                      # the ring of columns
SLOPE = math.atan((ZR - ZH) / (RF - RH))
LAD = math.pi                  # where the ladder is (on an axis, so the walk check can climb it)
RDOOR = math.radians(145)      # the ring room's door off the drain


def zf(r):
    if r >= RF: return ZR
    return ZH + (ZR - ZH) * (r - RH) / (RF - RH)


def make():
    R = Room('drain', 2, 2, res=2048, lo=-4.0)
    R.sockets(floor='terrazzo', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, TOP - 0.1, 'tile', bottom='terrazzo', top='plaster'))
    floor(R)
    columns(R)
    slid(R)
    ring_room(R)
    lights(R)
    navloop(R, [(2.2, 2.2), (16, 1.6), (29.8, 2.2), (30.4, 16), (29.8, 29.8), (16, 30.4), (2.2, 29.8), (1.6, 16)])
    rim = navloop(R, [(CX + 11.6 * math.cos(a), CY + 11.6 * math.sin(a)) for a in [math.radians(15 + 45 * k) for k in range(8)]], z=ZR)
    return finish(R, 'The Drain', weight=3, probe=(CX + 8.0, CY, 2.6),
                  blurb='The floor of this room tilts, very gently, toward a hole in the middle. Everything in it has been sliding that way for a long time. You keep one hand on the rail without meaning to.')


def floor(R):
    """The plinth steps, the tilted floor (a shell of marble), the lip, the rail, the drain and its grate."""
    for k in range(4):
        r1 = RP + 0.9 - 0.3 * k
        R.parts.add(ring(CX, CY, 0.0, 0.25 * (k + 1), RF - 0.1, r1, 64, top='terrazzo', bottom='tile', inner='tile', outer='tile'))
    # the tilted floor: a cone shell from the rim down to the lip, solid down to the old floor where it is above it
    n = 10
    top = [(RH + (RF - RH) * i / n, zf(RH + (RF - RH) * i / n)) for i in range(n + 1)]
    # (r, z) polygon: along the top from the rim in to the lip, down, back out along the underside
    prof = [(RF, ZR)] + [(r, z) for (r, z) in top[::-1][1:]] + [(RH, ZH - 0.15)]
    for (r, z) in top[1:]:
        if r < RR1: prof.append((r, z - 0.15))
    prof += [(RR1 + 0.05, zf(RR1 + 0.05) - 0.15), (RR1 + 0.05, 0.0), (RF, 0.0)]
    mats = ['terrazzo'] * n + ['tile'] + ['plaster'] * (len(prof) - n - 1)
    R.parts.add(lathe(CX, CY, prof, 64, mats))
    # cut away the old floor under the tilt: the ring room, the band by the lip, the drain
    R.cut(lathe(CX, CY, [(RR0, ZB), (RR1, ZB), (RR1, zf(RR1) - 0.15), (RR0, zf(RR0) - 0.15)], 64, 'plaster'))
    R.cut(cyl(CX, CY, -0.75, 0.3, RR0 + 0.02, 64, side='tile', top='tile', bottom='tile'))
    R.cut(cyl(CX, CY, ZB, 0.3, RH, 48, side='slate', top='slate', bottom='black'))
    R.cut(cyl(CX, CY, -3.9, 0.3, 2.4, 32, side='black', top='black', bottom='black'))
    # the lip: a rounded stone kerb, gilt edge; the rail round it (open where the ladder comes up)
    R.parts.add(ring(CX, CY, ZH - 0.4, ZH + 0.12, RH - 0.05, RH + 0.35, 64, top='tile', bottom='tile', inner='slate', outer='tile'))
    R.nocol.add(ring(CX, CY, ZH + 0.12, ZH + 0.15, RH - 0.06, RH + 0.05, 64, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    gap = 0.14
    ring_rail(R, CX, CY, RH + 0.22, ZH + 0.12, LAD + gap, LAD + 2 * math.pi - gap, n=40, m='brass')
    # the drain: slate walls, a grating over the deeper dark, the iron ladder
    R.col.add(cyl(CX, CY, ZB - 0.05, ZB, 2.45, 24))
    for k in range(-5, 6):
        o = k * 0.42
        h = math.sqrt(max(0.0, 2.45 ** 2 - o * o))
        R.nocol.add(box(CX + o - 0.03, CY - h, ZB - 0.06, CX + o + 0.03, CY + h, ZB, 'iron'))
        R.nocol.add(box(CX - h, CY + o - 0.03, ZB - 0.08, CX + h, CY + o + 0.03, ZB - 0.02, 'iron'))
    R.nocol.add(ring(CX, CY, ZB - 0.08, ZB, 2.35, 2.5, 32, top='iron', bottom='iron', inner='iron', outer='iron'))
    dx, dy = math.cos(LAD), math.sin(LAD)
    L = (ZH + 0.12 - ZB) / math.tan(math.radians(60))
    r_foot = RH - 0.05 - L
    # ladder_up takes an axis name; build it along +x at the origin and turn it
    save = (R.nocol, R.col)
    R.nocol, R.col = Geo(), Geo()
    ladder_up(R, 0.0, 0.0, ZB, ZH + 0.12, '+x', w=0.8, m='iron', rail='iron')
    lg, lc = R.nocol, R.col
    R.nocol, R.col = save
    lg.xform(LAD, CX + dx * r_foot, CY + dy * r_foot, 0.0); lc.xform(LAD, CX + dx * r_foot, CY + dy * r_foot, 0.0)
    R.nocol.add(lg); R.col.add(lc)


def columns(R):
    """Sixteen columns round the plinth carrying a ring of entablature; tall cases in the bays that face no door."""
    n = 16
    for k in range(n):
        a = 2 * math.pi * k / n
        x, y = CX + RC * math.cos(a), CY + RC * math.sin(a)
        R.parts.add(cyl(x, y, 0.3, 6.2, 0.36, 16, side='tile', caps=False))
        R.parts.add(box(x - 0.5, y - 0.5, 0, x + 0.5, y + 0.5, 0.3, 'tile', skip=('-z',)))
        R.parts.add(box(x - 0.5, y - 0.5, 6.0, x + 0.5, y + 0.5, 6.3, 'tile'))
    R.parts.add(ring(CX, CY, 6.3, 6.95, RC - 0.55, RC + 0.55, 64, top='tile', bottom='tile', inner='tile', outer='tile'))
    R.nocol.add(ring(CX, CY, 6.95, 7.05, RC - 0.62, RC + 0.62, 64, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    # cases in the bays centred on the axes (the others face doors)
    for k in range(n):
        am = 2 * math.pi * (k + 0.5) / n
        deg = math.degrees(am) % 360
        if not any(abs(((deg - c + 180) % 360) - 180) < 15 for c in (0, 90, 180, 270)): continue
        half = RC * math.sin(math.pi / n) - 0.5
        bx, by = CX + (RC + 0.45) * math.cos(am), CY + (RC + 0.45) * math.sin(am)
        fa = am + math.pi
        ux, uy = math.sin(fa), -math.cos(fa)
        shelf(R, bx - ux * half, by - uy * half, 0, 2 * half, fa, rows=13, frame='walnut')
    # the square corners outside the ring: cases on the walls, a table in each corner
    wall_cases(R, rows=12, frame='walnut')
    for (x, y, a) in ((4.2, 4.2, math.pi / 4), (27.8, 4.2, 3 * math.pi / 4), (27.8, 27.8, -3 * math.pi / 4), (4.2, 27.8, -math.pi / 4)):
        g = table(-0.9, -0.45, 0.9, 0.45, 0.78, 'walnut', top='leather'); g.xform(a, x, y, 0); R.parts.add(g)
        desk_lamp(R, x, y, 0.78)


def slid(R):
    """What has slid: rugs on the tilt (one over the lip), leaning armchairs, a table gone half over, chairs,
    a globe against the rail, books strewn down toward the hole."""
    rnd = rng(66)
    def at(r, a):
        return CX + r * math.cos(a), CY + r * math.sin(a)
    # rugs
    for (r, a, L, Wd, tw) in ((7.8, math.radians(30), 3.2, 2.0, 0.3), (8.2, math.radians(140), 3.6, 2.4, -0.2), (7.0, math.radians(255), 3.0, 1.9, 0.5)):
        x, y = at(r, a)
        g = box(-L / 2, -Wd / 2, 0.0, L / 2, Wd / 2, 0.015, 'oxblood')
        g.add(box(-L / 2 + 0.2, -Wd / 2 + 0.2, 0.015, L / 2 - 0.2, Wd / 2 - 0.2, 0.02, 'carpet'))
        g.xform(tw, 0, 0, 0)
        R.nocol.add(tilt_place(g, x, y, zf(r) + 0.005, a + math.pi, SLOPE))
    # the rug that has gone over the lip: on the slope, then hanging down into the drain
    a = math.radians(320)
    x, y = at(RH + 1.1, a)
    g = box(-1.1, -0.9, 0, 1.1, 0.9, 0.015, 'carpet'); g.add(box(-1.1, -0.9, 0.015, 1.1, -0.75, 0.02, 'oxblood'))
    R.nocol.add(tilt_place(g, x, y, zf(RH + 1.1) + 0.01, a + math.pi, SLOPE))
    g = box(-0.012, -0.9, -1.3, 0.0, 0.9, 0.0, 'carpet')
    rot(g, 'y', -0.12)
    x, y = at(RH - 0.08, a)
    R.nocol.add(g.xform(a + math.pi, x, y, ZH + 0.13))
    # armchairs leaning
    for (r, a) in ((8.6, math.radians(20)), (7.2, math.radians(95)), (9.3, math.radians(170)), (6.6, math.radians(300)), (9.8, math.radians(235))):
        x, y = at(r, a)
        g = Geo()
        g.add(box(-0.4, -0.4, 0, 0.4, 0.4, 0.42, 'velvet', sides='walnut'))
        g.add(box(-0.45, -0.4, 0, -0.3, 0.4, 1.0, 'velvet'))
        g.add(box(-0.4, -0.48, 0, 0.35, -0.38, 0.65, 'velvet'))
        g.add(box(-0.4, 0.38, 0, 0.35, 0.48, 0.65, 'velvet'))
        g.xform(rnd.uniform(-0.6, 0.6))
        R.parts.add(tilt_place(g, x, y, zf(r), a + math.pi, SLOPE))
    # plain chairs, some tipped right over
    for (r, a, tip) in ((6.2, math.radians(60), 0.0), (5.6, math.radians(200 + 25), 1.3), (8.8, math.radians(115), 0.0), (6.0, math.radians(345), 1.4), (9.6, math.radians(70), 0.0)):
        x, y = at(r, a)
        g = chair(0, 0, rnd.uniform(0, 2 * math.pi))
        if tip: rot(g, 'x', tip); g.xform(0, 0, 0, 0.25)
        R.parts.add(tilt_place(g, x, y, zf(r), a + math.pi, SLOPE))
    # a reading table gone half over (its inner legs lower, books slid to its low edge)
    x, y = at(8.0, math.radians(190))
    g = table(-1.2, -0.5, 1.2, 0.5, 0.76, 'walnut', top='leather')
    g.xform(math.pi / 2)
    R.parts.add(tilt_place(g, x, y, zf(8.0), math.radians(190) + math.pi, SLOPE))
    # a globe against the rail
    x, y = at(RH + 0.75, math.radians(110))
    R.parts.add(sphere(x, y, ZH + 0.12 + zf(RH + 0.75) - ZH + 0.35, 0.35, 16, 8, 'green'))
    R.nocol.add(ring(x, y, zf(RH + 0.75) + 0.33, zf(RH + 0.75) + 0.37, 0.36, 0.4, 20, top='brass', bottom='brass', inner='brass', outer='brass'))
    # books everywhere down the slope, thicker toward the lip
    g = Geo()
    for k in range(170):
        r = RH + 0.5 + (RF - RH - 0.8) * rnd.random() ** 1.8
        a = rnd.uniform(0, 2 * math.pi)
        x, y = at(r, a)
        b = Geo()
        book_scatter(b, 0, 0, 0, rnd, 1, spread=0.0, tilt=0.0)
        g.add(tilt_place(b, x, y, zf(r) + 0.003, a + math.pi, SLOPE))
    R.nocol.add(g)
    # a few open books caught on the lip
    for a in (0.4, 1.9, 2.8, 4.4, 5.6):
        x, y = at(RH + 0.5, a)
        open_book(R, x, y, zf(RH + 0.5) + 0.02, a + 1.2)


def ring_room(R):
    """Under the tilted floor: a low ring room round the drain, its ceiling sloping down toward the middle.
    Everything the drain swallowed has been shelved here."""
    # the door off the drain
    dx, dy = math.cos(RDOOR), math.sin(RDOOR)
    R.cut(obox(CX + dx * (RH - 0.3), CY + dy * (RH - 0.3), CX + dx * (RR0 + 0.4), CY + dy * (RR0 + 0.4), ZB, ZB + 1.45, 1.15, 'slate', bottom='oak', top='slate'))
    R.nocol.add(ring(CX, CY, ZB, ZB + 0.01, RR0, RR1, 64, top='oak', bottom='oak', inner='oak', outer='oak'))
    # cases round the outer wall, facing in (low: the ceiling comes down)
    n = 12
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        if abs(((a - RDOOR + math.pi) % (2 * math.pi)) - math.pi) < 0.2: continue
        half = RR1 * math.sin(math.pi / n) - 0.12
        bx, by = CX + (RR1 - 0.05) * math.cos(a), CY + (RR1 - 0.05) * math.sin(a)
        fa = a + math.pi
        ux, uy = math.sin(fa), -math.cos(fa)
        shelf(R, bx - ux * half, by - uy * half, ZB, 2 * half, fa, rows=5, frame='walnut')
    rnd = rng(7)
    # heaps of books, a bed of cushions, a lamp, a chair, a plaque
    for k in range(9):
        a = rnd.uniform(0, 2 * math.pi)
        if abs(((a - RDOOR + math.pi) % (2 * math.pi)) - math.pi) < 0.5: continue
        r = rnd.uniform(RR0 + 0.6, RR0 + 1.6)
        book_pile(R, CX + r * math.cos(a), CY + r * math.sin(a), ZB, rnd.randint(4, 9), seed=k, col=False)
    a = RDOOR + 0.9
    x, y = CX + 8.4 * math.cos(a), CY + 8.4 * math.sin(a)
    g = box(-1.0, -0.6, 0, 1.0, 0.6, 0.25, 'velvet', sides='oxblood')
    g.add(box(-0.95, -0.55, 0.25, -0.5, 0.55, 0.4, 'bed'))
    g.xform(a + math.pi / 2, x, y, ZB); R.parts.add(g)
    R.spot('bed', x, y, ZB + 0.25, a)
    a = RDOOR - 0.8
    x, y = CX + 8.6 * math.cos(a), CY + 8.6 * math.sin(a)
    R.parts.add(chair(x, y, a + math.pi).xform(0, 0, 0, ZB))
    R.spot('sit', x, y, ZB + 0.48, a + math.pi)
    x2, y2 = CX + 8.6 * math.cos(a - 0.2), CY + 8.6 * math.sin(a - 0.2)
    R.parts.add(cyl(x2, y2, ZB, ZB + 0.6, 0.25, 12, side='walnut', top='walnut'))
    desk_lamp(R, x2, y2, ZB + 0.6)
    for k in range(6):
        a = RDOOR + math.pi + (k - 2.5) * 0.9
        x, y = CX + 8.0 * math.cos(a), CY + 8.0 * math.sin(a)
        R.light(sphere(x, y, zf(8.0) - 0.45, 0.09, 8, 4, 'e_lamp' if k % 2 == 0 else 'e_candle'))
        R.nocol.add(cyl(x, y, zf(8.0) - 0.4, zf(8.0) - 0.15, 0.008, 4, side='iron', caps=False))
    for a in (RDOOR + 0.35, RDOOR - 0.35, RDOOR + math.pi):
        candle(R, CX + (RR0 + 0.3) * math.cos(a), CY + (RR0 + 0.3) * math.sin(a), ZB, h=0.2)
    a = RDOOR + math.pi / 2
    R.spot('plaque', CX + (RR1 - 0.4) * math.cos(a), CY + (RR1 - 0.4) * math.sin(a), ZB + 1.6, a + math.pi,
           text='LOST PROPERTY. EVERYTHING ARRIVES HERE EVENTUALLY.')
    a = RDOOR + 0.5
    secret(R, CX + 7.0 * math.cos(a), CY + 7.0 * math.sin(a), ZB, 'The Ring Under the Floor',
           'Down the ladder, through a low door, and under the tilted floor there is a round room of everything the drain has swallowed, dried out and shelved. Someone has been sleeping on the cushions.', r=2.0)


def lights(R):
    # a chandelier hanging over the drain, pendants between the columns, lamps under the entablature
    R.nocol.add(cyl(CX, CY, 5.6, TOP - 0.1, 0.02, 6, side='iron', caps=False))
    R.nocol.add(ring(CX, CY, 5.1, 5.18, 1.3, 1.42, 32, top='brass', bottom='brass', inner='brass', outer='brass'))
    for k in range(12):
        a = 2 * math.pi * k / 12
        R.nocol.add(beam((CX, CY, 5.6), (CX + 1.36 * math.cos(a), CY + 1.36 * math.sin(a), 5.15), 0.025, 'brass'))
        R.light(sphere(CX + 1.36 * math.cos(a), CY + 1.36 * math.sin(a), 5.3, 0.08, 8, 4, 'e_lamp'))
    for k in range(8):
        a = 2 * math.pi * (k + 0.25) / 8
        pendant(R, CX + 11.8 * math.cos(a), CY + 11.8 * math.sin(a), 4.2, TOP - 0.1, r=0.22)
    for k in range(16):
        a = 2 * math.pi * (k + 0.5) / 16
        R.light(sphere(CX + (RC + 0.7) * math.cos(a), CY + (RC + 0.7) * math.sin(a), 6.0, 0.1, 8, 4, 'e_amber'))
