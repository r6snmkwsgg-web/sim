"""The Stair Plaza: flights of stairs cross over and under each other between platforms at three
heights: a low walkway north to south, a high bridge east to west over it, landings, turns, and
long straight flights from the floor. Every way up is also a way down. Probably."""
from lib import *
from kit_f import *


def make():
    R = Room('escher', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    W = R.W
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, W - T + 0.02, TOP - 0.1, 'tile', bottom='terrazzo', top='plaster'))
    rr, ra, rs, ro = rot180(W)
    LO, HI = 2.5, 5.0
    # half the plan; the other half is the same turned through 180 degrees
    decks = [  # (rect, z, opens)
        ((15, 6.5, 17, 16.0), LO, {'S': [(15, 17)], 'W': [(9.4, 11.4)], 'N': [(15, 17)]}),          # low walkway, south half
        ((11, 4.5, 17, 6.5), LO, {'W': [(4.5, 6.5)], 'N': [(15, 17)], 'S': [(15, 17)]}),               # its south platform
        ((15, T, 17, 4.5), LO, {'N': [(15, 17)], 'S': [(15, 17)]}),                                    # ...on to a door in the wall
        ((6.5, 15, 16.0, 17), HI, {'W': [(15, 17)], 'N': [(11, 13)], 'E': [(15, 17)]}),                # high bridge, west half
        ((4.5, 15, 6.5, 17), HI, {'S': [(4.5, 6.5)], 'E': [(15, 17)], 'W': [(15, 17)]}),               # its west platform
        ((T, 15, 4.5, 17), HI, {'E': [(15, 17)], 'W': [(15, 17)]}),                                    # ...on to a door in the wall
        ((4.5, 9.4, 6.5, 11.4), LO, {'N': [(4.5, 6.5)], 'E': [(9.4, 11.4)]}),                          # a landing
        ((6.5, 9.4, 15, 11.4), LO, {'W': [(9.4, 11.4)], 'E': [(9.4, 11.4)]}),                          # low bridge to the walkway
    ]
    flights = [  # (rect, axis, z0, z1)
        ((7.4, 4.5, 11.0, 6.5), '+x', 0.0, LO),
        ((4.5, 11.4, 6.5, 15.0), '+y', LO, HI),
        ((19, 7.8, 21, 15.0), '+y', 0.0, HI),
    ]
    allrects = []
    for half in range(2):
        for (rect, z, opens) in decks:
            if half: rect, opens = rr(rect), ro(opens)
            deck(R, *rect, z, th=0.3)
            allrects.append((rect, z))
            # the seam between the two halves of the long decks is open
            rect_rails(R, *rect, z, opens=opens, sides=''.join(s for s in 'SNWE' if not _seam(rect, s, W)))
        for (rect, axis, z0, z1) in flights:
            if half: rect, axis = rr(rect), ra(axis)
            flight_rect(R, rect, axis, z0, z1)
            allrects.append((rect, -1))
    # the doors the decks lead to, which do not open
    for half in range(2):
        for (x, y, z, ax) in ((16, 0, LO, 'y'), (0, 16, HI, 'x')):
            if half: x, y = W - x, W - y
            pr = [(-0.75, 0), (0.75, 0), (0.75, 2.3), (-0.75, 2.3)]
            if ax == 'y':
                y0, y1 = (0.15, T + 0.02) if y == 0 else (W - T - 0.02, W - 0.15)
                R.cut(prism([(p + x, q + z) for p, q in pr], 'y', y0, y1, ['tile'] * 4))
                yd = 0.15 if y == 0 else W - 0.2
                R.parts.add(box(x - 0.75, yd, z, x + 0.75, yd + 0.05, z + 2.3, 'walnut'))
                R.parts.add(cyl(x + 0.5, yd + (0.08 if y == 0 else -0.03), z + 1.0, z + 1.1, 0.04, 8, side='brass', top='brass', bottom='brass'))
                R.light(box(x - 0.3, (T + 0.01) if y == 0 else (W - T - 0.05), z + 2.55, x + 0.3, (T + 0.05) if y == 0 else (W - T - 0.01), z + 2.8, 'e_exit'))
            else:
                x0, x1 = (0.15, T + 0.02) if x == 0 else (W - T - 0.02, W - 0.15)
                R.cut(prism([(p + y, q + z) for p, q in pr], 'x', x0, x1, ['tile'] * 4))
                xd = 0.15 if x == 0 else W - 0.2
                R.parts.add(box(xd, y - 0.75, z, xd + 0.05, y + 0.75, z + 2.3, 'walnut'))
                R.light(box((T + 0.01) if x == 0 else (W - T - 0.05), y - 0.3, z + 2.32, (T + 0.05) if x == 0 else (W - T - 0.01), y + 0.3, z + 2.46, 'e_exit'))
    # piers under the decks, where nothing walks or climbs beneath
    def clear_below(x, y, z):
        for (r, zz) in allrects:
            if r[0] - 0.35 < x < r[2] + 0.35 and r[1] - 0.35 < y < r[3] + 0.35 and (zz < 0 or zz < z - 0.1):
                return False
        return True
    for (rect, z) in list(allrects):
        if z < 0: continue
        x0, y0, x1, y1 = rect
        nx = max(1, int(math.ceil((x1 - x0 - 0.6) / 4.2))); ny = max(1, int(math.ceil((y1 - y0 - 0.6) / 4.2)))
        for i in range(nx + 1):
            for j in range(ny + 1):
                if 0 < i < nx and 0 < j < ny: continue
                x = x0 + 0.3 + (x1 - x0 - 0.6) * i / nx
                y = y0 + 0.3 + (y1 - y0 - 0.6) * j / ny
                if clear_below(x, y, z):
                    pier(R, x, y, 0, z - 0.3, 0.18)
    # ceiling lamps over the knot, low lamps on the floor
    for (x, y) in ((10, 10), (22, 22), (10, 22), (22, 10), (16, 16), (5.5, 13), (26.5, 19), (13, 5.5), (19, 26.5)):
        lamp(R, x, y, 6.9 if (x, y) != (16, 16) else 6.6, 0.28, chain=TOP - 0.1)
    for (x, y) in ((3.0, 3.0), (W - 3.0, W - 3.0), (W - 3.0, 3.0), (3.0, W - 3.0)):
        R.parts.add(cyl(x, y, 0, 1.4, 0.03, 6, side='brass', caps=False))
        R.parts.add(cyl(x, y, 0, 0.05, 0.22, 12, side='brass', top='brass'))
        R.light(cyl(x, y, 1.4, 1.65, 0.2, 12, side='e_amber', top='e_amber', bottom='e_amber'))
    for (x, y) in ((16, 3.0), (16, W - 3.0), (3.0, 16), (W - 3.0, 16)):
        R.light(sphere(x, y, 0.35, 0.18, 10, 5, 'e_candle'))
        R.parts.add(cyl(x, y, 0, 0.2, 0.25, 12, side='tile', top='tile'))
    # books: along the walls, and two short stacks in the open corners
    wall_shelves(R, ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)), rows=9, frame='walnut')
    for (x0, y0, x1, y1) in ((23.0, 4.2, 23.0, 11.0), (26.6, 4.2, 26.6, 11.0)):
        stack2_ax(R, x0, y0, x1, y1, 0, 6, frame='walnut')
        r = rr((x0, y0, x1, y1))
        stack2_ax(R, r[0], r[1], r[2], r[3], 0, 6, frame='walnut')
    # walkers on the floor
    loop(R, ((2.2, 2.2), (8, 2.2), (16, 2.2), (24, 2.2), (W - 2.2, 2.2), (W - 2.2, 8), (W - 2.2, 16), (W - 2.2, 24), (W - 2.2, W - 2.2),
             (24, W - 2.2), (16, W - 2.2), (8, W - 2.2), (2.2, W - 2.2), (2.2, 24), (2.2, 16), (2.2, 8)))
    loop(R, ((16, 7.5), (16, 24.5)), z=LO, close=False)
    loop(R, ((7.5, 16), (24.5, 16)), z=HI, close=False)
    R.spot('probe', 10, 13, 1.7)
    R.meta.update(label='The Stair Plaza', weight=4,
                  blurb='Stairs go up to bridges that go over stairs that go down to landings under bridges. You are fairly sure you have been on this one before.')
    R.meta['box'] = [[T, 0, T], [W - T, TOP - 0.1, W - T]]
    return R


def _seam(rect, s, W):
    """True if this side of the rectangle is the centre seam of a deck split in two halves."""
    x0, y0, x1, y1 = rect
    c = W / 2
    return (s == 'N' and abs(y1 - c) < 1e-6) or (s == 'S' and abs(y0 - c) < 1e-6) or (s == 'E' and abs(x1 - c) < 1e-6) or (s == 'W' and abs(x0 - c) < 1e-6)
