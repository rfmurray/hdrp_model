# char_chromatic_1.py  Characterize chromatic stimulus display and generate a cube file
#                      for gamma correction

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize
from hdrp import srgb, srgbinv, h, hinv, TonemapCube
from charfit import CharXYZ

# load color characterization measurements, made with tonemapping off
# df = pd.read_csv('data/characterize/data_chromatic_T0.txt')
# m = df[['m_r', 'm_g', 'm_b']].to_numpy()
# xyz = df[['x', 'y', 'z']].to_numpy()
# v = m

# print('using simulated characterization data')

# make an array of the post-processed values v_k displayed for the characterization measurements
mat = np.array([[1,0,0],[0,1,0],[0,0,1],[1,1,1]])
v = [np.array((0,0,0)).reshape(1,3)] + [k * mat for k in np.linspace(0.1,1,10)]
v = np.vstack(v)

# make an array of the XYZ coordinates recorded during the characterization measurements
# - step 1. make up XYZ coordinates for rgb primaries and the ambient background term
r = np.array((90,50,10)).reshape((1,3))
g = np.array((20,100,10)).reshape((1,3))
b = np.array((10,20,70)).reshape((1,3))
rgb = np.vstack((r,g,b))
z = np.array((4,8,5)).reshape((1,3))
# - step 2. use v_k, the primaries, and the ambient term to make up some XYZ measurements
# p = v ** 1.5
p = np.empty(v.shape)
p[:,0] = v[:,0] ** 1.5
p[:,1] = v[:,1] ** 1.8
p[:,2] = v[:,2] ** 2.0
xyz = p @ rgb + z
xyz += np.random.normal(scale=1, size=xyz.shape)

# fit a characterization model to xyz vs. v
char = CharXYZ(v=v, xyz=xyz)
char.fit()
char.plot()

# express the background term as a weighted sum of the primaries; solve z = w @ rgb for w
w = (char.z @ np.linalg.inv(char.rgb)).reshape((1, 3))

# define tonemapping function for gamma correction; see equation (24)
def f_k(u_k, k):
    return srgb(hinv((1+w[0,k])*u_k - w[0,k], v0=char.v0[k], gamma=char.gamma[k], maxout=False), maxout=False)

# create a tonemapping object by applying the tonemapping function f_k to the knot points
tonemap = TonemapCube()
t_knot = [f_k(tonemap.u_knot, k) for k in range(3)]
t_knot = np.column_stack(t_knot)
k1 = (tonemap.u_knot<(1/255)).nonzero()[0][-1]  # first knot point in u_knot below 1/255
k2 = (tonemap.u_knot>1).nonzero()[0][0]         # first knot point in u_knot above 1
t_knot[(k2+1):,:] = 1
tonemap.setchannels(t_knot)

# # we can make the tonemapping object's approxmation to f_k a bit better by optimizing t_knot
# # - step 1. create an objective function that finds the sum-of-squares error between f_k and
# #   the approximation from the tonemapping object
# uu = np.linspace(0,1,100)
# fuu = [f_k(uu, k) for k in range(3)]
# fuu = np.column_stack(fuu)
# uu3 = np.column_stack((uu,uu,uu))
# def errfn(param):
#     t_knot[k1:k2+1,:] = param.reshape((-1,3))
#     tonemap.setchannels(t_knot)
#     vv = tonemap.apply(uu3)
#     return ((vv-fuu)**2).sum()
# # - step 2. find the values at knot points that minimize the objective function
# pinit = t_knot[k1:k2+1,:].flatten()
# r = optimize.minimize(errfn, pinit)
# t_knot[k1:k2+1,:] = r.x.reshape((-1,3))
# tonemap.setchannels(t_knot)

# check linearization after tonemapping
u = np.linspace(0, 1, 20)
u3 = np.column_stack((u,u,u))
t = tonemap.apply(u3)
v = srgbinv(t)
p = [h(v[:,k], v0=char.v0[k], gamma=char.gamma[k]) for k in range(3)]
p = np.column_stack(p)
plt.plot([0,1], [0,1], 'k-')
for k in range(3):
    plt.plot(u, (p + w)[:,k], 'rgb'[k] + 'o-')
plt.xlabel('unprocessed $u_r$', fontsize=18)
plt.ylabel('primary coefficient', fontsize=18)
plt.legend(['y=x','red','green','blue'], frameon=False)
plt.show()

# save the cube file
# tonemap.save('cube/linearize_chromatic.cube')
