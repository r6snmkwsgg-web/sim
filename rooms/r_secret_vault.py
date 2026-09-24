"""The Vault: behind a false bookcase in the south doorway, a stone passage ends in a round hole
through a metre of wall. Its great bronze door stands open. Inside, a domed round room of gilt
shelves, and one book on a pedestal under the light."""
from lib import *
from kit_d import *
from r_secret_reading import false_case

VR, VZ = 1.5, 1.0          # the round opening: radius, height of its centre


def disc_profile(cx, cz, r, n=28, flat=None):
    if flat is None or cz - r >= flat:
        return [(cx + r * math.cos(2 * math.pi * k / n), cz + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    t0 = math.asin((flat - cz) / r)            # where the circle meets the flat bottom (negative angle)
    t1 = math.pi - t0
    pts = [(cx + r * math.cos(t0 + (t1 - t0) * k / n), cz + r * math.sin(t0 + (t1 - t0) * k / n)) for k in range(n + 1)]
    return pts


def make():
    R = Room('secret_vault', 1, 1, res=1024)
    shell(R, None, floor='floor', wall='tile', seal=('N', 'E', 'W'))
    R.meta['secret'] = True
    false_case(R)
    wy0, wy1 = 5.0, 6.0                        # the vault wall
    # the passage: stone, a little wider than the door, a flat ceiling
    R.cut(box(5.4, T - 0.02, 0, 10.6, wy0 + 0.02, 4.2, 'tile', bottom='terrazzo', top='plaster'))
    # the round opening through the wall (flat-bottomed)
    R.cut(prism(disc_profile(M, VZ, VR, 28, flat=0.0), 'y', wy0 - 0.02, wy1 + 0.6, 'bronze', cap='bronze'))
    # the door: a thick bronze disc, hinged on the west side of the opening, swung open against the passage wall
    d = Geo()
    d.add(prism(disc_profile(VR + 0.05, VZ, VR + 0.12, 28, flat=0.02), 'y', -0.55, 0.0, 'bronze', cap='bronze'))
    d.add(prism(disc_profile(VR + 0.05, VZ, 0.5, 16), 'y', -0.62, -0.55, 'brass', cap='brass'))          # the boss
    for a in (0, math.pi / 3, 2 * math.pi / 3):
        bar = [(VR + 0.05 + math.cos(a) * 0.9 - math.sin(a) * 0.04, VZ + math.sin(a) * 0.9 + math.cos(a) * 0.04),
               (VR + 0.05 - math.cos(a) * 0.9 - math.sin(a) * 0.04, VZ - math.sin(a) * 0.9 + math.cos(a) * 0.04),
               (VR + 0.05 - math.cos(a) * 0.9 + math.sin(a) * 0.04, VZ - math.sin(a) * 0.9 - math.cos(a) * 0.04),
               (VR + 0.05 + math.cos(a) * 0.9 + math.sin(a) * 0.04, VZ + math.sin(a) * 0.9 - math.cos(a) * 0.04)]
        d.add(prism(bar, 'y', -0.66, -0.55, 'brass', cap='brass'))
    hx, hy = M - VR - 0.35, wy0              # hinge
    R.parts.add(d.xform(-math.pi / 2 - 0.1, hx, hy - 0.05))
    R.parts.add(box(hx - 0.12, hy - 0.2, 0, hx + 0.05, hy, 2.6, 'bronze', skip=('-z',)))                    # hinge post
    # the vault: a round room with a dome
    vc, vr = (M, wy1 + 4.2), 4.2
    R.cut(cyl(vc[0], vc[1], 0, 3.0, vr, 40, side='gilt', top='plaster', bottom='terrazzo'))
    R.cut(sphere(vc[0], vc[1], 2.9, vr, 40, 10, 'plaster', lower=False))
    R.meta['box'] = [[5.4, 0, T], [10.6, 7.1, vc[1] + vr]]
    # gilt shelves all round, except at the way in
    N = 14
    ra = vr - 0.02
    L = 2 * ra * math.tan(math.pi / N) - 0.06
    for k in range(N):
        a = -math.pi / 2 + (k + 0.5) * 2 * math.pi / N
        if abs(math.remainder(a + math.pi / 2, 2 * math.pi)) < 0.5: continue
        shelf_at(R, vc[0] + ra * math.cos(a), vc[1] + ra * math.sin(a), 0, L, a + math.pi, 6, frame='gilt', row_h=0.44)
    # the pedestal, the book, the light from the top of the dome
    R.parts.add(cyl(vc[0], vc[1], 0, 0.15, 0.6, 20, side='terrazzo', top='terrazzo', caps=True))
    R.parts.add(cyl(vc[0], vc[1], 0.15, 1.0, 0.22, 16, side='bronze', caps=False))
    R.parts.add(cyl(vc[0], vc[1], 1.0, 1.08, 0.36, 16, side='gilt', top='velvet', bottom='gilt'))
    book(R, vc[0], vc[1], 1.08, 0.2, 'oxblood', open_=True)
    R.light(cyl(vc[0], vc[1], 2.9 + vr - 0.12, 2.9 + vr - 0.1, 0.7, 20, side='e_lamp', top='e_lamp', bottom='e_lamp'))
    for k in range(6):
        a = k * math.pi / 3 + 0.3
        R.light(cyl(vc[0] + 3.0 * math.cos(a), vc[1] + 3.0 * math.sin(a), 2.95, 3.0, 0.12, 8, side='e_candle', top='e_candle', bottom='e_candle'))
    # the passage: two lamps and plain stone
    for y in (2.5, 4.2):
        pendant(R, M, y, 3.2, r=0.14, top=4.2)
    loop(R, [(M, 1.5), (M, wy0 - 0.8), (M, wy1 + 1.0), (M + 2.2, vc[1]), (M, vc[1] + 2.2), (M - 2.2, vc[1]), (M, wy1 + 1.0)], close=False)
    R.spot('probe', M, vc[1] - 2.0, 1.6)
    R.meta.update(label='The Vault', weight=2,
                  blurb='Somebody built a vault in here, with a door a foot thick, and then left it standing open. Whatever was worth guarding, it is still here. It is a book.')
    return R
