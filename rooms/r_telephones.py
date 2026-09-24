"""The Telephone Room: oak phone booths in rows down both long walls, each with its directory and its
little lamp, and across the south wall a switchboard two storeys high, blinking with calls nobody takes."""
from lib import *
from kit_b import *


def booth(R, x, y, face, n, off_hook=False, red=False):
    """A booth 1 m square inside with an open front; (x, y) is the middle of its back wall, face = into the room."""
    g, e, nc = Geo(), Geo(), Geo()
    W2, D, Hb = 0.55, 1.1, 2.45
    g.add(box(0, -W2, 0, D, -W2 + 0.07, Hb, 'oak', skip=('-z',)))                 # side walls
    g.add(box(0, W2 - 0.07, 0, D, W2, Hb, 'oak', skip=('-z',)))
    g.add(box(0, -W2, Hb, D + 0.05, W2, Hb + 0.12, 'walnut'))                        # roof and cornice
    g.add(box(D - 0.02, -W2, Hb - 0.28, D + 0.05, W2, Hb, 'walnut', skip=('+z',)))   # lintel
    nc.add(box(0.0, -0.13, 1.25, 0.08, 0.13, 1.6, 'black', skip=('-x',)))            # the telephone
    nc.add(box(0.08, -0.03, 1.32, 0.13, 0.03, 1.5, 'black', skip=('-x',)))
    if off_hook:
        nc.add(box(0.3, 0.05, 0.55, 0.34, 0.09, 1.3, 'black'))                      # the cord, the receiver hanging
        nc.add(box(0.26, 0.02, 0.4, 0.38, 0.12, 0.6, 'black'))
    else:
        nc.add(box(0.13, -0.16, 1.5, 0.2, 0.16, 1.56, 'black'))                      # the receiver on its hook
    nc.add(box(D - 0.03, -0.12, Hb - 0.2, D + 0.06, 0.12, Hb - 0.08, 'brass'))       # number plate
    nc.add(box(0.0, -0.45, 0.95, 0.3, 0.45, 0.99, 'walnut'))                         # a little shelf
    e.add(box(0.35, -0.12, Hb - 0.03, 0.65, 0.12, Hb - 0.01, 'e_red' if red else 'e_amber'))
    R.parts.add(g.xform(face, x, y))
    R.nocol.add(nc.xform(face, x, y))
    R.light(e.xform(face, x, y))
    # directories on the shelf: a row of books
    c, s = math.cos(face), math.sin(face)
    ox, oy = x + c * 0.0 - s * 0.45, y + s * 0.0 + c * 0.45
    R.shelf(ox, oy, 0.99, 0.9, face, rows=1, row_h=0.36, depth=0.28, frame='walnut', back=False, sides=False, crown=False)


