# cal_achromatic.py

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from hdrp import srgb, gamma, gammainv, TonemapCube

# make an array of calibration stimuli
v_k = np.linspace(0, 1, 11)

# make up some luminance measurements
lum = 5 + 95*(v_k**2.2) + np.random.normal(scale=2, size=v_k.shape)

# fit a gamma function to luminance vs. v_k
def errfn(param):
    return ((lum - gamma(v_k, *param))**2).sum()
pinit = np.array((max(lum)-min(lum), 0, 2.2, min(lum)))
cons = optimize.LinearConstraint(np.array((0,1,0,0)).reshape((1,4)), np.array((0,)))
r = optimize.minimize(errfn, pinit, constraints=cons)
phat = r.x
print(r)

# plot data and fit
xx = np.linspace(0,1,1000)
plt.plot(xx, gamma(xx, *phat), 'k-')
plt.plot(v_k, lum, 'ro', markersize=10)
plt.xlabel('post-processed v_k', fontsize=18)
plt.ylabel('luminance (cd/m$^2$)', fontsize=18)
plt.show()

# - we can parameterize the display transfer function (equation (6)) using hdrp.gamma()
# def h(v_k):
#     return gamma(v_k, *phat)
#
# - then we can define the normalized display transfer function; see text just before equation (12)
# def hstar(v_k):
#     return gamma(v_k, *phat) / gamma(1, *phat)
#
# - for gamma correction, we need the inverse of hstar(), which we find as follows.
# - hstar() maps post-processed coordinates v_k to normalized luminance, Lstar = L / Lmax.
#     Lstar = hstar(v_k)
#           = gamma(v_k, *phat) / gamma(1, *phat)
# - which then inverts to the following.
#     gamma(v_k, *phat) = Lstar * gamma(1, *phat)
#     v_k = gammainv(Lstar * gamma(1, *phat), *phat)

# inverse of normalized display transfer function
def hstarinv(Lstar):
    return gammainv(Lstar * gamma(1,*phat), *phat)

# tonemapping function for gamma correction; equation (13); here I've set r = 1
def f(u_k):
    return srgb(hstarinv(u_k))

# - check that hstarinv() and f() are correct
# - check that they take care of domain and range correctly
# - may need to use versions of gamma() and gammainv() that don't clip above v_k = 1

# create a cube file with tonemapping function f() applied to knot points
tonemap = TonemapCube()
t_knot = f(tonemap.u_knot)
tonemap.setchannels(t_knot)
tonemap.save('linearize1.cube')

# plot f() and the approximation from the tonemap object

# optimize t_knot

# plot f() and the approximation from the tonemap object again
