"""The Well of Stairs: a wide round well through every floor. A stair winds round the inside of the wall,
one turn a floor, and at each floor it passes a ring landing where the doors are, with chairs, lamps and
desks in alcoves. Look over the parapet and the lamps in the middle go down and down to a point of light.
On the south-west of every landing one bookcase is not a bookcase: behind it, a cell with a bed."""
from kit_h7 import *

CX = CY = C / 2
RW = 7.2                      # the well's wall
RI, RM = 3.0, 4.7             # the stair from RI to RM; the landing ring from RM to the wall
TH0 = math.pi / 4             # where the stair meets each landing (north-east)
SEC = 5 * math.pi / 4         # the secret cell (south-west)


def make():
    R = Room('wellofstairs', 1, 1, res=1024, repeat=True, lo=-0.4)
    R.sockets(floor='floor', wall='tile')
    R.cut(cyl(CX, CY, -LH, 2 * LH, RW, 96, side='tile', top='tile', bottom='tile'))
    # the landing ring and the stair
    R.parts.add(ring(CX, CY, -0.35, 0.0, RM, RW + 0.05, 96, top='floor', bottom='plaster'))
    R.parts.add(ring(CX, CY, -1.25, -0.34, RM, RM + 0.2, 96, top='tile', bottom='tile', inner='tile', outer='tile'))
    R.parts.add(helix(CX, CY, RI, RM, 0.0, LH, TH0, TH0 + 2 * math.pi, 0.35, 128, top='oak', side='tile', bottom='plaster'))
    # a red runner up the middle of the stair, and brass stair-rods across it
    R.nocol.add(helix(CX, CY, RI + 0.45, RM - 0.3, 0.012, LH, TH0, TH0 + 2 * math.pi, 0.012, 128, top='carpet', side='carpet', bottom='carpet'))
    for k in range(1, 40):
        a = TH0 + 2 * math.pi * k / 40
        z = LH * k / 40
        p0 = (CX + (RI + 0.42) * math.cos(a), CY + (RI + 0.42) * math.sin(a))
        p1 = (CX + (RM - 0.27) * math.cos(a), CY + (RM - 0.27) * math.sin(a))
        R.nocol.add(obox(p0[0], p0[1], p1[0], p1[1], z + 0.005, z + 0.03, 0.03, 'brass'))
    # parapets: inside edge of the stair all the way; outside edge except where it meets a landing;
    # inside edge of the landing except at the meeting point
    ph, gap = 0.9, math.radians(28)
    R.parts.add(helix(CX, CY, RI, RI + 0.16, ph, LH, TH0, TH0 + 2 * math.pi, ph, 128, top='tile', side='tile', bottom='tile'))
    R.parts.add(helix(CX, CY, RM - 0.16, RM, ph + LH * gap / (2 * math.pi), LH, TH0 + gap, TH0 + 2 * math.pi - gap, ph, 110, top='tile', side='tile', bottom='tile'))
    R.parts.add(ring(CX, CY, 0.0, ph, RM, RM + 0.16, 80, top='tile', bottom='tile', inner='tile', outer='tile', a0=TH0 + gap, a1=TH0 + 2 * math.pi - gap))
    R.parts.add(helix(CX, CY, RI - 0.03, RI + 0.19, ph + 0.06, LH, TH0, TH0 + 2 * math.pi, 0.06, 128, top='brass', side='brass', bottom='brass'))
    R.parts.add(ring(CX, CY, ph, ph + 0.06, RM - 0.03, RM + 0.19, 80, top='brass', bottom='brass', inner='brass', outer='brass', a0=TH0 + gap, a1=TH0 + 2 * math.pi - gap))
    alcoves(R)
    shelves(R)
    cell(R)
    lights(R)
    pts = [R.navpt(CX + math.cos(k * math.pi / 4 + math.pi / 8) * 6.1, CY + math.sin(k * math.pi / 4 + math.pi / 8) * 6.1) for k in range(8)]
    R.link(*pts, pts[0])
    R.spot('probe', CX, CY, 3.5)
    R.meta['core'] = [CX, CY, RI]
    R.meta['ramp'] = [CX, CY, RI, RM, TH0, LH]
    R.meta.update(label='The Well of Stairs', weight=4,
                  blurb='A stair goes round and round the inside of a well, and every so often it passes a landing with chairs, as if it expected you to need a rest. Far below, the lamps shrink to a single point and do not stop.')
    R.meta['box'] = [[CX - RW, 0, CY - RW], [CX + RW, LH, CY + RW]]
    return tidy(R)


def dirv(a):
    return math.cos(a), math.sin(a)


