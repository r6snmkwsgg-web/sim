"""The Desert Room: a vaulted reading room buried in sand to the table tops, dunes rolling between the
rows, green lamps still burning where they stick out, hard sun through the tall east windows. Against
the west wall the biggest dune has swallowed a stone doorway to its lintel; the door stands open a
crack, and behind it a stair goes down into a room full of sand."""
from kit_h3 import *

W = D = 32.0
ST = 0.3125                        # the sand grid; the buried facade's face falls on a grid line
FX = 9.45                          # the buried facade's east face
FY0, FY1 = 13.8, 18.2              # its span
DY0, DY1 = 15.4, 16.6              # its doorway
DTOP = 2.35
SAND_AT_DOOR = 1.0
CX0, CX1, CY0, CY1 = 0.8, 6.0, 13.9, 18.1    # the cellar (floor -1.9)
RZ = -1.9
CEIL = 1.2
TABLES = [(x, y) for x in (9.6, 16.0, 22.4) for y in (4.6, 10.2, 21.8, 27.2)] + [(16.0, 16.0), (22.4, 16.0)]
DOORS = ((8, 0), (24, 0), (8, D), (24, D), (0, 8), (0, 24), (W, 8), (W, 24))


def dune(x, y):
    z = 0.42 + 0.3 * math.sin((x + y) * 0.42) + 0.16 * math.sin(x * 0.9 - y * 0.55 + 1.3) + 0.08 * math.sin(y * 2.1 + x * 0.3)
    # the great dune in the west, over the cellar
    d = math.hypot((x - 4.0) / 7.0, (y - 16.0) / 6.5)
    z = max(z, 3.2 * smooth_bump(max(0.0, d - 0.4) / 0.6, 1.0))
    # a drift poured in under the broken window
    d = math.hypot((x - 31.6) / 3.2, (y - 12.4) / 2.4)
    z = max(z, 1.6 * smooth_bump(d, 1.0))
    # a ridge along the north end
    z = max(z, 1.4 * smooth_bump(abs(y - 30.5) / 2.5, 1.0) * (0.6 + 0.4 * math.sin(x * 0.5)))
    return z


def sand(x, y):
    z = dune(x, y)
    if x < FX - 1e-6 and FY0 < y < FY1:
        g = smooth_bump(max(0.0, abs(y - 16.0) - 1.4) / 0.8, 1.0)
        z = max(z, 2.8 * g)
    elif FX - 1e-6 <= x < FX + 3.0 and FY0 - 0.5 < y < FY1 + 0.5:
        # in front of the facade: sand heaped against it, at the door just under half its height
        t = (x - FX) / 3.0
        top = SAND_AT_DOOR + (dune(x, y) - SAND_AT_DOOR) * t
        z = top if abs(y - 16.0) < 1.2 else max(min(z, SAND_AT_DOOR + 0.5), top)
    # scoops round the tables: the sand comes up to just under their tops
    for (tx, ty) in TABLES:
        dx = max(0.0, abs(x - tx) - 1.5); dy = max(0.0, abs(y - ty) - 0.6)
        dd = math.hypot(dx, dy)
        if dd < 1.2: z = min(z, 0.62 + 0.75 * dd)
    for (cx, cy) in DOORS:
        dd = max(abs(x - cx), abs(y - cy))
        f = max(0.0, min(1.0, (dd - 2.3) / 2.6))
        z = -0.05 + (z + 0.05) * f
    return z


def make():
    R = Room('desertroom', 2, 2, res=2048)
    R.sockets(floor='terrazzo', wall='tile')
    pr = arch_profile(W / 2, W - 2 * T + 0.04, 0, 5.0, 32, rise=2.4)
    R.cut(prism(pr, 'y', T - 0.02, D - T + 0.02, arch_mats(len(pr), 'terrazzo', 'tile'), cap='tile'))
    for k in range(9):
        y = 1.5 + k * 3.625
        R.nocol.add(prism(arc_band(W / 2, W - 2 * T, 5.0, 2.4, 0.0, 0.3, 32), 'y', y - 0.2, y + 0.2, 'tile', cap='tile'))
    # the sand
    skip = lambda x, y: FX - ST < x < FX and DY0 < y < DY1
    x0 = FX - 29 * ST
    R.parts.add(field(sand, x0, x0, x0 + 100 * ST, x0 + 100 * ST, 100, 100, m='plaster', skip=skip))
    hollow = lambda x, y: (CX0 - 0.6 < x < CX1 + 0.6 and CY0 - 0.6 < y < CY1 + 0.6) or (CX1 - 0.2 < x < FX + 0.2 and DY0 - 0.6 < y < DY1 + 0.6)
    fill_under(R, sand, x0, x0, ST, 100, 100, skip=hollow)
    windows_(R)
    west_wall(R)
    tables(R)
    facade(R)
    cellar(R)
    fx(R, 'dust', [16, T, 0.5, W - T, D - T, 5.0])
    nv = navloop(R, [(8, 2.3), (13.0, 7.4), (19.0, 7.4), (24, 2.3), (29.6, 8), (26.0, 13.2), (29.6, 24), (24, 29.6), (19.0, 24.5), (13.0, 24.5), (8, 29.6), (2.4, 24), (12.4, 19.0), (12.4, 13.0), (2.4, 8)])
    for i in nv:
        p = R.nav[i]; p[2] = max(0.0, sand(p[0], p[1]))
    secret(R, 3.4, 16.0, RZ, 'The Room Under the Dune',
           'A reading room like the one above, filled to the shoulders with sand that came in grain by grain. One lamp still works. Somebody dug a path to the desk and kept on reading.')
    return finish(R, 'The Desert Room', weight=4, probe=(18.5, 16.0, 2.4), top=7.4,
                  blurb='Sand. A reading room full of it, up to the table tops, and still coming in at the windows. The lamps are on. Nobody has asked for the room to be swept.')


