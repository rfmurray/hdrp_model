import numpy as np
from hdrp import TonemapCube

t = TonemapCube()

# square
t_knot = t.u_knot ** 2
t.setchannels(t_knot)
t.save('cube/square.cube')

# square root
t_knot = t.u_knot ** 0.5
t.setchannels(t_knot)
t.save('cube/square_root.cube')

# identity
t_knot = t.u_knot
t.setchannels(t_knot)
t.save('cube/identity.cube')

# sawtooth
t_knot = np.zeros(t.u_knot.shape)
t_knot[0::2] = 0.1
t_knot[1::2] = 0.9
t.setchannels(t_knot)
t.save('cube/sawtooth.cube')

## delta functions
#for m in range(1, 33):
#    t_knot = np.zeros(t.u_knot.shape)
#    t_knot[m-1] = 1
#    t.setchannels(t_knot)
#    t.save(f'cube/delta_{m:02d}.cube')
