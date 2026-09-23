"""The Long Hall: a vaulted stone nave with a sunken canal of books down its length, arcades on
both sides, vaulted aisles lined with books, and a skylight slot running the length of the vault."""
from lib import *


def make():
    R = Room('poolhall', 2, 1, res=2048)
    R.sockets()
    W, D = R.W, R.D
    cy = D / 2
    # nave: barrel vault along x
    nave_w, nave_j = 8.0, 3.4
    pr = arch_profile(cy, nave_w, 0, nave_j, 32)
    R.cut(prism(pr, 'x', T - 0.02, W - T + 0.02, arch_mats(len(pr))))
    # aisles: small barrel vaults along x
    aw = (cy - nave_w / 2) - T - 0.7          # aisle width, leaving a 0.7 m arcade wall
    for ay in (T + aw / 2, D - T - aw / 2):
        pa = arch_profile(ay, aw, 0, 2.3, 20)
        R.cut(prism(pa, 'x', T - 0.02, W - T + 0.02, arch_mats(len(pa))))
    # arcades between aisles and nave, an arch every 4 m (lined up with the side doors at x = 8 and 24)
    for x in range(4, int(W), 4):
        pa = arch_profile(x, 2.6, 0, 2.2, 18)
        for (y0, y1) in ((T + aw - 0.05, cy - nave_w / 2 + 0.05), (cy + nave_w / 2 - 0.05, D - T - aw + 0.05)):
            R.cut(prism([(p, q) for p, q in pa], 'y', y0, y1, arch_mats(len(pa))))
    # skylight slot along the crown of the vault
    R.cut(box(5.0, cy - 0.55, nave_j + nave_w / 2 - 0.4, W - 5.0, cy + 0.55, R.hi + 0.5, 'tile'))
    R.light(box(5.0, cy - 0.55, R.hi - 0.09, W - 5.0, cy + 0.55, R.hi - 0.05, 'e_sky'))
    # round lights in the aisle vaults
    for x in range(2, int(W), 4):
        for ay in (T + aw / 2, D - T - aw / 2):
            R.cut(cyl(x, ay, 2.3 + aw / 2 - 0.25, 2.3 + aw / 2 + 0.5, 0.26, 20))
            R.light(cyl(x, ay, 2.3 + aw / 2 + 0.42, 2.3 + aw / 2 + 0.45, 0.26, 20, side='e_panel', top='e_panel', bottom='e_panel'))
    # the canal: a sheer-sided trench of books, with steps down at the west end
    px0, px1, py0, py1, depth = 4.6, W - 4.6, cy - 2.8, cy + 2.8, 1.5
    R.pool(px0, py0, px1, py1, depth, steps=False)
    for k in range(1, 6):   # steps down at both ends
        R.parts.add(box(px0 - 0.01, py0, -depth, px0 + k * 0.36, py1, -k * 0.25, 'mosaic', skip=('-z',)))
        R.parts.add(box(px1 - k * 0.36, py0, -depth, px1 + 0.01, py1, -k * 0.25, 'mosaic', skip=('-z',)))
    L = (px1 - 2.2) - (px0 + 2.2)
    R.shelf(px0 + 2.2, py0, -depth, L, '+y', rows=3, frame='wood')
    R.shelf(px1 - 2.2, py1, -depth, L, '-y', rows=3, frame='wood')
    # a stone parapet with a brass rail along both long edges, open at the stairs
    for (y0, y1) in ((py0 - 0.22, py0), (py1, py1 + 0.22)):
        R.parts.add(box(px0 + 2.0, y0, 0, px1 - 2.0, y1, 0.9, 'tile', skip=('-z',)))
        R.parts.add(box(px0 + 1.97, y0 - 0.03, 0.9, px1 - 1.97, y1 + 0.03, 0.96, 'brass'))
    for x in (px0 + 3.0, (px0 + px1) / 2, px1 - 3.0):     # lamps along the canal's lip
        for (y, a) in ((py0 + 0.01, 0.0), (py1 - 0.01, math.pi)):
            R.light(box(x - 0.25, y - 0.04, -0.1, x + 0.25, y + 0.04, -0.02, 'e_pool'))
    # books along both aisle walls, and flanking the end doors
    for y0, face in ((T, '+y'), (D - T, '-y')):
        for (a, b) in ((0.7, 6.1), (9.9, 22.1), (25.9, W - 0.7)):
            if face == '+y': R.shelf(a, y0, 0, b - a, '+y', rows=5, frame='paint')
            else:            R.shelf(b, y0, 0, b - a, '-y', rows=5, frame='paint')
    for x0, face in ((T, '+x'), (W - T, '-x')):
        for (a, b) in ((cy - nave_w / 2 + 0.25, cy - 1.85), (cy + 1.85, cy + nave_w / 2 - 0.25)):
            if face == '+x': R.shelf(x0, b, 0, b - a, '+x', rows=6, frame='paint')
            else:            R.shelf(x0, a, 0, b - a, '-x', rows=6, frame='paint')
    # walkers' graph: pool decks, aisles, crossings through the arcade arches
    xs = [1.5] + list(range(4, 29, 4)) + [W - 1.5]
    deckS = [R.navpt(x, py0 - 0.65) for x in xs]; deckN = [R.navpt(x, py1 + 0.65) for x in xs]
    aisS = [R.navpt(x, T + aw / 2) for x in xs[1:-1]]; aisN = [R.navpt(x, D - T - aw / 2) for x in xs[1:-1]]
    for row in (deckS, deckN, aisS, aisN): R.link(*row)
    for i in range(len(aisS)):
        R.link(aisS[i], deckS[i + 1]); R.link(aisN[i], deckN[i + 1])
    R.link(deckS[0], deckN[0]); R.link(deckS[-1], deckN[-1])
    for x in (6, 14, 22, 26):
        R.spot('read', x, T + aw / 2, 0, math.pi / 2 * -1)
    R.spot('probe', W / 2, cy, 1.7)
    R.meta['label'] = 'The Long Hall'
    return R
