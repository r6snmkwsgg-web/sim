"""The Coral Archive: the stacks have gone under, some time ago, and come up again as reef. The
bookcases are pink and white coral now, branching over their crowns and crusting their ends, the
books still shelved inside them. The light comes down blue from far above. In the middle of the
room the largest coral of all has grown into a mound, and there is room inside it for one reader."""
from lib import *
from kit_h4 import *

W = 32.0
H = 7.4
CC = (16.0, 16.0)          # the great coral
STACK_Y = (4.0, 12.0, 20.0, 28.0)
SIDES = ((2.6, 11.4), (20.6, 29.4))
CORALS = ('coral', 'coral', 'coralw')


def make():
    R = Room('coralarchive', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    rnd = random.Random(33)
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, W - T + 0.02, H, 'tile', bottom='terrazzo', top='plaster'))
    # the ceiling: deep beams, and between them the light from the surface, far above
    for k in range(1, 8):
        p = k * 4.0
        R.nocol.add(box(T, p - 0.15, H - 0.7, W - T, p + 0.15, H, 'slate'))
        R.nocol.add(box(p - 0.15, T, H - 0.7, p + 0.15, W - T, H, 'slate'))
    for i in range(8):
        for j in range(8):
            if (i + j) % 2: continue
            x, y = 2.0 + 4.0 * i, 2.0 + 4.0 * j
            R.light(box(x - 1.1, y - 1.1, H - 0.04, x + 1.1, y + 1.1, H - 0.02, 'e_deep'))

    stacks(R, rnd)
    walls(R, rnd)
    great_coral(R, rnd)
    reading(R, rnd)

    navloop(R, [(13.0, 1.8), (19.0, 1.8), (19.2, 11.2), (21.5, 16.0), (19.2, 20.8), (19.0, 30.2), (13.0, 30.2), (12.8, 20.8), (10.5, 16.0), (12.8, 11.2)])
    navloop(R, [(1.6, 8.0), (12.4, 8.0)], close=False)
    navloop(R, [(19.6, 24.0), (30.4, 24.0)], close=False)
    navloop(R, [(1.6, 16.0), (10.5, 16.0)], close=False)
    R.spot('probe', 16.0, 8.0, 3.5)
    R.meta.update(label='The Coral Archive', weight=4,
                  blurb='The sea came in and went out again and took nothing, only left the shelves a little more alive than they were. Mind the corals; they are reading.')
    R.meta['box'] = [[T, 0, T], [W - T, H, W - T]]
    fx(R, 'dust', [T, T, 0.2, W - T, W - T, H - 0.3])
    fx(R, 'fog', [T, T, 0.0, W - T, W - T, H], density=0.04)
    secret(R, CC[0], CC[1], 0.0, 'Inside the Great Coral',
           'You found the way in behind the white fans. Inside the coral it is blue and hushed, like the bottom of a very old sea, and somebody has been reading down here.', r=1.6)
    return tidy(R)


def coral_tree(R, x, y, z, rnd, size=1.0, m=None, up=(0, 0, 1)):
    g = Geo()
    m = m or rnd.choice(CORALS)
    branches(g, (x, y, z - 0.05), up, 1.15 * size, 0.13 * size, 2, rnd, m, 4, 2, 0.95, 0.5, 0.85, 0.68, 0.3)
    R.nocol.add(g)


def crust(R, x, y, z, rnd, n=5, rad=0.6, m=None):
    for k in range(n):
        R.nocol.add(blob(x + rnd.uniform(-rad, rad), y + rnd.uniform(-rad, rad), z + rnd.uniform(-rad, rad),
                         rnd.uniform(0.15, 0.4), rnd.uniform(0.15, 0.4), rnd.uniform(0.12, 0.35), m or rnd.choice(CORALS), 6, 3, rnd.uniform(0, 3)))


def stacks(R, rnd):
    rows = 11
    top = rows * 0.42 + 0.12
    for (xa, xb) in SIDES:
        for y in STACK_Y:
            sh(R, '+y', y + 0.01, xa, xb, rows=rows, frame='coral')
            sh(R, '-y', y - 0.01, xa, xb, rows=rows, frame='coral')
            # coral branching over the crown, crusting the ends
            n = 3
            for k in range(n):
                x = xa + (k + 0.5) * (xb - xa) / n + rnd.uniform(-0.6, 0.6)
                coral_tree(R, x, y + rnd.uniform(-0.2, 0.2), top, rnd, rnd.uniform(1.2, 1.7))
            for xe in (xa, xb):
                crust(R, xe, y, 1.0, rnd, 3, 0.5)
                crust(R, xe, y, 3.2, rnd, 3, 0.5)
                coral_tree(R, xe + (0.1 if xe == xb else -0.1), y, 0.0, rnd, 1.1, 'coralw', (0.4 if xe == xb else -0.4, 0.0, 1.0))
            # books pushed out of true by growth
            for k in range(3):
                x = rnd.uniform(xa + 0.5, xb - 0.5)
                R.nocol.add(blob(x, y + rnd.choice((-0.37, 0.37)), rnd.uniform(0.6, 4.2), rnd.uniform(0.2, 0.5), 0.12, rnd.uniform(0.2, 0.5), rnd.choice(CORALS), 8, 4))


