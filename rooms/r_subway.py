"""The Station: an empty underground platform under a white-tiled vault, bookcases where the adverts
should be, the rails running off east into a dark tunnel. Every so often a train comes in out of the
tunnel, stands at the platform with nobody on it and nobody getting off, and goes back the way it
came. Beyond the platform, a tiled concourse with its ticket barriers and a kiosk of books. In the
tunnel, along the narrow walkway where you should not be, a service door stands open on the room
where the man who looks after the line keeps his kettle."""
from kit_h9 import *
from kit_h3 import arc_band

W, D = 32.0, 16.0
ZT = -0.95                     # the track bed
LY = 1.7                       # the south ledge's edge
PY = 5.4                       # the platform edge
TY1 = 5.6                      # the tunnel's north wall
WK = 4.85                      # the tunnel walkway's edge
PX = 17.0                      # the platform hall ends / the tunnel starts
TC = 3.2                       # the track's centre line
CY0 = 8.6                      # the concourse's south wall (west of the lamp room)
MX0, MX1, MY0, MY1 = 21.6, 27.0, 6.0, 8.2   # the maintenance room
TRAIN0, TRAIN1, SLIDE = 2.7, 15.7, 15.9


def make():
    R = Room('subway', 2, 1, res=2048)
    R.sockets(floor='terrazzo', wall='wtile')
    hall(R)
    tunnel(R)
    concourse(R)
    maintenance(R)
    train(R)
    fx(R, 'fog', [PX, T, ZT, W - T, TY1, 3.9], density=0.06)
    fx(R, 'dust', [T, PY, 0.5, PX, D - T, 6.0])
    # walkers: along the platform, into the concourse, along the ledge
    p = navloop(R, [(2.5, 7.5), (9.0, 7.0), (15.5, 7.2), (15.5, 13.5), (9.0, 14.0), (2.5, 13.5)])
    c = navloop(R, [(19.0, 10.0), (24.0, 10.5), (30.0, 9.0), (30.0, 14.0), (24.0, 14.0), (19.0, 14.0)])
    R.link(2, c[0]); R.link(3, c[5])
    l = [R.navpt(x, 1.05) for x in (3.4, 8.0, 14.0, 24.0, 29.0)]
    R.link(*l)
    secret(R, 23.2, 7.2, 0.0, 'The Lamp Room',
           'Behind the service door in the tunnel: a kettle, a tin mug, a rota with one name on it for every shift, and a shelf of manuals for a railway that goes nowhere. The kettle is still warm.')
    return finish(R, 'The Station', weight=3, probe=(9, 10, 1.8),
                  blurb='An underground platform, empty, very clean. A train is standing at it with its doors shut. You wait for someone to get off, and nobody does, and then it goes.')


