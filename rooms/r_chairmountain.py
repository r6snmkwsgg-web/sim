"""The Chair Mountain: every chair anyone ever lost, piled into a mountain under the vault. A red runner
winds up it between fences of chairs, lit by green lamps somebody left burning on the pile. At the
summit one armchair sits alone, facing the windows. On the far side, low down, a gap in the pile goes in
to a hollow among the chair legs, where somebody has made a bed of cushions."""
from kit_h1 import *

W = D = 64.0
CX, CY = 32.0, 33.0          # the mountain's centre
RB, RS = 22.0, 5.5           # its foot, its summit
HC, SZ = 11.7, 12.5          # the pile's top, the summit floor
TH0 = -math.pi / 2           # the path starts on the south side
SWEEP = 1.4 * 2 * math.pi
RC0, RC1 = RB + 2.4, RS + 0.2
HW = 1.2                     # half the path's width
N = 300
CAVE = (CX, CY + 11.0, 3.5)
TUN = 0.65                   # the tunnel's half width


def cone_h(r):
    if r <= RS: return HC
    if r >= RB: return 0.0
    return HC * (RB - r) / (RB - RS)


def rc(u): return RC0 + (RC1 - RC0) * u
def th(u): return TH0 + SWEEP * u


def ztop(u):
    return max(SZ * u, min(1.9, 1.9 * u / 0.055), cone_h(rc(u) - HW) + 0.12)


def make():
    R = Room('chairmountain', 4, 4, levels=2, res=2048)
    R.sockets(floor='floor', wall='tile')
    top = R.hi - 0.2
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, top, 'tile', bottom='floor', top='plaster'))
    rnd = random.Random(1313)
    g1 = wall_flight(R, 'W', 26.0, wd=2.0, rise=0.22, run=0.28, up=+1)
    g2 = wall_flight(R, 'E', 38.0, wd=2.0, rise=0.22, run=0.28, up=-1)
    gallery(R, gaps=[g1, g2])
    gallery_cases(R, rows=13, skip=[('N', k) for k in range(4)])
    gallery_lamps(R)
    lower_cases(R, rows=15)
    windows(R, top)
    path(R, rnd)
    summit(R, rnd)
    pile(R, rnd)
    cave(R, rnd)
    for (x, y) in ((10, 10), (54, 10), (10, 57), (54, 57)):
        R.parts.add(cyl(x, y, 11.4, top, 0.03, 6, side='iron', caps=False))
        R.light(sphere(x, y, 11.0, 0.45, 12, 6, 'e_lamp'))
    nav(R)
    R.spot('probe', 32.0, 12.0, 9.0)
    R.meta.update(label='The Chair Mountain', weight=2,
                  blurb='Every chair anyone ever got up from and did not come back to. Somebody has laid a carpet to the top, and somebody else has left the lamps on.')
    R.meta['box'] = [[T, 0, T], [W - T, top, D - T]]
    fx(R, 'dust', [8.0, 40.0, 2.0, 56.0, D - 1.0, top - 0.5])
    return tidy(R)


def windows(R, top):
    """Three tall arched windows in the north wall over the gallery, full of sky."""
    for x in (16.0, 32.0, 48.0):
        w, z0, jamb = 4.0, GZ + 1.2, 4.2
        pr = arch_profile(x, w, z0, jamb, 16)
        R.cut(prism(pr, 'y', D - T - 0.05, D - 0.06, arch_mats(len(pr), 'tile', 'tile'), cap='tile'))
        R.light(prism(arch_profile(x, w, z0, jamb, 16), 'y', D - 0.09, D - 0.07, 'e_sky', cap='e_sky'))
        for dx in (-0.7, 0.7):
            R.nocol.add(box(x + dx - 0.07, D - 0.3, z0, x + dx + 0.07, D - 0.12, z0 + jamb + 1.85, 'tile'))
        for z in (z0 + 1.6, z0 + 3.4):
            R.nocol.add(box(x - w / 2, D - 0.3, z - 0.06, x + w / 2, D - 0.12, z + 0.06, 'tile'))
        R.parts.add(box(x - w / 2 - 0.2, D - T - 0.3, z0 - 0.25, x + w / 2 + 0.2, D - T, z0, 'tile'))


def edge(u, r_off):
    a = th(u); r = rc(u) + r_off
    return (CX + r * math.cos(a), CY + r * math.sin(a), ztop(u))


