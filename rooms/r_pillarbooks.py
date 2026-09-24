"""The Book Columns: a low, wide hall held up by nine columns made of nothing but books, shelves
facing out all the way round, each one standing in a shaft of light from a round well above it."""
from lib import *
from kit_d import *


def column(R, cx, cy, H, ra=0.8, rows=5):
    """A hexagonal column of bookcases round a core; ra is the apothem of the core."""
    N = 6
    L = 2 * ra * math.tan(math.pi / N)
    rv = ra / math.cos(math.pi / N)                       # core vertex radius
    R.parts.add(cyl(cx, cy, 0, H, rv, N, side='walnut', caps=False))
    ro = (ra + 0.36) / math.cos(math.pi / N)
    rb = (ra + 0.35) / math.cos(math.pi / N)
    for r in range(rows + 1):       # one solid hexagonal board per row
        h = 0.1 + r * 0.42
        R.parts.add(cyl(cx, cy, h, h + 0.035, rb, N, side='walnut', top='walnut', bottom='walnut', caps=True))
    for k in range(N):
        a = math.pi / 6 + k * math.pi / 3
        e = a - math.pi / 2
        bx, by = cx + ra * math.cos(a) - math.cos(e) * L / 2, cy + ra * math.sin(a) - math.sin(e) * L / 2
        for r in range(rows):
            h0 = r * 0.42 + 0.035
            add_slab(R, bx, by, 0.1, L, a, h0, h0 + 0.42 - 0.035 - 0.03)
        # thin walnut fins at the corners between facets
        va = a + math.pi / 6
        fx, fy = cx + rv * math.cos(va), cy + rv * math.sin(va)
        R.parts.add(box(-0.02, 0, 0, 0.02, 0.4, 0.1 + rows * 0.42 + 0.035, 'walnut', skip=('-z', '+z', '-y')).xform(va - math.pi / 2, fx, fy, 0.1))
    R.parts.add(cyl(cx, cy, 0, 0.1, ro + 0.04, N, side='tile', top='tile', caps=True))          # plinth
    zc = 0.1 + rows * 0.42 + 0.035
    R.parts.add(cyl(cx, cy, zc, zc + 0.08, ro + 0.03, N, side='brass', top='brass', bottom='brass'))
    R.parts.add(cyl(cx, cy, zc + 0.08, H - 0.12, ro - 0.1, N, side='walnut', caps=False))
    R.parts.add(cyl(cx, cy, H - 0.12, H, ro + 0.12, N, side='tile', bottom='tile', caps=True))
    # the light well over it
    R.cut(cyl(cx, cy, H - 0.05, H + 3.4, 1.45, 16, side='plaster', top='plaster', bottom='plaster'))
    R.light(cyl(cx, cy, H + 3.3, H + 3.32, 1.3, 16, side='e_sky', top='e_sky', bottom='e_sky', caps=True))


def make():
    R = Room('pillarbooks', 1, 1, res=1024)
    H = 2.75
    shell(R, H, floor='terrazzo', wall='tile', top='plaster', rect=2.6)
    for x in (4.0, 8.0, 12.0):
        for y in (4.0, 8.0, 12.0):
            column(R, x, y, H)
    # small amber lamps on the walls between the doors, for the night
    for p in (2.0, 14.0):
        for (x, y) in ((p, I0 + 0.08), (p, I1 - 0.08), (I0 + 0.08, p), (I1 - 0.08, p)):
            R.light(cyl(x, y, 1.8, 2.0, 0.07, 8, side='e_amber', top='e_amber', bottom='e_amber'))
    # a dado of dark stone round the walls
    for (x0, y0, x1, y1) in ((I0, I0, I1, I0 + 0.03), (I0, I1 - 0.03, I1, I1), (I0, I0, I0 + 0.03, I1), (I1 - 0.03, I0, I1, I1)):
        R.nocol.add(box(x0, y0, 0, x1, y1, 0.9, 'slate', skip=('-z',)))
    loop(R, [(2.0, 2.0), (6.0, 2.0), (10.0, 2.0), (14.0, 2.0), (14.0, 6.0), (14.0, 10.0), (14.0, 14.0), (10.0, 14.0), (6.0, 14.0), (2.0, 14.0), (2.0, 10.0), (2.0, 6.0)])
    loop(R, [(6.0, 6.0), (10.0, 6.0), (10.0, 10.0), (6.0, 10.0)])
    R.link(R.navpt(6.0, 2.0), R.navpt(6.0, 6.0))
    R.spot('probe', 6.0, 6.0, 1.7)
    R.meta.update(label='The Book Columns', weight=7,
                  blurb='The columns are books, all the way round and all the way up. You try not to think about which ones are holding up the ceiling.')
    return R