# ---------------------------------------------------------------------------
def hall(R):
    pr = arch_profile(D / 2, D - 2 * T + 0.04, 0, 3.4, 30, rise=4.08)
    R.cut(prism(pr, 'x', T - 0.02, PX, arch_mats(len(pr), 'terrazzo', 'wtile')))
    # the track bed, and its end at the buffers
    R.cut(box(T - 0.02, LY, ZT, PX + 0.05, PY, 0.1, 'slate', bottom='slate'))
    R.parts.add(box(T, 2.3, ZT, 1.3, 4.1, ZT + 1.0, 'oxblood'))                         # the buffer stop
    for y in (2.6, 3.8):
        R.parts.add(cyl(1.3, y, ZT + 0.62, ZT + 0.72, 0.2, 10, side='iron', top='iron', bottom='iron').xform(0, 0, 0, 0))
        R.parts.add(box(1.3, y - 0.05, ZT + 0.62, 1.6, y + 0.05, ZT + 0.72, 'chrome'))
    R.light(box(0.6, 3.1, ZT + 1.0, 1.0, 3.3, ZT + 1.12, 'e_signal'))
    # stairs off the ends of the ledge and the platform, down onto the track
    R.flight(1.6, LY + 1.3, ZT, 1.0, 5, 0.19, 0.26, '-y', m='concrete', side='concrete')
    R.flight(1.6, PY - 1.3, ZT, 1.0, 5, 0.19, 0.26, '+y', m='concrete', side='concrete')
    R.parts.add(box(1.5, LY, ZT, 1.6, LY + 1.3, 0.0, 'concrete')); R.parts.add(box(2.6, LY, ZT, 2.7, LY + 1.3, 0.0, 'concrete'))
    R.parts.add(box(1.5, PY - 1.3, ZT, 1.6, PY, 0.0, 'concrete')); R.parts.add(box(2.6, PY - 1.3, ZT, 2.7, PY, 0.0, 'concrete'))
    rails(R, T, W - T)
    # the platform's edge: a white line and a strip of yellow, and the ledge's edge
    R.nocol.add(box(T, PY + 0.02, 0.0, PX, PY + 0.14, 0.006, 'ivory'))
    R.nocol.add(box(T, PY + 0.25, 0.0, PX, PY + 0.8, 0.006, 'tactile'))
    for k in range(int((PX - T) / 0.1)):
        x = T + 0.05 + k * 0.1
        R.nocol.add(box(x - 0.02, PY + 0.28, 0.006, x + 0.02, PY + 0.77, 0.012, 'tactile'))
    R.nocol.add(box(T, LY - 0.14, 0.0, W - T, LY - 0.02, 0.006, 'ivory'))
    R.parts.add(box(PX - 2.0, WK, ZT, PX, PY, 0.0, 'concrete'))     # the platform's nose, where the walkway starts
    # a dark band of tile and a frieze
    for (y0, y1) in ((D - T - 0.03, D - T), (T, T + 0.03)):
        R.nocol.add(box(T, y0, 0.0, PX, y1, 0.9, 'green'))
        R.nocol.add(box(T, y0, 3.0, PX, y1, 3.4, 'green'))
    # books where the adverts are: the platform wall and the wall across the tracks
    for (a, b) in ((0.7, 6.1), (9.9, 16.6)):
        n = 2 if b - a > 5.5 else 1
        L = (b - a - 0.6 * (n - 1)) / n
        for k in range(n):
            x0 = a + k * (L + 0.6)
            frame(R, x0, x0 + L, D - T, -1, 0.3, 3.2)
            sh(R, '-y', D - T, x0 + 0.12, x0 + L - 0.12, z=0.42, rows=6, frame='walnut', depth=0.28)
            frame(R, x0, x0 + L, T, 1, 0.3, 2.9)
            sh(R, '+y', T, x0 + 0.12, x0 + L - 0.12, z=0.42, rows=5, frame='walnut', depth=0.26)
    for c in (8.0,):
        sh(R, '-y', D - T, c - 2.2, c + 2.2, z=4.4, rows=3, frame='walnut', depth=0.28)
        roundel(R, c - 4.9, D - T, 4.6, -1)
        roundel(R, c - 4.9, T, 4.3, 1)
    for x in (13.2,):
        roundel(R, x, D - T, 4.6, -1)
        roundel(R, x, T, 4.3, 1)
    # benches down the middle of the platform, back to back
    for x in (4.5, 11.0):
        for (y, a) in ((10.3, -math.pi / 2), (10.9, math.pi / 2)):
            bench(R, x, y, a)
    # the lights: two long strips along the vault, green lamps between the bookcases
    for y in (8.0, 12.8):
        R.light(box(1.0, y - 0.08, 5.2, PX - 0.4, y + 0.08, 5.26, 'e_panel'))
        R.nocol.add(box(1.0, y - 0.12, 5.26, PX - 0.4, y + 0.12, 5.34, 'iron'))
        for x in (2.0, 6.0, 10.0, 14.0):
            R.nocol.add(box(x - 0.01, y - 0.01, 5.34, x + 0.01, y + 0.01, 6.9, 'iron'))
    for x in (0.55, 6.4, 9.6, 16.8):
        wall_lamp(R, x, D - T, 2.9, -1)
        wall_lamp(R, x, T, 2.7, 1)
    # the indicator: next train, and a clock
    R.nocol.add(box(7.0, 9.95, 3.4, 11.0, 10.05, 3.5, 'iron'))
    for x in (7.3, 10.7): R.nocol.add(box(x - 0.015, 9.985, 3.5, x + 0.015, 10.015, 5.26, 'iron'))
    R.parts.add(box(7.0, 9.9, 2.6, 11.0, 10.1, 3.4, 'black'))
    board_text(R, 7.2, 10.8, 9.88, 2.7, 3.3, -1, 3, seed=5)
    board_text(R, 7.2, 10.8, 10.12, 2.7, 3.3, 1, 3, seed=6)
    R.nocol.add(cyl(13.5, 10.0, 3.2, 3.24, 0.02, 6, side='iron', caps=False))
    for s in (-1, 1):
        R.nocol.add(clock_face(13.5, 10.0 + s * 0.06, 3.0, 0.32, s))
    R.nocol.add(box(13.47, 10.0 - 0.06, 3.0, 13.53, 10.06, 5.26, 'iron'))


