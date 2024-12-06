# cal_achromatic.py

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from hdrp import srgb, gamma, gammainv, TonemapCube

a = np.array((4,8,5)).reshape((1,3))
r = np.array((90,50,10)).reshape((1,3))
g = np.array((20,100,10)).reshape((1,3))
b = np.array((10,20,70)).reshape((1,3))
rgb = np.vstack((r,g,b))

mat = np.array([[1,0,0],[0,1,0],[0,0,1],[1,1,1]])
v_k = [(k**2.2) * mat for k in np.linspace(0.1,1,10)]
v_k = np.vstack(v_k)
v_k = np.vstack([np.array((0,0,0)).reshape(1,3), v_k])

xyz = v_k @ rgb + a
xyz += np.random.normal(scale=2, size=xyz.shape)

# pick up here

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
