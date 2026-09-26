"""Room generator for the Dreaming Library.

Rooms are modelled in Blender (Z up, metres), their lighting is baked with
Cycles into a lightmap, denoised with OIDN, and exported as JSON (the meshes
packed in as base64) that the game streams in. One room occupies w x d cells (16 m) and
one or more levels (8 m). Every cell edge on every level has the same arched
opening, so any room can sit next to any other.

Run a room script with:  python3 rooms/build.py <name> [--quick]
"""
import bpy, bmesh, math, json, os, time, struct, subprocess, sys, base64
import numpy as np
from mathutils import Vector

C = 16.0       # cell size
LH = 8.0       # level height
T = 0.35       # wall thickness inside the cell boundary
DW = 3.0       # door width
DJ = 2.6       # height where the door arch springs
DR = DW / 2    # door arch radius
TOP = 7.6      # highest ceiling inside one level (next floor slab above)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')          # raw bakes; pack.py turns them into game/rooms/
OIDN = os.environ.get('OIDN', '/tmp/oidn-2.3.3.x86_64.linux/bin/oidnDenoise')

# Albedo is what the bake bounces; the game draws the detail (tiles, grout, grain).
MATS = {
    'tile':      (0.80, 0.80, 0.76),   # glazed white wall tile, 15 cm
    'floor':     (0.74, 0.73, 0.70),   # floor tile, 30 cm
    'mosaic':    (0.34, 0.66, 0.72),   # pool mosaic, 2.5 cm
    'pink':      (0.86, 0.60, 0.56),
    'mint':      (0.58, 0.80, 0.70),
    'cobalt':    (0.16, 0.30, 0.62),
    'plaster':   (0.82, 0.76, 0.66),
    'terrazzo':  (0.72, 0.70, 0.66),
    'paper':     (0.74, 0.64, 0.34),   # yellow wallpaper
    'carpet':    (0.34, 0.09, 0.08),   # deep red
    'ceiltile':  (0.78, 0.76, 0.68),
    'wood':      (0.36, 0.22, 0.13),
    'oak':       (0.62, 0.46, 0.30),
    'paint':     (0.82, 0.82, 0.80),   # painted shelving
    'brass':     (0.78, 0.58, 0.28),
    'chrome':    (0.70, 0.72, 0.74),
    'books':     (0.24, 0.17, 0.13),   # the average book
    'black':     (0.03, 0.03, 0.03),
    'bed':       (0.82, 0.80, 0.74),
    'kiosk':     (0.30, 0.34, 0.36),
    # the library palette
    'stone':     (0.66, 0.60, 0.50),   # warm limestone, laid in courses
    'parquet':   (0.29, 0.19, 0.12),   # dark oak planks
    'marble':    (0.47, 0.45, 0.40),   # cream and near-black checker, polished
    'green':     (0.14, 0.26, 0.20),   # library green paint
    'oxblood':   (0.36, 0.11, 0.09),
    'damask':    (0.17, 0.24, 0.17),   # dark green patterned wallpaper
    'iron':      (0.13, 0.13, 0.14),   # dark metal: railings, cages, spiral stairs
    'bronze':    (0.55, 0.36, 0.18),
    'gilt':      (0.80, 0.62, 0.30),
    'velvet':    (0.30, 0.05, 0.06),   # curtains, cushions
    'slate':     (0.22, 0.23, 0.25),   # dark stone
    'blackboard':(0.08, 0.12, 0.10),
    'leather':   (0.30, 0.16, 0.09),
    'ivory':     (0.85, 0.82, 0.74),   # cream paint
    'walnut':    (0.20, 0.12, 0.07),   # very dark wood
}
# The rooms were first drawn in pool tile; the library wears these instead.
THEME = {'tile': 'stone', 'floor': 'parquet', 'terrazzo': 'marble', 'mosaic': 'marble', 'cobalt': 'marble',
         'mint': 'green', 'pink': 'oxblood', 'paper': 'damask', 'ceiltile': 'plaster', 'paint': 'wood'}
# Emitters: colour and strength (W/m^2-ish in Cycles emission units). Not baked; drawn glowing.
EMIT = {
    'e_sky':   ((1.00, 0.91, 0.76), 14.0),   # skylight / oculus: warm, like late afternoon
    'e_panel': ((1.00, 0.88, 0.70), 10.0),   # ceiling light panel
    'e_lamp':  ((1.00, 0.84, 0.62), 16.0),   # warm lamp
    'e_fluor': ((1.00, 0.82, 0.58), 9.0),    # low lamps in the labyrinth
    'e_pool':  ((1.00, 0.64, 0.32), 12.0),   # step lights in the sunken floors
    'e_amber': ((1.00, 0.55, 0.20), 6.0),    # night lamp
    'e_kiosk': ((0.85, 0.95, 1.00), 5.0),
    'e_portal': ((0.92, 0.92, 0.90), 1.0),   # stands in for the next room's light
    'e_red':   ((1.00, 0.25, 0.16), 6.0),    # stained glass
    'e_blue':  ((0.30, 0.50, 1.00), 6.0),
    'e_green': ((0.35, 1.00, 0.50), 5.0),
    'e_candle': ((1.00, 0.58, 0.24), 5.0),   # candles and night-lights: stay lit after lights-out
    'e_dim':   ((1.00, 0.80, 0.60), 2.5),    # weak bulbs, for the dark rooms
    'e_exit':  ((0.35, 1.00, 0.45), 4.0),    # little green signs over doors that go nowhere
    'e_skydome': ((0.75, 0.85, 1.00), 3.0),  # a painted sky (the game draws clouds and stars on it)
}
NIGHT_ON = {'e_pool', 'e_amber', 'e_kiosk', 'e_portal', 'e_candle', 'e_exit'}   # what stays lit after lights-out


# ---------------------------------------------------------------------------
# Scene and materials
# ---------------------------------------------------------------------------
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.max_bounces = 5
    sc.cycles.diffuse_bounces = 4
    sc.cycles.glossy_bounces = 0
    sc.cycles.transmission_bounces = 0
    sc.cycles.transparent_max_bounces = 0
    sc.cycles.use_light_tree = True
    w = bpy.data.worlds.new('W'); sc.world = w
    bg = w.node_tree.nodes.get('Background')
    if bg: bg.inputs[0].default_value = (0, 0, 0, 1); bg.inputs[1].default_value = 0
    return sc


_mat_cache = {}
def mat(name):
    m = _mat_cache.get(name)
    if m and m.name in bpy.data.materials: return m
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    b = nt.nodes.get('Principled BSDF')
    if name in EMIT:
        col, s = EMIT[name]
        b.inputs['Base Color'].default_value = (0, 0, 0, 1)
        b.inputs['Emission Color'].default_value = (*col, 1)
        b.inputs['Emission Strength'].default_value = s
    else:
        b.inputs['Base Color'].default_value = (*MATS[name], 1)
    b.inputs['Roughness'].default_value = 1.0
    for k in ('Specular IOR Level', 'Specular'):
        if k in b.inputs: b.inputs[k].default_value = 0.0; break
    _mat_cache[name] = m
    return m


def coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c


# ---------------------------------------------------------------------------
# Mesh building. Every primitive carries UV0 in metres (for tiles) and a
# material name per face. Solids are closed; their winding is fixed by volume.
# ---------------------------------------------------------------------------
class Geo:
    def __init__(self):
        self.v = []; self.f = []; self.m = []; self.uv = []

    def vert(self, p):
        self.v.append(tuple(float(c) for c in p)); return len(self.v) - 1

    def face(self, idx, m, uvs):
        self.f.append(tuple(idx)); self.m.append(THEME.get(m, m)); self.uv.append([tuple(u) for u in uvs])

    def fix(self):
        """Make a closed primitive face outward (reverse every face if its signed volume is negative)."""
        vol = 0.0
        for f in self.f:
            p0 = self.v[f[0]]
            for k in range(1, len(f) - 1):
                a, b = self.v[f[k]], self.v[f[k + 1]]
                vol += (p0[0] * (a[1] * b[2] - a[2] * b[1]) - p0[1] * (a[0] * b[2] - a[2] * b[0]) + p0[2] * (a[0] * b[1] - a[1] * b[0]))
        if vol < 0:
            self.f = [tuple(reversed(f)) for f in self.f]; self.uv = [list(reversed(u)) for u in self.uv]
        return self

    def xform(self, ang=0.0, tx=0.0, ty=0.0, tz=0.0):
        """Rotate about Z (radians) around the origin, then translate. UV0 stays in the local frame."""
        c, s = math.cos(ang), math.sin(ang)
        self.v = [(x * c - y * s + tx, x * s + y * c + ty, z + tz) for x, y, z in self.v]
        return self

    def add(self, g, dx=0, dy=0, dz=0):
        o = len(self.v)
        self.v += [(a + dx, b + dy, c + dz) for a, b, c in g.v]
        self.f += [tuple(i + o for i in f) for f in g.f]
        self.m += g.m; self.uv += g.uv
        return self

    def obj(self, name, collection, fix=True):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.v, [], self.f)
        uvl = me.uv_layers.new(name='UV0')
        names = []
        for n in self.m:
            if n not in names: names.append(n)
        for n in names: me.materials.append(mat(n))
        for fi, p in enumerate(me.polygons):
            p.material_index = names.index(self.m[fi])
            for k, li in enumerate(p.loop_indices):
                uvl.data[li].uv = self.uv[fi][k]
        ob = bpy.data.objects.new(name, me); collection.objects.link(ob)
        if fix:
            bm = bmesh.new(); bm.from_mesh(me)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
            bm.to_mesh(me); bm.free()
        return ob


def _boxuv(p, n):
    ax = max(range(3), key=lambda i: abs(n[i]))
    if ax == 2: return (p[0], p[1])
    if ax == 1: return (p[0], p[2])
    return (p[1], p[2])


def box(x0, y0, z0, x1, y1, z1, m='tile', top=None, bottom=None, sides=None, skip=()):
    """Axis-aligned box. skip: faces to leave out ('-x','+x','-y','+y','-z','+z') for open parts."""
    g = Geo()
    P = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    ids = [g.vert(p) for p in P]
    F = [((0, 3, 2, 1), '-z', (0, 0, -1)), ((4, 5, 6, 7), '+z', (0, 0, 1)), ((0, 1, 5, 4), '-y', (0, -1, 0)),
         ((1, 2, 6, 5), '+x', (1, 0, 0)), ((2, 3, 7, 6), '+y', (0, 1, 0)), ((3, 0, 4, 7), '-x', (-1, 0, 0))]
    for f, key, n in F:
        if key in skip: continue
        mm = (top if key == '+z' else bottom if key == '-z' else sides) or m
        g.face([ids[i] for i in f], mm, [_boxuv(P[i], n) for i in f])
    return g


def prism(profile, axis, a0, a1, edge_mats, cap='tile'):
    """Extrude a closed 2D profile [(p, q), ...] along axis 'x' or 'y' (q is always Z).
    Side faces get UV0 = (arc length round the profile, distance along the axis)."""
    g = Geo()
    def P(p, q, a):
        return (a, p, q) if axis == 'x' else (p, a, q)
    n = len(profile)
    r0 = [g.vert(P(p, q, a0)) for p, q in profile]
    r1 = [g.vert(P(p, q, a1)) for p, q in profile]
    s = [0.0]
    for i in range(n):
        p, q = profile[i]; p2, q2 = profile[(i + 1) % n]
        s.append(s[-1] + math.hypot(p2 - p, q2 - q))
    for i in range(n):
        j = (i + 1) % n
        mm = edge_mats[i] if isinstance(edge_mats, (list, tuple)) else edge_mats
        g.face([r0[i], r0[j], r1[j], r1[i]], mm, [(s[i], a0), (s[i + 1], a0), (s[i + 1], a1), (s[i], a1)])
    g.face(list(reversed(r0)), cap, [profile[i] for i in reversed(range(n))])
    g.face(r1, cap, list(profile))
    return g.fix()


def arch_profile(c, w, z0, jamb, segs=18, rise=None):
    """Rectangle with a round (or segmental, if rise < w/2) arch on top."""
    r = w / 2
    pts = [(c - r, z0), (c + r, z0), (c + r, z0 + jamb)]
    if rise is None or rise >= r - 1e-6:
        for k in range(1, segs):
            t = math.pi * k / segs
            pts.append((c + r * math.cos(t), z0 + jamb + r * math.sin(t)))
    else:   # segmental arch through the two springing points and the crown
        R = (r * r + rise * rise) / (2 * rise); cy = z0 + jamb + rise - R; a = math.asin(r / R)
        for k in range(1, segs):
            t = math.pi / 2 - a + 2 * a * k / segs
            pts.append((c + R * math.cos(t), cy + R * math.sin(t)))
    pts.append((c - r, z0 + jamb))
    return pts


def arch_mats(n, floor='floor', wall='tile'):
    return [floor] + [wall] * (n - 1)


