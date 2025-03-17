# char_achromatic_1.py  Characterize achromatic stimulus display and generate a cube file
#                       for gamma correction

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize
from hdrp import srgb, srgbinv, h, hinv, TonemapCube

# load luminance characterization measurements, made with tonemapping off
df = pd.read_csv('data/characterize/data_achromatic_T0.txt')
m_k = df['m_k'].to_numpy()
lum = df['lum'].to_numpy()
v_k = m_k

# fit a gamma function to luminance vs. v_k

# step 1. define the achromatic display model; see equation (6)
def v2lum(v, L0, L1, v0, gamma):
    return L1 * h(v, v0, gamma) + L0

# step 2. define a sum-of-squares error function
def errfn(param):
    return ((lum - v2lum(v_k, *param))**2).sum()

# step 3. find parameters that minimize the error
pinit = np.array((min(lum), max(lum)-min(lum), 0, 4))  # reasonable guesses for parameters
cons = optimize.LinearConstraint(np.array((0,0,1,0)).reshape((1,4)), np.array((0,)))  # constrain v0 >= 0
r = optimize.minimize(errfn, pinit, constraints=cons)
phat = r.x
print(r)

# plot the data and the fit
vv = np.linspace(0,1,100)
plt.plot(vv, v2lum(vv, *phat), 'k-')
plt.plot(v_k, lum, 'ro', markersize=10)
plt.legend(['fit', 'measurements'], frameon=False)
plt.xlabel('post-processed $v_k$', fontsize=18)
plt.ylabel('luminance (cd/m$^2$)', fontsize=18)
plt.show()

# define the tonemapping function for gamma correction; see equation (15)
# - here we implicitly set r = 1, so the displayable range of u_k is [0, 1]
# - clipping of the input to hinv to a lower bound of zero is done by hinv itself,
#   so we don't need an explicit max(x, 0) as in equation (15)
def f(u_k):
    L0, L1, v0, gamma = phat
    w = L0/L1
    return srgb(hinv((1+w)*u_k - w, v0, gamma, maxout=False), maxout=False)
    # in order for tonemapping to work for u_k over the full range [0, 1],
    # we need to set the output value, at the first knot point u_knot that is
    # greater than one, to a value greater than one. normally the functions
    # srgb and hinv clip their inputs to [0, 1], so here we pass the optional
    # argument maxout=False, so that instead they clip their inputs to [0, np.inf]

# create a tonemapping object by applying the tonemapping function f to the knot points
tonemap = TonemapCube()
t_knot = f(tonemap.u_knot)
k1 = (tonemap.u_knot<(1/255)).nonzero()[0][-1]  # first knot point in u_knot below 1/255
k2 = (tonemap.u_knot>1).nonzero()[0][0]         # first knot point in u_knot above 1
t_knot[(k2+1):] = 1
tonemap.setchannels(t_knot)

# we can make the tonemapping object's approxmation to f a bit better by optimizing t_knot
# - step 1. create an objective function that finds the sum-of-squares error between f and
#   the approximation from the tonemapping object
uu = np.linspace(0,1,100)
fuu = f(uu)
uu3 = np.column_stack((uu,uu,uu))
def errfn(param):
    t_knot[k1:k2+1] = param
    tonemap.setchannels(t_knot)
    vv = tonemap.apply(uu3)
    return ((vv[:,0]-fuu)**2).sum()
# - step 2. find the values at knot points that minimize the objective function
pinit = t_knot[k1:k2+1]
r = optimize.minimize(errfn, pinit)
t_knot[k1:k2+1] = r.x
tonemap.setchannels(t_knot)

# save the cube file
tonemap.save('cube/linearize_achromatic.cube')
