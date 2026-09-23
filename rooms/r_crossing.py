"""The Crossing: four stone barrel vaults meet under a dome with an oculus; a stepped round pit below it.
Book niches line the tunnels and the dome's diagonals."""
from lib import *


def make():
    R = Room('crossing', 1, 1, res=1024)
    R.sockets()
    cx = cy = C / 2
    # two tunnels crossing (their intersection is a groin vault)
    tw, tj = 4.2, 3.0
    pr = arch_profile(cx, tw, 0, tj, 24)
    R.cut(prism(pr, 'y', T - 0.02, C - T + 0.02, arch_mats(len(pr))))
    R.cut(prism(pr, 'x', T - 0.02, C - T + 0.02, arch_mats(len(pr))))
    # round chamber with a hemispherical dome
    rc, zs = 4.3, 3.1
    R.cut(cyl(cx, cy, 0, zs + 0.01, rc, 64, side='tile', bottom='floor', top='tile'))
    R.cut(sphere(cx, cy, zs, rc, 64, 24, 'tile', lower=False))
    R.cut(cyl(cx, cy, zs + rc - 0.5, R.hi + 0.5, 0.95, 40, side='tile', top='tile', bottom='tile'))   # oculus
    R.light(cyl(cx, cy, R.hi - 0.08, R.hi - 0.05, 0.95, 40, side='e_sky', top='e_sky', bottom='e_sky'))
    # the stepped pit under the oculus
    R.round_pool(cx, cy, 2.7, 1.1, segs=64)
    for k in range(4):   # step lights, lit day and night
        a = math.pi / 4 + k * math.pi / 2
        g = box(-0.22, -0.04, -0.22, 0.22, 0.04, -0.1, 'e_pool').xform(a + math.pi / 2, cx + math.cos(a) * 2.69, cy + math.sin(a) * 2.69)
        R.light(g)
    # niches along the tunnels (in the four corner piers), each holding a bookcase
    nw, nj, nd = 2.3, 2.5, 0.62
    arm_mid = (T + cy - math.sqrt(rc ** 2 - (tw / 2) ** 2)) / 2   # halfway between the door wall and the chamber
    for (px, py, face) in [(cx - tw / 2, arm_mid, 'x+'), (cx + tw / 2, arm_mid, 'x-'),
                           (cx - tw / 2, C - arm_mid, 'x+'), (cx + tw / 2, C - arm_mid, 'x-'),
                           (arm_mid, cy - tw / 2, 'y+'), (arm_mid, cy + tw / 2, 'y-'),
                           (C - arm_mid, cy - tw / 2, 'y+'), (C - arm_mid, cy + tw / 2, 'y-')]:
        npr = arch_profile(0, nw, 0.35, nj, 16)
        if face[0] == 'x':   # niche dug into a pier face that looks along x
            s = 1 if face[1] == '-' else -1   # dig toward +x on the east side of the tunnel
            x0, x1 = (px - nd, px + 0.05) if s < 0 else (px - 0.05, px + nd)
            R.cut(prism([(p + py, q) for p, q in npr], 'x', x0, x1, arch_mats(len(npr), 'tile', 'tile')))
            back = px - nd if s < 0 else px + nd
            if s < 0: R.shelf(back, py + nw / 2 - 0.08, 0.35, nw - 0.16, '+x', rows=5, frame='paint', sides=False, back=False)
            else:     R.shelf(back, py - nw / 2 + 0.08, 0.35, nw - 0.16, '-x', rows=5, frame='paint', sides=False, back=False)
        else:
            s = 1 if face[1] == '-' else -1
            y0, y1 = (py - nd, py + 0.05) if s < 0 else (py - 0.05, py + nd)
            R.cut(prism([(p + px, q) for p, q in npr], 'y', y0, y1, arch_mats(len(npr), 'tile', 'tile')))
            back = py - nd if s < 0 else py + nd
            if s < 0: R.shelf(px - nw / 2 + 0.08, back, 0.35, nw - 0.16, '+y', rows=5, frame='paint', sides=False, back=False)
            else:     R.shelf(px + nw / 2 - 0.08, back, 0.35, nw - 0.16, '-y', rows=5, frame='paint', sides=False, back=False)
    # four big niches on the chamber's diagonals
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        npr = arch_profile(0, 1.9, 0.3, 2.1, 18)
        g = prism(npr, 'y', rc - 0.4, rc + 0.75, arch_mats(len(npr), 'tile', 'tile')).xform(a - math.pi / 2, cx, cy)
        R.cut(g)
        bx, by = cx + math.cos(a) * (rc + 0.75), cy + math.sin(a) * (rc + 0.75)
        # back-left corner seen from the front (the shelf faces back toward the centre)
        fa = a + math.pi
        ux, uy = math.sin(fa), -math.cos(fa)
        R.shelf(bx - ux * 0.87, by - uy * 0.87, 0.3, 1.74, fa, rows=5, frame='paint', sides=False, back=False)
    # lamps: small round skylights along each tunnel crown
    for (lx, ly) in [(cx, 1.9), (cx, C - 1.9), (1.9, cy), (C - 1.9, cy)]:
        R.cut(cyl(lx, ly, tj + tw / 2 - 0.3, R.hi + 0.5, 0.45, 24))
        R.light(cyl(lx, ly, R.hi - 0.08, R.hi - 0.05, 0.45, 24, side='e_sky', top='e_sky', bottom='e_sky'))
    # where people stand and walk
    ring = [R.navpt(cx + math.cos(k * math.pi / 4) * 3.5, cy + math.sin(k * math.pi / 4) * 3.5) for k in range(8)]
    R.link(*ring, ring[0])
    for k, (dx, dy) in enumerate([(0, -1), (1, 0), (0, 1), (-1, 0)]):
        a = R.navpt(cx + dx * 6.6, cy + dy * 6.6)
        R.link(a, ring[(k * 2 + 6) % 8])
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        R.spot('read', cx + math.cos(a) * 3.3, cy + math.sin(a) * 3.3, 0, a)
    R.spot('probe', cx, cy, 1.7)
    R.meta['label'] = 'The Crossing'
    return R
