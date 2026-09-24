"""The Scissor Stairs: an open square shaft in the middle of each floor, and straight flights
zigzagging up it round an open well, a landing every half floor. Up or down, the same flights."""
from lib import *
from kit_e import *


def make():
    R = Room('scissor', 1, 1, res=1024, repeat=True, lo=-0.4)
    R.sockets(floor='terrazzo')
    xa, xw, xe, xb = 3.4, 5.0, 11.0, 12.6      # shaft: W landing xa..xw, flights xw..xe, E landing xe..xb
    ya, y1, y2, yb = 3.4, 4.9, 11.1, 12.6      # S band ya..y1, well y1..y2, N band y2..yb
    hz = LH / 2
    n, rs, rn = 20, hz / 20, 0.3
    R.cut(box(T - 0.02, T - 0.02, 0, C - T + 0.02, C - T + 0.02, TOP, 'tile', bottom='terrazzo', top='plaster'))
    R.cut(box(xw, ya, -LH, xb, yb, 2 * LH, 'tile'))            # the shaft, less the W landing, through every floor
    # the two flights of this floor, and the east landing half way up
    flight_x(R, xw, ya, 0.0, y1 - ya, n, rs, rn, 1, m='terrazzo', side='tile')
    flight_x(R, xe, y2, hz, yb - y2, n, rs, rn, -1, m='terrazzo', side='tile')
    R.parts.add(box(xe, ya, hz - 0.3, xb, yb, hz, 'tile', top='terrazzo'))
    # rails and parapets
    ph = 0.95
    # the S flight: a solid parapet on the gallery side, from the floor up, running on round the E landing
    R.parts.add(wedge((xw, ya - 0.1), (xe, ya - 0.1), 0.2, 0.0, 0.0, ph, hz + ph, 'tile'))
    R.parts.add(wedge((xw - 0.03, ya - 0.1), (xe, ya - 0.1), 0.26, ph, hz + ph, ph + 0.06, hz + ph + 0.06, 'brass'))
    R.parts.add(box(xe, ya - 0.2, 0, xb + 0.2, ya, hz + ph, 'tile'))
    R.parts.add(box(xe, ya - 0.23, hz + ph, xb + 0.23, ya + 0.03, hz + ph + 0.06, 'brass'))
    # the gallery's edge round the rest of the shaft (east and north), and the landing's and N flight's rails
    rail(R, [(xb + 0.1, ya, 0.0), (xb + 0.1, yb + 0.1, 0.0), (xw, yb + 0.1, 0.0)])
    rail(R, [(xb - 0.04, ya, hz), (xb - 0.04, yb - 0.04, hz)])
    rail(R, [(xb - 0.04, yb - 0.04, hz), (xe, yb - 0.04, hz), (xw, yb - 0.04, LH)])
    # the well's edges
    rail(R, [(xw + 0.04, y1 - 0.04, 0.0), (xe, y1 - 0.04, hz), (xe + 0.04, y1 - 0.04, hz), (xe + 0.04, y2 + 0.04, hz), (xe, y2 + 0.04, hz), (xw, y2 + 0.04, LH)])
    rail(R, [(xw + 0.04, y1, 0.0), (xw + 0.04, y2, 0.0)])
    # newel posts with lamps at the landing corners
    for (x, y, z) in ((xw + 0.04, y1 - 0.04, 0.0), (xw + 0.04, y2 + 0.04, 0.0), (xe + 0.04, y1 - 0.04, hz), (xe + 0.04, y2 + 0.04, hz)):
        R.parts.add(box(x - 0.1, y - 0.1, z, x + 0.1, y + 0.1, z + 1.15, 'bronze', skip=('-z',)))
        R.light(sphere(x, y, z + 1.32, 0.14, 10, 6, 'e_lamp'))
        R.light(box(x - 0.06, y - 0.06, z + 1.15, x + 0.06, y + 0.06, z + 1.2, 'e_amber'))
    # books round the walls; lamps over the gallery
    wall_shelves(R, rows=9, frame='walnut', segs_x=CELL_SEGS, segs_y=CELL_SEGS)
    for (x, y) in ((1.9, 1.9), (C - 1.9, 1.9), (1.9, C - 1.9), (C - 1.9, C - 1.9)):
        pendant(R, x, y, 3.8, TOP, r=0.35)
    for (x, y) in ((C / 2, 1.8), (C / 2, C - 1.8), (1.8, C / 2), (C - 1.8, C / 2)):
        R.light(cyl(x, y, TOP - 0.05, TOP - 0.02, 0.45, 20, side='e_panel', top='e_panel', bottom='e_panel'))
    # a light under the E landing and under each flight's soffit
    R.light(box(xe + 0.3, ya + 0.3, hz - 0.33, xb - 0.3, yb - 0.3, hz - 0.3, 'e_panel'))
    # walkers: the gallery, the W landing, up the S flight to the E landing, up the N flight to the next floor
    gl = loop(R, [(1.9, 1.9), (8.0, 1.9), (C - 1.9, 1.9), (C - 1.9, 8.0), (C - 1.9, C - 1.9), (8.0, C - 1.9), (1.9, C - 1.9), (1.9, 8.0)])
    w0 = R.navpt(4.2, 4.15); w1 = R.navpt(4.2, 8.0); w2 = R.navpt(4.2, 11.85)
    R.link(gl[7], w1, w0); R.link(w1, w2)
    e0 = R.navpt(11.8, 4.15, hz); e1 = R.navpt(11.8, 11.85, hz)
    R.link(w0, e0, e1)
    t = R.navpt(xw + 0.3, 11.85, LH - 0.2); R.link(e1, t)
    R.spot('edge', xw - 0.6, C / 2, 0.0, 0.0)
    R.spot('probe', 2.0, 8.0, 1.7)
    R.meta.update(label='The Scissor Stairs', weight=35,
                  blurb='Flights of stairs zigzag up an open shaft, a landing every half floor. From the rail you can see them going up out of sight and down out of sight, identical, the whole way.')
    R.meta['shaft'] = [xw, y1, xe, y2]
    R.meta['box'] = [[T, 0, T], [C - T, TOP, C - T]]
    return R
