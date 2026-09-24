"""The Chute: a round stone shaft through every floor. An iron stair winds round its wall, one turn a
floor, forever up and forever down; a railed ring at each floor meets it and the doorways. The
middle is open all the way."""
from lib import *
from kit_e import *

D2R = math.pi / 180


def make():
    R = Room('chute', 1, 1, res=1024, repeat=True, lo=-0.4)
    R.sockets()
    cx = cy = C / 2
    rw = 7.2                                   # the shaft wall
    s0, s1 = 5.7, rw                           # the stair's band
    r0 = 4.3                                   # the ring's inner edge (the open core)
    R.cut(cyl(cx, cy, -LH, 2 * LH, rw, 96, side='tile', top='tile', bottom='tile'))
    # the stair's heights: a flat landing at the south door (z=0), then up round the wall, passing
    # the east door at 2.7 m, the north at 4.0, the west at 5.3, and back over the south at 8.
    S = -90 * D2R
    keys = [(S + 10 * D2R, 0.0), (0.0, 2.7), (90 * D2R, 4.0), (180 * D2R, 5.3), (S + 350 * D2R, LH)]
    # the collider the feet ride (a smooth band), and the visible iron treads on a stringer
    R.col.add(spiral(cx, cy, s0, s1 + 0.05, keys, 0.12, math.radians(2)))
    tot = 0
    for (a0, z0), (a1, z1) in zip(keys, keys[1:]):
        n = max(1, int(round((z1 - z0) / 0.19)))
        for k in range(n):
            ta0 = a0 + (a1 - a0) * k / n; ta1 = a0 + (a1 - a0) * (k + 1) / n
            z = z0 + (z1 - z0) * (k + 0.5) / n + (z1 - z0) / n * 0.5
            R.nocol.add(ring(cx, cy, z - 0.07, z, s0 + 0.02, s1, 4, top='iron', bottom='iron', inner='brass', outer='iron', a0=ta0, a1=ta1 + 0.004))
            tot += 1
    R.parts.add(spiral(cx, cy, s0 - 0.02, s0 + 0.06, keys, 0.45, math.radians(3), top='iron', side='iron', bottom='iron', dz=0.1))
    # the ring at this floor, the south landing, and bridges from the other doors under the stair
    R.parts.add(ring(cx, cy, -0.3, 0.0, r0, s0, 96, top='floor', bottom='plaster', inner='tile', outer='tile'))
    R.parts.add(ring(cx, cy, -0.3, 0.0, s0 - 0.01, rw + 0.08, 12, top='floor', bottom='plaster', inner='tile', outer='tile', a0=S - 10 * D2R, a1=S + 10 * D2R))
    bh = 11 * D2R
    for ad in (0.0, 90 * D2R, 180 * D2R):
        R.parts.add(ring(cx, cy, -0.2, 0.0, s0 - 0.01, rw + 0.08, 12, top='floor', bottom='plaster', inner='tile', outer='tile', a0=ad - bh, a1=ad + bh))
    # rails: round the core; round the ring's outer edge between the bridges; along the bridges' sides;
    # along the stair's inner edge; across the doorways the stair passes above
    arc_rail(R, cx, cy, r0 + 0.04, 0, 2 * math.pi, lambda a: 0.0, step=math.radians(5))
    for (a, b) in ((11, 79), (101, 169), (191, 260), (280, 349)):
        arc_rail(R, cx, cy, s0 - 0.05, a * D2R, b * D2R, lambda a: 0.0)
    for ad in (0.0, 90 * D2R, 180 * D2R):
        for e in (ad - bh, ad + bh):
            p0 = (cx + math.cos(e) * (s0 - 0.05), cy + math.sin(e) * (s0 - 0.05), 0.0)
            p1 = (cx + math.cos(e) * (rw - 0.05), cy + math.sin(e) * (rw - 0.05), 0.0)
            rail(R, [p0, p1])
    arc_rail(R, cx, cy, s0 + 0.03, keys[0][0], keys[-1][0], lambda a: zpw(keys, a), step=math.radians(4))
    for ad in (0.0, 90 * D2R):
        arc_rail(R, cx, cy, rw - 0.05, ad - 13 * D2R, ad + 13 * D2R, lambda a: zpw(keys, a), step=math.radians(4))
    # lamps on the wall above the stair, and small amber ones at the ring
    for k in range(12):
        a = S + (15 + k * 30) * D2R
        z = zpw(keys, a) + 2.5
        bx, by = cx + math.cos(a) * (rw - 0.02), cy + math.sin(a) * (rw - 0.02)
        R.parts.add(beam((bx, by, z - 0.03), (cx + math.cos(a) * (rw - 0.35), cy + math.sin(a) * (rw - 0.35), z - 0.03), 0.05, 0.05, 'brass'))
        R.light(sphere(cx + math.cos(a) * (rw - 0.4), cy + math.sin(a) * (rw - 0.4), z + 0.08, 0.13, 10, 6, 'e_lamp'))
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        R.light(sphere(cx + math.cos(a) * (r0 + 0.04), cy + math.sin(a) * (r0 + 0.04), 1.05, 0.06, 8, 4, 'e_amber'))
    # shelves of books on the wall along the stair, between the doorways
    for k in range(10):
        a = S + (38 + k * 30) * D2R
        if min(abs(((a - ad + math.pi) % (2 * math.pi)) - math.pi) for ad in (S, 0.0, math.pi / 2, math.pi)) < 22 * D2R: continue
        half = 0.7
        z = zpw(keys, a) - 0.1
        bx, by = cx + math.cos(a) * (rw - 0.1), cy + math.sin(a) * (rw - 0.1)
        fa = a + math.pi
        ux, uy = math.sin(fa), -math.cos(fa)
        R.shelf(bx - ux * half, by - uy * half, z + 0.35, 2 * half, fa, rows=4, frame='walnut', back=True)
    # walkers: round the ring, out to each door, up the stair to the next floor
    ring_pts = [R.navpt(cx + math.cos(k * math.pi / 4 + math.pi / 8) * 5.0, cy + math.sin(k * math.pi / 4 + math.pi / 8) * 5.0) for k in range(8)]
    R.link(*ring_pts, ring_pts[0])
    for (ad, i) in ((S, 5), (0.0, 7), (math.pi / 2, 1), (math.pi, 3)):
        p = R.navpt(cx + math.cos(ad) * 6.4, cy + math.sin(ad) * 6.4)
        q = R.navpt(cx + math.cos(ad) * 5.0, cy + math.sin(ad) * 5.0)
        R.link(q, p)
        R.link(q, ring_pts[i]); R.link(q, ring_pts[(i + 1) % 8])
    R.spot('probe', cx, cy, 3.5)
    R.meta.update(label='The Chute', weight=40,
                  blurb='An iron stair turns round and round the wall of a round shaft, one turn to a floor. It does not end at the top, or the bottom. The middle is empty all the way down.')
    R.meta['core'] = [cx, cy, r0]
    R.meta['box'] = [[C / 2 - rw, 0, C / 2 - rw], [C / 2 + rw, LH, C / 2 + rw]]
    return R
