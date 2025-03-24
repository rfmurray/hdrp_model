# char_achromatic_1.py  Characterize achromatic stimulus display and generate a cube file
#                       for gamma correction

import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib.pyplot as plt
from hdrp import srgb, srgbinv, TonemapCube
from charfit import CharLum

# load luminance characterization measurements, made with tonemapping off
df = pd.read_csv('data/characterize/data_achromatic_T0.txt')
m_k = df['m_k'].to_numpy()
lum = df['lum'].to_numpy()
u_k = srgb(m_k)
v_k = m_k

# fit a characterization model to luminance vs. v_k
char = CharLum(v=v_k, lum=lum)
char.fit()

# plot luminance vs. unprocessed values u_k
# - the CharLum class has a method plot() that plots luminance vs.
#   post-processed values v_k, which is what is of interest for viewing
#   the fit of the characterization model; here, instead, we want to show
#   that without tonemapping for gamma correction, luminance is a nonlinear
#   function of u_k; so we'll plot that ourselves here.
u_fit = np.linspace(0, 1, 100)
v_fit = srgbinv(u_fit)
lum_fit = char.v2lum(v_fit)
plt.plot(u_fit, lum_fit, 'k-')
u_data = srgb(char.v)
plt.plot(u_data, char.lum, 'ro', markersize=10)
plt.legend(['fit', 'measurements'], frameon=False)
plt.xlabel('unprocessed $u_k$', fontsize=18)
plt.ylabel('luminance (cd/m$^2$)', fontsize=18)
plt.show()

# define the tonemapping function for gamma correction; see equation (15)
# - here we implicitly set r = 1, so the displayable range of u_k is [0, 1]
# - clipping of the input to hinv to a lower bound of zero is done by hinv itself,
#   so we don't need an explicit max(x, 0) as in equation (15)
def f(u_k):
    w = char.L0/char.L1
    return srgb(char.hinv((1+w)*u_k - w, maxout=False), maxout=False)
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

# show predicted effect of tonemapping with this cube file; we'll check
# this with measurements in the second part of the test (char_achromatic_2.py)
u = np.linspace(0, 1, 20)
u3 = np.column_stack((u,u,u))
t = tonemap.apply(u3)
v = srgbinv(t)
lum = char.v2lum(v[:,0])
plt.plot(u[[0,-1]], lum[[0,-1]], 'k-')
plt.plot(u, lum, 'ro')
plt.xlabel('unprocessed $u_k$', fontsize=18)
plt.ylabel('predicted luminance (cd/m$^2$)', fontsize=18)
plt.show()

# save the cube file
tonemap.save('cube/linearize_achromatic.cube')
