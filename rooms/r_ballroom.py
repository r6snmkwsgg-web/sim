"""The Ballroom: a vaulted ballroom of books in the middle of a party, and nobody at it. Chandeliers lit,
streamers hanging, confetti on the parquet, glasses half full on the white tables, one wall a great
mirror in which the room is fuller than it looks. Over the north end the musicians' gallery; its stair is
hidden in the wall, behind a bookcase that is not there."""
from kit_h10 import *

W = D = 32.0
YN = 28.5                           # the hall's north wall
NX0, NX1 = 6.3, 25.7                # the nave between the arcades
JAMB, RISE = 4.9, 2.5
AZ = 4.3                            # the aisles' ceiling; the balconies over them
GX0, GX1, GY0, GY1, GZ = 10.0, 22.0, 26.4, 31.3, 3.8     # the musicians' gallery (and its balcony into the hall)
SWY0, SWY1 = 29.0, 30.3                                  # the stairwell inside the north wall
SN, SR, SRUN = 19, GZ / 19, 0.3
SXF = 20.6                                               # the stair's foot (it climbs -x)
SXT = SXF - SN * SRUN                                    # its top
FX0, FX1 = 20.7, 21.9                                    # the false bookcase into it


def make():
    R = Room('ballroom', 2, 2, res=2048)
    R.sockets(floor='floor', wall='tile')
    vault_cut(R, 'y', 16.0, NX1 - NX0 + 0.04, T - 0.02, YN, 0.0, JAMB, rise=RISE, m='plaster', floor='floor', wall='tile')
    for (x0, x1) in ((T - 0.02, NX0 + 0.1), (NX1 - 0.1, W - T + 0.02)):
        R.cut(box(x0, T - 0.02, 0, x1, YN, AZ, 'tile', bottom='floor', top='plaster'))
        R.cut(box(x0, T - 0.02, AZ + 0.3, x1, YN, TOP - 0.2, 'tile', bottom='oak', top='plaster'))
    ribs(R, 'y', 16.0, NX1 - NX0, [4.0 * k for k in range(1, 7)], 0.0, JAMB, rise=RISE, d=0.3, t=0.4, m='gilt')
    tunnel_y(R, 8.0, YN - 0.05, D - T - 0.5)
    tunnel_y(R, 24.0, YN - 0.05, D - T - 0.5)
    arcades(R)
    walls(R)
    gallery(R)
    party(R)
    lights(R)
    R.meta['mirrors'] = [{'c': [16.0, T + 0.03, 0.2], 'n': [0, 1, 0], 'w': 10.6, 'h': 4.6}]
    navloop(R, [(9.0, 4.0), (16.0, 6.0), (23.0, 4.0), (24.0, 14.0), (23.0, 24.5), (16.0, 22.0), (9.0, 24.5), (8.0, 14.0)])
    a, c = R.navpt(3.0, 10.0), R.navpt(9.0, 10.0); R.link(a, c, 0)
    b, d = R.navpt(29.0, 10.0), R.navpt(23.0, 10.0); R.link(b, d, 2)
    e, f = R.navpt(12.0, 28.4, GZ), R.navpt(20.0, 27.4, GZ); R.link(e, f)
    secret(R, 12.5, 29.5, GZ, "The Musicians' Gallery",
           'Up the hidden stair, the musicians\' gallery: chairs, music stands, a harp, a cello laid down mid-bar. The music on the stands is the tune that has been in your head since you came into the library. You never heard where it was coming from.')
    fx(R, 'afterimage', [NX0 + 0.5, 3.0, 0.0, NX1 - 0.5, 25.0, 3.0])
    fx(R, 'dust', [NX0, 2.0, 1.0, NX1, 26.0, 7.0])
    return done(R, 'The Ballroom', weight=4, probe=(16.0, 14.0, 2.5),
                blurb='The party is in full swing: the chandeliers blaze, the glasses are poured, the streamers are still falling. Nobody is dancing. In the mirror, just for a moment, somebody is.')


# ---------------------------------------------------------------------------
def arcades(R):
    for x in (NX0, NX1):
        for k in range(1, 7):
            y = 4.0 * k
            g = Geo()
            g.add(box(x - 0.45, y - 0.45, 0, x + 0.45, y + 0.45, 0.5, 'tile', skip=('-z',)))
            g.add(cyl(x, y, 0.5, AZ - 0.35, 0.32, 16, side='tile', caps=False))
            g.add(box(x - 0.5, y - 0.5, AZ - 0.4, x + 0.5, y + 0.5, AZ, 'gilt', skip=('+z',)))
            R.parts.add(g)
        # the balcony's edge over the arcade, balustraded (not reachable: for the look)
        R.parts.add(box(x - 0.35, T, AZ, x + 0.35, YN, AZ + 0.3, 'tile'))
        balustrade_x(R, x, T + 0.3, YN - 0.3, AZ + 0.3)
        R.parts.add(box(x - 0.3, T, JAMB - 0.1, x + 0.3, YN, JAMB + 0.1, 'gilt'))