def alcoves(R):
    """Arched reading alcoves cut into the thick corners (north-west, south-east): a desk, a lamp, a chair."""
    for a in (3 * math.pi / 4, 7 * math.pi / 4):
        dx, dy = dirv(a)
        px, py = -dy, dx
        r0, r1, hw = RW - 0.3, 9.05, 1.3
        pr = arch_profile(0, 2 * hw, 0, 2.2)
        g = prism(pr, 'y', r0, r1, arch_mats(len(pr), 'floor', 'tile'))
        # prism along y: turn it so +y points out along a
        g.xform(a - math.pi / 2, CX, CY, 0)
        R.cut(g)
        # the desk against the back of the alcove, facing the well
        bx, by = CX + dx * (r1 - 0.45), CY + dy * (r1 - 0.45)
        desk(R, bx, by, a + math.pi / 2, w=1.6, d=0.7)
        desk_lamp(R, bx - px * 0.5, by - py * 0.5, 0.78)
        book_pile(R, bx + px * 0.5, by + py * 0.5, 0.78, 4, seed=int(a * 10))
        open_book(R, bx - dx * 0.1, by - dy * 0.1, 0.78, a + math.pi / 2)
        cxh, cyh = CX + dx * (r1 - 1.25), CY + dy * (r1 - 1.25)
        R.parts.add(chair(cxh, cyh, a))
        R.spot('sit', cxh, cyh, 0.48, a)
        rc = (r0 + r1) / 2 + 0.1
        rx, ry = CX + dx * rc, CY + dy * rc
        L, Wd = r1 - r0 - 0.7, 2 * hw - 0.5
        rug(R, rx - L / 2, ry - Wd / 2, rx + L / 2, ry + Wd / 2, 0.0, ang=a, cx=rx, cy=ry)
        # books up the alcove's sides, facing in
        L = r1 - r0 - 0.5
        for s in (-1, 1):
            face = math.atan2(-s * py, -s * px)
            rr = r0 + 0.35 + (L if s > 0 else 0.0)
            ox, oy = CX + dx * rr + s * px * hw, CY + dy * rr + s * py * hw
            R.shelf(ox, oy, 0, L, face, rows=5, frame='walnut')


def shelves(R):
    """Bookcases round the wall in straight runs between the doors; the one on the south-west is false."""
    for q in range(4):
        for off in (27, 45, 63):
            a = math.radians(q * 90 + off)
            if off == 45 and q in (1, 3): continue          # the alcoves
            half = 1.2 if off == 45 else 1.0
            bx, by = CX + math.cos(a) * (RW - 0.06), CY + math.sin(a) * (RW - 0.06)
            fa = a + math.pi
            ux, uy = math.sin(fa), -math.cos(fa)
            solid = not (q == 2 and off == 45)
            R.shelf(bx - ux * half, by - uy * half, 0, 2 * half, fa, rows=10 if off == 45 else 8, frame='walnut', back=True, solid=solid)
    # chairs and little tables on the landings, between the cases and the parapet
    for (a, kind) in ((math.radians(112), 'arm'), (math.radians(158), 'arm'), (math.radians(292), 'arm'), (math.radians(338), 'arm'),
                      (math.radians(200), 'chair'), (math.radians(250), 'chair')):
        x, y = CX + 6.4 * math.cos(a), CY + 6.4 * math.sin(a)
        if kind == 'arm':
            armchair(R, x, y, a + math.pi, m='velvet')
        else:
            R.parts.add(chair(x, y, a + math.pi))
            R.spot('sit', x, y, 0.48, a + math.pi)
    for a in (math.radians(103), math.radians(283), math.radians(167) - 0.18, math.radians(347) - 0.18):
        x, y = CX + 6.5 * math.cos(a + 0.18), CY + 6.5 * math.sin(a + 0.18)
        R.parts.add(cyl(x, y, 0, 0.62, 0.05, 8, side='walnut', caps=False))
        R.parts.add(cyl(x, y, 0.6, 0.65, 0.3, 16, side='walnut', top='walnut'))
        R.parts.add(cyl(x, y, 0, 0.04, 0.2, 10, side='walnut', top='walnut'))
        book_pile(R, x, y, 0.65, 3, seed=int(a * 7))
        R.light(sphere(x + 0.1, y, 0.72, 0.05, 6, 3, 'e_candle'))