def walls(R, rnd):
    for (a, b) in ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)):
        sh(R, '+y', T, a, b, rows=13, frame='coral')
        sh(R, '-y', W - T, a, b, rows=13, frame='coral')
        sh(R, '+x', T, a, b, rows=13, frame='coral')
        sh(R, '-x', W - T, a, b, rows=13, frame='coral')
        for (x, y) in ((a, T + 0.3), (b, T + 0.3), (a, W - T - 0.3), (b, W - T - 0.3), (T + 0.3, a), (T + 0.3, b), (W - T - 0.3, a), (W - T - 0.3, b)):
            crust(R, x, y, rnd.uniform(1.0, 4.5), rnd, 2, 0.4)
    for k in range(14):
        side = rnd.randrange(4); p = rnd.uniform(1.0, W - 1.0)
        if 6.0 < p < 10.0 or 22.0 < p < 26.0: continue
        x, y, d = ((p, T + 0.3, (0, 0.3, 1)), (p, W - T - 0.3, (0, -0.3, 1)), (T + 0.3, p, (0.3, 0, 1)), (W - T - 0.3, p, (-0.3, 0, 1)))[side]
        coral_tree(R, x, y, 13 * 0.42 + 0.12, rnd, rnd.uniform(0.8, 1.3))


def great_coral(R, rnd):
    cx, cy = CC
    gap = math.pi / 2          # the way in faces north, hidden behind white fans
    for (n, rr, z, r0, r1) in ((12, 3.25, 0.9, 1.35, 1.55), (9, 2.55, 2.55, 1.1, 1.3), (6, 1.55, 3.75, 0.9, 1.1)):
        for k in range(n):
            a = 2 * math.pi * k / n + (0.0 if n != 9 else 0.35)
            da = math.atan2(math.sin(a - gap), math.cos(a - gap))
            zz = z
            if n == 12 and abs(da) < 0.2: continue
            if n == 12 and abs(da) < 0.6: a += 0.2 if da > 0 else -0.2
            if n == 9 and abs(da) < 0.45: zz = z + 0.55
            r = rnd.uniform(r0, r1)
            R.parts.add(blob(cx + rr * math.cos(a), cy + rr * math.sin(a), zz, r, r * rnd.uniform(0.85, 1.0), r * rnd.uniform(0.8, 0.95),
                             rnd.choice(('coral', 'coral', 'coralw')), 10, 6, rnd.uniform(0, 3)))
    R.parts.add(blob(cx, cy, 4.35, 1.1, 1.1, 0.8, 'coral', 12, 6))
    # branching fans and antlers over the top
    for k in range(9):
        a = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.3, 2.2)
        coral_tree(R, cx + d * math.cos(a), cy + d * math.sin(a), 4.2 - d * 0.5, rnd, rnd.uniform(1.4, 2.0), rnd.choice(('coralw', 'coral')),
                   (math.cos(a) * 0.3, math.sin(a) * 0.3, 1.0))
    # the white fans that hide the way in
    gx, gy = cx + 3.25 * math.cos(gap), cy + 3.25 * math.sin(gap)
    for k in range(5):
        coral_tree(R, gx + rnd.uniform(-1.3, 1.3), gy + rnd.uniform(0.6, 1.4), 0.0, rnd, rnd.uniform(1.2, 1.7), 'coralw', (rnd.uniform(-0.3, 0.3), 0.2, 1.0))
    # inside: blue glow, a low stool, the reader's things
    R.light(sphere(cx, cy, 3.2, 0.14, 8, 4, 'e_glow'))
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3
        R.light(sphere(cx + 1.55 * math.cos(a), cy + 1.55 * math.sin(a), 0.5 + 0.3 * (k % 2), 0.05, 6, 3, 'e_glow'))
    R.parts.add(cyl(cx - 0.4, cy - 0.3, 0.0, 0.42, 0.22, 10, side='coralw', top='leather'))
    R.spot('sit', cx - 0.4, cy - 0.3, 0.42, math.pi / 2)
    open_book(R, cx + 0.3, cy - 0.7, 0.0, 0.5)
    book_pile(R, cx + 0.8, cy + 0.2, 0.0, 6, rnd)
    candle(R, cx - 0.9, cy + 0.5, 0.0, h=0.2)
    R.spot('plaque', cx + 0.2, cy + 0.5, 0.0, -math.pi / 2, text='Coral is patient. It had all the time in the world, and so, it turns out, do you.')


def reading(R, rnd):
    for (ya, yb) in ((2.6, 10.6), (21.4, 29.4)):
        for x in (13.9, 18.1):
            table(R, x - 0.55, ya, x + 0.55, yb, top='leather')
            k = 0
            y = ya + 0.8
            while y < yb - 0.5:
                desk_lamp(R, x, y, 0.76) if k % 2 == 0 else None
                chair(R, x - 0.95, y, 0.0); chair(R, x + 0.95, y, math.pi)
                if rnd.random() < 0.3: open_book(R, x + rnd.uniform(-0.2, 0.2), y + 0.6, 0.76, rnd.uniform(-0.4, 0.4))
                y += 1.3; k += 1
        crust(R, 16.0, ya + 1.0, 0.1, rnd, 3, 0.4, 'coralw')
    # night lights: little glowing polyps along the stacks' feet
    for (xa, xb) in SIDES:
        for y in STACK_Y:
            for x in (xa + 0.8, xb - 0.8):
                R.light(sphere(x, y + 0.45, 0.12, 0.06, 6, 3, 'e_glow'))
                R.light(sphere(x, y - 0.45, 0.12, 0.06, 6, 3, 'e_glow'))