def cyl(cx, cy, z0, z1, r, segs=32, side='tile', top='tile', bottom='tile', caps=True, a0=0.0, a1=2 * math.pi):
    """Vertical cylinder (or sector). UV0 on the side = (angle * r, z)."""
    g = Geo()
    full = abs(a1 - a0 - 2 * math.pi) < 1e-6
    n = segs if full else segs + 1
    ang = [a0 + (a1 - a0) * k / segs for k in range(n)]
    b = [g.vert((cx + r * math.cos(a), cy + r * math.sin(a), z0)) for a in ang]
    t = [g.vert((cx + r * math.cos(a), cy + r * math.sin(a), z1)) for a in ang]
    L = segs if full else segs
    for k in range(L):
        j = (k + 1) % n
        u0, u1 = ang[k] * r, (ang[k] + (a1 - a0) / segs) * r
        g.face([b[k], b[j], t[j], t[k]], side, [(u0, z0), (u1, z0), (u1, z1), (u0, z1)])
    if not full:
        c0 = g.vert((cx, cy, z0)); c1 = g.vert((cx, cy, z1))
        g.face([b[0], t[0], c1, c0], side, [(0, z0), (r, z0), (r, z1), (0, z1)])
        g.face([b[-1], c0, c1, t[-1]], side, [(0, z0), (r, z0), (r, z1), (0, z1)])
        if caps:
            g.face([c0] + list(reversed(b)), bottom, [(cx, cy)] + [(g.v[i][0], g.v[i][1]) for i in reversed(b)])
            g.face([c1] + t, top, [(cx, cy)] + [(g.v[i][0], g.v[i][1]) for i in t])
    elif caps:
        g.face(list(reversed(b)), bottom, [(g.v[i][0], g.v[i][1]) for i in reversed(b)])
        g.face(t, top, [(g.v[i][0], g.v[i][1]) for i in t])
    return g.fix() if caps else g


def sphere(cx, cy, cz, r, segs=32, rings=16, m='tile', lower=True):
    """Closed sphere (or upper hemisphere closed at the equator if lower=False).
    UV0 = (azimuth * r, elevation * r): tiles run in rings, as on a real tiled dome."""
    g = Geo()
    e0 = -math.pi / 2 if lower else 0.0
    R = []
    for i in range(rings + 1):
        e = e0 + (math.pi / 2 - e0) * i / rings
        if i == rings:
            R.append([g.vert((cx, cy, cz + r))]); continue
        R.append([g.vert((cx + r * math.cos(e) * math.cos(a), cy + r * math.cos(e) * math.sin(a), cz + r * math.sin(e)))
                  for a in [2 * math.pi * k / segs for k in range(segs)]])
    el = [e0 + (math.pi / 2 - e0) * i / rings for i in range(rings + 1)]
    for i in range(rings):
        for k in range(segs):
            j = (k + 1) % segs
            ua, ub = 2 * math.pi * k / segs * r, 2 * math.pi * (k + 1) / segs * r
            va, vb = el[i] * r, el[i + 1] * r
            if i + 1 == rings:
                g.face([R[i][k], R[i][j], R[i + 1][0]], m, [(ua, va), (ub, va), ((ua + ub) / 2, vb)])
            else:
                g.face([R[i][k], R[i][j], R[i + 1][j], R[i + 1][k]], m, [(ua, va), (ub, va), (ub, vb), (ua, vb)])
    if not lower:
        ring = R[0]
        g.face(list(reversed(ring)), m, [(g.v[i][0], g.v[i][1]) for i in reversed(ring)])
    return g.fix()


def poly_prism(pts, z0, z1, side='tile', top='tile', bottom='tile'):
    """Vertical prism from a closed 2D polygon (x, y)."""
    g = Geo(); n = len(pts)
    b = [g.vert((x, y, z0)) for x, y in pts]; t = [g.vert((x, y, z1)) for x, y in pts]
    s = 0.0
    for i in range(n):
        j = (i + 1) % n
        L = math.hypot(pts[j][0] - pts[i][0], pts[j][1] - pts[i][1])
        g.face([b[i], b[j], t[j], t[i]], side, [(s, z0), (s + L, z0), (s + L, z1), (s, z1)]); s += L
    g.face(list(reversed(b)), bottom, [pts[i] for i in reversed(range(n))])
    g.face(t, top, list(pts))
    return g.fix()


def slope_box(x0, x1, y0, y1, bot0, bot1, top0, top1, m, cap=None):
    """A box along X whose bottom and top rise linearly from x0 to x1 (parapets and rails beside a stair)."""
    g = Geo()
    ids = [g.vert(p) for p in ((x0, y0, bot0), (x1, y0, bot1), (x1, y1, bot1), (x0, y1, bot0),
                               (x0, y0, top0), (x1, y0, top1), (x1, y1, top1), (x0, y1, top0))]
    for f, mm, uv in (((0, 3, 2, 1), m, [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]),
                      ((4, 5, 6, 7), cap or m, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]),
                      ((0, 1, 5, 4), m, [(x0, bot0), (x1, bot1), (x1, top1), (x0, top0)]),
                      ((1, 2, 6, 5), m, [(y0, bot1), (y1, bot1), (y1, top1), (y0, top1)]),
                      ((2, 3, 7, 6), m, [(x1, bot1), (x0, bot0), (x0, top0), (x1, top1)]),
                      ((3, 0, 4, 7), m, [(y1, bot0), (y0, bot0), (y0, top0), (y1, top0)])):
        g.face([ids[i] for i in f], mm, uv)
    return g.fix()


def balustrade(x0, y0, x1, y1, z=0.0, h=1.0, m='tile', cap='brass'):
    """An axis-aligned solid balustrade (x0..x1, y0..y1 is its footprint, ~0.2 m thick) with a rail on top."""
    g = box(x0, y0, z, x1, y1, z + h, m, skip=('-z',))
    g.add(box(x0 - 0.03, y0 - 0.03, z + h, x1 + 0.03, y1 + 0.03, z + h + 0.06, cap))
    return g


def stairs(x0, y0, z0, width, n, rise, run, axis='+y', m='floor', riser=None, side='tile'):
    """Solid flight of n steps climbing along axis from (x0, y0, z0); width across.
    One closed prism with a sawtooth profile, so there are no coplanar faces to fight in the bake."""
    L = n * run
    prof = [(0.0, 0.0), (L, 0.0), (L, n * rise)]
    for i in range(n - 1, -1, -1):
        prof.append((i * run, (i + 1) * rise))
        if i > 0: prof.append((i * run, i * rise))
    mats = [side, side] + [m if k % 2 == 0 else (riser or side) for k in range(len(prof) - 2)]
    sgn = 1 if axis[0] == '+' else -1
    if axis[1] == 'x':
        pr = [(x0 + sgn * s, z0 + z) for s, z in prof]
        return prism(pr, 'y', y0, y0 + width, mats, cap=side)
    pr = [(y0 + sgn * s, z0 + z) for s, z in prof]
    return prism(pr, 'x', x0, x0 + width, mats, cap=side)


