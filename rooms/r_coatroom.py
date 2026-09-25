"""The Cloakroom: a long vaulted hall of coat rails, coats on every hook as far as you can see (and
further: the end walls are mirrors), a counter in the middle with a bell and a board of tickets nobody
has come back for. The coats hang loose; you can push through them. Behind the ones on the south wall
there is a low arch, and a narrow passage where somebody sits with one coat of their own."""
from kit_h10 import *

W, D = 32.0, 16.0
YS = 2.0                          # the hall's south wall; the passage runs behind it
JAMB, RISE = 4.3, 2.5
RZ = 1.95                         # the rails' underside (you pass under them)
RAILS = [(2.3, +1, ((1.2, 6.2), (9.8, 22.2), (25.8, 30.8))),
         (4.9, -1, ((1.4, 30.6),)), (4.9, +1, ((1.4, 30.6),)),
         (11.1, -1, ((1.4, 30.6),)), (11.1, +1, ((1.4, 30.6),)),
         (13.6, -1, ((1.2, 6.2), (9.8, 22.2), (25.8, 30.8))),
         (15.3, -1, ((1.2, 6.2), (9.8, 22.2), (25.8, 30.8)))]
PX0, PX1, PY0, PY1, PH = 10.3, 21.7, 0.45, 1.75, 2.8       # the passage
AX0, AX1 = 15.0, 16.6                                     # the arch into it
COATS = ('coat1', 'coat2', 'coat3', 'coat4', 'coat5', 'coat6', 'coat3', 'coat2', 'leather')


def make():
    R = Room('coatroom', 2, 1, res=2048)
    R.sockets(floor='floor', wall='tile')
    c = (YS + D - T) / 2
    vault_cut(R, 'x', c, D - T - YS + 0.04, T - 0.02, W - T + 0.02, 0.0, JAMB, rise=RISE, m='plaster', floor='terrazzo', wall='tile')
    ribs(R, 'x', c, D - T - YS, [T + (W - 2 * T) * k / 10 for k in range(1, 10)], 0.0, JAMB, rise=RISE, d=0.25, t=0.3)
    tunnel_y(R, 8.0, T + 0.4, YS + 0.05, floor='terrazzo')
    tunnel_y(R, 24.0, T + 0.4, YS + 0.05, floor='terrazzo')
    walls(R)
    rails(R)
    counter(R)
    passage(R)
    lights(R)
    R.meta['mirrors'] = [{'c': [T + 0.03, 12.6, 0.15], 'n': [1, 0, 0], 'w': 5.2, 'h': 3.9},
                         {'c': [W - T - 0.03, 12.6, 0.15], 'n': [-1, 0, 0], 'w': 5.2, 'h': 3.9}]
    navloop(R, [(1.8, 8.0), (8.0, 7.2), (13.0, 6.2), (19.0, 6.2), (24.0, 7.2), (30.2, 8.0), (24.0, 9.6), (19.0, 9.8), (13.0, 9.8), (8.0, 9.6)])
    a, b = R.navpt(3.0, 3.7), R.navpt(29.0, 3.7); R.link(a, b)
    a, b = R.navpt(3.0, 12.4), R.navpt(29.0, 12.4); R.link(a, b)
    secret(R, 18.5, 1.1, 0.0, 'Behind the Coats',
           'Behind the coats on the south wall there is an arch, and behind the arch a passage the width of a coat, where somebody has been sitting with a lamp, waiting for their number to be called.')
    fx(R, 'dust', [2.0, YS + 0.5, 0.5, 30.0, D - 1.0, 4.5])
    return done(R, 'The Cloakroom', weight=5, probe=(16.0, 10.0, 2.6),
                blurb='Coats, thousands of coats, on hooks as far as you can see, all of them left here by people who meant to come back for them. They are still faintly warm.')


# ---------------------------------------------------------------------------
def walls(R):
    # books above the rails on the long walls; full height on the end walls round the mirrors
    for (a, b) in ((0.6, 6.1), (9.9, 22.1), (25.9, W - 0.6)):
        sh(R, '+y', YS, a, b, z=2.3, rows=4, frame='walnut')
        sh(R, '-y', D - T, a, b, z=2.3, rows=4, frame='walnut')
    for (a, b) in ((YS + 0.3, 6.1), ):
        sh(R, '+x', T, a, b, rows=9, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=9, frame='walnut')
    for x, face in ((T, 0.0), (W - T, math.pi)):
        # the mirror's gilt frame
        s = 1 if face == 0.0 else -1
        y0, y1, z1 = 12.6 - 2.6, 12.6 + 2.6, 0.15 + 3.9
        g = Geo()
        g.add(box(min(x, x + s * 0.08), y0 - 0.12, 0.0, max(x, x + s * 0.08), y0, z1 + 0.12, 'gilt'))
        g.add(box(min(x, x + s * 0.08), y1, 0.0, max(x, x + s * 0.08), y1 + 0.12, z1 + 0.12, 'gilt'))
        g.add(box(min(x, x + s * 0.08), y0 - 0.12, z1, max(x, x + s * 0.08), y1 + 0.12, z1 + 0.14, 'gilt'))
        g.add(box(min(x, x + s * 0.08), y0 - 0.12, 0.0, max(x, x + s * 0.08), y1 + 0.12, 0.15, 'gilt'))
        R.parts.add(g)
        R.parts.add(box(min(x, x + s * 0.01), y0, 0.15, max(x, x + s * 0.01), y1, z1, 'black'))