def make():
    R = Room('telephones', 1, 1, res=1024)
    H = 6.2
    shell(R, H, wall='plaster', floor='terrazzo', ceil='plaster')
    # oak panelling to 2.6 m on the booth walls
    for (x0, x1) in ((T, T + 0.03), (C - T - 0.03, C - T)):
        R.nocol.add(box(x0, T, 0, x1, C - T, 2.8, 'walnut', skip=('-z',)))
    # booths: five either side of each side door
    k = 0
    for (a, b) in ((0.6, 6.2), (9.8, C - 0.6)):
        for i in range(5):
            y = a + 0.56 + i * 1.12
            booth(R, T + 0.03, y, 0.0, k, off_hook=(k == 7), red=(k == 12)); k += 1
            booth(R, C - T - 0.03, y, math.pi, k, off_hook=False, red=(k == 3)); k += 1
    # the switchboard: a desk along the south wall and a wall of lamps above it
    for (a, b) in ((0.6, 6.3), (9.7, C - 0.6)):
        R.parts.add(box(a, T, 0, b, T + 0.9, 0.78, 'walnut', skip=('-z',)))
        R.parts.add(box(a - 0.03, T, 0.78, b + 0.03, T + 0.95, 0.82, 'walnut', top='leather'))
        R.parts.add(box(a, T, 0.82, b, T + 0.3, 2.9, 'walnut'))
        R.parts.add(box(a, T, 2.9, b, T + 0.14, 5.6, 'walnut', sides='black'))
        R.parts.add(box(a - 0.05, T, 5.6, b + 0.05, T + 0.3, 5.75, 'brass'))
        # jacks and lamps: a grid, most dark, many lit
        nx = int((b - a - 0.3) / 0.24)
        for i in range(nx):
            px = a + 0.27 + i * 0.24
            for j in range(9):
                pz = 1.0 + j * 0.2
                h = (i * 73 + j * 151 + int(a * 10)) % 17
                if h < 7:
                    m = 'e_amber' if h < 5 else ('e_red' if h == 5 else 'e_green')
                    R.light(quad(px - 0.05, px + 0.05, T + 0.31, pz, pz + 0.07, m, '+y'))
                else:
                    R.nocol.add(quad(px - 0.03, px + 0.03, T + 0.31, pz, pz + 0.05, 'black', '+y'))
            for j in range(10):
                pz = 3.15 + j * 0.24
                h = (i * 37 + j * 91 + int(b * 10)) % 13
                if h < 5:
                    R.light(quad(px - 0.06, px + 0.06, T + 0.15, pz, pz + 0.1, 'e_amber' if h else 'e_red', '+y'))
        # cords: a few, looping down
        for i in range(7):
            px = a + 0.5 + i * (b - a - 1.0) / 6
            R.nocol.add(box(px - 0.01, T + 0.3, 0.84 + 0.1 * (i % 3), px + 0.01, T + 0.33, 1.4 + 0.25 * (i % 4), 'black'))
        # operators' chairs
        for i in range(4):
            chair(R, a + 0.8 + i * (b - a - 1.6) / 3, T + 1.45, -math.pi / 2, frame='walnut', seat='leather')
    # a clock over the south door
    R.parts.add(vdisk(8, T + 0.06, 5.0, 0.55, 0.1, 'y', 'brass', 24))
    R.nocol.add(vdisk(8, T + 0.12, 5.0, 0.48, 0.04, 'y', 'ivory', 24))
    R.nocol.add(box(7.98, T + 0.14, 5.0, 8.02, T + 0.16, 5.4, 'black'))
    R.nocol.add(box(8.0, T + 0.14, 4.98, 8.3, T + 0.16, 5.02, 'black'))
    # shelves of directories along the north wall
    wall_shelves(R, rows=12, frame='walnut', sides='N')
    # benches back to back down the middle, waiting
    for (y0, y1) in ((3.4, 6.2), (9.8, 12.6)):
        for x in (5.2, 10.8):
            bench(R, x - 0.5, y0, x - 0.05, y1, 'walnut', spots=False)
            bench(R, x + 0.05, y0, x + 0.5, y1, 'walnut', spots=False)
            R.parts.add(box(x - 0.05, y0, 0.45, x + 0.05, y1, 1.0, 'walnut'))
            for k2 in range(3):
                yy = y0 + 0.47 + k2 * (y1 - y0 - 0.94) / 2
                R.spot('sit', x - 0.28, yy, 0.45, math.pi)
                R.spot('sit', x + 0.28, yy, 0.45, 0.0)
    # lamps
    for x in (4.0, 8.0, 12.0):
        for y in (4.8, 11.2):
            pendant(R, x, y, 3.4, H, r=0.22, m='green')
    loop(R, [(2.4, 2.4), (8, 2.4), (C - 2.4, 2.4), (C - 2.4, 8), (C - 2.4, C - 2.4), (8, C - 2.4), (2.4, C - 2.4), (2.4, 8)])
    R.spot('probe', 8, 8, 2.0)
    R.meta.update(label='The Telephone Room', weight=4,
                  blurb='Twenty booths, and every line is busy. If you pick one up you hear breathing, and then someone says your name, and then the dialling tone.')
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    return R
