"""The Dead End: plain stone corridors in a cross, long and empty, lit by humming strip lamps. At
the end of each arm there is a doorway with its frame and its green sign. Only one of them is a
door; the other three are just the idea of one."""
from lib import *
from kit_d import *


def make():
    R = Room('deadend', 1, 1, res=1024)
    shell(R, None, floor='terrazzo', wall='tile', seal=('N', 'E', 'W'))
    H, hw = 4.9, 1.6                     # corridor height, half width
    door_arch_cut(R, 'S', 2.6, floor='terrazzo')
    R.cut(box(M - hw, T - 0.02, 0, M + hw, C - T + 0.02, H, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(T - 0.02, M - hw, 0, C - T + 0.02, M + hw, H, 'tile', bottom='terrazzo', top='plaster'))
    R.meta['box'] = [[T, 0, T], [C - T, H, C - T]]
    # the three doorways that are not
    for s in 'NEW':
        fake_door(R, s, floor='terrazzo', wall='tile', frame='walnut', sign=True, leaf=None, depth=0.25)
    # a real sign over the real door, the same as the others
    R.nocol.add(box(M - 0.3, T, DJ + DR + 0.45, M + 0.3, T + 0.07, DJ + DR + 0.72, 'iron'))
    R.light(box(M - 0.26, T + 0.07, DJ + DR + 0.48, M + 0.26, T + 0.08, DJ + DR + 0.69, 'e_exit'))
    # a skirting of dark stone, and a long run of strip lamps down every arm
    for (x0, y0, x1, y1) in ((M - hw, I0, M - hw + 0.03, M - hw), (M + hw - 0.03, I0, M + hw, M - hw),
                             (M - hw, M + hw, M - hw + 0.03, I1), (M + hw - 0.03, M + hw, M + hw, I1),
                             (I0, M - hw, M - hw, M - hw + 0.03), (I0, M + hw - 0.03, M - hw, M + hw),
                             (M + hw, M - hw, I1, M - hw + 0.03), (M + hw, M + hw - 0.03, I1, M + hw)):
        R.nocol.add(box(x0, y0, 0, x1, y1, 0.18, 'slate', skip=('-z',)))
    k = 0
    for t in (2.2, 4.4, 6.6, 9.4, 11.6, 13.8):
        k += 1
        dead = k == 5
        m = 'e_dim' if dead else 'e_fluor'
        R.light(box(M - 0.12, t - 0.6, H - 0.04, M + 0.12, t + 0.6, H - 0.02, m))
        if t != 2.2: R.light(box(t - 0.6, M - 0.12, H - 0.04, t + 0.6, M + 0.12, H - 0.02, 'e_fluor'))
    R.light(box(M - 0.6, M - 0.6, H - 0.04, M + 0.6, M + 0.6, H - 0.02, 'e_fluor'))
    # night: amber lamps low on the walls at the crossing
    for (x, y) in ((M - hw + 0.04, M - hw - 0.9), (M + hw - 0.04, M + hw + 0.9)):
        R.light(box(x - 0.03, y - 0.12, 0.35, x + 0.03, y + 0.12, 0.5, 'e_amber'))
    # one bench in the crossing, for waiting
    R.parts.add(box(M + 0.6, M - hw + 0.1, 0, M + 2.4, M - hw + 0.55, 0.45, 'walnut', skip=('-z',)))
    R.spot('sit', M + 1.5, M - hw + 0.33, 0.45, math.pi / 2)
    loop(R, [(M, 1.4), (M, M), (M, I1 - 1.0)], close=False)
    loop(R, [(I0 + 1.0, M), (M, M), (I1 - 1.0, M)], close=False)
    R.spot('probe', M, 5.0, 1.6)
    R.meta.update(label='The Dead End', weight=3,
                  blurb='Four doors, four signs. Three of them are painted on. You check all three anyway, and so does everybody.')
    return R