def balustrade_x(R, x, y0, y1, z):
    g = Geo()
    n = int((y1 - y0) / 0.28)
    for k in range(n + 1):
        y = y0 + (y1 - y0) * k / n
        g.add(box(x - 0.06, y - 0.06, z, x + 0.06, y + 0.06, z + 0.8, 'ivory', skip=('-z', '+z')))
    g.add(box(x - 0.14, y0, z + 0.8, x + 0.14, y1, z + 0.92, 'gilt'))
    R.nocol.add(g)


def walls(R):
    # under the arcades and on the balconies: bookcases along the outer walls
    for (x, face) in ((T, '+x'), (W - T, '-x')):
        for (a, b) in ((0.6, 6.1), (9.9, 22.1), (25.9, YN - 0.3)):
            sh(R, face, x, a, b, rows=9, frame='walnut')
        sh(R, face, x, 0.6, YN - 0.3, z=AZ + 0.3, rows=6, frame='walnut')
    for (a, b) in ((0.6, NX0 - 0.4), (NX1 + 0.4, W - 0.6)):
        sh(R, '+y', T, a, b, rows=9, frame='walnut')
        sh(R, '-y', YN, a, b, rows=9, frame='walnut')
    # the north wall under the gallery: books, the false case at its east end
    sh(R, '-y', YN, NX0 + 0.3, 6.1, rows=8, frame='walnut')
    sh(R, '-y', YN, 9.9, FX0 - 0.05, rows=8, frame='walnut')
    false_case(R, FX1, YN, FX1 - FX0, '-y', rows=8, frame='walnut', h=2.3, depth=0.4, floor='floor')
    R.cut(box(FX0 + 0.05, YN - 0.1, 0, FX1 - 0.05, SWY0 + 0.05, 2.3, 'wood', bottom='floor', top='wood'))
    sh(R, '-y', YN, FX1 + 0.05, 22.1, rows=8, frame='walnut')
    sh(R, '-y', YN, 25.9, NX1 - 0.3, rows=8, frame='walnut')
    # the south wall: the great mirror between the doors, in a gilt frame
    x0, x1, z1 = 16.0 - 5.3, 16.0 + 5.3, 0.2 + 4.6
    g = Geo()
    g.add(box(x0 - 0.25, T, 0, x0, T + 0.12, z1 + 0.25, 'gilt'))
    g.add(box(x1, T, 0, x1 + 0.25, T + 0.12, z1 + 0.25, 'gilt'))
    g.add(box(x0 - 0.25, T, z1, x1 + 0.25, T + 0.12, z1 + 0.4, 'gilt'))
    g.add(box(x0, T, 0, x1, T + 0.12, 0.2, 'gilt'))
    R.parts.add(g)
    R.parts.add(box(x0, T, 0.2, x1, T + 0.01, z1, 'black'))


