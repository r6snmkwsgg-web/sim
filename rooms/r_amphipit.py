"""The Book Pit: a round amphitheatre dug into the floor, its lower terraces walled with books,
under a shallow dome and one lamp. There is a chair at the bottom, facing nothing."""
from lib import *
from kit_c import *


def ring_books(R, cx, cy, r, z, h, n, d=0.3, frame='walnut'):
    """Cut a polygonal riser whose flat faces sit d behind radius r, and stand a bookcase against each face."""
    Rc = (r + d) / math.cos(math.pi / n)
    R.cut(cyl(cx, cy, z, z + h + 0.01, Rc, n, side='tile', bottom='floor', top='tile'))
    L = 2 * (r + d) * math.tan(math.pi / n) - 0.03
    for j in range(n):
        a = 2 * math.pi * (j + 0.5) / n
        ca, sa = math.cos(a), math.sin(a)
        bx, by = cx + (r + d) * ca, cy + (r + d) * sa
        tx, ty = -sa, ca
        book_riser(R, bx - tx * L / 2, by - ty * L / 2, L, z, h - 0.02, a + math.pi, frame=frame, depth=d)


def make():
    R = Room('amphipit', 1, 1, res=1024)
    R.sockets(floor='floor', wall='tile')
    H = 5.0
    shell(R, H, floor='floor', ceil='plaster')
    cx = cy = 8.0
    # the dome
    R.cut(sphere(cx, cy, 1.1, 6.4, 40, 12, 'plaster', lower=False))
    # terraces: three steps of 0.3, then two book risers of 0.45
    for (r, z) in ((5.65, -0.3), (5.2, -0.6), (4.75, -0.9)):
        R.cut(cyl(cx, cy, z, 0.3, r, 44, side='tile', bottom='floor', top='tile'))
    ring_books(R, cx, cy, 4.0, -1.35, 0.45, 24)
    ring_books(R, cx, cy, 2.9, -1.8, 0.45, 18)
    # the bottom: a round carpet, a chair, some books left on the floor
    R.parts.add(cyl(cx, cy, -1.8, -1.788, 2.2, 40, side='oxblood', top='oxblood', bottom='oxblood'))
    R.parts.add(cyl(cx, cy, -1.788, -1.784, 2.0, 40, side='carpet', top='carpet', bottom='carpet'))
    chair(R, cx, cy - 0.5, math.pi / 2 + 0.25, z=-1.8)
    book_pile(R, cx + 0.6, cy - 0.6, -1.784, 7, seed=11)
    book_pile(R, cx - 0.9, cy + 0.3, -1.784, 3, seed=5)
    open_book(R, cx + 0.2, cy + 0.9, -1.784, 0.7)
    # the lamp
    lz = 1.3
    R.light(sphere(cx, cy, lz, 0.32, 20, 10, 'e_lamp'))
    R.parts.add(ring(cx, cy, lz - 0.03, lz + 0.03, 0.34, 0.4, 32, top='brass', bottom='brass', inner='brass', outer='brass'))
    R.parts.add(cyl(cx, cy, lz + 0.28, lz + 0.42, 0.14, 16, side='brass', top='brass', bottom='brass'))
    R.parts.add(cyl(cx, cy, lz + 0.42, 7.55, 0.015, 6, side='iron', caps=False))
    # books round the room: tall cases up to the dome's foot
    wall_shelves(R, rows=10, frame='walnut')
    # little night lamps over the doors, and in the corners
    for (x, y) in ((8, T + 0.1), (8, C - T - 0.1), (T + 0.1, 8), (C - T - 0.1, 8)):
        R.light(box(x - 0.12, y - 0.1, 4.3, x + 0.12, y + 0.1, 4.42, 'e_amber'))
    for (x, y) in ((1.3, 1.3), (C - 1.3, 1.3), (C - 1.3, C - 1.3), (1.3, C - 1.3)):
        candle_stand(R, x, y, 0, h=1.1)
    # walkers
    ring_ = std_nav(R, 1.4)
    mid = navloop(R, [(cx + 3.6 * math.cos(k * math.pi / 3), cy + 3.6 * math.sin(k * math.pi / 3)) for k in range(6)], z=-1.35)
    bot = navloop(R, [(cx + 2.2 * math.cos(k * math.pi / 2 + 0.4), cy + 2.2 * math.sin(k * math.pi / 2 + 0.4)) for k in range(4)], z=-1.8)
    R.link(ring_[1], R.navpt(cx, 2.6, -0.3), R.navpt(cx, cy - 3.6, -1.35))
    R.spot('probe', cx, cy, -0.3)
    R.meta.update(label='The Book Pit', weight=6,
                  blurb='The floor goes down in rings, like a theatre, and the lowest rings are made of books. Someone has left a chair at the bottom to watch them.')
    R.meta['box'] = [[T, -1.8, T], [C - T, 7.6, C - T]]
    return R