# ---------------------------------------------------------------------------
# The room being built
# ---------------------------------------------------------------------------
class Room:
    def __init__(self, name, w=1, d=1, levels=1, repeat=False, res=1024, lo=-2.0):
        self.name, self.w, self.d, self.levels, self.repeat, self.res = name, w, d, levels, repeat, res
        self.W, self.D = w * C, d * C
        self.lo = lo                       # bottom of the solid block (pools dig down into it)
        self.hi = levels * LH - (LH - TOP) # top of the solid block
        self.base = Geo(); self.cuts = []; self.parts = Geo(); self.late = Geo(); self.emit = Geo()
        self.nocol = Geo()                 # drawn, baked, but not collided with (e.g. stair treads)
        self.col = Geo()                   # invisible colliders (ramps over stairs, rail walls)
        self.slabs = []; self.water = []; self.spots = []; self.nav = []; self.navlinks = []; self.meta = {}
        self.portals = []
        self.movers = []                   # moving parts: see mover()
        self.levels_open = set(range(levels))
        self.base.add(box(0, 0, lo, self.W, self.D, self.hi, 'tile'))

    # --- moving parts ----------------------------------------------------------
    def mover(self, type='spin', pivot=(0.0, 0.0, 0.0), axis='z', speed=0.2, amp=0.5, period=8.0, delta=(0.0, 0.0, 0.0), pause=0.0, phase=0.0):
        """A part of the room that moves in the game (baked where it stands). Add geometry to the returned
        object's .parts (collided), .nocol (drawn only) and .col (invisible colliders), in room coordinates.
        type 'spin': turns about `axis` through `pivot` at `speed` rad/s. 'swing': rocks amp radians,
        once per `period` s. 'slide': travels `delta` and back once per `period` s, resting `pause` s at
        each end (lifts, drawers, shelves on rails). Only movers that stay level (spin about 'z', slide)
        can be stood on and carry you; tilting ones (spin/swing about 'x' or 'y') are drawn but not collided."""
        class _M: pass
        M = _M(); M.parts = Geo(); M.nocol = Geo(); M.col = Geo()
        M.spec = {'type': type, 'pivot': list(pivot), 'axis': axis, 'speed': speed, 'amp': amp, 'period': period,
                  'delta': list(delta), 'pause': pause, 'phase': phase}
        self.movers.append(M)
        return M

    # --- the shared doorways, one per boundary cell edge per level -----------
    def cut(self, g):
        self.cuts.append(g); return g

    def sockets(self, floor='floor', wall='tile', skip=(), rect=None):
        """The shared doorways. rect=h gives a flat-topped opening h tall instead of the arch
        (the neighbour's arch then shows as a frame on its side)."""
        pr = arch_profile(0, DW, 0, DJ) if rect is None else [(-DW / 2, 0), (DW / 2, 0), (DW / 2, rect), (-DW / 2, rect)]
        out = []
        for L in range(self.levels):
            if L not in self.levels_open: continue
            z = L * LH
            for i in range(self.w):
                cx = i * C + C / 2
                for side, y0, y1 in (('S', -0.5, T + 0.6), ('N', self.D - T - 0.6, self.D + 0.5)):
                    if (side, i, L) in skip: continue
                    self.cut(prism([(p + cx, q + z) for p, q in pr], 'y', y0, y1, arch_mats(len(pr), floor, wall)))
                    out.append((side, i, L))
            for j in range(self.d):
                cy = j * C + C / 2
                for side, x0, x1 in (('W', -0.5, T + 0.6), ('E', self.W - T - 0.6, self.W + 0.5)):
                    if (side, j, L) in skip: continue
                    self.cut(prism([(p + cy, q + z) for p, q in pr], 'x', x0, x1, arch_mats(len(pr), floor, wall)))
                    out.append((side, j, L))
        self.portals = out
        return out

    # --- bookshelves: frame + one slab quad per row that the books replace --
    def shelf(self, x, y, z, length, dirn, rows=5, row_h=0.42, depth=0.34, frame='wood', board=0.035, top_gap=0.08, back=True, sides=True, crown=True, solid=True):
        """A bookcase facing dirn ('+x','-x','+y','-y' or an angle in radians); (x, y) is its back-left
        corner seen from the front, z its bottom. Adds one slab per row; returns their ids.
        solid=False makes a false bookcase: drawn and lit, but you walk straight through it."""
        a = {'+y': math.pi / 2, '-y': -math.pi / 2, '+x': 0.0, '-x': math.pi}[dirn] if isinstance(dirn, str) else dirn
        th = a - math.pi / 2
        H = rows * row_h + board + top_gap
        g = Geo()
        if back: g.add(box(0, 0, 0, length, 0.02, H, frame, skip=('-y',)))
        if sides:
            g.add(box(-0.04, 0, 0, 0, depth + 0.02, H + 0.03, frame, skip=('-z',)))
            g.add(box(length, 0, 0, length + 0.04, depth + 0.02, H + 0.03, frame, skip=('-z',)))
        if crown: g.add(box(-0.06, 0, H, length + 0.06, depth + 0.05, H + 0.06, frame))
        for r in range(rows + 1):
            h = r * row_h
            g.add(box(0, 0.02, h, length, depth + 0.01, h + board, frame, skip=('-z',) if r == 0 else ()))
        g.xform(th, x, y, z)
        (self.parts if solid else self.nocol).add(g)
        c, s_ = math.cos(th), math.sin(th)
        rot = lambda p: (p[0] * c - p[1] * s_, p[0] * s_ + p[1] * c, p[2])
        ids = []
        for r in range(rows):
            h0 = r * row_h + board; h1 = h0 + row_h - board - 0.03
            o = rot((0, depth - 0.02, h0)); o = (o[0] + x, o[1] + y, o[2] + z)
            self.slabs.append({'o': o, 'u': list(rot((length, 0, 0))), 'v': [0, 0, h1 - h0], 'n': [math.cos(a), math.sin(a), 0],
                               'len': length, 'h': h1 - h0, 'depth': depth - 0.04, 'ghost': not solid})
            ids.append(len(self.slabs) - 1)
        return ids

    def light(self, g):
        self.emit.add(g)

    def flight(self, x0, y0, z0, width, n, rise, run, axis='+y', m='floor', riser=None, side='tile'):
        """A walkable flight of stairs: the visible steps (not collided) plus an invisible ramp the feet
        ride, so climbing is smooth. Same arguments as stairs(). Put walls or rails on open sides."""
        self.nocol.add(stairs(x0, y0, z0, width, n, rise, run, axis, m, riser, side))
        L, Hh = n * run, n * rise
        if axis == '+y':   q = [(x0, y0 - 0.02, z0), (x0 + width, y0 - 0.02, z0), (x0 + width, y0 + L, z0 + Hh), (x0, y0 + L, z0 + Hh)]
        elif axis == '-y': q = [(x0, y0 + 0.02, z0), (x0, y0 - L, z0 + Hh), (x0 + width, y0 - L, z0 + Hh), (x0 + width, y0 + 0.02, z0)]
        elif axis == '+x': q = [(x0 - 0.02, y0, z0), (x0 + L, y0, z0 + Hh), (x0 + L, y0 + width, z0 + Hh), (x0 - 0.02, y0 + width, z0)]
        else:              q = [(x0 + 0.02, y0, z0), (x0 + 0.02, y0 + width, z0), (x0 - L, y0 + width, z0 + Hh), (x0 - L, y0, z0 + Hh)]
        g = Geo(); ids = [g.vert(p) for p in q]; g.face(ids, 'floor', [(0, 0)] * 4)
        # make it face up
        a, b, c = (Vector(q[1]) - Vector(q[0])), (Vector(q[2]) - Vector(q[0])), None
        if a.cross(b).z < 0: g.f = [tuple(reversed(f)) for f in g.f]
        self.col.add(g)

    def pool(self, x0, y0, x1, y1, depth, surface=None, m='mosaic', coping=None, z=0.0, steps=True):
        """A sunken floor: terraces 0.3 m down and 0.45 m in, to depth (steps=False: one sheer drop)."""
        k, d = 0, 0.0
        while d < depth - 1e-6:
            ins = k * 0.45 if steps else 0.0
            if min(x1 - x0, y1 - y0) - 2 * ins < 0.9: break
            d = min(depth, d + 0.3) if steps else depth
            self.cut(box(x0 + ins, y0 + ins, z - d, x1 - ins, y1 - ins, z + 0.3, m, top='tile'))
            k += 1
        if coping:
            c = 0.28
            for bx in ((x0 - c, y0 - c, x1 + c, y0), (x0 - c, y1, x1 + c, y1 + c), (x0 - c, y0, x0, y1), (x1, y0, x1 + c, y1)):
                self.parts.add(box(bx[0], bx[1], z, bx[2], bx[3], z + coping, 'tile', skip=('-z',)))

    def round_pool(self, cx, cy, r, depth, surface=None, m='mosaic', z=0.0, segs=48):
        """A round sunken pit, stepped like an amphitheatre."""
        k, d = 0, 0.0
        while d < depth - 1e-6 and r - k * 0.45 > 0.5:
            d = min(depth, d + 0.3)
            self.cut(cyl(cx, cy, z - d, z + 0.3, r - k * 0.45, segs, side=m, bottom=m, top='tile'))
            k += 1

    def spot(self, kind, x, y, z=0.0, face=0.0, **kw):
        s = {'k': kind, 'p': [x, y, z], 'f': face}; s.update(kw); self.spots.append(s); return s

    def navpt(self, x, y, z=0.0):
        self.nav.append([x, y, z]); return len(self.nav) - 1

    def link(self, *ids):
        for a, b in zip(ids, ids[1:]): self.navlinks.append([a, b])


