"""The Lift: a square well two storeys deep, every face of it shelves, and in the middle an open brass
lift cage that goes up and down between the floors, resting a few seconds at each end. At both ends of
its run a brass drum stands round the shaft, turning; its door comes round to meet the cage's only while
the cage is there. A stair hung off the west face climbs the well too. Halfway up, where the stair's
rail has a gap, there is a door in the shelves across a metre of nothing."""
from kit_h12 import *

W = D = 32.0
H = 2 * LH - (LH - TOP)          # 15.6
CX = CY = 16.0
A0, A1 = 10.0, 22.0              # the well
RC = 4.3                          # the ground floor ring's ceiling
SZ = 4.5                          # the secret room's floor (and the ledge)
CR = 1.55                         # the cage
DRI, DRO = 1.62, 1.72             # the drums
DH = 2.6
P, PA = 24.0, 5.0                 # the lift: period, pause
OM = 2 * math.pi / P
DOOR = -math.pi / 2               # the cage's door faces south
STX0, STX1 = 11.5, 13.1           # the hung stair
STY0, NST = 11.7, 37
RUN = 0.27
LY0, LY1 = 16.5, 18.1             # the ledge
SX0, SX1, SY0, SY1 = 3.0, 9.7, 12.5, 19.5   # the room behind it


def make():
    R = Room('elevator', 2, 2, levels=2, res=2048)
    rs = rng(54)
    R.sockets(floor='terrazzo', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, RC, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(A0, A0, 0, A1, A1, H - 0.1, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(T - 0.02, T - 0.02, LH, W - T + 0.02, D - T + 0.02, H - 0.1, 'tile', bottom='floor', top='plaster'))
    well(R, rs)
    ground(R, rs)
    upper(R, rs)
    stair(R)
    shaft(R, rs)
    cage(R, rs)
    drums(R)
    secret_room(R, rs)
    lamps(R)
    P_ = {'s1': (8.0, 1.6), 's2': (24.0, 1.6), 'n1': (8.0, 30.4), 'n2': (24.0, 30.4), 'w1': (1.6, 8.0), 'w2': (1.6, 24.0), 'e1': (30.4, 8.0), 'e2': (30.4, 24.0),
          'a': (6.0, 6.0), 'b': (16.0, 6.0), 'c': (26.0, 6.0), 'd': (26.0, 16.0), 'e': (26.0, 26.0), 'f': (16.0, 26.0), 'g': (6.0, 26.0), 'h': (6.0, 16.0),
          'l0': (16.0, 12.5), 'U1': (8.0, 2.0, LH), 'U2': (24.0, 2.0, LH), 'U3': (24.0, 30.0, LH), 'U4': (8.0, 30.0, LH),
          'u1': (16.0, 9.2, LH), 'u2': (16.0, 12.8, LH), 'u3': (12.3, 23.0, LH)}
    navgrid(R, P_, [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'f'), ('f', 'g'), ('g', 'h'), ('h', 'a'), ('a', 's1'), ('a', 'w1'),
                    ('c', 's2'), ('c', 'e1'), ('e', 'n2'), ('e', 'e2'), ('g', 'n1'), ('g', 'w2'), ('b', 'l0'),
                    ('U1', 'U2'), ('U2', 'U3'), ('U3', 'U4'), ('U4', 'U1'), ('U1', 'u1'), ('u1', 'u2'), ('U4', 'u3')])
    secret(R, 7.0, 16.0, SZ, 'The Attendant\'s Cubby',
           'Halfway up the well, across the gap, a door. Behind it the lift attendant\'s room: a stool, a cap on a hook, a logbook in which every line says the same two floors.', r=2.0)
    return finish(R, 'The Brass Lift', weight=3, probe=(16.0, 7.0, 2.2), top=H - 0.1,
                  blurb='The lift only goes between these two floors. People ride it anyway, up and down, for the pleasure of standing still while the shelves go by.')


