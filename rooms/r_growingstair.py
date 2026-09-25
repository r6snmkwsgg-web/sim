"""The Growing Stair: a round tower through every floor with one living tree up the middle of it. Its
branches have grown into a spiral stair, one turn a floor, and its leaves fill the shaft. Somewhere on
every turn the trunk is hollow."""
from kit_h5 import *

CX = CY = C / 2
RW = 7.2                       # the tower wall
RT = 2.15                      # the trunk
RM = 4.7                       # the stair runs from the trunk to here; the landing from here to the wall
TH0 = math.pi / 4              # where the stair meets each landing
NST = 40                       # treads per turn
GAP = math.radians(28)
AS = TH0 + 2 * math.pi * 3.05 / LH      # the crack in the trunk: where the stair is 3.05 m up
ZS = 3.05
RH = 1.42                      # the hollow's radius


def zr(a):
    """Height of the stair at angle a (in this copy, 0..8)."""
    return LH * (((a - TH0) / (2 * math.pi)) % 1.0)


def make():
    R = Room('growingstair', 1, 1, res=1024, repeat=True, lo=-0.4)
    rng = random.Random(37)
    R.sockets()
    # the shaft, leaving the trunk standing: a ring cut from the bark to the tower wall
    R.cut(ring(CX, CY, -LH, 2 * LH, RT, RW, 64, top='tile', bottom='tile', inner='walnut', outer='tile'))
    # the landing ring on each floor, with a deep fascia so the stair arriving from below can't slip under
    R.parts.add(ring(CX, CY, -0.35, 0.0, RM, RW + 0.05, 64, top='floor', bottom='wood'))
    R.parts.add(ring(CX, CY, -1.25, -0.34, RM, RM + 0.2, 64, top='wood', bottom='wood', inner='wood', outer='wood'))
    # the stair: an invisible ramp to walk on, oak treads growing out of the trunk on a spiral branch
    R.col.add(helix(CX, CY, RT - 0.05, RM, 0.0, LH, TH0, TH0 + 2 * math.pi, 0.3, 96))
    da = 2 * math.pi / NST
    for k in range(NST):
        a0 = TH0 + k * da; zt = (k + 1) * LH / NST
        jit = rng.uniform(-0.12, 0.12)
        R.nocol.add(ring(CX, CY, zt - 0.09, zt, RT - 0.1, RM + 0.06 + jit, 2, top='oak', bottom='wood', inner='wood', outer='wood', a0=a0 + 0.01, a1=a0 + da - 0.01))
    R.parts.add(helix(CX, CY, RM - 0.32, RM + 0.02, -0.02, LH, TH0, TH0 + 2 * math.pi, 0.55, 96, top='walnut', side='walnut', bottom='walnut'))
    # the rail: a thin branch along the stair's outer edge, twigs for posts; and round the landing's edge
    ph = 0.95
    R.nocol.add(helix(CX, CY, RM - 0.12, RM - 0.02, ph + LH * GAP / (2 * math.pi), LH, TH0 + GAP, TH0 + 2 * math.pi - GAP, 0.08, 96, top='walnut', side='walnut', bottom='walnut'))
    R.col.add(helix(CX, CY, RM - 0.1, RM - 0.04, ph + 0.15 + LH * GAP / (2 * math.pi), LH, TH0 + GAP, TH0 + 2 * math.pi - GAP, ph + 0.4, 96))
    R.nocol.add(ring(CX, CY, ph - 0.04, ph + 0.04, RM + 0.04, RM + 0.14, 48, top='walnut', bottom='walnut', inner='walnut', outer='walnut', a0=TH0 + GAP, a1=TH0 + 2 * math.pi - GAP))
    R.col.add(ring(CX, CY, 0.0, ph + 0.15, RM + 0.06, RM + 0.12, 48, a0=TH0 + GAP, a1=TH0 + 2 * math.pi - GAP))
    n = 30
    for k in range(n + 1):
        a = TH0 + GAP + (2 * math.pi - 2 * GAP) * k / n
        x, y = CX + math.cos(a) * (RM - 0.07), CY + math.sin(a) * (RM - 0.07)
        z = zr(a) if k < n else LH - LH * GAP / (2 * math.pi)
        R.nocol.add(beam((x, y, z - 0.05), (x + rng.uniform(-0.04, 0.04), y + rng.uniform(-0.04, 0.04), z + ph), 0.035, 'walnut'))
        x, y = CX + math.cos(a) * (RM + 0.09), CY + math.sin(a) * (RM + 0.09)
        R.nocol.add(beam((x, y, 0.0), (x, y, ph), 0.035, 'walnut'))
    # bark: ridges twisting up the trunk
    for k in range(14):
        a = 2 * math.pi * k / 14
        pts = []
        for j in range(5):
            z = -0.4 + j * 2.0
            b = a + 0.5 * j / 4
            pts.append((CX + math.cos(b) * (RT + 0.02), CY + math.sin(b) * (RT + 0.02), z))
        for p, q in zip(pts, pts[1:]):
            R.nocol.add(beam(p, q, 0.22, 'walnut', 0.08))
    branches(R, rng)
    hollow(R, rng)
    # tall windows of daylight in the diagonals, and bookcases round the wall between them and the doors
    for q in range(4):
        a = math.radians(45 + 90 * q)
        ux, uy = math.cos(a), math.sin(a)
        win = box(RW - 0.3, -0.75, 1.0, RW + 1.1, 0.75, 6.6, 'tile', bottom='tile')
        R.cut(win.xform(a, CX, CY, 0))
        pr = arch_profile(0, 1.5, 6.6, 0.0, 10)
        R.light(box(RW + 0.95, -0.72, 1.05, RW + 1.0, 0.72, 6.55, 'e_skydome').xform(a, CX, CY, 0))
        for s in (-1, 1):   # sunlight on the reveals
            R.light(box(RW - 0.25, s * 0.74 - 0.01, 1.05, RW + 0.9, s * 0.74 + 0.01, 6.55, 'e_sky').xform(a, CX, CY, 0))
        for s in (-0.25, 0.25):
            R.nocol.add(box(RW + 0.9, s - 0.02, 1.0, RW + 0.95, s + 0.02, 6.6, 'iron').xform(a, CX, CY, 0))
        for z in (2.4, 3.8, 5.2):
            R.nocol.add(box(RW + 0.9, -0.75, z - 0.02, RW + 0.95, 0.75, z + 0.02, 'iron').xform(a, CX, CY, 0))
        R.parts.add(box(RW - 0.4, -0.85, 0.0, RW + 0.1, 0.85, 1.0, 'tile', top='oak').xform(a, CX, CY, 0))
        for off in (-20, 20):
            b = a + math.radians(off)
            half = 1.2
            bx, by = CX + math.cos(b) * (RW - 0.06), CY + math.sin(b) * (RW - 0.06)
            fa = b + math.pi
            vx, vy = math.sin(fa), -math.cos(fa)
            shelf(R, bx - vx * half, by - vy * half, 0, 2 * half, fa, rows=14, frame='walnut')
    # hanging lanterns in the leaves (amber: they stay lit), green lamps on the window sills
    for k in range(6):
        a = TH0 + math.pi / 6 + k * math.pi / 3
        x, y = CX + math.cos(a) * 5.9, CY + math.sin(a) * 5.9
        z = 3.6 + 0.4 * (k % 2)
        R.nocol.add(cyl(x, y, z + 0.24, 6.9, 0.008, 4, side='iron', caps=False))
        lantern(R, x, y, z, 'e_amber', s=1.3)
    for q in range(4):
        a = math.radians(45 + 90 * q)
        desk_lamp(R, CX + math.cos(a) * (RW - 0.1), CY + math.sin(a) * (RW - 0.1), 1.0)
    pts = [R.navpt(CX + math.cos(k * math.pi / 4 + math.pi / 8) * 6.0, CY + math.sin(k * math.pi / 4 + math.pi / 8) * 6.0) for k in range(8)]
    R.link(*pts, pts[0])
    R.spot('ramp', CX + math.cos(TH0) * 3.4, CY + math.sin(TH0) * 3.4, 0.05, TH0 + math.pi / 2)
    R.spot('probe', CX + 5.9, CY, 3.0)
    R.meta.update(label='The Growing Stair', weight=4,
                  blurb='A tree has come up through the floor and kept going. Somebody taught its branches to be a staircase, or it learned by watching.')
    R.meta['ramp'] = [CX, CY, RT, RM, TH0, LH]
    R.meta['box'] = [[CX - RW, 0, CY - RW], [CX + RW, LH, CY + RW]]
    fx(R, 'dust', [CX - RW, 0, CY - RW, CX + RW, TOP, CY + RW])
    return tidy(R)


