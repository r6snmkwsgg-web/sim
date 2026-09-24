"""The Rotunda: a round room of books under a coffered dome, open at the top to a painted sky.
A ring of low bookcases circles a round table in the pool of light from the oculus."""
from lib import *
from kit_a import *

CX = CY = C / 2
RR = 7.3          # radius of the drum
ZS = 4.3          # where the dome springs
DH = 3.1          # dome height (it is squashed)


def dome_pt(e, a, r=RR):
    return (CX + r * math.cos(e) * math.cos(a), CY + r * math.cos(e) * math.sin(a), ZS + DH * (r / RR) * math.sin(e))


def make():
    R = Room('rotunda', 1, 1, res=1024)
    R.sockets(floor='terrazzo', wall='tile')
    R.cut(cyl(CX, CY, 0, ZS + 0.01, RR, 32, side='tile', bottom='terrazzo', top='tile'))
    dome = sphere(CX, CY, ZS, RR, 32, 10, 'plaster', lower=False)
    dome.v = [(x, y, ZS + (z - ZS) * DH / RR) for x, y, z in dome.v]
    R.cut(dome)
    ro = 1.05
    R.cut(cyl(CX, CY, ZS + DH - 0.6, R.hi + 0.5, ro, 40, side='tile', top='tile', bottom='tile'))
    R.light(cyl(CX, CY, R.hi - 0.08, R.hi - 0.05, ro, 40, side='e_sky', top='e_sky', bottom='e_sky'))
    R.parts.add(ring(CX, CY, ZS + DH - 0.62, ZS + DH - 0.5, ro, ro + 0.25, 40, top='gilt', bottom='gilt', inner='gilt', outer='gilt'))
    # coffers: rings of ribs and meridian ribs, just inside the dome
    es = [0.0, 0.36, 0.72, 1.08]
    for e in es[1:]:
        p = dome_pt(e, 0)
        r = math.hypot(p[0] - CX, p[1] - CY)
        R.nocol.add(ring(CX, CY, p[2] - 0.08, p[2] + 0.06, r - 0.32, r + 0.1, 24, top='tile', bottom='tile', inner='tile', outer='tile'))
    for k in range(16):
        a = 2 * math.pi * k / 16
        pts = [dome_pt(e, a, RR - 0.16) for e in [es[0] + (es[-1] - es[0]) * t / 4 for t in range(5)]]
        for p, q in zip(pts, pts[1:]):
            R.nocol.add(beam(p, q, 0.22, 'tile', 0.26))
    # cornice at the spring, with a cove light washing up the dome
    R.nocol.add(ring(CX, CY, ZS - 0.35, ZS, RR - 0.3, RR + 0.02, 32, top='tile', bottom='tile', inner='tile', outer='tile'))
    R.light(ring(CX, CY, ZS, ZS + 0.03, RR - 0.26, RR - 0.18, 32, top='e_fluor', bottom='e_fluor', inner='e_fluor', outer='e_fluor'))
    # tall bookcases following the drum wall, between the doors
    for q in range(4):
        base = q * math.pi / 2
        n = 2
        a0, a1 = base + math.radians(21), base + math.radians(69)
        for i in range(n):
            a = a0 + (a1 - a0) * (i + 0.5) / n
            L = 2 * (RR - 0.02) * math.sin((a1 - a0) / n / 2) - 0.05
            rr = (RR - 0.02) * math.cos((a1 - a0) / n / 2)
            ang_shelf(R, CX + rr * math.cos(a), CY + rr * math.sin(a), a + math.pi, L, rows=8, frame='walnut')
    # the inner ring: low double-faced cases, gaps on the four door axes
    ri = 4.2
    for q in range(4):
        base = q * math.pi / 2
        a0, a1 = base + math.radians(18), base + math.radians(72)
        n = 2
        for i in range(n):
            a = a0 + (a1 - a0) * (i + 0.5) / n
            L = 2 * ri * math.sin((a1 - a0) / n / 2) - 0.03
            ang_shelf(R, CX + (ri + 0.01) * math.cos(a), CY + (ri + 0.01) * math.sin(a), a, L, rows=3, frame='walnut', crown=False, sides=False)
            ang_shelf(R, CX + (ri - 0.01) * math.cos(a), CY + (ri - 0.01) * math.sin(a), a + math.pi, L * (ri - 0.36) / ri, rows=3, frame='walnut', crown=False, sides=False)
        R.nocol.add(ring(CX, CY, 1.34, 1.4, ri - 0.4, ri + 0.4, 8, top='oak', bottom='oak', inner='oak', outer='oak', a0=a0, a1=a1))
        # a night lamp on the end of each arc
        for a in (a0, a1):
            x, y = CX + ri * math.cos(a), CY + ri * math.sin(a)
            R.parts.add(cyl(x, y, 1.4, 1.46, 0.07, 10, side='brass', top='brass'))
            R.light(sphere(x, y, 1.56, 0.09, 8, 4, 'e_amber'))
    # the round table in the middle, lamps on it
    R.nocol.add(cyl(CX, CY, 0.72, 0.78, 1.3, 32, side='walnut', top='leather', bottom='walnut'))
    R.col.add(cyl(CX, CY, 0.0, 0.78, 1.3, 8, side='tile', top='tile', bottom='tile'))
    R.parts.add(cyl(CX, CY, 0.0, 0.72, 0.28, 16, side='walnut', top='walnut'))
    R.parts.add(cyl(CX, CY, 0.0, 0.06, 0.7, 24, side='walnut', top='walnut', bottom='walnut'))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        desk_lamp(R, CX + 0.85 * math.cos(a), CY + 0.85 * math.sin(a), 0.78)
        R.nocol.add(chair(CX + 1.75 * math.cos(a), CY + 1.75 * math.sin(a), a + math.pi))
        R.col.add(box(-0.26, -0.25, 0, 0.25, 0.25, 0.48, 'tile').xform(a + math.pi, CX + 1.75 * math.cos(a), CY + 1.75 * math.sin(a)))
        R.spot('sit', CX + 1.75 * math.cos(a), CY + 1.75 * math.sin(a), 0.48, a + math.pi)
    # a compass in the floor
    for k in range(8):
        a = k * math.pi / 4
        L = 2.9 if k % 2 == 0 else 2.2
        R.nocol.add(obox(CX + 1.35 * math.cos(a), CY + 1.35 * math.sin(a), CX + L * math.cos(a), CY + L * math.sin(a), 0, 0.012, 0.12, 'brass'))
    R.nocol.add(ring(CX, CY, 0, 0.012, 3.0, 3.1, 32, top='brass', bottom='brass', inner='brass', outer='brass'))
    outer = [R.navpt(CX + 5.7 * math.cos(k * math.pi / 4 + math.pi / 8), CY + 5.7 * math.sin(k * math.pi / 4 + math.pi / 8)) for k in range(8)]
    R.link(*outer, outer[0])
    inner = [R.navpt(CX + 2.6 * math.cos(k * math.pi / 2), CY + 2.6 * math.sin(k * math.pi / 2)) for k in range(4)]
    R.link(*inner, inner[0])
    for k in range(4):
        d = R.navpt(CX + 5.9 * math.cos(k * math.pi / 2), CY + 5.9 * math.sin(k * math.pi / 2))
        R.link(d, inner[k]); R.link(d, outer[(2 * k) % 8]); R.link(d, outer[(2 * k + 7) % 8])
    R.spot('probe', CX + 2.4, CY + 2.4, 1.7)
    R.meta.update(label='The Rotunda', weight=7,
                  blurb='A drum of books under a dome, and a circle of sky at the top that never changes. Everything here faces the middle, including you.')
    R.meta['box'] = [[T, 0, T], [C - T, ZS + DH, C - T]]
    return tidy(R)