# ---------------------------------------------------------------------------
# Build: booleans, clean-up, lightmap UVs, bake, denoise, export
# ---------------------------------------------------------------------------
def _apply_bool(ob, cutter_coll, op='DIFFERENCE'):
    md = ob.modifiers.new('B', 'BOOLEAN')
    md.operation = op
    md.operand_type = 'COLLECTION'; md.collection = cutter_coll
    md.solver = 'EXACT'
    try: md.use_self = False; md.use_hole_tolerant = True
    except Exception: pass
    try: md.material_mode = 'TRANSFER'
    except Exception: pass
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    ob.modifiers.clear(); old = ob.data; ob.data = me; bpy.data.meshes.remove(old)


def _strip_outside(ob, R):
    """Delete faces on the room's outer skin (walls' outsides, slab undersides, block top)."""
    bm = bmesh.new(); bm.from_mesh(ob.data)
    kill = []
    for f in bm.faces:
        c = f.calc_center_median(); n = f.normal
        e = 1e-3
        if (abs(c.x) < e and n.x < -0.9) or (abs(c.x - R.W) < e and n.x > 0.9) or \
           (abs(c.y) < e and n.y < -0.9) or (abs(c.y - R.D) < e and n.y > 0.9) or \
           (abs(c.z - R.lo) < e and n.z < -0.9) or (abs(c.z - R.hi) < e and n.z > 0.9):
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    bm.to_mesh(ob.data); bm.free()


def _join(objs, name):
    objs = [o for o in objs if o is not None]
    if not objs: return None
    with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, object=objs[0]):
        bpy.ops.object.join()
    objs[0].name = name
    return objs[0]


def _face_attr(ob, name, value):
    a = ob.data.attributes.new(name, 'INT', 'FACE')
    a.data.foreach_set('value', [value] * len(ob.data.polygons))