def gallery(R):
    """The musicians' gallery: a loggia in the north wall at GZ with a balcony out over the floor; its
    stair climbs inside the wall from the false bookcase."""
    R.cut(box(GX0, YN - 0.1, GZ, GX1, GY1, TOP - 0.3, 'damask', bottom='oak', top='plaster'))
    # the balcony out into the hall, on gilt brackets
    R.parts.add(box(GX0, GY0, GZ - 0.3, GX1, YN, GZ, 'oak', sides='gilt', bottom='plaster'))
    for x in (GX0 + 0.4, 13.0, 16.0, 19.0, GX1 - 0.4):
        R.parts.add(box(x - 0.15, YN - 0.6, GZ - 1.2, x + 0.15, YN, GZ - 0.3, 'gilt'))
    for (p, q) in (((GX0 + 0.06, YN), (GX0 + 0.06, GY0 + 0.06)), ((GX0 + 0.06, GY0 + 0.06), (GX1 - 0.06, GY0 + 0.06)), ((GX1 - 0.06, GY0 + 0.06), (GX1 - 0.06, YN))):
        R.parts.add(obox(p[0], p[1], q[0], q[1], GZ, GZ + 0.9, 0.14, 'ivory', skip=('-z',)))
        R.parts.add(obox(p[0], p[1], q[0], q[1], GZ + 0.9, GZ + 1.0, 0.22, 'gilt'))
    # the stair inside the wall: a landing at the false case, then up westward
    R.cut(box(SXT - 0.02, SWY0, 0, 22.2, SWY1, TOP - 0.3, 'tile', bottom='floor', top='plaster'))
    R.flight(SXF, SWY0, 0.0, SWY1 - SWY0, SN, SR, SRUN, '-x', m='oak', riser='walnut', side='tile')
    R.parts.add(box(SXT - 0.02, SWY0, 0.0, SXT + 0.02, SWY1, GZ, 'tile'))
    # rails round the stairwell on the gallery floor (open at its west end, where the stair arrives)
    rail(R, SXT + 0.9, SWY0 - 0.05, 22.2, SWY0 - 0.05, GZ, m='brass')
    rail(R, SXT + 0.9, SWY1 + 0.05, 22.2, SWY1 + 0.05, GZ, m='brass')
    rail(R, 22.15, SWY0, 22.15, SWY1, GZ, m='brass')
    stair_rail(R, SXF - 0.3, SWY0 + 0.06, SR * 1, SXT + 1.0, SWY0 + 0.06, GZ - SR * 3, m='brass')
    bulb(R, 21.4, (SWY0 + SWY1) / 2, 3.0, r=0.09, m='e_lamp', top=TOP - 0.3)
    bulb(R, 17.0, (SWY0 + SWY1) / 2, 5.6, r=0.07, m='e_dim', top=TOP - 0.3)
    # the band: chairs in a curve, stands, a harp, a cello laid down, a piano
    rs = rng(4)
    g = Geo()
    for k, x in enumerate((11.0, 12.3, 13.6, 14.9, 16.2, 17.5, 18.8)):
        y = 27.8 + 0.4 * math.sin(k / 6 * math.pi)
        g.add(lchair(x, y + 0.5, -math.pi / 2 + rs.uniform(-0.3, 0.3), frame='gilt', seat='velvet'))
        g.add(box(x - 0.012, y - 0.2, 0.0, x + 0.012, y - 0.18, 1.1, 'iron'))
        g.add(box(x - 0.22, y - 0.25, 1.1, x + 0.22, y - 0.2, 1.4, 'iron'))
        g.add(box(x - 0.18, y - 0.27, 1.14, x + 0.18, y - 0.25, 1.38, 'ivory'))
    R.parts.add(g.xform(0, 0, 0, GZ))
    # harp
    hp = Geo()
    hp.add(beam((0, 0, 0.1), (0, 0, 1.8), 0.08, 'gilt'))
    hp.add(beam((0, 0, 1.8), (0.9, 0, 1.5), 0.08, 'gilt'))
    hp.add(beam((0.9, 0, 1.5), (0.3, 0, 0.1), 0.1, 'gilt'))
    hp.add(box(-0.2, -0.2, 0, 0.5, 0.2, 0.1, 'gilt'))
    for k in range(9):
        t = (k + 1) / 10
        hp.add(beam((0.02, 0, 0.2 + 1.5 * t), (0.3 + 0.6 * t, 0, 0.1 + 1.4 * t), 0.008, 'ivory'))
    R.nocol.add(hp.xform(0.4, 12.0, 30.4, GZ))
    R.col.add(box(11.7, 30.0, GZ, 13.0, 30.8, GZ + 1.8, 'tile'))
    # cello laid on its side
    ce = Geo()
    ce.add(blob(0, 0, 0.18, 0.4, 0.22, 0.12, 10, 4, 'walnut'))
    ce.add(beam((0.35, 0, 0.18), (1.1, 0, 0.2), 0.06, 'black'))
    R.nocol.add(ce.xform(2.3, 15.0, 29.9, GZ))
    # a small piano
    R.parts.add(box(GX0 + 0.3, 30.4, GZ, GX0 + 1.9, 31.2, GZ + 1.3, 'black'))
    R.parts.add(box(GX0 + 0.3, 30.1, GZ + 0.72, GX0 + 1.9, 30.4, GZ + 0.78, 'ivory'))
    R.parts.add(box(GX0 + 0.3, 30.1, GZ + 0.62, GX0 + 1.9, 30.4, GZ + 0.72, 'black'))
    # scattered sheet music
    sm = Geo()
    for k in range(16):
        sm.add(box(-0.1, -0.14, 0, 0.1, 0.14, 0.003, 'ivory').xform(rs.uniform(0, 3), rs.uniform(10.6, 19.0), rs.uniform(27.0, 30.8), GZ))
    R.nocol.add(sm)
    for x in (11.0, 21.0):
        sconce(R, x, GY1 - 0.1, GZ + 2.2, -math.pi / 2, m='e_amber')
    sh(R, '-y', GY1, GX0 + 2.2, SXT - 0.3, z=GZ, rows=7, frame='walnut')