def rails(R, x0, x1):
    g = Geo()
    for y in (TC - 0.72, TC + 0.72):
        g.add(box(x0, y - 0.04, ZT + 0.12, x1, y + 0.04, ZT + 0.26, 'chrome', sides='iron'))
    n = int((x1 - x0) / 0.7)
    for k in range(n):
        x = x0 + 0.35 + k * 0.7
        g.add(box(x - 0.13, TC - 1.25, ZT, x + 0.13, TC + 1.25, ZT + 0.12, 'walnut', skip=('-z',)))
    g.add(box(x0, TC + 1.35, ZT, x1, TC + 1.47, ZT + 0.2, 'iron'))           # the live rail, on its pots
    R.nocol.add(g)


def frame(R, x0, x1, y, face, z0, z1, m='gilt'):
    """A narrow gilt frame round a poster-sized bookcase on the tiles."""
    t = 0.06; d = 0.05 * face
    ya, yb = (y, y + d) if face > 0 else (y + d, y)
    R.nocol.add(box(x0, ya, z0, x1, yb, z0 + t, m)); R.nocol.add(box(x0, ya, z1 - t, x1, yb, z1, m))
    R.nocol.add(box(x0, ya, z0, x0 + t, yb, z1, m)); R.nocol.add(box(x1 - t, ya, z0, x1, yb, z1, m))


def roundel(R, x, y, z, face, r=0.75):
    """The station's sign: a ring and a bar across it, blank."""
    d = 0.04 * face
    g = ring(0, 0, 0, 0.05, r * 0.7, r, 24, top='oxblood', bottom='oxblood', inner='oxblood', outer='oxblood')
    rot(g, 'x', math.pi / 2)
    g.xform(0, x, y + d, z)
    R.nocol.add(g)
    ya, yb = sorted((y + 0.02 * face, y + 0.1 * face))
    R.nocol.add(box(x - r * 1.15, ya, z - 0.16, x + r * 1.15, yb, z + 0.16, 'green'))
    R.nocol.add(box(x - r * 0.9, yb if face > 0 else ya - 0.005, z - 0.05, x + r * 0.9, (yb + 0.005) if face > 0 else ya, z + 0.05, 'ivory'))


def bench(R, x, y, a, L=2.8):
    g = box(-L / 2, -0.22, 0.42, L / 2, 0.22, 0.47, 'walnut')
    g.add(box(-L / 2, 0.18, 0.47, L / 2, 0.23, 0.95, 'walnut'))
    for s in (-L / 2 + 0.2, 0, L / 2 - 0.2):
        g.add(box(s - 0.04, -0.2, 0, s + 0.04, 0.2, 0.42, 'iron'))
    R.parts.add(g.xform(a - math.pi / 2, x, y, 0))
    for k in (-1, 0, 1):
        R.spot('sit', x + k * 0.9 * math.cos(a - math.pi / 2), y + k * 0.9 * math.sin(a - math.pi / 2), 0.47, a)


