"""The Organ: a brass pipe organ fills the north wall under a stone barrel vault, its pipes rising
into the lunette; you come in underneath it. A console with a bench, candles, books in its case."""
from lib import *
from kit_b import *


def make():
    R = Room('organ', 1, 1, res=1024)
    R.sockets(floor='floor', wall='tile')
    H = 5.7
    R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, C - T + 0.02, H, 'tile', bottom='floor', top='plaster'))
    vp = arch_profile(8, C - 2 * T, 0, H, 32, rise=1.8)
    R.cut(prism(vp, 'y', T - 0.02, C - T + 0.02, arch_mats(len(vp), 'floor', 'tile')))
    # ribs across the vault
    for y in (3.2, 6.4, 9.6, 12.8):
        rib = arch_profile(8, C - 2 * T, 0, H, 32, rise=1.8)
        inner = arch_profile(8, C - 2 * T - 0.5, 0, H, 32, rise=1.62)
        R.parts.add(prism(rib[2:] + inner[2:][::-1], 'y', y - 0.18, y + 0.18, 'tile', cap='tile'))
    # the case: bookcases below, a ledge of pipes above, a gap for the north doorway
    ZC, Y0 = 2.45, 14.0
    for (a, b) in ((T, 6.25), (9.75, C - T)):
        R.parts.add(box(a, Y0, 0, b, C - T, ZC, 'walnut', skip=('-z',)))
        R.parts.add(box(a, Y0 - 0.12, ZC, b, C - T, ZC + 0.18, 'walnut'))
        bshelf(R, b - 0.15, Y0 - 0.0, 0.1, b - a - 0.3, '-y', rows=5, frame='walnut', back=True, sides=True, crown=False)
    R.parts.add(box(6.25, Y0 - 0.12, 4.3, 9.75, C - T, 4.6, 'walnut'))            # bridge over the door
    for x in (6.1, 9.9):
        R.parts.add(box(x - 0.18, Y0 - 0.2, 0, x + 0.18, Y0 + 0.2, 4.6, 'walnut', skip=('-z',)))
    # up-lights along the ledge front
    for (a, b, z) in ((T + 0.2, 6.0, ZC + 0.18), (10.0, C - T - 0.2, ZC + 0.18), (6.5, 9.5, 4.6)):
        R.light(box(a, Y0 - 0.1, z, b, Y0 - 0.02, z + 0.04, 'e_pool'))
    # pipes: heights follow the lunette, two rows (brass in front, bronze behind)
    def lun(x):
        u = (x - 8) / (C / 2 - T)
        return H + 1.8 * max(0.0, 1 - u * u) - 0.35
    for row, (y, m, r0, off) in enumerate(((Y0 + 0.35, 'brass', 0.15, 0.0), (Y0 + 0.95, 'bronze', 0.19, 0.22))):
        x = T + 0.35 + off
        k = 0
        while x < C - T - 0.3:
            over_door = 6.0 < x < 10.0
            z0 = 4.6 if over_door else ZC + 0.18
            wave = 0.5 + 0.5 * math.cos(k * 0.9)
            top = lun(x) - (0.45 if row == 0 else 0.12) - 0.9 * wave * (1 if row == 0 else 0.3)
            if over_door: top = min(top, lun(x) - 0.3)
            r = r0 * (0.75 + 0.35 * (top - z0) / 5.0)
            R.nocol.add(cyl(x, y, z0 + 0.35, top, r, 8, side=m, caps=False))
            R.nocol.add(cyl(x, y, z0, z0 + 0.35, r * 0.35, 5, side=m, caps=False))   # the foot
            if row == 0:
                R.nocol.add(box(x - r * 0.55, y - r - 0.01, z0 + 0.5, x + r * 0.55, y - r + 0.03, z0 + 0.62, 'black', skip=('+x', '-x', '+y', '+z', '-z')))   # mouth
            x += 2 * r + 0.08
            k += 1
    # the console, facing the organ, and its bench
    cx, cy = 8.0, 10.4
    R.parts.add(box(cx - 1.1, cy, 0, cx + 1.1, cy + 0.85, 1.25, 'walnut', skip=('-z',)))
    R.parts.add(box(cx - 1.15, cy - 0.05, 1.25, cx + 1.15, cy + 0.9, 1.32, 'walnut'))
    for k, (z, m) in enumerate(((0.74, 'ivory'), (0.86, 'ivory'), (0.98, 'ivory'))):
        R.parts.add(box(cx - 0.85, cy - 0.34 + k * 0.1, z, cx + 0.85, cy, z + 0.05, 'walnut', top=m))
        for j in range(21):
            if j % 7 in (0, 3): continue
            bx = cx - 0.8 + j * 1.6 / 21
            R.nocol.add(box(bx, cy - 0.24 + k * 0.1, z + 0.05, bx + 0.03, cy - 0.02, z + 0.07, 'black', skip=('-z', '+y')))
    R.parts.add(slope_box(cx - 0.6, cx + 0.6, cy - 0.05, cy + 0.05, 1.32, 1.32, 1.72, 1.72, 'walnut'))   # music desk
    for s in (-1, 1):
        for k in range(4):
            R.nocol.add(box(cx + s * 0.97 - 0.025, cy - 0.06, 0.8 + k * 0.12, cx + s * 0.97 + 0.025, cy, 0.84 + k * 0.12, 'ivory', skip=('+y',)))
        candle(R, cx + s * 0.95, cy + 0.4, 1.32, h=0.2)
    R.parts.add(box(cx - 0.8, cy - 1.15, 0.45, cx + 0.8, cy - 0.8, 0.52, 'walnut'))
    for x in (cx - 0.75, cx + 0.7):
        R.parts.add(box(x, cy - 1.12, 0, x + 0.05, cy - 0.83, 0.45, 'walnut', skip=('-z',)))
    R.spot('sit', cx, cy - 0.98, 0.52, math.pi / 2)
    # candelabra round it
    for (x, y) in ((5.4, 11.2), (10.6, 11.2), (5.4, 8.2), (10.6, 8.2)):
        candelabrum(R, x, y, 1.45)
    # books on the other walls
    wall_shelves(R, rows=9, frame='oak', sides='SWE', segs=((0.6, 6.2), (9.8, 13.6)))
    wall_shelves(R, rows=9, frame='oak', sides='S', segs=((9.8, C - 0.6),))
    # lamps hung from the vault
    for y in (3.2, 6.4, 9.6):
        pendant(R, 8, y, 3.6, H + 1.75, r=0.22)
    for (x, y) in ((4.0, 4.8), (12.0, 4.8)):
        pendant(R, x, y, 3.8, H + 1.2, r=0.16)
    # pews facing the organ
    for y in (3.4, 5.2, 7.0):
        for (a, b) in ((2.9, 6.4), (9.6, 13.1)):
            R.parts.add(box(a, y - 0.25, 0.42, b, y + 0.25, 0.48, 'walnut', top='velvet'))
            R.parts.add(box(a, y - 0.3, 0.48, b, y - 0.24, 0.95, 'walnut'))
            for x in (a + 0.05, b - 0.12):
                R.parts.add(box(x, y - 0.3, 0, x + 0.07, y + 0.25, 0.95, 'walnut', skip=('-z',)))
            for k in range(4):
                R.spot('sit', a + 0.5 + k * (b - a - 1.0) / 3, y, 0.48, math.pi / 2)
    loop(R, [(1.6, 1.8), (8, 1.8), (C - 1.6, 1.8), (C - 1.6, 8), (C - 1.6, 12.8), (8, 12.8), (1.6, 12.8), (1.6, 8)])
    a = R.navpt(8, 8.4); b = R.navpt(8, 2.6); R.link(b, a)
    R.spot('probe', 8, 6, 2.0)
    R.meta.update(label='The Organ', weight=4,
                  blurb='An organ the size of a wall, and no one to play it. The stops are labelled in a language that is almost yours.')
    R.meta['box'] = [[T, 0, T], [C - T, H + 1.8, C - T]]
    return R