def party(R):
    rs = rng(21)
    g = Geo(); gl = Geo(); cl = Geo()
    tables = []
    for x in (2.6, W - 2.6):
        for y in (4.0, 12.0, 16.0, 20.0):
            tables.append((x + (0.4 if x < 16 else -0.4), y))
    for (x, y) in ((8.6, 3.2), (23.4, 3.2), (8.8, 25.2), (23.2, 25.2)):
        tables.append((x, y))
    for (x, y) in tables:
        r = 0.75
        cl.add(cyl(x, y, 0.0, 0.76, r + 0.08, 16, side='cloth', top='cloth', bottom='cloth'))
        n = 5
        for k in range(n):
            a = 2 * math.pi * k / n + rs.uniform(-0.2, 0.2)
            d = r + 0.45 + rs.uniform(0, 0.4)
            g.add(lchair(x + math.cos(a) * d, y + math.sin(a) * d, a + math.pi + rs.uniform(-0.5, 0.5), frame='gilt', seat='velvet', back_h=0.95))
            gx, gy = x + math.cos(a) * (r - 0.2), y + math.sin(a) * (r - 0.2)
            if rs.random() < 0.8:
                gl.add(cyl(gx, gy, 0.86, 0.98, 0.03, 6, side='chrome', caps=False))
                gl.add(hdisc(gx, gy, 0.92, 0.028, 6, 'gilt'))
                gl.add(box(gx - 0.007, gy - 0.007, 0.76, gx + 0.007, gy + 0.007, 0.86, 'chrome', skip=('-z', '+z')))
        llamp(R, x, y, 0.76, rs.uniform(0, 3), lit=True, m='e_lamp')
        candles(R, [(x + 0.3, y - 0.2, 0.76), (x - 0.25, y + 0.3, 0.76)], rs, 0.08, 0.14, 0.02, 0.03)
    R.parts.add(cl); R.parts.add(g); R.nocol.add(gl)
    # streamers down from the vault and the balcony edges; confetti and dropped things on the floor
    for k in range(28):
        x = rs.uniform(NX0 + 1.0, NX1 - 1.0); y = rs.uniform(2.0, 26.0)
        dx = abs(x - 16.0) / ((NX1 - NX0) / 2)
        ztop = JAMB + RISE * math.sqrt(max(0.0, 1 - dx * dx)) - 0.1
        streamer(R, x, y, ztop, rs.uniform(1.8, 4.2), rs, m=rs.choice(('gilt', 'gilt', 'ivory', 'oxblood')), r=0.06, w=0.035)
    for x in (NX0, NX1):
        for k in range(6):
            y = rs.uniform(1.5, 27.0)
            streamer(R, x + (0.4 if x < 16 else -0.4), y, AZ + 0.2, rs.uniform(1.0, 2.8), rs, m='gilt', r=0.05, w=0.03)
    confetti(R, NX0, 1.0, NX1, 27.0, 0.0, 450, rs)
    hats = Geo()
    for k in range(6):
        c = cone(0, 0, 0.0, 0.3, 0.09, 0.005, 8, rs.choice(('oxblood', 'gilt', 'green')))
        rot(c, 'x', math.pi / 2)
        hats.add(c.xform(rs.uniform(0, 6), rs.uniform(9, 23), rs.uniform(5, 24), 0.09))
    for k in range(5):
        gg = cyl(0, 0, -0.05, 0.05, 0.03, 6, side='chrome', caps=False)
        rot(gg, 'x', math.pi / 2)
        hats.add(gg.xform(rs.uniform(0, 6), rs.uniform(9, 23), rs.uniform(5, 24), 0.03))
    R.nocol.add(hats)


def lights(R):
    for y in (7.0, 14.0, 21.0):
        chandelier(R, 16.0, y, 4.2, 1.8, n=14, chain=JAMB + RISE - 0.1, bulb=0.13, tiers=2)
    for y in (2.0, 26.5):
        for x in (2.0, W - 2.0):
            R.light(sphere(x, y, 2.6, 0.12, 8, 4, 'e_amber'))
    for x in (NX0, NX1):
        for k in range(1, 7):
            y = 4.0 * k
            sconce(R, x + (0.35 if x < 16 else -0.35), y + 0.0, 2.6, 0.0 if x < 16 else math.pi, m='e_lamp', r=0.09)