def cell(R):
    """Behind the false case on the south-west: a low door and a cell in the corner with a bed."""
    dx, dy = dirv(SEC)
    x0, y0, x1, y1 = T + 0.05, T + 0.05, 2.62, 2.62
    CH = 2.3
    R.cut(box(x0, y0, 0, x1, y1, CH, 'plaster', bottom='floor', top='plaster'))
    # the passage from behind the case, through the wall
    a0 = (CX + dx * (RW - 0.25), CY + dy * (RW - 0.25))
    a1 = (x1 - 0.5, y1 - 0.5)
    R.cut(obox(a0[0], a0[1], a1[0], a1[1], 0, 1.5, 0.9, 'plaster', bottom='floor', top='oak'))
    # inside: a bed, a shelf, a candle, a chair, a plaque
    R.parts.add(box(x0 + 0.02, y0 + 0.02, 0, x0 + 0.95, y0 + 2.0, 0.42, 'bed', sides='walnut'))
    R.parts.add(box(x0 + 0.02, y0 + 0.02, 0.42, x0 + 0.95, y0 + 0.08, 0.95, 'walnut'))
    R.nocol.add(box(x0 + 0.12, y0 + 0.15, 0.42, x0 + 0.85, y0 + 0.55, 0.52, 'ivory'))
    R.spot('bed', x0 + 0.5, y0 + 1.0, 0.42, math.pi / 2)
    R.shelf(x1 - 0.02, y0 + 0.02, 0.0, 1.2, '+y', rows=4, frame='walnut', depth=0.28)
    R.parts.add(box(x1 - 0.45, y0 + 1.35, 0, x1 - 0.02, y0 + 1.95, 0.7, 'walnut'))
    candle(R, x1 - 0.25, y0 + 1.55, 0.7, h=0.18)
    book_pile(R, x1 - 0.25, y0 + 1.8, 0.7, 3, seed=5)
    R.light(sphere(x0 + 1.5, y0 + 1.2, CH - 0.35, 0.07, 8, 4, 'e_dim'))
    R.nocol.add(cyl(x0 + 1.5, y0 + 1.2, CH - 0.3, CH, 0.008, 4, side='iron', caps=False))
    R.spot('plaque', x0 + 1.2, y0 + 0.02, 1.4, math.pi / 2, text='REST HERE. THE STAIR WILL STILL BE THERE.')
    secret(R, x0 + 1.4, y0 + 1.3, 0.0, 'The Cell in the Wall',
           'Behind the bookcase, a low door, and a cell just big enough for a bed. Someone lived here long enough to wear a hollow in the pillow, and left the candle for you.', r=1.2)


def lights(R):
    # a glowing ring under each landing, sconces on the wall, and the lamps down the middle
    R.light(ring(CX, CY, -0.4, -0.37, RW - 0.35, RW - 0.12, 96, top='e_panel', bottom='e_panel', inner='e_panel', outer='e_panel'))
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        if abs(((a - 3 * math.pi / 4 + math.pi) % (2 * math.pi)) - math.pi) < 0.3: continue
        x, y = CX + (RW - 0.05) * math.cos(a), CY + (RW - 0.05) * math.sin(a)
        sconce_(R, x, y, 5.0, a + math.pi)
    # the lamp down the middle: one per floor, on a chain, so looking down they shrink to a point
    chain(R, CX, CY, 3.9, LH + 0.0, link=0.3, w=0.03)
    R.nocol.add(cyl(CX, CY, 3.55, 3.62, 0.34, 16, side='brass', top='brass', bottom='brass'))
    for k in range(6):
        a = k * math.pi / 3
        R.nocol.add(beam((CX, CY, 3.9), (CX + 0.33 * math.cos(a), CY + 0.33 * math.sin(a), 3.6), 0.02, 'brass'))
        R.light(sphere(CX + 0.33 * math.cos(a), CY + 0.33 * math.sin(a), 3.72, 0.07, 8, 4, 'e_lamp'))
    R.light(sphere(CX, CY, 3.35, 0.2, 12, 6, 'e_lamp'))
    # night lamps on the parapet by the meeting point
    for a in (TH0 + math.radians(30), TH0 - math.radians(30)):
        x, y = CX + (RM + 0.08) * math.cos(a), CY + (RM + 0.08) * math.sin(a)
        R.light(cyl(x, y, 0.96, 1.18, 0.07, 10, side='e_amber', top='e_amber', bottom='e_amber'))


def sconce_(R, x, y, z, face):
    dx, dy = math.cos(face), math.sin(face)
    R.nocol.add(beam((x, y, z - 0.2), (x + dx * 0.35, y + dy * 0.35, z - 0.05), 0.035, 'brass'))
    R.nocol.add(box(x - 0.08, y - 0.08, z - 0.35, x + 0.08, y + 0.08, z - 0.05, 'brass'))
    R.nocol.add(frustum(x + dx * 0.38, y + dy * 0.38, z - 0.02, z + 0.2, 0.17, 0.07, 10, 'green', inner='ivory'))
    R.light(cyl(x + dx * 0.38, y + dy * 0.38, z, z + 0.04, 0.1, 8, side='e_lamp', top='e_lamp', bottom='e_lamp'))