# ---------------------------------------------------------------------------
def well(R, rs):
    """The well's faces: at the ground, walls with one arch each and cases either side; in the band between
    the floors, cases from edge to edge (the west face broken by the ledge and its door)."""
    t = 0.4
    for (side, c) in (('S', A0), ('N', A1), ('W', A0), ('E', A1)):
        s = -1 if side in 'SW' else 1                  # which way is outside
        for (u0, u1) in (((A0 - t, 14.5), (17.5, A1 + t)) if side != 'W' else ((A0 - t, A1 + t),)):
            if side in 'SN': R.parts.add(box(u0, min(c, c + s * t), 0, u1, max(c, c + s * t), RC, 'tile', skip=('-z', '+z')))
            else: R.parts.add(box(min(c, c + s * t), u0, 0, max(c, c + s * t), u1, RC, 'tile', skip=('-z', '+z')))
        if side in 'SN': R.parts.add(box(14.5, min(c, c + s * t), 3.3, 17.5, max(c, c + s * t), RC, 'tile', skip=('+z',)))
        elif side == 'E': R.parts.add(box(min(c, c + s * t), 14.5, 3.3, max(c, c + s * t), 17.5, RC, 'tile', skip=('+z',)))
        # cases on the inside faces at the ground, and in the band above
        face_in = {'S': '+y', 'N': '-y', 'W': '+x', 'E': '-x'}[side]
        face_out = {'S': '-y', 'N': '+y', 'W': '-x', 'E': '+x'}[side]
        for (u0, u1) in (((A0 + 0.2, 14.3), (17.7, A1 - 0.2)) if side != 'W' else ((A0 + 0.2, 15.4), (19.2, A1 - 0.2))):
            sh(R, face_in, c, u0, u1, rows=7, frame='walnut')
            sh(R, face_out, c + s * t, u0 - 0.3 if u0 < 14 else u0, u1, rows=7, frame='walnut')
        band = [(A0 + 0.1, A1 - 0.1)] if side != 'W' else [(A0 + 0.1, LY0 - 0.25), (LY1 + 0.25, A1 - 0.1)]
        for (u0, u1) in band:
            sh(R, face_in, c, u0, u1, z=SZ - 0.05, rows=8, frame='walnut')
        # cornices at the band's foot and top
        for z in (RC - 0.05, LH - 0.2):
            if side in 'SN': R.parts.add(box(A0, min(c, c - s * 0.4), z, A1, max(c, c - s * 0.4), z + 0.15, 'walnut'))
            else: R.parts.add(box(min(c, c - s * 0.4), A0, z, max(c, c - s * 0.4), A1, z + 0.15, 'walnut'))
    # the ledge on the west face, and its door
    R.parts.add(box(A0, LY0, SZ - 0.25, A0 + 0.7, LY1, SZ, 'tile', top='terrazzo'))
    for y in (LY0 + 0.2, LY1 - 0.2):
        R.nocol.add(beam((A0, y, SZ - 1.0), (A0 + 0.6, y, SZ - 0.26), 0.1, 'walnut'))
    brass_rail(R, A0, LY0 + 0.05, A0 + 0.7, LY0 + 0.05, SZ, h=0.95)
    brass_rail(R, A0, LY1 - 0.05, A0 + 0.7, LY1 - 0.05, SZ, h=0.95)
    R.cut(box(SX1 - 0.05, 16.8, SZ, A0 + 0.02, 17.8, SZ + 2.2, 'walnut', bottom='terrazzo', top='walnut'))
    R.nocol.add(frame_rect('x', A0, 16.8, 17.8, SZ, SZ + 2.2, 1, w=0.12, d=0.06, m='brass'))
    # a low chest along the face under the ledge (whoever misses the jump lands on it)
    R.parts.add(box(A0, 15.6, 0, 11.45, 19.0, 0.55, 'walnut', top='leather'))
    for k in range(6):
        yy = 15.75 + k * 0.54
        for zz in (0.12,):
            R.nocol.add(box(11.45, yy, zz, 11.48, yy + 0.45, zz + 0.3, 'oak'))
            R.nocol.add(box(11.48, yy + 0.2, zz + 0.13, 11.51, yy + 0.25, zz + 0.17, 'brass'))