def coat(x, y, L, m, side, rs):
    """A coat hanging on a hook at (x, y, RZ), broad face across the rail, its front to `side` (+-y)."""
    w0, w1 = 0.36, rs.uniform(0.5, 0.62)
    t = rs.uniform(0.07, 0.12)
    z1 = RZ - 0.06; z0 = z1 - L
    yc = y + side * 0.3
    P = [(x - t / 2, yc - w1 / 2, z0), (x + t / 2, yc - w1 / 2, z0), (x + t / 2, yc + w1 / 2, z0), (x - t / 2, yc + w1 / 2, z0),
         (x - t / 2 + 0.01, yc - w0 / 2, z1), (x + t / 2 - 0.01, yc - w0 / 2, z1), (x + t / 2 - 0.01, yc + w0 / 2, z1), (x - t / 2 + 0.01, yc + w0 / 2, z1)]
    from kit_h2 import hexa
    g = hexa(P, m)
    g.f = g.f[2:]; g.m = g.m[2:]; g.uv = g.uv[2:]          # no top or bottom: nobody sees them
    lean = rs.uniform(-0.12, 0.12)
    rot(g, 'y', lean, x, yc, z1)
    return g


def rails(R):
    rs = rng(17)
    rl = Geo()
    by = {m: Geo() for m in COATS}
    for (y, side, spans) in RAILS:
        for (a, b) in spans:
            # the rail: an oak board on brass posts; hooks along it
            if side > 0 or (y, +1, spans) not in RAILS:
                rl.add(box(a, y - 0.06, RZ, b, y + 0.06, RZ + 0.1, 'walnut'))
                n = max(1, int(math.ceil((b - a) / 2.4)))
                for k in range(n + 1):
                    x = a + (b - a) * k / n
                    rl.add(box(x - 0.03, y - 0.03, 0.0, x + 0.03, y + 0.03, RZ, 'brass', skip=('-z', '+z')))
                    R.col.add(box(x - 0.04, y - 0.04, 0.0, x + 0.04, y + 0.04, RZ, 'tile'))
                    rl.add(box(x - 0.1, y - 0.1, 0.0, x + 0.1, y + 0.1, 0.04, 'brass', skip=('-z',)))
                rl.add(box(a, y - 0.02, RZ + 0.1, b, y + 0.02, RZ + 0.16, 'brass'))
            x = a + 0.15
            while x < b - 0.15:
                L = rs.uniform(0.85, 1.25)
                m = rs.choice(COATS)
                by[m].add(coat(x + rs.uniform(-0.03, 0.03), y, L, m, side, rs))
                x += rs.uniform(0.2, 0.32)
    R.parts.add(rl)
    for g in by.values():
        R.nocol.add(g)
    # a few hats on the rails, an umbrella stand at each end
    hg = Geo()
    for k in range(18):
        (y, side, spans) = rs.choice(RAILS)
        a, b = rs.choice(spans)
        x = rs.uniform(a + 0.3, b - 0.3)
        hg.add(cyl(x, y, RZ + 0.16, RZ + 0.18, 0.2, 10, side='coat3', top='coat3', bottom='coat3'))
        hg.add(cyl(x, y, RZ + 0.18, RZ + 0.3, 0.11, 10, side=rs.choice(('coat3', 'coat1', 'black')), top='coat3'))
    R.nocol.add(hg)
    for x in (2.6, 29.4):
        R.parts.add(cyl(x, 8.0 + (1.2 if x < 16 else -1.2), 0, 0.6, 0.18, 10, side='brass', top='black'))
        for k in range(4):
            a = k * 1.57 + 0.4
            R.nocol.add(beam((x + 0.05 * math.cos(a), 8.0 + (1.2 if x < 16 else -1.2) + 0.05 * math.sin(a), 0.1),
                             (x + 0.12 * math.cos(a), 8.0 + (1.2 if x < 16 else -1.2) + 0.12 * math.sin(a), 0.95), 0.025, 'black'))


