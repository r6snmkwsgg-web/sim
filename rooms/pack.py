"""Pack raw room bakes (rooms/out/) into the files the game loads (game/rooms/).

    python3 rooms/pack.py            # every room in rooms/out
    python3 rooms/pack.py tower well # just these
    python3 rooms/pack.py x --noindex  # pack for testing without adding it to the catalogue

One JSON file per room: the layout, the meshes quantized to 16 bits and deflated, and both
lightmaps embedded as WebP, all base64. Also writes game/rooms/index.json, the catalogue the
world generator draws from (sizes, kinds, weights, labels).
"""
import sys, os, json, base64, zlib, io
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'out')
DST = os.path.join(HERE, '..', 'game', 'rooms')
LM_QUALITY = 80

# the original rooms predate catalogue metadata in their scripts
LEGACY = {
    'rest':      {'weight': 45, 'label': 'A rest area'},
    'crossing':  {'weight': 28, 'label': 'The Crossing'},
    'bath':      {'weight': 20, 'label': 'The Sunken Court'},
    'reading':   {'weight': 20, 'label': 'The Reading Room'},
    'poolhall':  {'weight': 50, 'label': 'The Long Hall'},
    'stacks':    {'weight': 50, 'label': 'The Sunken Stacks'},
    'backrooms': {'weight': 50, 'label': 'The Labyrinth'},
    'pillars':   {'weight': 50, 'label': 'The Pillar Forest'},
    'grand':     {'weight': 50, 'label': 'The Great Hall'},
    'well':      {'weight': 55, 'label': 'The Well'},
    'tower':     {'weight': 45, 'label': 'The Spiral'},
}


def kind_of(m):
    if m.get('repeat'): return 'column'
    w, d, L = m['w'], m['d'], m['levels']
    if (w, d, L) == (1, 1, 1): return 'single'
    if sorted((w, d)) == [1, 2] and L == 1: return 'long'
    if (w, d, L) == (2, 2, 1): return 'quad'
    if (w, d, L) == (2, 2, 2): return 'tall'
    if w % 2 == 0 and d % 2 == 0 and L % 2 == 0: return 'giant'
    raise ValueError('room %s: size %dx%dx%d fits no kind' % (m['name'], w, d, L))


def webp_b64(path):
    im = Image.open(path).convert('RGB')
    b = io.BytesIO(); im.save(b, 'WEBP', quality=LM_QUALITY, method=6)
    return base64.b64encode(b.getvalue()).decode('ascii')


