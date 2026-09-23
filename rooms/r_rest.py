"""A rest area, as in the book: a kiosk that feeds you, cots, a washroom, a plaque with the rules.
Here it is a low mint-tiled room with coffered skylights and a small round plunge pool."""
from lib import *


def make():
    R = Room('rest', 1, 1, res=1024)
    R.sockets(wall='mint')
    H = 4.2
    R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, C - T + 0.02, H, 'mint', bottom='floor', top='plaster'))
    # coffers with light panels
    for (x, y) in ((4.6, 4.6), (11.4, 4.6), (4.6, 11.4), (11.4, 11.4)):
        R.cut(box(x - 1.3, y - 1.3, H - 0.05, x + 1.3, y + 1.3, H + 0.35, 'plaster'))
        R.light(box(x - 1.05, y - 1.05, H + 0.28, x + 1.05, y + 1.05, H + 0.31, 'e_panel'))
    R.cut(cyl(8, 8, H - 0.05, H + 0.5, 1.1, 32, side='plaster', top='plaster', bottom='plaster'))
    R.light(cyl(8, 8, H + 0.42, H + 0.45, 1.1, 32, side='e_sky', top='e_sky', bottom='e_sky'))
    # plunge pool under the round skylight
    R.round_pool(8, 8, 1.75, 1.2, segs=48)
    for k in range(3):
        a = k * 2 * math.pi / 3 + 0.4
        R.light(box(-0.18, -0.04, -0.7, 0.18, 0.04, -0.5, 'e_pool').xform(a + math.pi / 2, 8 + math.cos(a) * 1.74, 8 + math.sin(a) * 1.74))
    # cots in two arched alcoves on the east wall
    beds = []
    for yc in (3.3, 12.7):
        pa = arch_profile(yc, 2.5, 0, 1.7, 16)
        R.cut(prism(pa, 'x', C - T - 2.35, C - T + 0.02, arch_mats(len(pa), 'floor', 'mint')))
        x0 = C - T - 2.2
        R.parts.add(box(x0 + 0.05, yc - 0.5, 0, x0 + 2.12, yc + 0.5, 0.42, 'bed', skip=('-z',)))              # mattress
        R.parts.add(box(x0 + 1.62, yc - 0.38, 0.42, x0 + 2.05, yc + 0.38, 0.55, 'bed', skip=('-z',)))       # pillow
        R.parts.add(box(x0 + 0.02, yc - 0.54, 0, x0 + 2.16, yc + 0.54, 0.16, 'oak', skip=('-z',)))          # frame
        R.light(box(C - T - 0.1, yc - 0.12, 1.5, C - T - 0.05, yc + 0.12, 1.62, 'e_amber'))                 # reading lamp
        beds.append(R.spot('bed', x0 + 1.1, yc, 0.5, math.pi / 2))
    # washroom door in a recess on the west wall
    R.cut(box(0.12, 2.55, 0, T + 0.02, 3.85, 2.3, 'mint', bottom='floor'))
    R.parts.add(box(0.14, 2.6, 0, 0.19, 3.8, 2.25, 'oak'))
    R.parts.add(box(0.19, 3.62, 1.0, 0.24, 3.7, 1.12, 'brass'))
    R.light(box(0.2, 2.9, 2.36, 0.24, 3.5, 2.5, 'e_amber'))      # the little sign above it
    R.spot('bath', T + 0.12, 3.2, 0, 0)
    # the kiosk, glowing, against the north wall
    kx = 3.3
    R.parts.add(box(kx - 0.8, C - T - 0.85, 0, kx + 0.8, C - T + 0.01, 2.35, 'kiosk', skip=('-z',)))
    R.parts.add(box(kx - 0.86, C - T - 0.9, 2.35, kx + 0.86, C - T + 0.01, 2.5, 'brass'))
    R.light(box(kx - 0.6, C - T - 0.87, 1.15, kx + 0.6, C - T - 0.85, 1.95, 'e_kiosk'))
    R.parts.add(box(kx - 0.35, C - T - 0.95, 0.75, kx + 0.35, C - T - 0.85, 0.95, 'black'))   # the slot
    R.spot('kiosk', kx, C - T - 0.9, 0, 0)
    # the plaque with the rules
    R.parts.add(box(11.8, C - T - 0.04, 1.1, 13.4, C - T + 0.01, 2.1, 'brass'))
    R.spot('plaque', 12.6, C - T - 0.03, 0, 0)
    # books along the south wall and the west wall
    for (a, b) in ((0.7, 6.1), (9.9, C - 0.7)):
        R.shelf(a, T, 0, b - a, '+y', rows=6, frame='oak')
    for (a, b) in ((4.4, 6.1), (9.9, C - 0.7)):
        R.shelf(T, b, 0, b - a, '+x', rows=6, frame='oak')
    # benches round the pool
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        R.parts.add(box(-0.9, -0.25, 0, 0.9, 0.25, 0.45, 'mint', skip=('-z',)).xform(a + math.pi / 2, 8 + math.cos(a) * 3.4, 8 + math.sin(a) * 3.4))
    ring = [R.navpt(8 + math.cos(k * math.pi / 4) * 2.6, 8 + math.sin(k * math.pi / 4) * 2.6) for k in range(8)]
    R.link(*ring, ring[0])
    outer = [R.navpt(8 + math.cos(k * math.pi / 2) * 5.6, 8 + math.sin(k * math.pi / 2) * 5.6) for k in range(4)]
    for k in range(4): R.link(outer[k], ring[k * 2])
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        R.spot('sit', 8 + math.cos(a) * 3.4, 8 + math.sin(a) * 3.4, 0.45, a + math.pi)
    R.spot('probe', 8, 8, 1.6)
    R.meta['label'] = 'A rest area'
    R.meta['box'] = [[T, -1.3, T], [C - T, H, C - T]]
    return R
