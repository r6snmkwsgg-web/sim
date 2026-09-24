"""The Sea of Shelves: a room 96 m square under a ceiling you could touch on tiptoe. Double-faced
stacks in rows every 3.2 m, broken by cross aisles that line up with the doorways, lamps in a grid
over the aisles, a few of them dead. It goes on further than the eye can follow in the haze."""
from lib import *
from kit_g import *
import random


def make():
    R = Room('seaofshelves', 6, 6, levels=2, res=2048)
    W, D = R.W, R.D
    H = 3.2
    seal(R, upper_sockets(R), floor='floor', wall='tile')
    R.cut(box(T - 0.02, T - 0.02, 0, W - T + 0.02, D - T + 0.02, H, 'tile', bottom='floor', top='plaster'))
    rnd = random.Random(808)
    # stacks along x, a row every 4 m; cross aisles 4 m wide on the doorway lines
    segs = [(T + 2.2, 6.0)] + [(i * C + 10.0, i * C + 22.0) for i in range(R.w - 1)] + [(W - 6.0, W - T - 2.2)]
    rows_y = [2.0 + 4.0 * m for m in range(int(D / 4.0))]
    for y in rows_y:
        for (a, b) in segs:
            stack2(R, a, b, y, rows=5, row_h=0.4, half=0.33, frame='oak')
    # lamps over every other aisle, in a grid; some dead
    for m in range(int(D / 4.0)):
        y = 4.0 * m
        for i in range(2 * R.w):
            x = i * 8.0 + (4.0 if m % 2 else 8.0)
            if y < 1 or x > W - 2 or rnd.random() < 0.12 or (abs((x - 8) % C) < 0.1 and abs((y - 8) % C) < 0.1): continue
            R.light(box(x - 0.7, y - 0.22, H - 0.03, x + 0.7, y + 0.22, H - 0.01, 'e_fluor', skip=('+z',)))
    # and some on the doorway aisles
    for j in range(R.d):
        for i in range(R.w):
            R.light(box(i * C + C / 2 - 0.4, j * C + C / 2 - 0.4, H - 0.03, i * C + C / 2 + 0.4, j * C + C / 2 + 0.4, H - 0.01, 'e_amber', skip=('+z',)))
    # walkers: the perimeter aisle and a cross of doorway aisles
    e = 1.45
    per = [R.navpt(x, y) for (x, y) in ((e, 8), (W / 2 + 8, 8), (W - e, 8), (W - e, D / 2 + 8), (W - e, D - 8), (W / 2 + 8, D - 8), (e, D - 8), (e, D / 2 + 8))]
    R.link(*per, per[0])
    R.link(per[7], R.navpt(W / 2 + 8, D / 2 + 8), per[3])
    c = len(R.nav) - 1
    R.link(per[1], c, per[5])
    R.spot('probe', W / 2 + 8, D / 2 + 8, 1.7)
    R.meta.update(label='The Sea of Shelves', weight=3,
                  blurb='Stacks, and aisles, and stacks, under a ceiling low enough to be personal. Somewhere out there a lamp is buzzing, which is odd, because none of them are electric.')
    R.meta['box'] = [[T, 0, T], [W - T, H, D - T]]
    return R