def ground(R, rs):
    """The ring round the well at the ground: cases on the outer walls, stacks, reading tables, lights."""
    for (a, b) in ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)):
        sh(R, '+y', T, a, b, rows=9, frame='walnut')
        sh(R, '-y', D - T, a, b, rows=9, frame='walnut')
        sh(R, '+x', T, a, b, rows=9, frame='walnut')
        sh(R, '-x', W - T, a, b, rows=9, frame='walnut')
    for (x0, x1, y0, y1) in ((24.5, 29.0, 12.0, 13.0), (24.5, 29.0, 19.0, 20.0), (12.0, 20.0, 3.3, 4.3), (12.0, 20.0, 27.7, 28.7)):
        reading_table(R, x0, y0, x1, y1, lamps=3, chairs=True)
    for (x, y) in ((5.5, 5.5), (26.5, 5.5), (26.5, 26.5), (5.5, 26.5), (16.0, 5.0), (16.0, 27.0), (27.0, 16.0)):
        R.light(box(x - 0.6, y - 0.6, RC - 0.02, x + 0.6, y + 0.6, RC - 0.01, 'e_panel'))


def upper(R, rs):
    """The upper floor: a walk round the well's edge behind a balustrade, stacks facing the well a pace back
    from it (so the well is shelves on every side up here too), cases on the outer walls."""
    # balustrade round the edge, with gaps for the bridge (south) and the stair (north)
    for (side, c) in (('S', A0), ('N', A1), ('W', A0), ('E', A1)):
        gaps = {'S': [(15.2, 16.8)], 'N': [(STX0, STX1)]}.get(side, [])
        us = [A0]
        for (a, b) in gaps: us += [a, b]
        us.append(A1)
        off = -0.07 if side in 'SW' else 0.07
        for k in range(0, len(us), 2):
            if side in 'SN': stone_rail(R, us[k], c + off, us[k + 1], c + off, LH, h=1.0)
            else: stone_rail(R, c + off, us[k], c + off, us[k + 1], LH, h=1.0)
    # stacks a pace back, double-faced
    for (side, c) in (('S', A0 - 1.6), ('N', A1 + 1.6), ('W', A0 - 1.6), ('E', A1 + 1.6)):
        for (u0, u1) in ((8.4, 14.3), (17.7, 23.6)):
            if side in 'SN': stack(R, 'x', c, u0, u1, z=LH, rows=10, frame='walnut')
            else: stack(R, 'y', c, u0, u1, z=LH, rows=10, frame='walnut')
    for (a, b) in ((0.8, 6.2), (9.8, 22.2), (25.8, W - 0.8)):
        sh(R, '+y', T, a, b, z=LH, rows=10, frame='walnut')
        sh(R, '-y', D - T, a, b, z=LH, rows=10, frame='walnut')
        sh(R, '+x', T, a, b, z=LH, rows=10, frame='walnut')
        sh(R, '-x', W - T, a, b, z=LH, rows=10, frame='walnut')
    for (x0, x1, y0, y1) in ((2.5, 6.0, 12.0, 13.0), (26.0, 29.5, 19.0, 20.0)):
        reading_table(R, x0, y0 + 0.0, x1, y1, lamps=2, chairs=True, z=LH)


def stair(R):
    """A flight hung a little off the west face, climbing north from the ground to the upper floor; its
    rail on the wall side has a gap halfway, level with the ledge."""
    rise = LH / NST
    rflight(R, STX0, STY0, 0.0, STX1 - STX0, NST, rise, RUN, '+y', m='oak', riser='walnut', side='walnut', soffit='walnut')
    y1 = STY0 + NST * RUN
    R.parts.add(box(STX0, y1 - 0.02, LH - 0.3, STX1, A1 + 0.05, LH, 'oak', sides='walnut'))
    zf = lambda y: (y - STY0) / RUN * rise
    stair_rail(R, STX1 - 0.03, STY0, rise, STX1 - 0.03, y1, LH)
    g0, g1 = 16.8, 17.6                       # the gap in the rail, across from the ledge
    stair_rail(R, STX0 + 0.03, STY0, rise, STX0 + 0.03, g0, zf(g0))
    stair_rail(R, STX0 + 0.03, g1, zf(g1), STX0 + 0.03, y1, LH)
    # iron hangers from the band's cornice to the flight's west edge
    for y in (13.0, 19.0):
        R.nocol.add(beam((A0, y, LH - 0.3), (STX0 + 0.1, y, zf(y) + 1.1), 0.05, 'iron'))