def build(R, quick=False, night=True, bake=True):
    t0 = time.time()
    sc = bpy.context.scene
    cc = coll('cut'); main = coll('main'); lights = coll('lights')
    base = R.base.obj('base', main)
    for k, g in enumerate(R.cuts): g.obj('cut%d' % k, cc)
    _apply_bool(base, cc)
    cc.hide_render = True
    for o in list(cc.objects): bpy.data.objects.remove(o)
    _strip_outside(base, R)
    print('boolean %.1fs, %d faces' % (time.time() - t0, len(base.data.polygons)))
    # additive parts
    objs = [base]
    _face_attr(base, 'nocol', 0)
    if R.parts.f:
        p = R.parts.obj('parts', main, fix=False); _face_attr(p, 'nocol', 0); objs.append(p)
    if R.nocol.f:
        p = R.nocol.obj('nocol', main, fix=False); _face_attr(p, 'nocol', 1); objs.append(p)
    for o in objs: _face_attr(o, 'mover', 0)
    for k, M in enumerate(R.movers):
        for g, nc, nm in ((M.parts, 0, 'mvp%d' % k), (M.nocol, 1, 'mvn%d' % k)):
            if g.f:
                p = g.obj(nm, main, fix=False); _face_attr(p, 'nocol', nc); _face_attr(p, 'mover', k + 1); objs.append(p)
    # book slabs: one quad per shelf row, tagged so their lightmap rectangle can be read back
    if R.slabs:
        g = Geo()
        for s in R.slabs:
            o, u, v = s['o'], s['u'], s['v']
            P = [o, [o[i] + u[i] for i in range(3)], [o[i] + u[i] + v[i] for i in range(3)], [o[i] + v[i] for i in range(3)]]
            ids = [g.vert(p) for p in P]
            g.face(ids, 'books', [(0, 0), (s['len'], 0), (s['len'], s['h']), (0, s['h'])])
        so = g.obj('slabs', main, fix=False)
        a = so.data.attributes.new('slab', 'INT', 'FACE'); a.data.foreach_set('value', list(range(1, len(R.slabs) + 1)))
        a = so.data.attributes.new('nocol', 'INT', 'FACE'); a.data.foreach_set('value', [1 if s.get('ghost') else 0 for s in R.slabs])
        _face_attr(so, 'mover', 0)
        # make sure each slab faces the way the shelf does
        for i, p in enumerate(so.data.polygons):
            n = R.slabs[i]['n']
            if p.normal.x * n[0] + p.normal.y * n[1] < 0: p.flip()
        objs.append(so)
    room = _join(objs, 'room')
    room.data.shade_smooth(); room.data.set_sharp_from_angle(angle=math.radians(35))
    if 'slab' not in room.data.attributes:
        room.data.attributes.new('slab', 'INT', 'FACE')
    # emitters (lit in the bake, drawn as glowing geometry in the game)
    em = R.emit.obj('emit', lights, fix=False) if R.emit.f else None
    # portals: soft light standing in for the neighbouring rooms
    pg = Geo()
    for side, i, L in R.portals:
        z = L * LH; c = i * C + C / 2
        q = [(c - DR, z), (c + DR, z), (c + DR, z + DJ + DR), (c - DR, z + DJ + DR)]
        if side in 'SN':
            y = -0.6 if side == 'S' else R.D + 0.6
            ids = [pg.vert((p, y, zz)) for p, zz in q]
        else:
            x = -0.6 if side == 'W' else R.W + 0.6
            ids = [pg.vert((x, p, zz)) for p, zz in q]
        pg.face(ids, 'e_portal', [(0, 0)] * 4)
    po = pg.obj('portals', lights, fix=False) if pg.f else None
    if po:   # face them inward
        for p in po.data.polygons:
            c = p.center
            want = Vector((R.W / 2 - c.x, R.D / 2 - c.y, 0))
            if p.normal.dot(want) < 0: p.flip()
    # repeat vertically for shafts: bake with copies above and below so the light matches at the seams
    if R.repeat:
        for dz in (-LH * R.levels, LH * R.levels):
            for src in [room, em]:
                if src is None: continue
                cp = src.copy(); cp.data = src.data.copy(); cp.location.z += dz
                (lights if src is em else main).objects.link(cp); cp['copy'] = 1
    # lightmap UVs
    t1 = time.time()
    me = room.data
    lm = me.uv_layers.new(name='LM'); me.uv_layers.active = lm
    for o in bpy.context.view_layer.objects: o.select_set(False)
    room.select_set(True); bpy.context.view_layer.objects.active = room
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(50), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=4.5 / R.res, shape_method='CONCAVE')
    bpy.ops.object.mode_set(mode='OBJECT')
    # with very many small islands the margins can eat the whole map and everything packs to nothing (a black
    # bake): measure what the islands cover and repack with thinner margins until they get a real share
    def _uv_cover():
        lay = room.data.uv_layers['LM']   # fetch afresh: edit-mode toggles invalidate older references
        uv = np.zeros(len(room.data.loops) * 2, np.float32); lay.data.foreach_get('uv', uv); uv = np.nan_to_num(uv.reshape(-1, 2))
        mm = room.data
        st = np.zeros(len(mm.polygons), np.int32); mm.polygons.foreach_get('loop_start', st)
        nt = np.zeros(len(mm.polygons), np.int32); mm.polygons.foreach_get('loop_total', nt)
        a = 0.0
        for k in range(3, int(nt.max()) + 1 if len(nt) else 3):   # shoelace, grouped by corner count
            sel = st[nt == k]
            if not len(sel): continue
            q = uv[sel[:, None] + np.arange(k)[None, :]]
            x, y = q[..., 0], q[..., 1]
            a += float(np.abs((x * np.roll(y, -1, 1) - y * np.roll(x, -1, 1)).sum(1)).sum() * 0.5)
        return a
    cover = _uv_cover()
    for mg in (1.5, 0.5):
        if cover > 0.25: break
        print('uv islands cover only %.3f of the lightmap: repacking with margin %.1f px' % (cover, mg))
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=mg / R.res, shape_method='AABB')
        bpy.ops.object.mode_set(mode='OBJECT')
        cover = _uv_cover()
    print('uv cover %.2f' % cover)
    me = room.data; lm = me.uv_layers['LM']
    print('uv %.1fs' % (time.time() - t1))
    res = R.res if not quick else R.res // 2
    maps = {}
    if not bake:   # geometry check only: a flat grey lightmap
        maps['day'] = np.tile(np.array([0.45, 0.43, 0.40, 1.0], np.float32), (16, 16, 1))
    else:
        for mode in (['day', 'night'] if night else ['day']):
            maps[mode] = _bake(R, room, em, po, mode, res, quick)
    export(R, room, em, maps)
    print('%s built in %.0fs' % (R.name, time.time() - t0))


def _set_emit(em_objs, mode):
    for o in em_objs:
        if o is None: continue
        for m in o.data.materials:
            b = m.node_tree.nodes.get('Principled BSDF')
            if m.name.split('.')[0] not in EMIT: continue   # a stray non-emitter face on a light: leave it as it is
            col, s = EMIT[m.name.split('.')[0]]
            on = mode == 'day' or m.name.split('.')[0] in NIGHT_ON
            b.inputs['Emission Strength'].default_value = s if on else 0.0


def _bake(R, room, em, po, mode, res, quick):
    sc = bpy.context.scene
    sc.cycles.samples = (24 if quick else 96) if mode == 'day' else (16 if quick else 48)
    emitters = [o for o in bpy.data.objects if o.data and hasattr(o.data, 'materials') and any(m and m.name.split('.')[0] in EMIT for m in o.data.materials)]
    _set_emit(emitters, mode)
    img = bpy.data.images.new('LM_' + mode, res, res, float_buffer=True, alpha=True)
    img.generated_color = (0, 0, 0, 0)
    for m in room.data.materials:
        nt = m.node_tree
        n = nt.nodes.get('BAKE') or nt.nodes.new('ShaderNodeTexImage'); n.name = 'BAKE'
        n.image = img; nt.nodes.active = n
    bk = sc.render.bake
    bk.use_pass_direct = True; bk.use_pass_indirect = True; bk.use_pass_color = False
    bk.margin = 0; bk.use_clear = True; bk.target = 'IMAGE_TEXTURES'
    for o in bpy.context.view_layer.objects: o.select_set(False)
    room.select_set(True); bpy.context.view_layer.objects.active = room
    t = time.time()
    bpy.ops.object.bake(type='DIFFUSE')
    print('bake %s %dpx %.0fs' % (mode, res, time.time() - t))
    a = np.array(img.pixels[:], dtype=np.float32).reshape(res, res, 4)
    return a


def _dilate(rgb, mask, n):
    rgb = rgb.copy(); m = mask.copy()
    for _ in range(n):
        acc = np.zeros_like(rgb); cnt = np.zeros(m.shape, np.float32)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            acc += np.roll(np.roll(rgb * m[..., None], dy, 0), dx, 1); cnt += np.roll(np.roll(m, dy, 0), dx, 1)
        grow = (m == 0) & (cnt > 0)
        rgb[grow] = acc[grow] / cnt[grow][:, None]; m = np.maximum(m, grow.astype(np.float32))
    return rgb


def _denoise(rgb):
    import tempfile
    d = tempfile.mkdtemp()
    def wpfm(p, a):
        h, w, _ = a.shape
        with open(p, 'wb') as f:
            f.write(b'PF\n%d %d\n-1.0\n' % (w, h)); f.write(np.ascontiguousarray(a.astype('<f4')).tobytes())
    def rpfm(p):
        with open(p, 'rb') as f:
            f.readline(); w, h = map(int, f.readline().split()); f.readline()
            return np.frombuffer(f.read(), dtype='<f4').reshape(h, w, 3).copy()
    wpfm(d + '/i.pfm', rgb)
    subprocess.run([OIDN, '-f', 'RTLightmap', '--hdr', d + '/i.pfm', '-o', d + '/o.pfm', '-q', 'high', '-v', '0'], check=True, stdout=subprocess.DEVNULL)
    return rpfm(d + '/o.pfm')