def wall_lamp(R, x, y, z, face, m='e_lamp'):
    d = face
    R.nocol.add(box(x - 0.04, min(y, y + 0.35 * d), z - 0.03, x + 0.04, max(y, y + 0.35 * d), z + 0.03, 'brass'))
    R.nocol.add(frustum(x, y + 0.4 * d, z - 0.22, z - 0.02, 0.2, 0.07, 12, 'green', inner='ivory'))
    R.light(cyl(x, y + 0.4 * d, z - 0.16, z - 0.12, 0.1, 8, side=m, top=m, bottom=m))


def board_text(R, x0, x1, y, z0, z1, face, lines, seed=0, m='e_board'):
    """Lines of glowing letters (blocks for words) on a black board facing +-y."""
    rnd = random.Random(seed)
    g = Geo()
    lh = (z1 - z0) / lines
    for i in range(lines):
        z = z1 - (i + 0.5) * lh
        x = x0
        while x < x1 - 0.3:
            wl = rnd.uniform(0.12, 0.5)
            if x + wl > x1: break
            n = max(1, int(wl / 0.06))
            for k in range(n):
                cx = x + k * 0.06
                h = lh * rnd.uniform(0.35, 0.5)
                ya, yb = sorted((y, y + 0.01 * face))
                g.add(box(cx, ya, z - h / 2, cx + 0.045, yb, z + h / 2, m))
            x += wl + rnd.uniform(0.08, 0.2)
    R.light(g)


def clock_face(x, y, z, r, face):
    g = cyl(0, 0, 0, 0.05, r, 20, side='iron', top='ivory', bottom='ivory')
    rot(g, 'x', -face * math.pi / 2)
    g.xform(0, x, y, z)
    g.add(box(x - 0.01, y + face * 0.03 - 0.005, z, x + 0.01, y + face * 0.03 + 0.005, z + r * 0.75, 'black'))
    g.add(box(x, y + face * 0.03 - 0.005, z - 0.01, x + r * 0.5, y + face * 0.03 + 0.005, z + 0.01, 'black'))
    return g


# ---------------------------------------------------------------------------
def tunnel(R):
    pr = arch_profile((T + TY1) / 2, TY1 - T + 0.02, ZT, 2.2, 20, rise=(TY1 - T) / 2)
    R.cut(prism(pr, 'x', PX - 0.05, W - T + 0.02, arch_mats(len(pr), 'slate', 'wtile')))
    # the tunnel mouth: a stone ring
    band = [(p, z + ZT) for (p, z) in arc_band((T + TY1) / 2, TY1 - T, 2.2, (TY1 - T) / 2, -0.4, 0.0, 16)]
    R.parts.add(prism(band, 'x', PX - 0.25, PX, 'green', cap='green'))
    for (a, b) in ((T, T + 0.4), (TY1, TY1 + 0.4)):
        R.parts.add(box(PX - 0.25, a, 0.0, PX, b, ZT + 2.2, 'green'))
    R.parts.add(box(PX, T, ZT, W - T, LY, 0.0, 'concrete'))          # the ledge on the south side
    R.parts.add(box(PX, WK, ZT, W - T, TY1, 0.0, 'concrete'))        # the walkway on the north side
    R.nocol.add(box(PX, WK + 0.02, 0.0, W - T, WK + 0.12, 0.006, 'ivory'))
    # a grime band, cables along the wall, caged lamps far apart, a red light at the end
    for (y, s) in ((TY1 - 0.08, -1), (T + 0.08, 1)):
        for z in (1.0, 1.12, 1.24):
            R.nocol.add(xtube(PX, W - T, y, z, 0.022, 5, 'black'))
    for x in (20.0, 26.0, 30.5):
        for (y, f) in ((TY1 - 0.1, -1), (T + 0.1, 1)):
            R.nocol.add(box(x - 0.1, min(y, y + 0.12 * f), 1.9, x + 0.1, max(y, y + 0.12 * f), 2.1, 'iron'))
            R.light(sphere(x, y + 0.14 * f, 2.0, 0.06, 8, 4, 'e_dim'))
    R.parts.add(box(W - T - 0.3, TC - 0.2, ZT, W - T, TC + 0.2, 2.6, 'iron'))
    R.light(sphere(W - T - 0.32, TC, 2.2, 0.1, 8, 4, 'e_signal'))
    R.light(sphere(W - T - 0.32, TC, 1.9, 0.1, 8, 4, 'e_signal'))