def path(R, rnd):
    us = [k / N for k in range(N + 1)]
    inner = [edge(u, -HW) for u in us]
    outer = [edge(u, HW) for u in us]
    R.parts.add(ribbon(inner, outer, thick=0.35, top='carpet', side='walnut', bottom='walnut'))
    # brass stair rods across the runner, every metre and a bit
    acc, last = 0.0, None
    for u in us:
        p = edge(u, 0)
        if last: acc += math.dist(p, last)
        last = p
        if acc > 1.25:
            acc = 0.0
            a, b = edge(u, -HW + 0.25), edge(u, HW - 0.25)
            R.nocol.add(beam((a[0], a[1], a[2] + 0.02), (b[0], b[1], b[2] + 0.02), 0.035, 'brass'))
    # invisible fences just inside the edges, the inner one ending where the summit's rim takes over
    uin = min(1.0, (RC0 - (RS + HW)) / (RC0 - RC1))
    col_fence(R, [edge(u, HW - 0.28) for u in us])
    col_fence(R, [edge(u, -HW + 0.28) for u in us if u <= uin])
    R.uin = uin
    # fences of chairs along both edges, their backs to the path; a green lamp every so often
    acc, last, k = 0.0, None, 0
    for u in us:
        p = edge(u, 0)
        if last: acc += math.dist(p, last)
        last = p
        if acc < 1.35: continue
        acc = 0.0; k += 1
        a = th(u)
        for side in (1, -1):
            if side < 0 and u > uin: continue
            q = edge(u, side * (HW - 0.2))
            g = tilted_chair(rnd, tilt=0.12)
            face = a + (0 if side > 0 else math.pi) + rnd.uniform(-0.35, 0.35)
            g.xform(face, q[0], q[1], q[2] - 0.02)
            R.nocol.add(g)
        if k % 7 == 3:
            q = edge(u, HW + 0.15)
            lamp(R, q[0], q[1], q[2] - 0.1, 1.45)


def lamp(R, x, y, z, h=1.4):
    """A green banker's-lamp shade on a brass stalk, left burning on the pile."""
    R.nocol.add(cyl(x, y, z, z + h, 0.025, 6, side='brass', caps=False))
    R.nocol.add(frustum(x, y, z + h - 0.02, z + h + 0.2, 0.26, 0.1, 12, m='green', inner='ivory'))
    R.light(cyl(x, y, z + h - 0.04, z + h - 0.01, 0.23, 10, side='e_lamp', top='e_lamp', bottom='e_lamp'))


def summit(R, rnd):
    R.parts.add(cyl(CX, CY, HC - 0.8, SZ, RS, 40, side='walnut', top='oak', bottom='walnut'))
    R.nocol.add(cyl(CX, CY, SZ, SZ + 0.01, 2.2, 32, side='carpet', top='carpet'))
    te = th(1.0)
    gap = 0.5
    a0, a1 = te, te + 2 * math.pi - gap
    n = 44
    pts = [(CX + (RS - 0.28) * math.cos(a0 + (a1 - a0) * k / n), CY + (RS - 0.28) * math.sin(a0 + (a1 - a0) * k / n), SZ) for k in range(n + 1)]
    col_fence(R, pts)
    p, q = edge(1.0, HW + 0.05), (CX + (RS - 0.28) * math.cos(te), CY + (RS - 0.28) * math.sin(te), SZ)
    col_fence(R, [q, p])
    for k in range(20):
        a = a0 + (a1 - a0) * (k + 0.5) / 20
        g = tilted_chair(rnd, tilt=0.1)
        g.xform(a + rnd.uniform(-0.3, 0.3), CX + (RS - 0.25) * math.cos(a), CY + (RS - 0.25) * math.sin(a), SZ)
        R.nocol.add(g)
    for k in range(3):
        g = tilted_chair(rnd, tilt=0.1)
        a = te + 0.05 + k * 0.03
        r = RS - 0.3 + k * 0.5
        g.xform(te + math.pi / 2, CX + r * math.cos(te + 0.04), CY + r * math.sin(te + 0.04), SZ)
        R.nocol.add(g)
    # the one chair, facing the windows
    armchair(R, CX, CY + 0.6, SZ, math.pi / 2)
    R.spot('sit', CX, CY + 0.6, SZ + 0.5, math.pi / 2)
    lamp(R, CX + 1.1, CY + 0.9, SZ, 1.3)