def encode_lightmap(a, path):
    """HDR lightmap -> 8-bit PNG. y = (v / (v + 1)) ^ (1 / 2.2); the game inverts it."""
    from PIL import Image
    rgb = a[..., :3]; mask = (a[..., 3] > 0.5).astype(np.float32)
    rgb = _dilate(rgb, mask, 6)
    rgb = np.maximum(_denoise(rgb), 0)
    rgb = _dilate(rgb, mask, 8)
    y = np.clip(rgb / (rgb + 1.0), 0, 1) ** (1 / 2.2)
    img = Image.fromarray((y * 255 + 0.5).astype(np.uint8)[::-1])   # Blender rows run bottom-up
    img.save(path, quality=92, method=6)
    return float(rgb[mask > 0].mean()) if mask.any() else 0.0


def export(R, room, em, maps):
    os.makedirs(OUT, exist_ok=True)
    name = R.name
    avg = {}
    for mode, a in maps.items():
        avg[mode] = encode_lightmap(a, os.path.join(OUT, '%s_%s.webp' % (name, mode)))
    groups = []; blob = bytearray(); col_tris = []; mv_tris = {}
    def put(arr):
        nonlocal blob
        while len(blob) % 4: blob += b'\0'
        off = len(blob); blob += arr.tobytes(); return off
    def dump(ob, emissive=False):
        me = ob.data
        me.calc_loop_triangles()
        nlt = len(me.loop_triangles)
        if not nlt: return
        tri_loops = np.zeros(nlt * 3, np.int32); me.loop_triangles.foreach_get('loops', tri_loops)
        tri_poly = np.zeros(nlt, np.int32); me.loop_triangles.foreach_get('polygon_index', tri_poly)
        pmat = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', pmat)
        loop_v = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', loop_v)
        co = np.zeros(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        cn = np.zeros(len(me.loops) * 3, np.float32); me.corner_normals.foreach_get('vector', cn); cn = cn.reshape(-1, 3)
        uv0 = np.zeros(len(me.loops) * 2, np.float32); me.uv_layers['UV0'].data.foreach_get('uv', uv0); uv0 = uv0.reshape(-1, 2)
        if 'LM' in me.uv_layers:
            uv1 = np.zeros(len(me.loops) * 2, np.float32); me.uv_layers['LM'].data.foreach_get('uv', uv1); uv1 = uv1.reshape(-1, 2)
        else: uv1 = np.zeros((len(me.loops), 2), np.float32)
        nocol = np.zeros(len(me.polygons), np.int32)
        if 'nocol' in me.attributes: me.attributes['nocol'].data.foreach_get('value', nocol)
        slab = np.zeros(len(me.polygons), np.int32)
        if 'slab' in me.attributes: me.attributes['slab'].data.foreach_get('value', slab)
        mover = np.zeros(len(me.polygons), np.int32)
        if 'mover' in me.attributes: me.attributes['mover'].data.foreach_get('value', mover)
        tri_mat = pmat[tri_poly]; tri_mv = mover[tri_poly]
        for mi, m in enumerate(me.materials):
          mname = m.name.split('.')[0]
          for mv in np.unique(tri_mv[tri_mat == mi]):
            sel = np.where((tri_mat == mi) & (tri_mv == mv))[0]
            if not len(sel): continue
            loops = tri_loops.reshape(-1, 3)[sel]            # (t, 3)
            loops = loops[:, ::-1]                             # Blender (x, y, z) -> game (x, z, y) mirrors, so flip winding
            L = loops.reshape(-1)
            uniq, inv = np.unique(L, return_inverse=True)
            P = co[loop_v[uniq]][:, [0, 2, 1]]
            N = cn[uniq][:, [0, 2, 1]]
            U0 = uv0[uniq]; U1 = uv1[uniq]
            idx = inv.astype(np.uint32 if len(uniq) > 65535 else np.uint16)
            g = {'mat': mname, 'n': int(len(uniq)), 'i': int(len(idx)), 'i32': bool(idx.dtype == np.uint32),
                 'p': put(P.astype(np.float32)), 'nr': put(np.clip(np.round(N * 127), -127, 127).astype(np.int8)),
                 'u0': put(U0.astype(np.float32)), 'u1': put(np.clip(np.round(U1 * 65535), 0, 65535).astype(np.uint16)),
                 'ix': put(idx), 'emit': emissive}
            if mv: g['mv'] = int(mv)
            groups.append(g)
            if not emissive:
                cs = sel[nocol[tri_poly[sel]] == 0]
                if len(cs):
                    tris = co[loop_v[tri_loops.reshape(-1, 3)[cs][:, ::-1].reshape(-1)]][:, [0, 2, 1]]
                    (mv_tris.setdefault(int(mv), []) if mv else col_tris).append(tris)
    dump(room)
    if em: dump(em, True)
    if R.col.f:
        co = R.col.obj('colonly', coll('lights'), fix=False)
        me = co.data; me.calc_loop_triangles()
        vs = np.array([v.co[:] for v in me.vertices], np.float32)
        tr = np.array([[t.vertices[2], t.vertices[1], t.vertices[0]] for t in me.loop_triangles], np.int32)
        col_tris.append(vs[tr.reshape(-1)][:, [0, 2, 1]])
    ct = np.concatenate(col_tris) if col_tris else np.zeros((0, 3), np.float32)
    col_off = put(ct.astype(np.float32))
    movers = []
    for k, M in enumerate(R.movers):
        tl = mv_tris.get(k + 1, [])
        if M.col.f:
            o = M.col.obj('mvcol%d' % k, coll('lights'), fix=False); me2 = o.data; me2.calc_loop_triangles()
            vs = np.array([v.co[:] for v in me2.vertices], np.float32)
            tr = np.array([[t.vertices[2], t.vertices[1], t.vertices[0]] for t in me2.loop_triangles], np.int32)
            tl.append(vs[tr.reshape(-1)][:, [0, 2, 1]])
        mc = np.concatenate(tl) if tl else np.zeros((0, 3), np.float32)
        sp = dict(M.spec); sp['pivot'] = [sp['pivot'][0], sp['pivot'][2], sp['pivot'][1]]; sp['delta'] = [sp['delta'][0], sp['delta'][2], sp['delta'][1]]
        sp['axis'] = {'x': 'x', 'y': 'z', 'z': 'y'}[sp['axis']]
        sp['col'] = {'off': put(mc.astype(np.float32)), 'n': int(len(mc) // 3)}
        movers.append(sp)
    # slab lightmap rectangles
    me = room.data
    sl = np.zeros(len(me.polygons), np.int32); me.attributes['slab'].data.foreach_get('value', sl)
    lmuv = me.uv_layers['LM'].data
    slabs = []
    for k, s in enumerate(R.slabs):
        pi = int(np.where(sl == k + 1)[0][0]); p = me.polygons[pi]
        # corners in the order the slab was made: o, o+u, o+u+v, o+v (flip() may have reversed them)
        want = [Vector(s['o']), Vector(s['o']) + Vector(s['u']), Vector(s['o']) + Vector(s['u']) + Vector(s['v']), Vector(s['o']) + Vector(s['v'])]
        uvs = []
        for w in want:
            best = min(p.loop_indices, key=lambda li: (me.vertices[me.loops[li].vertex_index].co - w).length)
            uvs.append(list(lmuv[best].uv))
        slabs.append({'o': [s['o'][0], s['o'][2], s['o'][1]], 'u': [s['u'][0], s['u'][2], s['u'][1]], 'v': [s['v'][0], s['v'][2], s['v'][1]],
                      'n': [s['n'][0], 0, s['n'][1]], 'len': s['len'], 'h': s['h'], 'depth': s['depth'], 'lm': uvs})
    sw = lambda p: [p[0], p[2], p[1]]
    water = []
    for wv in R.water:
        if 'r' in wv: water.append({'cx': wv['cx'], 'cz': wv['cy'], 'r': wv['r'], 'top': wv['top'], 'bot': wv['bot']})
        else: water.append({'x0': wv['x0'], 'z0': wv['y0'], 'x1': wv['x1'], 'z1': wv['y1'], 'top': wv['top'], 'bot': wv['bot']})
    meta = {
        'name': name, 'w': R.w, 'd': R.d, 'levels': R.levels, 'repeat': R.repeat, 'res': R.res,
        'groups': groups, 'col': {'off': col_off, 'n': int(len(ct) // 3)}, 'slabs': slabs, 'water': water, 'movers': movers,
        'spots': [dict(s, p=sw(s['p'])) for s in R.spots], 'nav': [sw(p) for p in R.nav], 'links': R.navlinks,
        'avg': avg, 'emit': {k: [list(v[0]), v[1]] for k, v in EMIT.items()}, 'albedo': MATS, 'meta': R.meta,
        'night_on': sorted(NIGHT_ON),
        'bin': base64.b64encode(bytes(blob)).decode('ascii')   # the meshes, as base64 so every host serves it
    }
    with open(os.path.join(OUT, name + '.json'), 'w') as f: json.dump(meta, f, separators=(',', ':'))
    print('exported %s: %d groups, %.0f KB, %d col tris, %d slabs' % (name, len(groups), len(blob) / 1024, len(ct) // 3, len(slabs)))


def ring(cx, cy, z0, z1, r0, r1, segs=64, top='floor', bottom='plaster', inner='tile', outer='tile', a0=0.0, a1=2 * math.pi):
    """Annulus slab (or a sector of one). Top/bottom UV0 = plan (x, y); sides = (angle * r, z)."""
    g = Geo()
    full = abs(a1 - a0 - 2 * math.pi) < 1e-6
    n = segs if full else segs + 1
    ang = [a0 + (a1 - a0) * k / segs for k in range(n)]
    P = lambda r, a, z: (cx + r * math.cos(a), cy + r * math.sin(a), z)
    ib = [g.vert(P(r0, a, z0)) for a in ang]; ob = [g.vert(P(r1, a, z0)) for a in ang]
    it = [g.vert(P(r0, a, z1)) for a in ang]; ot = [g.vert(P(r1, a, z1)) for a in ang]
    xy = lambda i: (g.v[i][0], g.v[i][1])
    for k in range(segs):
        j = (k + 1) % n
        g.face([ot[k], ot[j], it[j], it[k]], top, [xy(ot[k]), xy(ot[j]), xy(it[j]), xy(it[k])])
        g.face([ib[k], ib[j], ob[j], ob[k]], bottom, [xy(ib[k]), xy(ib[j]), xy(ob[j]), xy(ob[k])])
        u0, u1 = ang[k] * r1, (ang[k] + (a1 - a0) / segs) * r1
        g.face([ob[k], ob[j], ot[j], ot[k]], outer, [(u0, z0), (u1, z0), (u1, z1), (u0, z1)])
        u0, u1 = ang[k] * r0, (ang[k] + (a1 - a0) / segs) * r0
        g.face([ib[j], ib[k], it[k], it[j]], inner, [(u1, z0), (u0, z0), (u0, z1), (u1, z1)])
    if not full:
        g.face([ib[0], ob[0], ot[0], it[0]], inner, [(r0, z0), (r1, z0), (r1, z1), (r0, z1)])
        g.face([ob[-1], ib[-1], it[-1], ot[-1]], inner, [(r1, z0), (r0, z0), (r0, z1), (r1, z1)])
    return g.fix()


def helix(cx, cy, r0, r1, z0, rise, a0, a1, thick=0.35, segs=96, top='floor', side='tile', bottom='plaster'):
    """A helical ramp band from angle a0 to a1 (radians), rising `rise` per full turn, starting at z0."""
    g = Geo()
    n = segs + 1
    ang = [a0 + (a1 - a0) * k / segs for k in range(n)]
    zt = [z0 + rise * (a - a0) / (2 * math.pi) for a in ang]
    P = lambda r, a, z: (cx + r * math.cos(a), cy + r * math.sin(a), z)
    it = [g.vert(P(r0, a, z)) for a, z in zip(ang, zt)]; ot = [g.vert(P(r1, a, z)) for a, z in zip(ang, zt)]
    ib = [g.vert(P(r0, a, z - thick)) for a, z in zip(ang, zt)]; ob = [g.vert(P(r1, a, z - thick)) for a, z in zip(ang, zt)]
    rm = (r0 + r1) / 2
    L = [abs(a - a0) * rm for a in ang]
    for k in range(segs):
        j = k + 1
        g.face([ot[k], ot[j], it[j], it[k]], top, [(L[k], r1), (L[j], r1), (L[j], r0), (L[k], r0)])
        g.face([ib[k], ib[j], ob[j], ob[k]], bottom, [(L[k], r0), (L[j], r0), (L[j], r1), (L[k], r1)])
        g.face([ob[k], ob[j], ot[j], ot[k]], side, [(L[k], zt[k] - thick), (L[j], zt[j] - thick), (L[j], zt[j]), (L[k], zt[k])])
        g.face([ib[j], ib[k], it[k], it[j]], side, [(L[j], zt[j] - thick), (L[k], zt[k] - thick), (L[k], zt[k]), (L[j], zt[j])])
    g.face([ib[0], ob[0], ot[0], it[0]], side, [(r0, 0), (r1, 0), (r1, thick), (r0, thick)])
    g.face([ob[-1], ib[-1], it[-1], ot[-1]], side, [(r1, 0), (r0, 0), (r0, thick), (r1, thick)])
    return g.fix()