def arc_ring(pr, t):
    """The band just inside an arch profile (the profile's arch part offset inward by t)."""
    pts = pr[2:]
    c = (pr[0][0] + pr[1][0]) / 2
    zs = pr[2][1]
    inner = []
    for (p, z) in pts:
        dp, dz = p - c, z - zs
        L = math.hypot(dp, max(dz, 0.0)) or 1.0
        if dz <= 1e-6: inner.append((p - t * (1 if dp > 0 else -1), z))
        else: inner.append((p - dp / L * t, z - dz / L * t))
    return pts + list(reversed(inner))


# ---------------------------------------------------------------------------
def concourse(R):
    CH = 4.2
    R.cut(box(PX + 0.4, CY0, 0, W - T + 0.02, D - T + 0.02, CH, 'wtile', bottom='terrazzo', top='plaster'))
    R.cut(box(MX1 + 0.4, MY0, 0, W - T + 0.02, CY0 + 0.05, CH, 'wtile', bottom='terrazzo', top='plaster'))
    for (a, b) in ((9.0, 11.6), (12.4, 15.0)):
        pr = arch_profile((a + b) / 2, b - a, 0, 2.6, 14)
        R.cut(prism(pr, 'x', PX - 0.05, PX + 0.45, arch_mats(len(pr), 'terrazzo', 'wtile')))
    R.nocol.add(box(PX + 0.4, D - T - 0.03, 0, W - T, D - T, 0.9, 'green'))
    R.nocol.add(box(PX + 0.4, CY0, 0, MX1 + 0.4, CY0 + 0.03, 0.9, 'green'))
    # ticket barriers across the concourse, with gaps to walk through
    y = CY0
    xb = 20.6
    for k in range(6):
        y0 = CY0 + 0.3 + k * 1.2
        if y0 + 0.5 > D - T: break
        R.parts.add(box(xb - 0.6, y0, 0, xb + 0.6, y0 + 0.35, 1.05, 'iron', top='chrome'))
        R.light(box(xb - 0.1, y0 + 0.1, 1.05, xb + 0.1, y0 + 0.25, 1.08, 'e_exit'))
    # the kiosk: a little booth with a counter, full of books
    kx0, kx1, ky0, ky1 = 25.0, 29.0, 12.4, D - T
    R.parts.add(box(kx0, ky0, 0, kx1, ky0 + 0.35, 1.05, 'walnut', top='oak'))
    R.parts.add(box(kx0, ky0, 2.7, kx1, ky0 + 0.35, 3.1, 'green'))
    R.parts.add(box(kx0 - 0.15, ky0, 0, kx0, ky1, 3.1, 'walnut'))
    R.parts.add(box(kx1, ky0, 0, kx1 + 0.15, ky1, 3.1, 'walnut'))
    sh(R, '-y', ky1, kx0 + 0.1, kx1 - 0.1, rows=6, frame='oak', depth=0.3)
    R.light(box(kx0 + 0.2, ky0 + 0.1, 2.65, kx1 - 0.2, ky0 + 0.25, 2.7, 'e_fluor'))
    book_pile(R, 26.0, ky0 + 0.18, 1.05, 4, random.Random(2), 0.2)
    book_pile(R, 27.8, ky0 + 0.18, 1.05, 6, random.Random(3), 1.2)
    # bookcases round the rest of the concourse walls, and a way-out sign
    sh(R, '-y', D - T, PX + 0.8, 22.1, rows=8, frame='walnut')
    sh(R, '+y', CY0, 21.2, MX1 + 0.2, rows=8, frame='walnut')
    sh(R, '-x', W - T, 10.0, 12.2, rows=8, frame='walnut')
    R.parts.add(box(22.5, D - T - 0.12, 2.9, 25.5, D - T, 3.3, 'black'))
    R.light(box(22.7, D - T - 0.13, 2.97, 25.3, D - T - 0.12, 3.23, 'e_exit'))
    R.parts.add(box(W - T - 0.12, 6.6, 3.0, W - T, 9.4, 3.4, 'black'))
    R.light(box(W - T - 0.13, 6.8, 3.07, W - T - 0.12, 9.2, 3.33, 'e_exit'))
    for (x, y) in ((19.0, 10.5), (19.0, 14.0), (24.0, 10.2), (28.0, 9.5), (24.0, 13.6), (30.2, 13.8)):
        R.light(box(x - 0.6, y - 0.3, CH - 0.04, x + 0.6, y + 0.3, CH - 0.01, 'e_panel'))
    for y in (10.0, 13.5):
        R.parts.add(box(30.6, y - 1.0, 0.0, 31.2, y + 1.0, 0.45, 'walnut')); R.spot('sit', 30.9, y, 0.45, math.pi)