def windows_(R):
    """Tall windows full of hard sun in the east wall, the desert outside them."""
    for c in (3.6, 12.4, 19.6, 28.4):
        window(R, 'E', c, 1.0, 2.4, 2.6, em='e_sky', mull=2, trans=2)
        # dunes outside, in silhouette against the lower panes
        g = Geo()
        pts = [(c - 1.2 + 2.4 * k / 12, 1.0 + 0.55 + 0.35 * math.sin(k * 0.9 + c)) for k in range(13)]
        poly = [(c - 1.2, 1.0)] + pts + [(c + 1.2, 1.0)]
        g.add(prism(poly, 'x', W - 0.1, W - 0.07, 'plaster', cap='plaster'))
        R.nocol.add(g)
    # the broken one: its glazing bars bent, sand pouring in over the sill
    R.nocol.add(beam((W - T - 0.2, 11.6, 1.1), (W - T - 0.6, 12.2, 2.0), 0.05, 'iron'))
    # pilasters between the windows
    for y in (6.0, 10.0, 22.0, 26.0, 16.0):
        R.parts.add(box(W - T - 0.3, y - 0.35, 0, W - T, y + 0.35, 5.0, 'tile', skip=('-z',)))


def west_wall(R):
    rows = 11
    for (a, b) in ((0.6, 5.8), (10.2, 13.4), (18.6, 21.8), (26.2, D - 0.6)):
        sh(R, '+x', T, a, b, rows=rows, frame='walnut')
    for (bk, a, b, d) in ((T, 0.6, 5.8, '+y'), (T, 10.2, 21.8, '+y'), (T, 26.2, W - 0.6, '+y'),
                          (D - T, 0.6, 5.8, '-y'), (D - T, 10.2, 21.8, '-y'), (D - T, 26.2, W - 0.6, '-y')):
        sh(R, d, bk, a, b, rows=rows, frame='walnut')
    # sconces
    for y in (4.0, 12.0, 20.0, 28.0):
        R.light(sphere(T + 0.3, y, 5.1, 0.12, 10, 5, 'e_lamp'))
        R.nocol.add(box(T, y - 0.04, 4.85, T + 0.3, y + 0.04, 4.95, 'brass'))


def tables(R):
    k = 0
    for (tx, ty) in TABLES:
        R.parts.add(table(tx - 1.5, ty - 0.6, tx + 1.5, ty + 0.6, 0.78, 'walnut', top='leather'))
        blanket(R, tx - 1.5, ty - 0.6, tx - 0.2 + 0.6 * math.sin(k), ty + 0.6, 0.78, t=0.03, m='plaster')
        desk_lamp(R, tx - 0.8, ty, 0.78); desk_lamp(R, tx + 0.8, ty, 0.78)
        for xx in (tx - 0.8, tx + 0.8):
            for (yy, a) in ((ty - 1.05, math.pi / 2), (ty + 1.05, -math.pi / 2)):
                R.parts.add(chair(xx, yy, a))
        if k % 3 == 0: book_pile(R, tx + 0.3, ty + 0.2, 0.78, 4, seed=k)
        k += 1
    # standard lamps drowned to their shades
    for (x, y) in ((12.8, 13.0), (19.2, 19.0), (26.0, 30.2), (6.4, 28.8), (26.2, 3.6)):
        lamp_post(R, x, y, 0, 2.7)


def facade(R):
    """A stone front with a doorway, buried by the great dune: the door stands ajar."""
    t = 0.5
    for (y0, y1) in ((FY0, DY0), (DY1, FY1)):
        R.parts.add(box(FX - t, y0, 0, FX, y1, 2.6, 'tile'))
    R.parts.add(box(FX - t, DY0, DTOP, FX, DY1, 2.6, 'tile'))
    R.parts.add(box(FX - 0.02, DY0 - 0.25, DTOP, FX + 0.12, DY1 + 0.25, DTOP + 0.22, 'tile'))       # a lintel
    for y in (DY0 - 0.2, DY1 + 0.2):
        R.parts.add(box(FX - 0.02, y - 0.1, 0, FX + 0.1, y + 0.1, DTOP, 'tile'))
    R.parts.add(box(FX - 0.2, FY0 - 0.1, 2.6, FX + 0.08, FY1 + 0.1, 2.75, 'tile'))                    # a cornice
    door = box(0, 0, 0, 0.05, DY1 - DY0 - 0.05, DTOP - 0.05, 'oak')
    for (z0, z1) in ((0.2, 1.0), (1.2, 2.1)):
        door.add(box(0.05, 0.12, z0, 0.07, DY1 - DY0 - 0.2, z1, 'walnut'))
    door.xform(0.55, FX - t - 0.02, DY0 + 0.02, 0)
    R.nocol.add(door)
    R.parts.add(box(FX - 0.4, DY0 + 0.3, DTOP + 0.3, FX - 0.1, DY1 - 0.3, DTOP + 0.5, 'black'))
    R.light(box(FX + 0.13, 15.75, DTOP + 0.05, FX + 0.15, 16.25, DTOP + 0.17, 'e_exit'))