def armchair(R, x, y, z, a):
    g = Geo()
    for (px, py) in ((-0.38, -0.38), (0.38, -0.38), (0.38, 0.38), (-0.38, 0.38)):
        g.add(box(px - 0.04, py - 0.04, 0, px + 0.04, py + 0.04, 0.2, 'walnut', skip=('-z',)))
    g.add(box(-0.42, -0.42, 0.2, 0.42, 0.42, 0.5, 'velvet'))
    g.add(box(-0.46, -0.46, 0.2, -0.26, 0.46, 1.25, 'velvet'))
    g.add(box(-0.3, -0.46, 0.5, 0.42, -0.32, 0.72, 'velvet'))
    g.add(box(-0.3, 0.32, 0.5, 0.42, 0.46, 0.72, 'velvet'))
    g.xform(a, x, y, z)
    R.parts.add(g)


def pile(R, rnd):
    """The mountain itself: a lumpy dark cone of chairs (drawn, not collided: the path's fences keep you
    on it), strewn with chairs and loose legs, with a hole low on the north side for the tunnel."""
    nr, na = 16, 96
    da = 2 * math.pi / na
    a0 = math.pi / 2 - da / 2
    rings = [RS + (RB + 0.4 - RS) * i / nr for i in range(nr + 1)]
    noise = {}
    def hgt(i, j):
        r = rings[i]
        if (i, j % na) not in noise:
            noise[(i, j % na)] = 0.0 if i in (0, nr) else -rnd.uniform(0.0, 0.7)
        return max(0.0, cone_h(r) + noise[(i, j % na)]) if i < nr else -0.05
    g = Geo()
    vid = {}
    def V(i, j):
        key = (i, j % na)
        if key not in vid:
            a = a0 + j * da; r = rings[i]
            vid[key] = g.vert((CX + r * math.cos(a), CY + r * math.sin(a), hgt(i, j)))
        return vid[key]
    for i in range(nr):
        for j in range(na):
            if j == 0 and rings[i] > 17.5: continue          # the tunnel's mouth
            ids = [V(i, j), V(i + 1, j), V(i + 1, j + 1), V(i, j + 1)]
            m = 'walnut' if (i + j) % 3 else 'wood'
            g.face(ids, m, [(g.v[k][0], g.v[k][1]) for k in ids])
    # make it face up
    f = g.f[0]; p0, p1, p2 = g.v[f[0]], g.v[f[1]], g.v[f[2]]
    if (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0]) < 0:
        g.f = [tuple(reversed(f)) for f in g.f]; g.uv = [list(reversed(u)) for u in g.uv]
    R.nocol.add(g)
    # the invisible skirt round its foot (too steep to climb), open at the tunnel
    for j in range(na):
        if j == 0: continue
        aa, bb = a0 + j * da, a0 + (j + 1) * da
        q = [(CX + RB * math.cos(aa), CY + RB * math.sin(aa), 0.0), (CX + RB * math.cos(bb), CY + RB * math.sin(bb), 0.0),
             (CX + (RB - 0.5) * math.cos(bb), CY + (RB - 0.5) * math.sin(bb), 1.45), (CX + (RB - 0.5) * math.cos(aa), CY + (RB - 0.5) * math.sin(aa), 1.45)]
        s = Geo(); s.face([s.vert(p) for p in q], 'tile', [(0, 0)] * 4); R.col.add(s)
    # chairs everywhere on it
    def near_path(r, a):
        for kk in range(3):
            u = ((a - TH0) % (2 * math.pi) + 2 * math.pi * kk) / SWEEP
            if u <= 1.0 and abs(r - rc(u)) < HW + 0.7: return True
        return False
    placed = 0
    while placed < 520:
        r = math.sqrt(rnd.uniform((RS + 0.3) ** 2, (RB - 0.3) ** 2)); a = rnd.uniform(0, 2 * math.pi)
        if near_path(r, a): continue
        if abs(((a - math.pi / 2 + math.pi) % (2 * math.pi)) - math.pi) < 0.12 and r > 16.0: continue
        x, y = CX + r * math.cos(a), CY + r * math.sin(a)
        gch = tilted_chair(rnd, scale=rnd.uniform(1.0, 1.5), tilt=0.9)
        gch.xform(rnd.uniform(0, 2 * math.pi), x, y, cone_h(r) - rnd.uniform(0.1, 0.4))
        R.nocol.add(gch)
        placed += 1
    for k in range(380):
        r = math.sqrt(rnd.uniform((RS + 0.3) ** 2, (RB - 0.2) ** 2)); a = rnd.uniform(0, 2 * math.pi)
        if near_path(r, a): continue
        x, y = CX + r * math.cos(a), CY + r * math.sin(a)
        L = rnd.uniform(0.5, 1.1)
        st = box(-L / 2, -0.025, -0.025, L / 2, 0.025, 0.025, rnd.choice(['walnut', 'oak', 'wood']))
        rot(st, 'y', rnd.uniform(-0.9, 0.9))
        R.nocol.add(st.xform(rnd.uniform(0, 6.3), x, y, cone_h(r) + 0.05))
    # lamps left burning on the slopes
    for k in range(12):
        while True:
            r = rnd.uniform(RS + 1.0, RB - 2.0); a = rnd.uniform(0, 2 * math.pi)
            if not near_path(r, a): break
        lamp(R, CX + r * math.cos(a), CY + r * math.sin(a), cone_h(r) - 0.2, 1.2)
    # a jumble of chairs round the foot, some fallen outward
    for k in range(70):
        a = rnd.uniform(0, 2 * math.pi)
        if abs(((a - math.pi / 2 + math.pi) % (2 * math.pi)) - math.pi) < 0.1: continue
        if abs(((a - TH0 + math.pi) % (2 * math.pi)) - math.pi) < 0.25: continue
        r = RB - rnd.uniform(0.3, 1.2)
        g = tilted_chair(rnd, tilt=0.5)
        R.nocol.add(g.xform(rnd.uniform(0, 6.3), CX + r * math.cos(a), CY + r * math.sin(a), cone_h(r) * 0.3))