def shaft(R, rs):
    """The static parts of the shaft: four brass guide rails floor to ceiling, a lattice tube between the
    drums (with an invisible wall), the ring platform the upper drum stands on, and the bridge to it."""
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        x, y = CX + 2.65 * math.cos(a), CY + 2.65 * math.sin(a)
        R.parts.add(cyl(x, y, 0, H - 0.1, 0.09, 10, side='brass', caps=False))
        for z in (DH + 0.2, LH - 0.2, LH + DH + 0.2):
            R.nocol.add(beam((x, y, z), (CX + DRO * math.cos(a), CY + DRO * math.sin(a), z), 0.05, 'brass'))
    g = Geo()
    cyl_lattice(g, CX, CY, (DRI + DRO) / 2, DH, LH - 0.4, 0, 2 * math.pi, m='brass', step=0.3, hoops=(0.0, 0.25, 0.5, 0.75, 1.0))
    R.nocol.add(g)
    R.col.add(ring(CX, CY, DH, LH - 0.4, DRI + 0.01, DRO - 0.01, 32, top='tile', bottom='tile', inner='tile', outer='tile'))
    # the ring platform at the upper floor, and the bridge from the south edge
    R.parts.add(ring(CX, CY, LH - 0.4, LH, DRI - 0.02, 2.5, 40, top='floor', bottom='brass', inner='brass', outer='brass'))
    R.parts.add(box(15.2, A0 - 0.05, LH - 0.3, 16.8, CY - 2.3, LH, 'floor', sides='walnut', bottom='iron'))
    for x in (15.24, 16.76):
        brass_rail(R, x, A0, x, CY - 2.42, LH, h=1.0)
    ring_rail(R, CX, CY, 2.44, LH, a0=-math.pi / 2 + 0.36, a1=-math.pi / 2 + 2 * math.pi - 0.36, h=1.0, m='brass')
    for y in (11.5, 12.8):
        R.nocol.add(beam((15.2, y, LH - 0.3), (15.2, y - 1.2, LH - 1.6), 0.06, 'iron'))
        R.nocol.add(beam((16.8, y, LH - 0.3), (16.8, y - 1.2, LH - 1.6), 0.06, 'iron'))
    # a pit ring at the ground where the lower drum stands
    R.nocol.add(ring(CX, CY, 0.0, 0.01, DRO, DRO + 0.5, 40, top='brass', bottom='brass', inner='brass', outer='brass'))


def cage(R, rs):
    """The cage: a round brass birdcage on a floor of oak, its door always open to the south; it rises
    eight metres and falls again, resting five seconds at each end."""
    M = R.mover('slide', delta=(0, 0, LH), period=P, pause=PA, phase=0.0)
    M.parts.add(cyl(CX, CY, 0.0, 0.15, CR, 32, side='brass', top='floor', bottom='iron'))
    M.nocol.add(ring(CX, CY, 0.15, 0.16, 1.2, 1.35, 32, top='brass', bottom='brass', inner='brass', outer='brass'))
    half = 0.62 / CR
    a0, a1 = DOOR + half, DOOR + 2 * math.pi - half
    g = Geo()
    cyl_lattice(g, CX, CY, CR - 0.03, 0.15, 2.6, a0, a1, m='brass', step=0.16, hoops=(0.0, 0.35, 0.4, 0.7, 1.0))
    # diagonal lattice in the lower panel
    n = 28
    for k in range(n):
        u0 = a0 + (a1 - a0) * k / n; u1 = a0 + (a1 - a0) * (k + 1) / n
        r = CR - 0.03
        g.add(beam((CX + r * math.cos(u0), CY + r * math.sin(u0), 0.2), (CX + r * math.cos(u1), CY + r * math.sin(u1), 1.0), 0.02, 'brass'))
        g.add(beam((CX + r * math.cos(u1), CY + r * math.sin(u1), 0.2), (CX + r * math.cos(u0), CY + r * math.sin(u0), 1.0), 0.02, 'brass'))
    # the door posts and the canopy: a brass dome with a finial
    for s in (-1, 1):
        u = DOOR + s * half
        x, y = CX + (CR - 0.03) * math.cos(u), CY + (CR - 0.03) * math.sin(u)
        g.add(box(x - 0.05, y - 0.05, 0.15, x + 0.05, y + 0.05, 2.65, 'gilt'))
    g.add(ring(CX, CY, 2.6, 2.7, 1.1, CR + 0.05, 32, top='gilt', bottom='brass', inner='brass', outer='gilt'))
    for k in range(12):
        a = 2 * math.pi * k / 12
        g.add(beam((CX + CR * math.cos(a), CY + CR * math.sin(a), 2.7), (CX, CY, 3.3), 0.05, 'brass'))
    g.add(sphere(CX, CY, 3.35, 0.14, 10, 5, 'gilt'))
    # inside: a folding seat, the lever
    g.add(box(CX - 0.4, CY + CR - 0.45, 0.5, CX + 0.4, CY + CR - 0.08, 0.56, 'velvet'))
    g.add(cyl(CX + 0.9, CY + 0.9, 0.15, 1.05, 0.06, 8, side='brass', top='brass'))
    g.add(beam((CX + 0.9, CY + 0.9, 1.05), (CX + 0.75, CY + 0.75, 1.35), 0.025, 'brass'))
    g.add(sphere(CX + 0.75, CY + 0.75, 1.37, 0.045, 6, 3, 'ivory'))
    M.nocol.add(g)
    M.col.add(ring(CX, CY, 0.15, 2.6, CR - 0.06, CR, 32, top='tile', bottom='tile', inner='tile', outer='tile', a0=a0, a1=a1))