def branches(R, rng):
    """Boughs from the trunk out over the landing to the wall, kept clear of the stair's headroom,
    with leaves where they end."""
    k = 0
    for i in range(22):
        a = TH0 + 2 * math.pi * (i + rng.uniform(-0.3, 0.3)) / 22
        best = None
        for zb in (2.6, 3.1, 3.6, 4.1, 4.6, 5.1, 5.6, 6.0):
            if (zb - zr(a)) % LH >= 2.7 and (zb - zr(a)) % LH <= 5.6 and (zb + 0.4 - zr(a + 0.2)) % LH >= 2.7:
                best = zb if best is None or rng.random() < 0.4 else best
        if best is None: continue
        zb = best
        rise = rng.uniform(0.6, 1.3)
        b = a + rng.uniform(-0.2, 0.2)
        p0 = (CX + math.cos(a) * (RT - 0.3), CY + math.sin(a) * (RT - 0.3), zb)
        p1 = (CX + math.cos(b) * RM, CY + math.sin(b) * RM, zb + rise * 0.6)
        p2 = (CX + math.cos(b + 0.1) * (RW - 0.1), CY + math.sin(b + 0.1) * (RW - 0.1), min(7.2, zb + rise))
        R.nocol.add(beam(p0, p1, 0.34, 'walnut', 0.3))
        R.nocol.add(beam(p1, p2, 0.22, 'walnut', 0.2))
        k += 1
        leaves(R, p2[0] - math.cos(b) * 0.9, p2[1] - math.sin(b) * 0.9, p2[2] - 0.1, 1.2, 5, rng)
    # the canopy over the landing (never over the stair)
    for i in range(26):
        a = 2 * math.pi * i / 26 + rng.uniform(-0.1, 0.1)
        r = rng.uniform(RM + 0.8, RW - 0.6)
        leaves(R, CX + math.cos(a) * r, CY + math.sin(a) * r, rng.uniform(5.7, 6.9), 0.9, 3, rng)
    # ivy down the tower wall
    for i in range(18):
        a = 2 * math.pi * i / 18 + 0.1
        if min(abs(math.remainder(a - q * math.pi / 2, 2 * math.pi)) for q in range(4)) < 0.3: continue
        vine(R, CX + math.cos(a) * (RW - 0.08), CY + math.sin(a) * (RW - 0.08), rng.uniform(2.6, 4.5), 7.4, rng)