def cave(R, rnd):
    """Through the gap on the north side: a low tunnel of chair legs, then a hollow in the pile with a
    bed of cushions and a candle. Somebody sleeps here."""
    cx, cy, cr = CAVE
    y0, y1 = cy + cr - 0.3, CY + RB + 0.3
    th_ = 2.25
    # tunnel: walls and roof of dark wood, legs poking through
    R.parts.add(box(CX - TUN - 0.3, y0, 0, CX - TUN, y1, th_ + 0.25, 'walnut'))
    R.parts.add(box(CX + TUN, y0, 0, CX + TUN + 0.3, y1, th_ + 0.25, 'walnut'))
    R.parts.add(box(CX - TUN - 0.3, y0, th_, CX + TUN + 0.3, y1, th_ + 0.25, 'walnut'))
    for k in range(60):
        y = rnd.uniform(y0, y1)
        s = rnd.choice([-1, 1])
        L = rnd.uniform(0.3, 0.7)
        st = box(0, -0.025, -0.025, L, 0.025, 0.025, rnd.choice(['walnut', 'oak', 'wood']))
        rot(st, 'y', rnd.uniform(-0.6, 0.6)); rot(st, 'z', rnd.uniform(-0.5, 0.5))
        if s < 0: st.xform(math.pi, 0, 0, 0)
        R.nocol.add(st.xform(0, CX + s * TUN, y, rnd.uniform(0.3, th_ - 0.1)))
    for k in range(40):
        y = rnd.uniform(y0, y1)
        st = box(-0.025, -0.025, 0, 0.025, 0.025, rnd.uniform(0.2, 0.5), rnd.choice(['walnut', 'oak']))
        rot(st, 'x', math.pi + rnd.uniform(-0.5, 0.5))
        R.nocol.add(st.xform(0, CX + rnd.uniform(-TUN, TUN), y, th_))
    # the mouth: a frame of chair backs and a toppled armchair half across it
    for dx in (-TUN - 0.15, TUN + 0.15):
        R.nocol.add(box(CX + dx - 0.18, y1 - 0.15, 0, CX + dx + 0.18, y1 + 0.15, th_ + 0.4, 'walnut'))
    R.nocol.add(box(CX - TUN - 0.3, y1 - 0.15, th_, CX + TUN + 0.3, y1 + 0.15, th_ + 0.45, 'walnut'))
    g = Geo()
    g.add(box(-0.45, -0.45, 0, 0.45, 0.45, 0.4, 'velvet')); g.add(box(-0.5, -0.5, 0.4, -0.3, 0.5, 1.1, 'velvet'))
    rot(g, 'y', 1.3)
    R.nocol.add(g.xform(0.4, CX + 1.55, y1 + 0.5, 0.45))
    # the hollow: a round room with a dome of wood, walls bristling with legs
    R.parts.add(ring(cx, cy, 0, 3.3, cr, cr + 0.3, 32, top='walnut', bottom='walnut', inner='walnut', outer='walnut',
                     a0=math.pi / 2 + 0.22, a1=math.pi / 2 + 2 * math.pi - 0.22))
    dome = sphere(cx, cy, 3.1, cr + 0.1, 24, 8, 'walnut', lower=False)
    dome.f = [tuple(reversed(f)) for f in dome.f]; dome.uv = [list(reversed(u)) for u in dome.uv]
    R.nocol.add(dome)
    for k in range(150):
        a = rnd.uniform(0, 2 * math.pi); z = rnd.uniform(0.4, 5.0)
        if abs(((a - math.pi / 2 + math.pi) % (2 * math.pi)) - math.pi) < 0.35 and z < 2.6: continue
        rr = cr if z < 3.1 else max(0.4, math.sqrt(max(0.0, (cr + 0.1) ** 2 - (z - 3.1) ** 2)))
        L = rnd.uniform(0.35, 0.8)
        st = box(-L, -0.025, -0.025, 0.0, 0.025, 0.025, rnd.choice(['walnut', 'oak', 'wood', 'oak']))
        rot(st, 'y', rnd.uniform(-0.7, 0.7) + (0.8 if z > 3.1 else 0.0)); rot(st, 'z', rnd.uniform(-0.4, 0.4))
        R.nocol.add(st.xform(a, cx + rr * math.cos(a), cy + rr * math.sin(a), z))
    R.nocol.add(cyl(cx, cy, 0.0, 0.01, cr, 32, side='carpet', top='carpet'))
    # a bed of cushions, a candle on a stool, a book
    for (x0, y0_, x1, y1_, h, m) in ((-1.6, -1.8, 0.2, -0.6, 0.28, 'velvet'), (-1.7, -0.7, 0.3, 0.3, 0.3, 'green'),
                                     (-1.5, 0.2, 0.1, 1.2, 0.26, 'oxblood'), (-2.2, -1.5, -1.5, 0.9, 0.5, 'velvet'),
                                     (-1.2, -0.9, -0.4, -0.2, 0.42, 'bed')):
        R.parts.add(box(cx + x0, cy + y0_, 0, cx + x1, cy + y1_, h, m))
    R.spot('bed', cx - 0.7, cy - 0.3, 0.3, 0.0)
    R.parts.add(box(cx + 1.0, cy - 1.2, 0, cx + 1.4, cy - 0.8, 0.45, 'oak'))
    R.parts.add(cyl(cx + 1.2, cy - 1.0, 0.45, 0.6, 0.04, 8, side='ivory', top='ivory'))
    R.light(sphere(cx + 1.2, cy - 1.0, 0.66, 0.05, 6, 3, 'e_candle'))
    R.light(sphere(cx + 0.9, cy + 1.6, 2.4, 0.09, 6, 3, 'e_amber'))
    lamp(R, cx + 1.8, cy + 1.0, 0.0, 1.1)
    R.light(sphere(cx - 1.5, cy + 2.0, 1.2, 0.07, 6, 3, 'e_candle'))
    R.parts.add(box(cx + 0.6, cy - 1.6, 0, cx + 0.9, cy - 1.2, 0.05, 'ivory'))
    R.spot('plaque', cx + 0.2, cy + 0.2, 0.0)
    # its walls, for the walker
    secret(R, cx - 0.2, cy, 0.0, 'The Hollow',
           'Inside the mountain, a room made of chair legs, and a bed of cushions still warm. Whoever lives here has read every book on the pile.', r=2.5)


def nav(R):
    g = 1.6
    gal = [R.navpt(x, y, GZ) for (x, y) in ((g, g), (W - g, g), (W - g, D - g), (g, D - g), (g, 37.0))]
    R.link(*gal, gal[0])
    ground = [R.navpt(x, y) for (x, y) in ((7.0, 6.0), (32.0, 6.0), (57.0, 6.0), (57.0, 60.0), (7.0, 60.0), (7.0, 25.3))]
    R.link(*ground, ground[0])
    st = R.navpt(4.1, 25.3)
    tp = R.navpt(4.1, 37.1, GZ)
    R.link(ground[5], st, tp, gal[4])
    pts = [R.navpt(*edge(k / 25, 0)[:2], edge(k / 25, 0)[2]) for k in range(26)]
    R.link(ground[1], *pts)
    R.link(pts[-1], R.navpt(CX, CY - 0.6, SZ))