# ---------------------------------------------------------------------------
def maintenance(R):
    """Off the tunnel walkway: the lamp room."""
    H = 2.6
    R.cut(box(MX0, MY0, 0, MX1, MY1, H, 'green', bottom='concrete', top='plaster'))
    dx0, dx1 = 22.3, 23.3
    R.cut(box(dx0, TY1 - 0.4, 0, dx1, MY0 + 0.05, 2.1, 'green', bottom='concrete', top='green'))
    R.nocol.add(door_leaf(0.95, 2.05, 'green', 'green', 'brass').xform(math.pi / 2 + 1.1, dx0, MY0 + 0.02, 0))
    R.parts.add(box(dx0 - 0.3, TY1 - 0.06, 2.15, dx1 + 0.3, TY1 + 0.0, 2.45, 'black'))
    R.light(box(dx0 + 0.1, TY1 - 0.07, 2.2, dx1 - 0.1, TY1 - 0.06, 2.4, 'e_signal'))
    # the desk, the lamp, the logbook, the kettle
    R.parts.add(table(24.4, MY1 - 0.7, 26.3, MY1 - 0.05, 0.76, 'oak', top='leather'))
    desk_lamp(R, 26.0, MY1 - 0.35, 0.76)
    g = box(-0.2, -0.14, 0, 0.2, 0.14, 0.02, 'green'); g.add(box(-0.19, -0.13, 0.02, 0.19, 0.13, 0.04, 'ivory'))
    R.nocol.add(g.xform(0.1, 25.2, MY1 - 0.4, 0.76))
    R.nocol.add(cyl(24.65, MY1 - 0.25, 0.76, 0.98, 0.09, 10, side='chrome', top='chrome', bottom='chrome'))
    R.nocol.add(cyl(24.9, MY1 - 0.2, 0.76, 0.86, 0.04, 8, side='ivory', top='ivory', bottom='ivory'))
    R.parts.add(chair(25.3, MY1 - 1.05, math.pi / 2)); R.spot('sit', 25.3, MY1 - 1.05, 0.48, math.pi / 2)
    # manuals, a line diagram, lockers, a cot
    sh(R, '-x', MX1, MY0 + 0.1, MY1 - 0.1, rows=5, frame='iron', depth=0.3)
    R.parts.add(box(22.3, MY1 - 0.04, 1.0, 24.2, MY1, 1.9, 'blackboard'))
    R.nocol.add(box(22.45, MY1 - 0.05, 1.45, 24.05, MY1 - 0.04, 1.47, 'ivory'))
    for k in range(6):
        x = 22.55 + k * 0.3
        R.nocol.add(cyl(x, MY1 - 0.05, 1.42, 1.5, 0.03, 8, side='ivory', top='ivory', bottom='ivory'))
    for k in range(3):
        R.parts.add(box(MX0 + 0.05, MY0 + 0.4 + k * 0.55, 0, MX0 + 0.5, MY0 + 0.92 + k * 0.55, 1.9, 'green', top='iron'))
    cot(R, 23.6, MY0 + 0.05, 25.5, MY0 + 0.85, 0.0, h=0.42, frame='iron', blanket='oxblood')
    bulb(R, 23.6, 7.2, 2.1, r=0.07, m='e_lamp', top=H)