def cellar(R):
    """Under the dune: the stair down, and a room full of sand."""
    R.cut(box(CX0, CY0, RZ, CX1, CY1, 0.05, 'damask', bottom='floor', top='plaster'))
    R.cut(box(CX1 - 0.4, DY0, RZ, FX - 0.5 + 0.02, DY1, 0.05, 'tile', bottom='floor', top='tile'))
    n, rise, run = 12, (SAND_AT_DOOR - RZ) / 12, 0.28
    fx0 = FX - 0.5 - n * run
    R.flight(fx0, DY0, RZ, DY1 - DY0, n, rise, run, '+x', m='plaster', riser='tile', side='tile')
    R.parts.add(box(FX - 0.5, DY0, 0, FX, DY1, SAND_AT_DOOR, 'plaster'))
    R.parts.add(box(fx0 - 0.4, DY0, RZ, fx0 + 0.02, DY1, RZ + 0.02, 'plaster'))
    # the passage's walls and roof above floor level, and the cellar's: solid, inside the dune
    R.parts.add(box(CX1, DY1, 0, FX - 0.5, DY1 + 0.4, 2.6, 'tile'))
    R.parts.add(box(CX1, DY0 - 0.4, 0, FX - 0.5, DY0, 2.6, 'tile'))
    R.parts.add(box(CX1, DY0 - 0.4, 2.4, FX - 0.5, DY1 + 0.4, 2.6, 'tile'))
    w = 0.4
    R.parts.add(box(CX0 - w, CY0 - w, 0, CX1 + w, CY0, CEIL, 'damask'))
    R.parts.add(box(CX0 - w, CY1, 0, CX1 + w, CY1 + w, CEIL, 'damask'))
    R.parts.add(box(CX0 - w, CY0, 0, CX0, CY1, CEIL, 'damask'))
    for (y0, y1) in ((CY0, DY0), (DY1, CY1)):
        R.parts.add(box(CX1, y0, 0, CX1 + w, y1, CEIL, 'damask'))
    R.parts.add(box(CX1, DY0, CEIL, CX1 + w, DY1, 2.4, 'tile'))
    R.parts.add(box(CX0 - w, CY0 - w, CEIL, CX1 + w, CY1 + w, CEIL + 0.2, 'plaster'))
    # the sand inside: heaped against the walls, a clear path to the desk
    def fill(x, y):
        z = RZ - 0.05
        z = max(z, RZ + 1.6 * smooth_bump(max(0.0, x - CX0) / 1.6, 1.0) * (0.7 + 0.3 * math.sin(y * 1.7)))
        z = max(z, RZ + 1.1 * smooth_bump(max(0.0, CY1 - y) / 1.3, 1.0))
        z = max(z, RZ + 0.8 * smooth_bump(max(0.0, y - CY0) / 1.0, 1.0))
        if abs(y - 16.0) < 0.9 and x > 2.6: z = min(z, RZ + 0.05)
        return z
    R.parts.add(field(fill, CX0, CY0, CX1 - 0.4, CY1, 16, 14, m='plaster', floor=RZ))
    sh(R, '-y', CY1, 2.4, CX1 - 0.3, z=RZ, rows=6, frame='walnut')
    sh(R, '+y', CY0, 2.2, CX1 - 0.3, z=RZ, rows=6, frame='walnut')
    R.parts.add(table(2.9, 15.5, 4.1, 16.5, 0.74, 'walnut', top='leather').xform(0, 0, 0, RZ))
    open_book(R, 3.5, 16.0, RZ + 0.74, math.pi / 2)
    desk_lamp(R, 3.2, 16.3, RZ + 0.74)
    c = chair(4.5, 16.0, math.pi); c.xform(0, 0, 0, RZ); R.parts.add(c)
    R.spot('sit', 4.5, 16.0, RZ + 0.48, math.pi)
    R.spot('read', 3.5, 16.0, RZ + 0.74, math.pi)
    R.light(sphere(CX1 - 0.3, CY0 + 0.3, RZ + 1.2, 0.05, 6, 3, 'e_candle'))
    a, b = R.navpt(FX + 0.8, 16.0, SAND_AT_DOOR), R.navpt(CX1 - 0.9, 16.0, RZ)
    R.link(a, b)