def hollow(R, rng):
    """A room inside the trunk: a crack by the stair, crouch through, and there is a bed in the tree."""
    ux, uy = math.cos(AS), math.sin(AS)
    zf = ZS
    R.cut(cyl(CX, CY, zf, zf + 2.4, RH, 20, side='oak', top='oak', bottom='oak'))
    # the crack: a narrow slot through the bark, at crawl height
    crack = box(RH - 0.3, -0.42, zf, RT + 0.25, 0.42, zf + 1.3, 'walnut', bottom='oak')
    R.cut(crack.xform(AS, CX, CY, 0))
    # ivy hanging over the crack
    for s in (-0.35, -0.12, 0.1, 0.3):
        vine(R, CX + ux * (RT + 0.12) - uy * s, CY + uy * (RT + 0.12) + ux * s, zf + 0.5 + abs(s), zf + 2.6, rng)
    # the bed on the far side, a candle in a niche, a small shelf, an open book
    bx, by = CX - ux * 0.55, CY - uy * 0.55
    R.parts.add(box(-0.95, -0.42, 0, 0.95, 0.42, 0.35, 'bed', sides='wood').xform(AS + math.pi / 2, bx, by, zf))
    R.nocol.add(box(-0.3, -0.35, 0.35, 0.3, 0.35, 0.47, 'velvet').xform(AS + math.pi / 2, bx + math.cos(AS + math.pi / 2) * 0.6, by + math.sin(AS + math.pi / 2) * 0.6, zf))
    R.spot('bed', bx, by, zf + 0.35, AS)
    sa = AS - math.pi / 2
    sx, sy = CX + math.cos(sa) * (RH - 0.03), CY + math.sin(sa) * (RH - 0.03)
    fa = sa + math.pi
    vx, vy = math.sin(fa), -math.cos(fa)
    shelf(R, sx - vx * 0.45, sy - vy * 0.45, zf + 0.9, 0.9, fa, rows=3, frame='oak', depth=0.26)
    na = AS + math.pi / 2
    candle(R, CX + math.cos(na) * 1.05, CY + math.sin(na) * 1.05, zf, h=0.2, stand=0.5)
    R.light(sphere(CX, CY, zf + 2.2, 0.08, 8, 4, 'e_amber'))
    R.spot('plaque', CX + math.cos(na) * 1.05, CY + math.sin(na) * 1.05, zf + 0.6)
    secret(R, CX + ux * 0.4, CY + uy * 0.4, zf, 'The Hollow in the Trunk',
           'The tree is hollow here, and warm, and someone has put a bed in it. The rings in the walls go back further than the library does.', r=1.3)
