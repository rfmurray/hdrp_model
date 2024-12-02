import numpy as np
from hdrp import TonemapCube

t = TonemapCube()

t_knot = t.u_knot ** 2
t.setchannels(t_knot)
t.save('square.cube')

t_knot = t.u_knot ** 0.5
t.setchannels(t_knot)
t.save('square_root.cube')

t_knot = np.zeros(t.u_knot.shape)
t_knot[15] = 1
t.setchannels(t_knot)
t.save('delta_16.cube')

t_knot = t.u_knot
t.setchannels(t_knot)
t.save('identity.cube')

t_knot = np.zeros(t.u_knot.shape)
t_knot[0::2] = 0.1
t_knot[1::2] = 0.9
t.setchannels(t_knot)
t.save('sawtooth.cube')
