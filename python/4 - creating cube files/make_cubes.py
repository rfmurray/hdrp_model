# make_cubes.py  Make cube files for tonemapping

import numpy as np
import matplotlib.pyplot as plt
from hdrp import TonemapCube

def clip(x):
    'set the elements of a 1D array to one, after the first element greater than one'
    k = (x>1).nonzero()[0]
    if len(k) >= 2:
        x[k[1]:] = 1
    return x

def plot_red(t):
    'plot the red channel of a tonemapping table that processes the three color channels independently'
    plt.plot(t.u_knot, t.cube[:,0,0,0], 'ro-')
    plt.xlim((t.u_knot[2], t.u_knot[-1]))
    plt.xscale('log')
    plt.xlabel('unprocessed input $u_r$')
    plt.ylabel('tonemapped output $t_r$')
    plt.title(t.filename)

# create tonemapping object
t = TonemapCube()

# tonemapping function is square (u_k ** 2); maps [0, 1] to [0, 1]
t_knot = t.u_knot ** 2
t_knot = clip(t_knot)
t.setchannels(t_knot)
t.save('cube/square_max1.cube')
plot_red(t) ; plt.show()

# tonemapping function is scaled square ((x/58) ** 2); maps [0, 58] to [0, 1]
t_knot = (t.u_knot/58) ** 2
t_knot = clip(t_knot)
t.setchannels(t_knot)
t.save('cube/square_max58.cube')
plot_red(t) ; plt.show()

# tonemapping function is square root (u_k ** 0.5); maps [0, 1] to [0, 1]
t_knot = t.u_knot ** 0.5
t_knot = clip(t_knot)
t.setchannels(t_knot)
t.save('cube/square_root_max1.cube')
plot_red(t) ; plt.show()

# tonemapping function is scaled square root((u_k/58) ** 0.5); maps [0, 58] to [0, 1]
t_knot = (t.u_knot/58) ** 0.5
t_knot = clip(t_knot)
t.setchannels(t_knot)
t.save('cube/square_root_max58.cube')
plot_red(t) ; plt.show()

# tonemapping is linear; maps [0, 1] to [0, 1]
t_knot = t.u_knot.copy()
t_knot = clip(t_knot)
t.setchannels(t_knot)
t.save('cube/linear_max1.cube')
plot_red(t) ; plt.show()

# tonemapping is linear; maps [0, 58] to [0, 1]
t_knot = t.u_knot/58
t_knot = clip(t_knot)
t.setchannels(t_knot)
t.save('cube/linear_max58.cube')
plot_red(t) ; plt.show()

# this code generates cube files for delta functions, which are used in the
# project render_delta; commented out here because we don't usually need
# these 32 files outside that project
# for m in range(1, 33):
#    t_knot = np.zeros(t.u_knot.shape)
#    t_knot[m-1] = 1
#    t.setchannels(t_knot)
#    t.save(f'cube/delta_{m:02d}.cube')
