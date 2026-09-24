"""The Portrait Gallery: oxblood walls hung frame above frame to the cornice, a salon hang of heavy
gilt frames, every one of them empty and dark. Except one, which shows the sky."""
import random
from lib import *
from kit_b import *


def frame(R, side, u0, u1, z0, z1, panel='slate', b=0.1, light=False):
    """A gilt frame on the wall `side`, spanning u0..u1 along it and z0..z1."""
    g = Geo()
    L = u1 - u0
    g.add(box(0, 0, z0, L, 0.07, z1, 'gilt', skip=('-y',)))
    pm = panel if not panel.startswith('e_') else 'black'
    g.add(box(b, 0.07, z0 + b, L - b, 0.08, z1 - b, pm, skip=('-y', '-x', '+x', '-z', '+z')))
    ang = {'S': 0.0, 'N': math.pi, 'W': -math.pi / 2, 'E': math.pi / 2}[side]
    ox, oy = {'S': (u0, T), 'N': (C - u0, C - T), 'W': (T, C - u0), 'E': (C - T, u0)}[side]
    R.nocol.add(g.xform(ang, ox, oy))
    if panel.startswith('e_'):
        e = box(b, 0.075, z0 + b, L - b, 0.085, z1 - b, panel)
        R.light(e.xform(ang, ox, oy))
    if light:   # a brass picture light over it
        p = Geo()
        p.add(box(L / 2 - 0.02, 0.0, z1 + 0.05, L / 2 + 0.02, 0.25, z1 + 0.09, 'brass'))
        p.add(box(L / 2 - 0.3, 0.2, z1 + 0.02, L / 2 + 0.3, 0.28, z1 + 0.09, 'brass'))
        R.nocol.add(p.xform(ang, ox, oy))
        R.light(box(L / 2 - 0.27, 0.21, z1 + 0.0, L / 2 + 0.27, 0.27, z1 + 0.02, 'e_lamp').xform(ang, ox, oy))


def make():
    R = Room('portrait', 1, 1, res=1024)
    rnd = random.Random(11)
    H = TOP - 0.1
    shell(R, H, wall='oxblood', floor='floor', ceil='plaster')
    # a laylight in a deep coffer
    R.cut(box(4.0, 4.0, H - 0.05, C - 4.0, C - 4.0, H + 0.05, 'plaster'))
    R.light(box(4.2, 4.2, H + 0.0, C - 4.2, C - 4.2, H + 0.03, 'e_panel'))
    # a dado of low bookcases, all round
    wall_shelves(R, rows=2, frame='walnut', depth=0.3)
    # the salon hang
    rows = ((1.3, 2.9), (3.1, 4.5), (4.7, 5.8), (6.0, 6.9))
    sky_done = False
    for side in 'SNWE':
        for ri, (za, zb) in enumerate(rows):
            u = 0.55
            while u < C - 0.8:
                w = rnd.choice((0.7, 0.9, 1.1, 1.3, 1.6)) if ri < 2 else rnd.choice((0.6, 0.8, 1.0, 1.2))
                if u + w > C - 0.55: w = C - 0.55 - u
                if w < 0.45: break
                if ri < 2 and u < 9.9 and u + w > 6.1:   # the doorway
                    u = 9.9; continue
                h0 = zb - za
                hh = h0 * rnd.uniform(0.72, 1.0)
                z0 = za + (h0 - hh) * rnd.uniform(0.2, 0.8)
                panel = rnd.choice(('slate', 'black', 'slate', 'blackboard'))
                if side == 'N' and ri == 0 and not sky_done and u > 10.0:
                    panel = 'e_skydome'; sky_done = True; w = 1.6; hh = h0; z0 = za
                frame(R, side, u, u + w, z0, z0 + hh, panel, b=0.08 + 0.04 * (w > 1.0), light=(ri == 0 and rnd.random() < 0.6))
                u += w + rnd.uniform(0.18, 0.32)
    # ottomans down the middle
    for (x0, y0, x1, y1) in ((6.9, 4.2, 9.1, 5.0), (6.9, 11.0, 9.1, 11.8), (4.2, 6.9, 5.0, 9.1), (11.0, 6.9, 11.8, 9.1)):
        R.parts.add(box(x0, y0, 0, x1, y1, 0.46, 'velvet', skip=('-z',)))
        R.parts.add(box(x0 + 0.05, y0 + 0.05, 0, x1 - 0.05, y1 - 0.05, 0.08, 'walnut', skip=('-z',)))
    for (x, y, f) in ((7.5, 4.6, -math.pi / 2), (8.5, 4.6, -math.pi / 2), (7.5, 11.4, math.pi / 2), (8.5, 11.4, math.pi / 2),
                      (4.6, 7.5, math.pi), (4.6, 8.5, math.pi), (11.4, 7.5, 0.0), (11.4, 8.5, 0.0)):
        R.spot('sit', x, y, 0.46, f)
    # a brass rail keeping you a pace from the walls, on posts
    loop(R, [(2.0, 2.0), (8, 2.0), (C - 2.0, 2.0), (C - 2.0, 8), (C - 2.0, C - 2.0), (8, C - 2.0), (2.0, C - 2.0), (2.0, 8)])
    R.spot('probe', 8, 8, 1.8)
    R.meta.update(label='The Portrait Gallery', weight=5,
                  blurb='Hundreds of frames, and nobody in any of them. One is a window, or a painting of the sky good enough to pass for one.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return R
