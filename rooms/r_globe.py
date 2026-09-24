"""The Globe: a giant bronze globe caged in armillary rings stands on a pedestal in a stepped round
pit under a painted sky. A railed walk circles the pit; books line the walls."""
from lib import *
from kit_a import *

H = 7.0
CX = CY = C / 2
GZ, GR = 3.1, 1.9          # globe centre height, radius
PR, PD = 4.3, 1.5          # pit radius, depth


def band(r0, r1, t, segs, m):
    """A flat ring (annulus) in the x-y plane about the origin, t thick: an armillary hoop."""
    g = Geo()
    ang = [2 * math.pi * k / segs for k in range(segs)]
    P = lambda r, a, z: (r * math.cos(a), r * math.sin(a), z)
    ob = [g.vert(P(r1, a, -t / 2)) for a in ang]; ot = [g.vert(P(r1, a, t / 2)) for a in ang]
    ib = [g.vert(P(r0, a, -t / 2)) for a in ang]; it = [g.vert(P(r0, a, t / 2)) for a in ang]
    for k in range(segs):
        j = (k + 1) % segs
        u = [(0, 0), (1, 0), (1, 1), (0, 1)]
        g.face([ot[k], ot[j], it[j], it[k]], m, u)
        g.face([ib[k], ib[j], ob[j], ob[k]], m, u)
        g.face([ob[k], ob[j], ot[j], ot[k]], m, u)
        g.face([it[k], it[j], ib[j], ib[k]], m, u)
    return g


def hoop(r, w, t, tilt_x, spin_z, m='bronze', segs=24, tilt_y=0.0):
    """An armillary hoop of radius r (w wide radially, t thick), tilted, around the globe's centre."""
    g = band(r - w, r, t, segs, m)
    if tilt_x: rot(g, 'x', tilt_x)
    if tilt_y: rot(g, 'y', tilt_y)
    if spin_z: rot(g, 'z', spin_z)
    g.v = [(x + CX, y + CY, z + GZ) for x, y, z in g.v]
    return g