# ---------------------------------------------------------------------------
def train(R):
    """Two cars, nobody aboard, doors shut. It rolls out into the tunnel and back."""
    M = R.mover('slide', delta=(SLIDE, 0.0, 0.0), period=80.0, pause=24.0)
    g = Geo()
    zb, zt = ZT + 0.55, ZT + 3.4
    hw = 1.3
    cars = ((TRAIN0, (TRAIN0 + TRAIN1) / 2 - 0.25), ((TRAIN0 + TRAIN1) / 2 + 0.25, TRAIN1))
    for ci, (x0, x1) in enumerate(cars):
        g.add(box(x0, TC - hw, zb, x1, TC + hw, zt, 'fuselage', top='iron', bottom='iron'))
        g.add(box(x0 + 0.1, TC - hw - 0.02, zb + 0.9, x1 - 0.1, TC + hw + 0.02, zb + 1.0, 'oxblood'))
        # bogies
        for xb in (x0 + 1.2, x1 - 1.2):
            g.add(box(xb - 0.9, TC - 0.9, ZT + 0.2, xb + 0.9, TC + 0.9, zb, 'iron'))
        # windows and doors down both sides
        for s in (-1, 1):
            y = TC + s * (hw + 0.012)
            ya, yb = sorted((TC + s * hw, y))
            L = x1 - x0
            for k in range(4):
                xd = x0 + L * (k + 0.5) / 4
                if k % 2 == 0:
                    g.add(box(xd - 0.65, ya, zb + 0.05, xd + 0.65, yb, zb + 2.25, 'slate'))
                    g.add(box(xd - 0.5, ya - 0.004 * s, zb + 1.2, xd - 0.05, yb + 0.004 * s, zb + 2.05, 'black'))
                    g.add(box(xd + 0.05, ya - 0.004 * s, zb + 1.2, xd + 0.5, yb + 0.004 * s, zb + 2.05, 'black'))
                else:
                    g.add(box(xd - 1.0, ya, zb + 1.15, xd + 1.0, yb, zb + 2.15, 'black'))
        # the cab ends
        for (x, f) in ((x0, -1), (x1, 1)):
            xa, xb2 = sorted((x, x + 0.012 * f))
            g.add(box(xa, TC - 0.9, zb + 1.3, xb2, TC + 0.9, zb + 2.2, 'black'))
            if (ci == 0 and f < 0) or (ci == 1 and f > 0):
                g.add(box(xa - 0.004, TC - 0.5, zb + 2.3, xb2 + 0.004, TC + 0.5, zb + 2.6, 'ivory'))
                for s in (-0.8, 0.8):
                    g.add(box(xa - 0.006, TC + s - 0.12, zb + 0.55, xb2 + 0.006, TC + s + 0.12, zb + 0.75, 'ivory'))
    M.nocol.add(g)
