import numpy as np
import matplotlib.pyplot as plt
from hdrp import TonemapCube

def clip(x):
    k = (x>1).nonzero()[0]
    if len(k) >= 2:
        x[k[1]:] = 1
    return x

def plot(t):
    plt.plot(t.u_knot, t.cubeR[:,0,0], 'ro-')
    plt.xlim((t.u_knot[2], t.u_knot[-1]))
    plt.xscale('log')
    plt.xlabel('unprocessed input $u_k$')
    plt.ylabel('tonemapped output $t_k$')
    plt.title(t.filename)

t = TonemapCube()

# square; maps [0, 1] to [0, 1]
t_knot = t.u_knot ** 2
t_knot = clip(t_knot)
t.setchannels(t_knot)
t.save('cube/square_max1.cube')
plot(t) ; plt.show()

# square; maps [0, 58] to [0, 1]
t_knot = (t.u_knot/58) ** 2
t_knot = clip(t_knot)
t.setchannels(t_knot)
t.save('cube/square_max58.cube')
plot(t) ; plt.show()

# square root; maps [0, 1] to [0, 1]
t_knot = t.u_knot ** 0.5
t_knot = clip(t_knot)
t.setchannels(t_knot)
t.save('cube/square_root_max1.cube')
plot(t) ; plt.show()

# square root; maps [0, 58] to [0, 1]
t_knot = (t.u_knot/58) ** 0.5
t_knot = clip(t_knot)
t.setchannels(t_knot)
t.save('cube/square_root_max58.cube')
plot(t) ; plt.show()

# linear; maps [0, 1] to [0, 1]
t_knot = t.u_knot.copy()
t_knot = clip(t_knot)
t.setchannels(t_knot)
t.save('cube/linear_max1.cube')
plot(t) ; plt.show()

# linear; maps [0, 58] to [0, 1]
t_knot = t.u_knot/58
t_knot = clip(t_knot)
t.setchannels(t_knot)
t.save('cube/linear_max58.cube')
plot(t) ; plt.show()

# I've commented out the code that generates cube files for delta functions,
# which are used in the project render_delta, because we don't need
# these 32 files outside that project. but this is how they're generated.

## delta functions
#for m in range(1, 33):
#    t_knot = np.zeros(t.u_knot.shape)
#    t_knot[m-1] = 1
#    t.setchannels(t_knot)
#    t.save(f'cube/delta_{m:02d}.cube')
