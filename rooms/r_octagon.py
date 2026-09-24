"""The Octagon: eight walls, eight arched niches of books, an eight-sided dome, and a great brass
lantern hanging on a long chain in the middle over an eight-pointed star."""
from lib import *
from kit_a import *

CX = CY = C / 2
A = 7.3                         # apothem: the cardinal walls
RC = A / math.cos(math.pi / 8)  # circumradius
ZS = 4.9
DH = 2.5


def make():
    R = Room('octagon', 1, 1, res=1024)
    R.sockets(floor='terrazzo', wall='tile')
    oct_pts = [(CX + RC * math.cos(math.pi / 8 + k * math.pi / 4), CY + RC * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    R.cut(poly_prism(oct_pts, 0, ZS + 0.01, side='tile', top='tile', bottom='terrazzo'))
    dome = sphere(0, 0, 0, RC, 8, 6, 'plaster', lower=False)
    dome.v = [(x, y, z * DH / RC) for x, y, z in dome.v]
    dome.xform(math.pi / 8, CX, CY, ZS)
    R.cut(dome)
    # a little lantern skylight at the crown
    R.cut(cyl(CX, CY, ZS + DH - 0.4, R.hi + 0.5, 0.75, 8, side='tile', top='tile', bottom='tile', a0=math.pi / 8, a1=math.pi / 8 + 2 * math.pi))
    R.light(cyl(CX, CY, R.hi - 0.08, R.hi - 0.05, 0.75, 8, side='e_sky', top='e_sky', bottom='e_sky', a0=math.pi / 8, a1=math.pi / 8 + 2 * math.pi))
    # ribs up the dome's eight hips, and a cornice where it springs
    for k in range(8):
        a = math.pi / 8 + k * math.pi / 4
        pts = []
        for i in range(7):
            e = (math.pi / 2) * i / 6 * 0.9
            r = (RC - 0.12) * math.cos(e)
            pts.append((CX + r * math.cos(a), CY + r * math.sin(a), ZS + (RC - 0.12) * math.sin(e) * DH / RC))
        for p, q in zip(pts, pts[1:]):
            R.nocol.add(beam(p, q, 0.3, 'gilt', 0.25))
        # engaged column in each corner
        x, y = CX + (RC - 0.2) * math.cos(a), CY + (RC - 0.2) * math.sin(a)
        R.nocol.add(cyl(x, y, 0.3, ZS - 0.45, 0.24, 12, side='tile', caps=False))
        R.nocol.add(cyl(x, y, 0, 0.3, 0.34, 12, side='tile', top='tile'))
        R.nocol.add(cyl(x, y, ZS - 0.45, ZS - 0.3, 0.34, 12, side='gilt', top='gilt', bottom='gilt'))
        R.col.add(box(x - 0.34, y - 0.34, 0, x + 0.34, y + 0.34, ZS - 0.3, 'tile'))
    inner = [(CX + (RC - 0.35) * math.cos(math.pi / 8 + k * math.pi / 4), CY + (RC - 0.35) * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    for k in range(8):
        p, q = oct_pts[k], oct_pts[(k + 1) % 8]
        pi, qi = inner[k], inner[(k + 1) % 8]
        R.parts.add(poly_prism([p, q, qi, pi], ZS - 0.3, ZS, side='tile', top='tile', bottom='tile'))
        R.light(poly_prism([(pi[0] * 0.98 + CX * 0.02, pi[1] * 0.98 + CY * 0.02), (qi[0] * 0.98 + CX * 0.02, qi[1] * 0.98 + CY * 0.02), qi, pi], ZS, ZS + 0.03, side='e_fluor', top='e_fluor', bottom='e_fluor'))
    # eight arched niches, two in each diagonal wall, each holding a bookcase and a lamp
    nw, nd, nz, nj = 2.2, 0.95, 0.0, 3.0
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        for off in (-1.5, 1.5):
            npr = arch_profile(off, nw, nz, nj, 20)
            R.cut(prism(npr, 'y', A - 0.05, A + nd, arch_mats(len(npr), 'terrazzo', 'damask'), cap='damask').xform(a - math.pi / 2, CX, CY))
            # gilt archivolt round the opening
            outer = arch_profile(off, nw + 0.36, nz, nj, 20)[2:]
            inn = arch_profile(off, nw + 0.02, nz, nj, 20)[2:]
            R.nocol.add(prism(outer + list(reversed(inn)), 'y', A - 0.1, A + 0.01, 'tile', cap='tile').xform(a - math.pi / 2, CX, CY))
            ux, uy = -math.sin(a), math.cos(a)
            bx, by = CX + math.cos(a) * (A + nd) + ux * off, CY + math.sin(a) * (A + nd) + uy * off
            ang_shelf(R, bx, by, a + math.pi, nw - 0.1, z=0.0, rows=7, frame='walnut', sides=False, back=False, crown=False)
            lx, ly = CX + math.cos(a) * (A + nd - 0.4) + ux * off, CY + math.sin(a) * (A + nd - 0.4) + uy * off
            R.nocol.add(cyl(lx, ly, nj + 0.6, nj + 1.1, 0.01, 6, side='brass', caps=False))
            R.light(sphere(lx, ly, nj + 0.5, 0.1, 8, 4, 'e_amber'))
    # the lantern, on a long chain from the crown
    lz0, lz1 = 3.0, 4.0
    R.nocol.add(cyl(CX, CY, lz1 + 0.35, R.hi - 0.3, 0.025, 6, side='iron', caps=False))
    for k in range(18):
        z = lz1 + 0.4 + k * 0.14
        if z > R.hi - 0.4: break
        R.nocol.add(box(CX - 0.05, CY - 0.012, z, CX + 0.05, CY + 0.012, z + 0.1, 'iron').xform(0, 0, 0, 0) if k % 2 else box(CX - 0.012, CY - 0.05, z, CX + 0.012, CY + 0.05, z + 0.1, 'iron'))
    R.light(cyl(CX, CY, lz0 + 0.05, lz1 - 0.05, 0.42, 8, side='e_lamp', top='e_lamp', bottom='e_lamp', a0=math.pi / 8, a1=math.pi / 8 + 2 * math.pi))
    for k in range(8):
        a = math.pi / 8 + k * math.pi / 4
        x, y = CX + 0.47 * math.cos(a), CY + 0.47 * math.sin(a)
        R.nocol.add(box(x - 0.03, y - 0.03, lz0, x + 0.03, y + 0.03, lz1, 'brass'))
    R.nocol.add(cyl(CX, CY, lz1, lz1 + 0.08, 0.56, 8, side='brass', top='brass', bottom='brass', a0=math.pi / 8, a1=math.pi / 8 + 2 * math.pi))
    R.nocol.add(cyl(CX, CY, lz1 + 0.08, lz1 + 0.3, 0.3, 8, side='brass', top='brass', bottom='brass', a0=math.pi / 8, a1=math.pi / 8 + 2 * math.pi))
    R.nocol.add(cyl(CX, CY, lz0 - 0.08, lz0, 0.56, 8, side='brass', top='brass', bottom='brass', a0=math.pi / 8, a1=math.pi / 8 + 2 * math.pi))
    R.nocol.add(cyl(CX, CY, lz0 - 0.4, lz0 - 0.08, 0.12, 8, side='brass', top='brass', bottom='brass'))
    # the star in the floor
    sr = 3.2
    sp = [(CX + sr * math.cos(k * math.pi / 4), CY + sr * math.sin(k * math.pi / 4)) for k in range(8)]
    for k in range(8):
        p, q = sp[k], sp[(k + 3) % 8]
        R.parts.add(obox(p[0], p[1], q[0], q[1], 0, 0.01, 0.07, 'brass'))
    R.parts.add(ring(CX, CY, 0, 0.01, sr, sr + 0.08, 48, top='brass', bottom='brass', inner='brass', outer='brass'))
    # four velvet benches on the diagonals, facing out toward the niches
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        R.parts.add(box(-0.9, -0.25, 0, 0.9, 0.25, 0.44, 'velvet', sides='walnut', skip=('-z',)).xform(a + math.pi / 2, CX + 4.4 * math.cos(a), CY + 4.4 * math.sin(a)))
        R.spot('sit', CX + 4.4 * math.cos(a), CY + 4.4 * math.sin(a), 0.44, a)
    ringp = [R.navpt(CX + 2.5 * math.cos(k * math.pi / 4 + math.pi / 8), CY + 2.5 * math.sin(k * math.pi / 4 + math.pi / 8)) for k in range(8)]
    R.link(*ringp, ringp[0])
    for k in range(4):
        d = R.navpt(CX + 5.8 * math.cos(k * math.pi / 2), CY + 5.8 * math.sin(k * math.pi / 2))
        R.link(d, ringp[(2 * k) % 8]); R.link(d, ringp[(2 * k + 7) % 8])
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        R.spot('read', CX + 6.3 * math.cos(a), CY + 6.3 * math.sin(a), 0, a)
    R.spot('probe', CX + 1.6, CY + 1.6, 1.7)
    R.meta.update(label='The Octagon', weight=7,
                  blurb='Eight walls, eight niches, eight ways the light falls. You count the doors twice and get a different answer each time.')
    R.meta['box'] = [[T, 0, T], [C - T, ZS + DH, C - T]]
    return tidy(R)