def drums(R):
    """The turning gates: a brass drum round the shaft at each end of the cage's run, one turn per trip.
    The lower one's door faces south when the cage rests at the bottom, the upper one's when it rests at
    the top; the rest of the time they are a wall. (Built with the lower door facing south: the cage rests
    at the bottom when the room is checked.)"""
    ph = round(math.pi * PA / P, 5)
    M = R.mover('spin', pivot=(CX, CY, 0), axis='z', speed=round(OM, 6), phase=ph)
    half = 0.8 / ((DRI + DRO) / 2)
    for (z0, door) in ((0.0, DOOR), (LH, DOOR + math.pi)):
        a0, a1 = door + half, door + 2 * math.pi - half
        M.parts.add(ring(CX, CY, z0, z0 + 1.1, DRI, DRO, 40, top='brass', bottom='brass', inner='brass', outer='brass', a0=a0, a1=a1))
        g = Geo()
        cyl_lattice(g, CX, CY, (DRI + DRO) / 2, z0 + 1.1, z0 + DH, a0, a1, m='brass', step=0.2, hoops=(0.0, 0.5, 1.0))
        g.add(ring(CX, CY, z0 + DH - 0.08, z0 + DH, DRI - 0.02, DRO + 0.04, 40, top='gilt', bottom='gilt', inner='gilt', outer='gilt', a0=a0, a1=a1))
        for s in (-1, 1):
            u = door + s * half
            x, y = CX + (DRI + DRO) / 2 * math.cos(u), CY + (DRI + DRO) / 2 * math.sin(u)
            g.add(box(x - 0.06, y - 0.06, z0, x + 0.06, y + 0.06, z0 + DH, 'gilt'))
        M.nocol.add(g)
        M.col.add(ring(CX, CY, z0 + 1.1, z0 + DH, DRI, DRO, 40, top='tile', bottom='tile', inner='tile', outer='tile', a0=a0, a1=a1))