def make():
    R = Room('globe', 1, 1, res=1024)
    shell(R, wall='tile', floor='terrazzo', ceil='plaster', h=H)
    # a round recess in the ceiling, painted with a sky
    R.cut(cyl(CX, CY, H - 0.05, R.hi - 0.1, 5.2, 32, side='plaster', top='plaster', bottom='plaster'))
    R.light(cyl(CX, CY, R.hi - 0.13, R.hi - 0.11, 5.2, 32, side='e_skydome', top='e_skydome', bottom='e_skydome'))
    R.nocol.add(ring(CX, CY, H - 0.25, H, 5.2, 5.5, 32, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    # the stepped pit
    R.round_pool(CX, CY, PR, PD, m='terrazzo', segs=32)
    for k in range(8):
        a = math.pi / 8 + k * math.pi / 4
        for (d, rr) in ((0.3, PR - 0.02), (0.9, PR - 0.92)):
            g = box(-0.2, -0.03, -d + 0.08, 0.2, 0.0, -d + 0.18, 'e_pool').xform(a + math.pi / 2, CX + math.cos(a) * rr, CY + math.sin(a) * rr)
            R.light(g)
    # a bronze curb and a brass rail round the walk, with four gaps to step down
    for q in range(4):
        a0, a1 = q * math.pi / 2 + math.radians(14), q * math.pi / 2 + math.radians(76)
        R.parts.add(ring(CX, CY, 0, 0.12, PR + 0.02, PR + 0.3, 16, top='bronze', bottom='bronze', inner='bronze', outer='bronze', a0=a0, a1=a1))
        n = 4
        pts = [(CX + (PR + 0.16) * math.cos(a0 + (a1 - a0) * i / n), CY + (PR + 0.16) * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            pass
    # the pedestal: a stepped drum and a fluted stem
    zb = -PD
    R.parts.add(cyl(CX, CY, zb, zb + 0.35, 1.25, 24, side='tile', top='tile'))
    R.parts.add(cyl(CX, CY, zb + 0.35, zb + 0.6, 0.95, 24, side='tile', top='tile'))
    R.parts.add(cyl(CX, CY, zb + 0.6, GZ - GR + 0.1, 0.32, 16, side='bronze', caps=False))
    R.parts.add(cyl(CX, CY, GZ - GR - 0.3, GZ - GR + 0.15, 0.55, 24, side='bronze', top='bronze', bottom='bronze'))
    # the globe, its axis tilted, and its cage of hoops
    tilt = math.radians(23.4)
    R.nocol.add(sphere(CX, CY, GZ, GR, 24, 12, 'bronze'))
    import random
    rnd = random.Random(9)
    for _ in range(8):   # continents nobody has charted: gilt blisters on the bronze
        la, lo, rr = rnd.uniform(-1.1, 1.1), rnd.uniform(0, 2 * math.pi), rnd.uniform(0.35, 0.8)
        d = (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))
        c = GR + 0.035 - math.sqrt(max(rr * rr, 0.0))
        g = sphere(d[0] * c, d[1] * c, d[2] * c, rr, 8, 4, 'gilt')
        rot(g, 'y', math.radians(23.4)); g.v = [(x + CX, y + CY, z + GZ) for x, y, z in g.v]
        R.nocol.add(g)
    for lat in (-0.7, 0.0, 0.7):     # graticule rings raised on the globe
        r = GR * math.cos(lat) + 0.02
        g = band(r - 0.03, r, 0.03, 20, 'gilt')
        g.v = [(x, y, z + GR * math.sin(lat)) for x, y, z in g.v]
        rot(g, 'y', tilt); g.v = [(x + CX, y + CY, z + GZ) for x, y, z in g.v]
        R.nocol.add(g)
    for k in range(4):                          # meridians
        g = band(GR - 0.01, GR + 0.02, 0.03, 20, 'gilt')
        rot(g, 'x', math.pi / 2); rot(g, 'z', k * math.pi / 4); rot(g, 'y', tilt)
        g.v = [(x + CX, y + CY, z + GZ) for x, y, z in g.v]
        R.nocol.add(g)
    R.nocol.add(beam((CX - math.sin(tilt) * (GR + 0.9), CY, GZ - math.cos(tilt) * (GR + 0.9)),
                     (CX + math.sin(tilt) * (GR + 0.9), CY, GZ + math.cos(tilt) * (GR + 0.9)), 0.07, 'brass'))
    RH = GR + 0.55
    R.nocol.add(hoop(RH, 0.12, 0.06, math.pi / 2, 0.0, 'bronze', tilt_y=tilt))          # the meridian
    R.nocol.add(hoop(RH - 0.14, 0.1, 0.05, 0.0, 0.0, 'gilt', tilt_y=tilt))              # the equator
    R.nocol.add(hoop(RH - 0.14, 0.28, 0.04, 0.41, 0.0, 'bronze', tilt_y=tilt))          # the ecliptic, broad
    R.nocol.add(hoop(RH - 0.28, 0.08, 0.05, math.pi / 2, math.pi / 2, 'bronze', tilt_y=tilt))  # the colure
    R.nocol.add(hoop(RH + 0.35, 0.16, 0.08, 0.0, 0.0, 'bronze', segs=32))                # the horizon, level
    for k in range(4):   # legs from the horizon ring down to the pedestal's drum
        a = math.pi / 4 + k * math.pi / 2
        R.nocol.add(beam((CX + (RH + 0.27) * math.cos(a), CY + (RH + 0.27) * math.sin(a), GZ),
                         (CX + 1.1 * math.cos(a), CY + 1.1 * math.sin(a), zb + 0.35), 0.1, 'bronze'))
    # lamps on brass posts round the walk, turned on the globe
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        x, y = CX + (PR + 1.3) * math.cos(a), CY + (PR + 1.3) * math.sin(a)
        R.parts.add(cyl(x, y, 0, 0.05, 0.22, 12, side='brass', top='brass'))
        R.parts.add(cyl(x, y, 0.05, 2.6, 0.03, 6, side='brass', caps=False))
        R.light(sphere(x, y, 2.75, 0.16, 10, 5, 'e_lamp'))
        R.parts.add(cyl(x, y, 2.85, 2.95, 0.22, 12, side='brass', top='brass', bottom='brass'))
    # books all round the walls
    for (a, b) in ((0.6, 6.2), (9.8, C - 0.6)):
        for f, w in (('+y', T), ('-y', C - T), ('+x', T), ('-x', C - T)):
            sh(R, f, w, a, b, rows=10, frame='walnut')
    for f, w in (('+y', T), ('-y', C - T), ('+x', T), ('-x', C - T)):
        sh(R, f, w, 6.2, 9.8, z=4.25, rows=5, frame='walnut')
    for (x, y) in ((1.4, 1.4), (C - 1.4, 1.4), (C - 1.4, C - 1.4), (1.4, C - 1.4)):
        R.light(sphere(x, y, 5.9, 0.15, 10, 5, 'e_lamp'))
        R.nocol.add(cyl(x, y, 6.0, H, 0.012, 6, side='brass', caps=False))
    ringp = [R.navpt(CX + (PR + 0.9) * math.cos(k * math.pi / 4 + math.pi / 8), CY + (PR + 0.9) * math.sin(k * math.pi / 4 + math.pi / 8)) for k in range(8)]
    R.link(*ringp, ringp[0])
    for k in range(4):
        d = R.navpt(CX + 6.2 * math.cos(k * math.pi / 2), CY + 6.2 * math.sin(k * math.pi / 2))
        R.link(d, ringp[(2 * k) % 8]); R.link(d, ringp[(2 * k + 7) % 8])
    R.spot('probe', CX + 5.0, CY - 5.0, 1.8)
    R.meta.update(label='The Globe', weight=5,
                  blurb='A globe of some other world, caged in bronze hoops. None of the coastlines are ones you know. The library is not marked on it.')
    R.meta['box'] = [[T, -PD, T], [C - T, H, C - T]]
    return tidy(R)
