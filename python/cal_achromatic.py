# cal_achromatic.py

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from hdrp import srgb, gamma, gammainv, TonemapCube

v_k = np.linspace(0, 1, 10)

lum = 5 + 95*(v_k**2.2) + np.random.normal(scale=2, size=v_k.shape)

def errfn(param):
    return ((lum - gamma(v_k, *param))**2).sum()
pinit = np.array((max(lum)-min(lum), 0, 2.2, min(lum)))
cons = optimize.LinearConstraint(np.array((0,1,0,0)).reshape((1,4)), np.array((0,)))
r = optimize.minimize(errfn, pinit, constraints=cons)
phat = r.x
print(r)

xx = np.linspace(0,1,1000)
plt.plot(xx, gamma(xx, *phat), 'k-')
plt.plot(v_k, lum, 'ro', markersize=10)
plt.xlabel('unprocessed v_k', fontsize=18)
plt.ylabel('luminance (cd/m$^2$)', fontsize=18)
plt.show()

# def h(v_k):
#     return gamma(v_k, *phat)
#
# def hstar(v_k):
#     return gamma(v_k, *phat) / gamma(1, *phat)

def hstarinv(lumstar):
    return gammainv(lumstar*gamma(1,*phat), *phat)  # check this

def f(u_k):
    return srgb(hstarinv(u_k))

tonemap = TonemapCube()
t_knot = f(tonemap.u_knot)
tonemap.setchannels(t_knot)
tonemap.save('linearize1.cube')

# optimize t_knot
