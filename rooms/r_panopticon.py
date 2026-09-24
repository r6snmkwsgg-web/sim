"""The Panopticon: a round hall under a shallow dome. Sixteen stacks radiate from a round tower in the
middle, a desk wrapped round its foot and a crown of lamps on its head; from its dark slit windows
someone could see straight down every aisle. A corridor runs round the wall."""
from lib import *
from kit_f import *


def make():
    R = Room('panopticon', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    W = R.W
    cx = cy = W / 2
    Rr, Hw, rise = 15.3, 5.2, 2.1
    R.cut(cyl(cx, cy, 0, Hw + 0.01, Rr, 96, side='tile', bottom='terrazzo', top='plaster'))
    R.cut(dome_cap(cx, cy, Hw, Rr, rise, 96, 10, 'plaster', 'plaster'))
    R.cut(cyl(cx, cy, Hw + rise - 0.3, TOP - 0.08, 1.4, 32, side='tile', top='plaster', bottom='plaster'))
    R.light(cyl(cx, cy, TOP - 0.12, TOP - 0.1, 1.4, 32, side='e_sky', top='e_sky', bottom='e_sky'))
    R.parts.add(ring(cx, cy, Hw - 0.25, Hw, Rr - 0.25, Rr + 0.05, 96, top='tile', bottom='tile', inner='tile', outer='tile'))
    # short vaulted passages from the doorways to the ring
    pr = arch_profile(0, DW, 0, DJ, 18)
    for c in (8.0, 24.0):
        R.cut(prism([(p + c, q) for p, q in pr], 'y', T - 0.05, 5.0, arch_mats(len(pr), 'terrazzo', 'tile')))
        R.cut(prism([(p + c, q) for p, q in pr], 'y', W - 5.0, W - T + 0.05, arch_mats(len(pr), 'terrazzo', 'tile')))
        R.cut(prism([(p + c, q) for p, q in pr], 'x', T - 0.05, 5.0, arch_mats(len(pr), 'terrazzo', 'tile')))
        R.cut(prism([(p + c, q) for p, q in pr], 'x', W - 5.0, W - T + 0.05, arch_mats(len(pr), 'terrazzo', 'tile')))
    # the tower: stone drum, slit windows, a desk round its foot, a crown of lamps on top
    rt, ht = 2.1, 5.0
    R.parts.add(cyl(cx, cy, 0, ht, rt, 40, side='tile', top='tile', caps=True))
    R.parts.add(cyl(cx, cy, ht, ht + 0.3, rt + 0.3, 40, side='tile', top='tile', bottom='tile'))
    R.parts.add(cyl(cx, cy, 0, 0.3, rt + 0.15, 40, side='tile', top='tile', bottom='tile'))
    for k in range(16):
        a = (k + 0.5) * 2 * math.pi / 16
        g = box(-0.12, -0.03, 2.9, 0.12, 0.02, 4.3, 'black').xform(a - math.pi / 2, cx + math.cos(a) * rt, cy + math.sin(a) * rt)
        if k == 5:
            R.light(box(-0.12, -0.03, 2.9, 0.12, 0.02, 4.3, 'e_amber').xform(a - math.pi / 2, cx + math.cos(a) * rt, cy + math.sin(a) * rt))
        else:
            R.parts.add(g)
    # the desk: a ring counter with a gap to the south-west, a gilt edge
    a0, a1 = -math.pi * 0.62, -math.pi * 0.62 + 2 * math.pi - 0.5
    R.parts.add(ring(cx, cy, 0, 1.0, 3.2, 3.5, 64, top='walnut', bottom='walnut', inner='walnut', outer='walnut', a0=a0, a1=a1))
    R.parts.add(ring(cx, cy, 1.0, 1.06, 3.0, 3.62, 64, top='leather', bottom='walnut', inner='gilt', outer='gilt', a0=a0, a1=a1))
    for k in range(6):
        a = a0 + 0.4 + k * (a1 - a0 - 0.8) / 5
        x, y = cx + math.cos(a) * 3.3, cy + math.sin(a) * 3.3
        R.nocol.add(cyl(x, y, 1.06, 1.4, 0.015, 5, side='brass', caps=False))
        R.nocol.add(cyl(x, y, 1.36, 1.46, 0.14, 10, side='green', top='green', bottom='green'))
        R.light(cyl(x, y, 1.34, 1.36, 0.12, 10, side='e_candle', top='e_candle', bottom='e_candle'))
    R.spot('read', cx + math.cos(0.5) * 2.65, cy + math.sin(0.5) * 2.65, 0, 0.5 + math.pi)
    zc = ht + 0.3
    R.nocol.add(ring(cx, cy, zc, zc + 0.12, rt - 0.2, rt + 0.1, 40, top='brass', bottom='brass', inner='brass', outer='brass'))
    for k in range(16):
        a = k * 2 * math.pi / 16
        x, y = cx + math.cos(a) * (rt - 0.05), cy + math.sin(a) * (rt - 0.05)
        R.nocol.add(bar((x, y, zc + 0.1), (x + math.cos(a) * 0.25, y + math.sin(a) * 0.25, zc + 0.75), 0.04, 0.04, 'brass'))
        R.light(sphere(x + math.cos(a) * 0.28, y + math.sin(a) * 0.28, zc + 0.85, 0.13, 10, 5, 'e_lamp'))
    R.light(sphere(cx, cy, zc + 0.9, 0.45, 16, 8, 'e_lamp'))
    # sixteen radial stacks
    r0, r1 = 5.6, 11.8
    for k in range(16):
        a = k * 2 * math.pi / 16
        stack2(R, cx + math.cos(a) * r0, cy + math.sin(a) * r0, a, r1 - r0, 0, 6, frame='oak', crown='walnut', ends='walnut')
    # lamps down each aisle and round the ring corridor
    for k in range(16):
        a = (k + 0.5) * 2 * math.pi / 16
        for (r, z) in ((8.7, 3.3), (13.8, 3.4)):
            x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
            lamp(R, x, y, z, 0.2, chain=dome_z(r, Rr, Hw, rise) if r < Rr - 0.3 else Hw)
    # bookcases on the wall between the passages
    door_angles = [math.atan2(p[1] - cy, p[0] - cx) for p in ((8, 0), (24, 0), (32, 8), (32, 24), (24, 32), (8, 32), (0, 24), (0, 8))]
    door_angles = sorted((a % (2 * math.pi)) for a in door_angles)
    gap = math.radians(9.0)
    for i in range(8):
        s, e = door_angles[i] + gap, door_angles[(i + 1) % 8] - gap
        if e < s: e += 2 * math.pi
        n = max(1, int(round((e - s) * Rr / 3.0)))
        arc_shelf(R, cx, cy, Rr - 0.06, s, e, n, 0, 8, frame='walnut')
    # walkers: round the ring corridor, round the desk, and out along four aisles
    outer = loop(R, [(cx + 13.8 * math.cos((k + 0.5) * math.pi / 8), cy + 13.8 * math.sin((k + 0.5) * math.pi / 8)) for k in range(16)])
    inner = loop(R, [(cx + 4.5 * math.cos((k + 0.5) * math.pi / 8), cy + 4.5 * math.sin((k + 0.5) * math.pi / 8)) for k in range(16)])
    for k in (0, 4, 8, 12):
        R.link(inner[k], outer[k])
    R.spot('probe', cx + 8.7, cy + 1.7, 1.7)
    R.meta.update(label='The Panopticon', weight=5,
                  blurb='Every aisle runs straight to the tower in the middle. The windows in the tower are dark, which is not the same as empty.')
    R.meta['box'] = [[T, 0, T], [W - T, TOP - 0.1, W - T]]
    return R
