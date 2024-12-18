# cal_achromatic_1.py

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from hdrp import srgb, srgbinv, h, hinv, TonemapCube

# make an array of the post-processed values v_k displayed for the characterization measurements
v_k = np.linspace(0, 1, 11)

# make an array of the luminances recorded during the characterization measurements
# - here we'll make up some measurements; alternatively, replace 'lum' with an array of real luminance measurements
lum = 5 + 95*(v_k ** 2.2) + np.random.normal(scale=2, size=v_k.shape)

# fit a gamma function to luminance vs. v_k

# step 1. define the achromatic display model; see equation (6)
def v2lum(v, L0, L1, v0, gamma):
    return L1 * h(v, v0, gamma) + L0

# step 2. define a sum-of-squares error function
def errfn(param):
    return ((lum - v2lum(v_k, *param))**2).sum()

# step 3. find parameters that minimize the error
pinit = np.array((min(lum), max(lum)-min(lum), 0, 2.2))  # reasonable guesses for parameters
cons = optimize.LinearConstraint(np.array((0,0,1,0)).reshape((1,4)), np.array((0,)))  # constrain v0 >= 0
r = optimize.minimize(errfn, pinit, constraints=cons)
phat = r.x
print(r)

# plot the data and the fit
vv = np.linspace(0,1,100)
plt.plot(vv, v2lum(vv, *phat), 'k-')
plt.plot(v_k, lum, 'ro', markersize=10)
plt.legend(['fit', 'measurements'], frameon=False)
plt.xlabel('post-processed v_k', fontsize=18)
plt.ylabel('luminance (cd/m$^2$)', fontsize=18)
plt.show(block=False)
plt.pause(2)
plt.close()

# define the tonemapping function for gamma correction; see equation (15)
# - here we implicitly set r = 1, so the displayable range of u_k is [0, 1]
# - clipping of the input to h to [0, 1] is done by h, so we don't need an explicit max(x, 0) as in equation (15)
def f(u_k):
    L0, L1, v0, gamma = phat
    w = L1/L0
    return srgb(hinv((1+w)*u_k - w, v0, gamma))

# create a tonemapping object by applying the tonemapping function f to the knot points
tonemap = TonemapCube()
k1 = (tonemap.u_knot<(1/255)).nonzero()[0][-1]  # first knot point below u_knot = 1/255
k2 = (tonemap.u_knot>1).nonzero()[0][0]         # first knot point above u_knot = 1
t_knot = f(tonemap.u_knot)
t_knot[(k2+1):] = 1
tonemap.setchannels(t_knot)

# we can make the tonemapping object's approxmation to f a bit better by optimizing t_knot
# - step 1. create an objective function that finds the sum-of-squares error between f and
#   the approximation from the tonemapping object
uu = np.linspace(0,1,100)
fuu = f(uu)
uu3 = np.column_stack((uu,uu,uu))
def errfn(p):
    t_knot[k1:k2] = p
    tonemap.setchannels(t_knot)
    vv = tonemap.apply(uu3)
    return ((vv[:,0]-fuu)**2).sum()
# - step 2. find the values at knot points that minimize the objective function
pinit = t_knot[k1:k2]
r = optimize.minimize(errfn, pinit)
t_knot[k1:k2] = r.x

# save the cube file to use for gamma correction
tonemap.save('cube/linearize_achromatic.cube')
