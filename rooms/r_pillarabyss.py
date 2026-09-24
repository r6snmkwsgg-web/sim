"""The Pillar Abyss: nine square pillars, each six metres across, rise from a dim floor 16 m below the
doorways you arrive by. At that height a railed ledge runs round the walls, and railed bridges cross
between collars built round the pillars. One pillar carries a long stair wound round it, down to the
floor, where the ground-level doorways are."""
from lib import *
from kit_g import *


def gaps_rail(R, x0, y0, x1, y1, z, gaps, gw):
    """An iron rail along an axis-aligned line, broken for openings centred at `gaps` (width gw)."""
    along_x = abs(y1 - y0) < abs(x1 - x0)
    a, b = (min(x0, x1), max(x0, x1)) if along_x else (min(y0, y1), max(y0, y1))
    cuts = sorted(g for g in gaps if a < g < b)
    p = a
    for g in cuts + [None]:
        q = b if g is None else g - gw / 2
        if q - p > 0.2:
            if along_x: iron_rail(R, p, y0, q, y0, z)
            else:       iron_rail(R, x0, p, x0, q, z)
        if g is not None: p = g + gw / 2


def make():
    R = Room('pillarabyss', 4, 4, levels=4, res=2048)
    W, D = R.W, R.D
    keep = [(s, i, 2) for s in 'SNWE' for i in range(4)]
    seal(R, upper_sockets(R, keep), floor='slate', wall='tile')
    ceil = R.hi - 0.4
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, ceil, 'tile', bottom='slate', top='plaster'))
    Z = 16.0                                   # the walkways
    ps, co, bw, le = 3.0, 5.0, 2.4, 3.4        # pillar half size, collar half size, bridge width, ledge edge
    G = (16.0, 32.0, 48.0)
    P = (16.0, 16.0)                           # the stair pillar
    # pillars, floor to ceiling
    for gx in G:
        for gy in G:
            R.parts.add(box(gx - ps, gy - ps, 0, gx + ps, gy + ps, ceil + 0.05, 'tile', skip=('-z', '+z')))
    # the ledge round the walls
    for (x0, y0, x1, y1) in ((T - 0.02, T - 0.02, W - T + 0.02, le), (T - 0.02, D - le, W - T + 0.02, D - T + 0.02),
                             (T - 0.02, le, le, D - le), (W - le, le, W - T + 0.02, D - le)):
        R.parts.add(box(x0, y0, Z - 0.7, x1, y1, Z, 'tile', top='terrazzo', bottom='plaster'))
    r_ = 0.05
    gaps_rail(R, le, le - r_, W - le, le - r_, Z, G, bw)
    gaps_rail(R, le, D - le + r_, W - le, D - le + r_, Z, G, bw)
    gaps_rail(R, le - r_, le, le - r_, D - le, Z, (32.0, 48.0), bw)          # no bridge west of the stair pillar
    gaps_rail(R, W - le + r_, le, W - le + r_, D - le, Z, G, bw)
    # collars round the pillars
    sx, sy = P
    for gx in G:
        for gy in G:
            if (gx, gy) == P:
                # open over the top flight on the west side
                R.parts.add(box(gx - ps, gy - co, Z - 0.7, gx + co, gy + co, Z, 'tile', top='terrazzo', bottom='plaster'))
                R.parts.add(box(gx - co, gy - co, Z - 0.7, gx - ps, gy - ps, Z, 'tile', top='terrazzo', bottom='plaster'))
                R.parts.add(box(gx - co, gy + ps, Z - 0.7, gx - ps, gy + co, Z, 'tile', top='terrazzo', bottom='plaster'))
                iron_rail(R, gx - co, gy + ps + r_, gx - ps, gy + ps + r_, Z)            # over the flight's top end
                iron_rail(R, gx - co + r_, gy + ps, gx - co + r_, gy + co, Z)
                iron_rail(R, gx - co + r_, gy - co, gx - co + r_, gy - ps, Z)
            else:
                R.parts.add(box(gx - co, gy - co, Z - 0.7, gx + co, gy + co, Z, 'tile', top='terrazzo', bottom='plaster'))
                gaps_rail(R, gx - co + r_, gy - co, gx - co + r_, gy + co, Z, (gy,), bw)
            gaps_rail(R, gx + co - r_, gy - co, gx + co - r_, gy + co, Z, (gy,), bw)
            gaps_rail(R, gx - co, gy - co + r_, gx + co, gy - co + r_, Z, (gx,), bw)
            gaps_rail(R, gx - co, gy + co - r_, gx + co, gy + co - r_, Z, (gx,), bw)
    # bridges on the grid lines, ledge to collar to collar to ledge
    spans = [(le, G[0] - co), (G[0] + co, G[1] - co), (G[1] + co, G[2] - co), (G[2] + co, W - le)]
    for g in G:
        for (a, b) in spans:
            for along in 'xy':
                if along == 'x' and g == P[1] and a == le: continue
                if along == 'x':
                    R.parts.add(box(a - 0.02, g - bw / 2, Z - 0.45, b + 0.02, g + bw / 2, Z, 'tile', top='terrazzo', bottom='plaster'))
                    iron_rail(R, a, g - bw / 2 + r_, b, g - bw / 2 + r_, Z); iron_rail(R, a, g + bw / 2 - r_, b, g + bw / 2 - r_, Z)
                else:
                    R.parts.add(box(g - bw / 2, a - 0.02, Z - 0.45, g + bw / 2, b + 0.02, Z, 'tile', top='terrazzo', bottom='plaster'))
                    iron_rail(R, g - bw / 2 + r_, a, g - bw / 2 + r_, b, Z); iron_rail(R, g + bw / 2 - r_, a, g + bw / 2 - r_, b, Z)
    # the long stair down the stair pillar: four flights round it, landings on the corners
    cx, cy = P
    n, rise, run, fw = 20, 0.2, 0.3, co - ps
    legs = [(cx - ps, cy - co, '+x', 0), (cx + ps, cy - ps, '+y', 1), (cx + ps, cy + ps, '-x', 1), (cx - co, cy + ps, '-y', 0)]
    corners = {'+x': (1, -1), '+y': (1, 1), '-x': (-1, 1), '-y': (-1, -1)}
    for k in range(4):
        x0, y0, ax, side = legs[k]
        z0 = k * n * rise
        flight(R, x0, y0, z0, fw, n, rise, run, ax, m='terrazzo', riser='tile', side='tile')
        flight_rail(R, x0, y0, z0, fw, n, rise, run, ax, which=(side,), m='iron', cap='iron', t=0.08)
        if k == 3: break
        csx, csy = corners[ax]; z = z0 + n * rise
        lx0, lx1 = (cx + ps, cx + co) if csx > 0 else (cx - co, cx - ps)
        ly0, ly1 = (cy + ps, cy + co) if csy > 0 else (cy - co, cy - ps)
        R.parts.add(box(lx0, ly0, z - 0.45, lx1, ly1, z, 'tile', top='terrazzo', bottom='plaster'))
        ex, ey = cx + csx * (co - r_), cy + csy * (co - r_)
        iron_rail(R, lx0, ey, lx1, ey, z); iron_rail(R, ex, ly0, ex, ly1, z)
        R.light(box(ex - 0.08, ey - 0.08, z + 1.0, ex + 0.08, ey + 0.08, z + 1.25, 'e_lamp'))
    # lamps: sconces on the pillar faces (bright at the walkways, dim above and below), lamps on the ledge walls
    for gx in G:
        for gy in G:
            for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                fx, fy = gx + dx * (ps + 0.1), gy + dy * (ps + 0.1)
                for (zz, e) in ((Z + 3.2, 'e_lamp'), (8.5, 'e_dim'), (26.0, 'e_dim')):
                    if (gx, gy) == P and zz < Z: continue
                    R.light(box(fx - 0.12 - abs(dy) * 0.1, fy - 0.12 - abs(dx) * 0.1, zz, fx + 0.12 + abs(dy) * 0.1, fy + 0.12 + abs(dx) * 0.1, zz + 0.35, e))
    for k in range(4):
        c = 16.0 * k
        if k == 0: continue
        for (x, y, w_, h_) in ((c, T + 0.06, 0.25, 0.06), (c, D - T - 0.06, 0.25, 0.06), (T + 0.06, c, 0.06, 0.25), (W - T - 0.06, c, 0.06, 0.25)):
            R.light(box(x - w_, y - h_, Z + 3.0, x + w_, y + h_, Z + 3.4, 'e_lamp'))
            R.light(box(x - w_, y - h_, 3.0, x + w_, y + h_, 3.4, 'e_dim'))
    # a few night lights on the floor far below
    for (x, y) in ((24, 24), (40, 40), (24, 40), (40, 24)):
        lamppost(R, x, y, h=2.6, e='e_candle', r=0.12)
    # books: round the pillars on the collars and on the floor, round the walls at both levels
    for gx in G:
        for gy in G:
            for (z, rows) in ((Z, 8), (0.0, 11)):
                if (gx, gy) == P and z < Z: continue
                L = 2 * ps - 0.4
                R.shelf(gx + ps - 0.2, gy - ps, z, L, '-y', rows=rows, frame='walnut')
                R.shelf(gx - ps + 0.2, gy + ps, z, L, '+y', rows=rows, frame='walnut')
                R.shelf(gx + ps, gy + ps - 0.2, z, L, '+x', rows=rows, frame='walnut')
                if not ((gx, gy) == P):
                    R.shelf(gx - ps, gy - ps + 0.2, z, L, '-x', rows=rows, frame='walnut')
    wall_cases(R, rows=10, frame='walnut')
    wall_cases(R, z=Z, rows=8, frame='walnut')
    # walkers: the ledge, and the floor
    e = 1.9
    up = [R.navpt(x, y, Z) for (x, y) in ((e, e), (W - e, e), (W - e, D - e), (e, D - e))]
    R.link(*up, up[0])
    lo = [R.navpt(x, y) for (x, y) in ((4, 4), (W - 4, 4), (W - 4, D - 4), (4, D - 4))]
    R.link(*lo, lo[0])
    R.spot('probe', 24, 24, Z + 1.7)
    R.meta.update(label='The Pillar Abyss', weight=2,
                  blurb='The doorway lets you out onto a ledge sixteen metres above a floor you can barely see. The bridges are railed. Someone thought of that, at least.')
    R.meta['box'] = [[T, 0, T], [W - T, ceil, D - T]]
    return R