def pack(name):
    src = json.load(open(os.path.join(RAW, name + '.json')))
    blob = base64.b64decode(src['bin'])
    groups, parts = [], []
    size = 0
    def put(a):
        nonlocal size
        a = np.ascontiguousarray(a); pad = (-size) % 4
        if pad: parts.append(b'\0' * pad); size += pad
        off = size; parts.append(a.tobytes()); size += a.nbytes; return off
    # one quantization box for the whole room, so every mesh and the collision agree
    allp = [np.frombuffer(blob, np.float32, g['n'] * 3, g['p']).reshape(-1, 3) for g in src['groups']]
    col = np.frombuffer(blob, np.float32, src['col']['n'] * 9, src['col']['off']).reshape(-1, 3)
    mcols = [np.frombuffer(blob, np.float32, m['col']['n'] * 9, m['col']['off']).reshape(-1, 3) for m in src.get('movers', [])]
    pts = np.concatenate(allp + [c for c in [col] + mcols if len(c)])
    lo = pts.min(0) - 0.01; hi = pts.max(0) + 0.01
    step = (hi - lo) / 65535.0
    q = lambda P: np.clip(np.round((P - lo) / step), 0, 65535).astype(np.uint16)
    uvmax = max(float(np.abs(np.frombuffer(blob, np.float32, g['n'] * 2, g['u0'])).max()) for g in src['groups'])
    ustep = max(1 / 256, uvmax / 32000)
    for g, P in zip(src['groups'], allp):
        n = g['n']
        U0 = np.frombuffer(blob, np.float32, n * 2, g['u0'])
        ix = np.frombuffer(blob, np.uint32 if g['i32'] else np.uint16, g['i'], g['ix'])
        groups.append({'mat': g['mat'], 'n': n, 'i': g['i'], 'i32': g['i32'], 'emit': g['emit'],
                       'p': put(q(P)), 'nr': put(np.frombuffer(blob, np.int8, n * 3, g['nr'])),
                       'u0': put(np.round(U0 / ustep).astype(np.int16)), 'u1': put(np.frombuffer(blob, np.uint16, n * 2, g['u1'])),
                       'ix': put(ix)})
        if g.get('mv'): groups[-1]['mv'] = g['mv']
    # collision: shared vertices + triangle indices
    cq = q(col)
    uniq, inv = np.unique(cq, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    cidx = inv.astype(np.uint32 if len(uniq) > 65535 else np.uint16)
    colm = {'nv': int(len(uniq)), 'nt': int(len(col) // 3), 'i32': bool(cidx.dtype == np.uint32), 'v': put(uniq), 'ix': put(cidx)}
    movers = []
    for m, mc in zip(src.get('movers', []), mcols):   # moving parts: their own collision, in the same quantization
        u2, i2 = np.unique(q(mc), axis=0, return_inverse=True) if len(mc) else (np.zeros((0, 3), np.uint16), np.zeros(0, np.int64))
        i2 = i2.reshape(-1).astype(np.uint32 if len(u2) > 65535 else np.uint16)
        mm = {k: v for k, v in m.items() if k != 'col'}
        mm['col'] = {'nv': int(len(u2)), 'nt': int(len(mc) // 3), 'i32': bool(i2.dtype == np.uint32), 'v': put(u2), 'ix': put(i2)}
        movers.append(mm)
    # shelf rows: 18 floats each (origin, run, normal x/z, height, depth, lightmap corners) instead of JSON
    sl = src.get('slabs', [])
    if sl:
        A = np.array([s_['o'] + s_['u'] + [s_['n'][0], s_['n'][2], s_['h'], s_['depth']] + [c for q_ in s_['lm'] for c in q_] for s_ in sl], np.float32)
        slm = {'off': put(A), 'n': len(sl)}
    else:
        slm = {'off': 0, 'n': 0}
    raw = b''.join(parts)
    z = zlib.compress(raw, 9)
    out = {k: v for k, v in src.items() if k not in ('bin', 'groups', 'col', 'movers')}
    if movers: out['movers'] = movers
    # layout numbers need millimetres, lightmap coordinates a little more: trim the digits
    def rnd(v, d):
        if isinstance(v, float): return round(v, d)
        if isinstance(v, list): return [rnd(x, d) for x in v]
        if isinstance(v, dict): return {k: rnd(x, 5 if k == 'lm' else d) for k, x in v.items()}
        return v
    for k in ('slabs', 'spots', 'nav', 'water'):
        if k in out: out[k] = rnd(out[k], 3)
    out.pop('slabs', None)
    out.update({'sl': slm, 'fmt': 2, 'groups': groups, 'col': colm, 'q': {'lo': lo.tolist(), 'step': step.tolist(), 'uv': ustep},
                'zbin': base64.b64encode(z).decode('ascii'), 'rawSize': len(raw)})
    lm = {'day': webp_b64(os.path.join(RAW, name + '_day.webp'))}
    nightp = os.path.join(RAW, name + '_night.webp')
    if os.path.exists(nightp): lm['night'] = webp_b64(nightp)
    out['lm'] = lm
    with open(os.path.join(DST, name + '.json'), 'w') as f: json.dump(out, f, separators=(',', ':'))
    m = dict(LEGACY.get(name, {}))
    mm = src.get('meta', {})
    for k in ('weight', 'label', 'blurb', 'secret'):
        if k in mm: m[k] = mm[k]
    entry = {'size': [src['w'], src['d'], src['levels']], 'repeat': bool(src.get('repeat')), 'kind': kind_of(src),
             'weight': m.get('weight', 10), 'label': m.get('label', name), 'bytes': os.path.getsize(os.path.join(DST, name + '.json'))}
    if m.get('blurb'): entry['blurb'] = m['blurb']
    return entry


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    noindex = '--noindex' in sys.argv
    names = args or sorted(f[:-5] for f in os.listdir(RAW) if f.endswith('.json'))
    os.makedirs(DST, exist_ok=True)
    ip = os.path.join(DST, 'index.json')
    index = json.load(open(ip)) if os.path.exists(ip) else {}
    for n in names:
        e = pack(n)
        print('%-14s %-7s %5.0f KB' % (n, e['kind'], e['bytes'] / 1024))
        if not noindex: index[n] = e
    if noindex: return
    for n in list(index):
        if not os.path.exists(os.path.join(DST, n + '.json')): del index[n]
    with open(ip, 'w') as f: json.dump(dict(sorted(index.items())), f, indent=0, separators=(',', ':'))
    tot = sum(e['bytes'] for e in index.values())
    print('%d rooms, %.1f MB' % (len(index), tot / 1e6))


if __name__ == '__main__':
    main()
