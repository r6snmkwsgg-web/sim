"""The Hidden Reading Room: three of the doorways are walled up; the fourth is filled by a bookcase,
and the bookcase is not there. Behind it, a small vaulted reading room lit by candles."""
from lib import *
from kit_d import *


def false_case(R):
    """A false bookcase standing in the south doorway, books on both faces, and a false lunette
    filling the arch above it, so from either side it looks like a bookcase in a blind arch."""
    L = DW - 0.06
    rows = 6
    bookcase(R, M + L / 2, 0.36, 0, L, '-y', rows, frame='walnut', solid=False, sides=True)
    bookcase(R, M - L / 2, 0.40, 0, L, '+y', rows, frame='walnut', solid=False, sides=True)
    top = rows * 0.42 + 0.035 + 0.08 + 0.06
    # the lunette: the part of the arch above the case, filled with a walnut panel
    pr = [(M - DR, top), (M + DR, top)] + [(M + DR * math.cos(math.pi * k / 18), DJ + DR * math.sin(math.pi * k / 18)) for k in range(1, 18)]
    pr = [p for p in pr if p[1] >= top - 1e-6]
    R.nocol.add(prism(pr, 'y', 0.02, 0.72, 'walnut', cap='walnut'))


def make():
    R = Room('secret_reading', 1, 1, res=1024)
    shell(R, None, floor='floor', wall='tile', seal=('N', 'E', 'W'))
    R.meta['secret'] = True
    x0, x1, y0, y1, H = 4.6, 11.4, T - 0.02, 7.2, 2.9
    R.cut(box(x0, y0, 0, x1, y1, H, 'damask', bottom='floor', top='plaster'))
    # a shallow barrel vault
    pr = arch_profile((x0 + x1) / 2, x1 - x0, H - 0.05, 0.05, 24, rise=1.1)
    R.cut(prism(pr, 'y', y0, y1, arch_mats(len(pr), 'plaster', 'plaster'), cap='plaster'))
    R.meta['box'] = [[x0, 0, y0], [x1, H + 1.1, y1]]
    false_case(R)
    # shelves on the side walls and the back wall
    for (a, b) in ((0.9, 3.0), (3.3, 6.8)):
        wall_shelf(R, '+x', a, b, 0, rows=6, off=x0, frame='walnut')
        wall_shelf(R, '-x', a, b, 0, rows=6, off=x1, frame='walnut')
    wall_shelf(R, '-y', x0 + 0.5, x1 - 0.5, 0, rows=6, off=y1, frame='walnut')
    # the reading nook: a rug, three armchairs round a little table with a candelabrum
    R.nocol.add(box(5.6, 3.0, 0, 10.4, 6.4, 0.012, 'oxblood', skip=('-z',)))
    R.nocol.add(box(5.85, 3.25, 0.012, 10.15, 6.15, 0.018, 'carpet', skip=('-z',)))
    armchair(R, 6.5, 4.9, -0.25)
    armchair(R, 9.5, 4.9, math.pi + 0.25)
    armchair(R, 8.0, 5.95, -math.pi / 2)
    R.parts.add(cyl(8, 4.6, 0, 0.55, 0.06, 8, side='walnut', caps=False))
    R.parts.add(cyl(8, 4.6, 0.55, 0.6, 0.45, 16, side='walnut', top='walnut', bottom='walnut'))
    R.nocol.add(cyl(8, 4.6, 0.6, 0.9, 0.025, 6, side='brass', caps=False))
    R.nocol.add(box(7.75, 4.58, 0.88, 8.25, 4.62, 0.91, 'brass'))
    for dx in (-0.25, 0.0, 0.25):
        R.light(cyl(8 + dx, 4.6, 0.91 + (0.06 if dx == 0 else 0), 1.03 + (0.06 if dx == 0 else 0), 0.018, 6, side='e_candle', top='e_candle', bottom='e_candle'))
    book(R, 7.7, 4.35, 0.6, 0.5, 'oxblood', open_=True)
    # a lamp with a fringed shade hanging low over the table
    pendant(R, 8, 4.6, 2.05, r=0.22, m='e_amber', top=H + 1.0, shade='velvet')
    book(R, 8.35, 4.8, 0.6, 1.9, 'green')
    # candle sconces on the walls
    for y in (3.15, 6.95):
        for (x, s) in ((x0 + 0.06, 1), (x1 - 0.06, -1)):
            R.nocol.add(box(x - 0.05, y - 0.06, 1.7, x + 0.05, y + 0.06, 1.75, 'brass'))
            R.light(cyl(x + s * 0.02, y, 1.75, 1.9, 0.02, 6, side='e_candle', top='e_candle', bottom='e_candle'))
            R.light(sphere(x + s * 0.12, y, 2.05, 0.1, 8, 4, 'e_amber'))
    loop(R, [(8, 1.5), (8, 2.6), (5.3, 2.6), (5.3, 6.6), (10.7, 6.6), (10.7, 2.6), (8, 2.6)], close=False)
    R.spot('probe', 8, 2.4, 1.6)
    R.meta.update(label='The Hidden Reading Room', weight=2,
                  blurb='The bookcase was not really there. Behind it, somebody kept a little room of their own, and left the candles burning.')
    return R