def secret_room(R, rs):
    """Behind the door on the ledge: the attendant's cubby, inside the band between the floors; a narrow
    enclosed stair goes down from it to the ground floor, where it comes out behind a false case."""
    R.cut(box(SX0, SY0, SZ, SX1, SY1, LH - 0.4, 'damask', bottom='floor', top='plaster'))
    # the stair down: x 3.0..4.1, from y 11.0 (ground) up north to y 17.2 (the room's floor)
    n = 22; rise = SZ / n; run = 0.28
    y0 = 17.2 - n * run
    R.flight(SX0, y0, 0.0, 1.1, n, rise, run, '+y', m='oak', riser='walnut', side='tile')
    prof = [(y0 - 0.25, -0.02), (17.25, SZ - 0.02), (17.25, SZ + 2.5), (y0 - 0.25, 2.5)]
    R.cut(prism(prof, 'x', SX0, SX0 + 1.1, ['tile', 'tile', 'plaster', 'tile'], cap='tile'))
    for x in (SX0 - 0.2, SX0 + 1.1):
        R.parts.add(box(x, y0 - 0.25, 0, x + 0.2, 17.2, RC, 'tile', skip=('-z',)))
    R.parts.add(box(SX0, y0 - 0.25, 2.3, SX0 + 1.1, y0 - 0.05, RC, 'tile'))
    R.shelf(SX0 + 1.1, y0 - 0.25, 0.0, 1.1, '-y', rows=5, frame='walnut', solid=False)
    brass_rail(R, SX0 + 1.15, SY0, SX0 + 1.15, 17.2, SZ, h=0.95)
    brass_rail(R, SX0, SY0 + 0.05, SX0 + 1.15, SY0 + 0.05, SZ, h=0.95)
    # the cubby: a stool, a cap on a hook, a desk with the logbook, a window slot on the well
    R.parts.add(table_geo(7.6, 18.4, 9.5, 19.3, 0.78, 'walnut', top='leather').xform(0, 0, 0, SZ))
    R.parts.add(stool(8.5, 17.8, math.pi / 2, back=False).xform(0, 0, 0, SZ))
    desk_lamp(R, 9.1, 19.0, SZ + 0.78)
    open_book(R, 8.4, 18.85, SZ + 0.78, math.pi / 2)
    R.nocol.add(box(5.0, SY1 - 0.08, SZ + 1.6, 5.1, SY1, SZ + 1.65, 'brass'))
    R.nocol.add(cyl(5.05, SY1 - 0.2, SZ + 1.55, SZ + 1.68, 0.14, 12, side='oxblood', top='oxblood', bottom='black'))
    R.nocol.add(box(4.9, SY1 - 0.3, SZ + 1.55, 5.2, SY1 - 0.06, SZ + 1.58, 'black'))
    R.parts.add(box(5.2, SY0 + 0.05, SZ, 7.4, SY0 + 0.95, SZ + 0.45, 'walnut', top='bed'))
    R.spot('bed', 6.3, SY0 + 0.5, SZ + 0.45, 0.0)
    sh(R, '-y', SY1, 5.3, 7.4, z=SZ, rows=6, frame='walnut')
    R.cut(box(SX1 - 0.02, 13.4, SZ + 1.2, A0 + 0.02, 14.6, SZ + 1.5, 'walnut'))
    R.light(sphere(6.5, 16.0, SZ + 2.4, 0.07, 8, 4, 'e_amber'))
    R.nocol.add(cyl(6.5, 16.0, SZ + 2.46, LH - 0.4, 0.01, 4, side='iron', caps=False))
    R.spot('plaque', 8.4, 18.85, SZ, math.pi / 2,
           text='The logbook. Every line: UP. DOWN. UP. DOWN. On the last page someone has written: there is no third floor, I have checked.')


def lamps(R):
    """Sconces on the well's faces, pendants on the upper floor, a laylight over the well."""
    for (x, y, a) in ((A0 + 0.05, 12.0, 0.0), (A0 + 0.05, 20.0, 0.0), (A1 - 0.05, 12.0, math.pi), (A1 - 0.05, 20.0, math.pi),
                      (12.0, A0 + 0.05, math.pi / 2), (20.0, A0 + 0.05, math.pi / 2), (12.0, A1 - 0.05, -math.pi / 2), (20.0, A1 - 0.05, -math.pi / 2)):
        sconce(R, x, y, RC + 0.35, a)
    R.cut(box(12.0, 12.0, H - 0.4, 20.0, 20.0, H - 0.03, 'plaster'))
    R.light(box(12.0, 12.0, H - 0.07, 20.0, 20.0, H - 0.05, 'e_sky'))
    for k in range(1, 4):
        R.nocol.add(box(12.0 + k * 2 - 0.04, 12.0, H - 0.35, 12.0 + k * 2 + 0.04, 20.0, H - 0.07, 'iron'))
        R.nocol.add(box(12.0, 12.0 + k * 2 - 0.04, H - 0.35, 20.0, 12.0 + k * 2 + 0.04, H - 0.07, 'iron'))
    for (x, y) in ((4.0, 4.0), (28.0, 4.0), (28.0, 28.0), (4.0, 28.0), (16.0, 4.0), (16.0, 28.0), (4.0, 16.0), (28.0, 16.0)):
        pendant(R, x, y, LH + 3.4, H - 0.1, r=0.24)
    for (x, y) in ((A0 + 0.3, A0 + 0.3), (A1 - 0.3, A0 + 0.3), (A1 - 0.3, A1 - 0.3), (A0 + 0.3, A1 - 0.3)):
        R.light(sphere(x, y, LH + 1.3, 0.08, 8, 4, 'e_amber'))
