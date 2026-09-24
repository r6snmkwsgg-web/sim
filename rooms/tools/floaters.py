"""Find geometry floating in mid-air in packed rooms: pieces of mesh that touch nothing that
leads back to the room's shell (walls, floor, ceiling).

    python3 rooms/tools/floaters.py            # every room
    python3 rooms/tools/floaters.py chapel ... # some

A piece is a connected set of triangles (sharing vertices). Pieces touch when their bounding boxes,
grown by 3 cm, overlap. Starting from the biggest piece (the shell), everything reachable through
touching pieces is supported; the rest floats. Lights are left out (lamps may hang on nothing
visible). Reports each floating piece's material, size and position (game axes: x, height, z).
"""
import sys, os, json, base64, zlib
import numpy as np

DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'game', 'rooms')


def pieces(name):
    m = json.load(open(os.path.join(DST, name + '.json')))
    raw = zlib.decompress(base64.b64decode(m['zbin']))
    lo = np.array(m['q']['lo']); st = np.array(m['q']['step'])
    out = []
    for g in m['groups']:
        if g['emit'] or g['mat'] == 'books': continue
        P = np.frombuffer(raw, np.uint16, g['n'] * 3, g['p']).reshape(-1, 3) * st + lo
        I = np.frombuffer(raw, np.uint32 if g['i32'] else np.uint16, g['i'], g['ix']).reshape(-1, 3)
        # weld vertices at the same spot (seams split them), then union-find over triangles
        key = np.round(P / 0.002).astype(np.int64)
        _, weld = np.unique(key, axis=0, return_inverse=True); weld = weld.reshape(-1)
        parent = np.arange(weld.max() + 1)
        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]; a = parent[a]
            return a
        for t in I:
            a, b, c = find(weld[t[0]]), find(weld[t[1]]), find(weld[t[2]])
            if a != b: parent[b] = a
            if a != c: parent[find(c)] = a
        roots = np.array([find(weld[t[0]]) for t in I])
        for r in np.unique(roots):
            tri = I[roots == r].reshape(-1)
            V = P[tri]
            out.append({'mat': g['mat'], 'lo': V.min(0), 'hi': V.max(0), 'n': len(tri) // 3})
    return m, out


def floaters(name, grow=0.03):
    m, ps = pieces(name)
    if not ps: return m, []
    big = max(range(len(ps)), key=lambda i: np.prod(ps[i]['hi'] - ps[i]['lo'] + 0.01))
    lo = np.array([p['lo'] for p in ps]) - grow; hi = np.array([p['hi'] for p in ps]) + grow
    seen = np.zeros(len(ps), bool); seen[big] = True; stack = [big]
    while stack:
        i = stack.pop()
        touch = np.all((lo <= hi[i]) & (hi >= lo[i]), axis=1) & ~seen
        for j in np.where(touch)[0]: seen[j] = True; stack.append(j)
    return m, [ps[i] for i in range(len(ps)) if not seen[i]]


def main():
    names = [a for a in sys.argv[1:]] or sorted(f[:-5] for f in os.listdir(DST) if f.endswith('.json') and f != 'index.json')
    total = 0
    for n in names:
        m, fl = floaters(n)
        if not fl: continue
        total += 1
        print('%-15s %d floating piece(s)' % (n, len(fl)))
        for p in sorted(fl, key=lambda p: -np.prod(p['hi'] - p['lo'] + 0.01))[:8]:
            c = (p['lo'] + p['hi']) / 2; s = p['hi'] - p['lo']
            print('    %-9s %4d tris  size %5.2f x %5.2f x %5.2f  at x %6.2f  h %5.2f  z %6.2f  (bottom %5.2f)' % (p['mat'], p['n'], s[0], s[1], s[2], c[0], c[1], c[2], p['lo'][1]))
    print('%d of %d rooms have floating pieces' % (total, len(names)))


if __name__ == '__main__':
    main()


def outside(name, tol=0.02):
    """Geometry reaching outside the room's own box: it would appear inside the neighbouring room."""
    m = json.load(open(os.path.join(DST, name + '.json')))
    raw = zlib.decompress(base64.b64decode(m['zbin']))
    lo = np.array(m['q']['lo']); st = np.array(m['q']['step'])
    W, D, L = m['w'] * 16, m['d'] * 16, m['levels']
    ytop = L * 8 - 0.4 if not m.get('repeat') else None
    bad = {}
    for g in m['groups']:
        P = np.frombuffer(raw, np.uint16, g['n'] * 3, g['p']).reshape(-1, 3) * st + lo
        out = (P[:, 0] < -tol) | (P[:, 0] > W + tol) | (P[:, 2] < -tol) | (P[:, 2] > D + tol) | (P[:, 1] < -2 - tol)
        if ytop is not None: out |= P[:, 1] > ytop + tol
        if out.any():
            Q = P[out]; bad[g['mat']] = (int(out.sum()), Q.min(0).round(2).tolist(), Q.max(0).round(2).tolist())
    return bad


if __name__ == '__main__' and '--outside' in sys.argv:
    pass