def counter(R):
    """The cloakroom counter in the middle of the hall: a bell, a board of tickets, a tray of tags."""
    x0, x1, y0, y1 = 13.6, 18.4, 7.4, 8.6
    R.parts.add(box(x0, y0, 0, x1, y1, 1.0, 'walnut', top='oak'))
    R.parts.add(box(x0 - 0.05, y0 - 0.05, 1.0, x1 + 0.05, y1 + 0.05, 1.06, 'oak'))
    # the ticket board standing on it, with brass tags on pegs (one row per hundred)
    R.parts.add(box(15.2, 7.95, 1.06, 16.8, 8.05, 2.2, 'walnut'))
    tg = Geo()
    rs = rng(4)
    for i in range(12):
        for j in range(8):
            if rs.random() < 0.9:
                x = 15.3 + i * 0.125; z = 1.15 + j * 0.13
                tg.add(box(x, 7.9, z, x + 0.07, 7.95, z + 0.08, 'brass'))
                tg.add(box(x, 8.05, z, x + 0.07, 8.1, z + 0.08, 'brass'))
    R.nocol.add(tg)
    R.nocol.add(cyl(14.2, 8.0, 1.06, 1.08, 0.07, 10, side='brass', top='brass'))
    R.nocol.add(sphere(14.2, 8.0, 1.1, 0.06, 8, 4, 'brass', lower=False))
    for k in range(6):
        R.nocol.add(box(17.4 + k * 0.06, 7.7, 1.06 + k * 0.002, 17.46 + k * 0.06, 7.82, 1.07 + k * 0.002, 'ivory').xform(0, 0, 0, 0))
    llamp(R, 17.6, 8.3, 1.06, 0.3, lit=True, m='e_lamp')
    R.spot('plaque', 16.0, 7.9, 1.4, -math.pi / 2, text='CLOAKROOM. Please retain your ticket. Items not collected are kept for ever.')


def passage(R):
    """Behind the south wall: an arch hidden by the coats, and a passage the width of a coat."""
    R.cut(box(PX0, PY0, 0, PX1, PY1, PH, 'tile', bottom='floor', top='plaster'))
    arch_hole(R, 'y', (AX0 + AX1) / 2, PY1 - 0.05, YS + 0.05, AX1 - AX0, 1.4, floor='floor', wall='tile')
    # inside: a bench, a coat of their own on a hook, a lamp, a pile of tickets, books along the wall
    R.parts.add(box(PX0 + 0.4, PY0 + 0.05, 0, PX0 + 2.2, PY0 + 0.5, 0.45, 'oak'))
    R.spot('sit', PX0 + 1.3, PY0 + 0.4, 0.45, math.pi / 2)
    R.nocol.add(box(PX0 + 2.5, PY0 + 0.02, 1.8, PX0 + 2.56, PY0 + 0.12, 1.86, 'brass'))
    rs = rng(2)
    R.nocol.add(coat(PX0 + 2.53, PY0 - 0.2, 1.1, 'coat4', 1, rs))
    sh(R, '+y', PY0, PX0 + 3.2, AX0 - 0.3, rows=5, frame='walnut', depth=0.24)
    sh(R, '+y', PY0, AX1 + 0.3, PX1 - 0.3, rows=5, frame='walnut', depth=0.24)
    R.parts.add(box(PX1 - 1.2, PY0 + 0.05, 0, PX1 - 0.3, PY0 + 0.55, 0.72, 'walnut', top='leather'))
    llamp(R, PX1 - 0.7, PY0 + 0.3, 0.72, 0.0, lit=True, m='e_amber')
    g = Geo()
    for k in range(20):
        g.add(box(-0.04, -0.025, 0, 0.04, 0.025, 0.004, 'ivory').xform(rs.uniform(0, 3), PX1 - 1.0 + rs.uniform(0, 0.4), PY0 + 0.3 + rs.uniform(-0.1, 0.1), 0.72 + k * 0.004))
    R.nocol.add(g)
    R.parts.add(lchair_legs(PX1 - 0.8, PY0 + 0.95, -math.pi / 2))
    R.spot('sit', PX1 - 0.8, PY0 + 0.95, 0.48, -math.pi / 2)
    bulb(R, (PX0 + PX1) / 2 - 2.0, (PY0 + PY1) / 2, PH - 0.5, r=0.06, m='e_dim', top=PH)
    a, b = R.navpt(PX0 + 2.6, 1.2), R.navpt(AX1 + 1.0, 1.2)
    R.link(a, b)


def lights(R):
    for x in (5.0, 12.0, 20.0, 27.0):
        for y in (3.7, 8.0, 12.4):
            pendant(R, x, y, 3.3 if y != 8.0 else 3.8, JAMB + 1.0, r=0.2)
    for x in (1.2, W - 1.2):
        R.light(sphere(x, 3.6, 2.4, 0.1, 8, 4, 'e_amber'))
