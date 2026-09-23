"""The Spiral: a round tower through every floor. A ramp winds up the middle, one turn per floor,
meeting a ring of bookcases at each level. The core is open; you can jump."""
from lib import *


def make():
    R = Room('tower', 1, 1, res=1024, repeat=True, lo=-0.4)
    R.sockets()
    cx = cy = C / 2
    rw = 7.2                                    # inner radius of the tower wall
    R.cut(cyl(cx, cy, -LH, 2 * LH, rw, 96, side='tile', top='tile', bottom='tile'))
    ri, rm = 2.3, 5.0                           # ramp from ri to rm; landing ring from rm to the wall
    th0 = math.pi / 4                           # where the ramp meets each landing
    R.parts.add(ring(cx, cy, -0.35, 0.0, rm, rw + 0.05, 96, top='floor', bottom='plaster'))
    # a deep fascia under the landing's inner edge, so the ramp arriving from below can't slip under it
    R.parts.add(ring(cx, cy, -1.25, -0.34, rm, rm + 0.2, 96, top='tile', bottom='tile', inner='tile', outer='tile'))
    R.parts.add(helix(cx, cy, ri, rm, 0.0, LH, th0, th0 + 2 * math.pi, 0.35, 128, top='floor', side='tile', bottom='plaster'))
    # parapets: inside edge of the ramp all the way; outside edge except where it meets a landing;
    # inside edge of the landing except at the meeting point
    ph, gap = 0.9, math.radians(28)
    R.parts.add(helix(cx, cy, ri, ri + 0.16, ph, LH, th0, th0 + 2 * math.pi, ph, 128, top='tile', side='tile', bottom='tile'))
    R.parts.add(helix(cx, cy, rm - 0.16, rm, ph + LH * gap / (2 * math.pi), LH, th0 + gap, th0 + 2 * math.pi - gap, ph, 110, top='tile', side='tile', bottom='tile'))
    R.parts.add(ring(cx, cy, 0.0, ph, rm, rm + 0.16, 80, top='tile', bottom='tile', inner='tile', outer='tile', a0=th0 + gap, a1=th0 + 2 * math.pi - gap))
    # brass rail along the ramp's inner parapet
    R.parts.add(helix(cx, cy, ri - 0.03, ri + 0.19, ph + 0.06, LH, th0, th0 + 2 * math.pi, 0.06, 128, top='brass', side='brass', bottom='brass'))
    # light: a glowing ring under each landing, and floating lamps in the core
    R.light(ring(cx, cy, -0.4, -0.37, rw - 0.35, rw - 0.12, 96, top='e_panel', bottom='e_panel', inner='e_panel', outer='e_panel'))
    for k in range(6):
        a = k * math.pi / 3
        R.light(sphere(cx + math.cos(a) * 1.25, cy + math.sin(a) * 1.25, 5.6 + 0.35 * math.sin(3 * a), 0.16, 16, 8, 'e_lamp'))
    # bookcases round the wall in straight runs between the doors
    for q in range(4):
        for off in (24, 45, 66):
            a = math.radians(q * 90 + off)
            half = 1.2
            bx, by = cx + math.cos(a) * (rw - 0.06), cy + math.sin(a) * (rw - 0.06)
            fa = a + math.pi
            ux, uy = math.sin(fa), -math.cos(fa)
            R.shelf(bx - ux * half, by - uy * half, 0, 2 * half, fa, rows=7, frame='wood', back=True)
    pts = [R.navpt(cx + math.cos(k * math.pi / 4 + math.pi / 8) * 6.1, cy + math.sin(k * math.pi / 4 + math.pi / 8) * 6.1) for k in range(8)]
    R.link(*pts, pts[0])
    R.spot('ramp', cx + math.cos(th0) * 3.6, cy + math.sin(th0) * 3.6, 0.05, th0 + math.pi / 2)
    R.spot('probe', cx, cy, 3.5)
    R.meta['label'] = 'The Spiral'
    R.meta['core'] = [cx, cy, ri]
    R.meta['ramp'] = [cx, cy, ri, rm, th0, LH]
    R.meta['box'] = [[C / 2 - rw, 0, C / 2 - rw], [C / 2 + rw, LH, C / 2 + rw]]
    return R
