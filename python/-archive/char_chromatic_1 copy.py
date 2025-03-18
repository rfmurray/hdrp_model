# char_chromatic_1.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize
from hdrp import srgb, srgbinv, h, hinv, TonemapCube

# load color characterization measurements, made with tonemapping off
df = pd.read_csv('data/characterize/data_chromatic_T0.txt')
m = df[['m_r', 'm_g', 'm_b']].to_numpy()
xyz = df[['x', 'y', 'z']].to_numpy()
v = m

# estimate the primaries and background term
def lookup(row):
    'find the entry in xyz corresponding to a given row of v_k'
    return xyz[(v==row).all(axis=1).nonzero()[0],:].reshape((1,3))
z_hat = lookup((0,0,0))
r_hat = lookup((1,0,0)) - z_hat
g_hat = lookup((0,1,0)) - z_hat
b_hat = lookup((0,0,1)) - z_hat
rgb_hat = np.vstack((r_hat,g_hat,b_hat))

# express the background term as a weighted sum of the primaries; solve z_hat = w @ rgb_hat for w
w = (z_hat @ np.linalg.inv(rgb_hat)).reshape((1,3))

# step through the primaries
phat = []
for k in range(3):

    # estimate the activation as a function of v_k
    # - step 1. find the rows of v where the other primaries are not activated
    # *** maybe we don't need to do this; and maybe it's better not to do this; we can just examine the
    #     activation in each channel as a function of the corresponding v_k, and if there are multiple
    #     measurements for a given value of v_k in this channel, that's fine too
    kk = (v[:,[i for i in range(3) if i != k]] == 0).all(axis=1)
    vv = v[kk,k]
    # - step 2. estimate the activations for those rows
    xx = xyz[kk,:] - z_hat
    p = xx.dot(rgb_hat[k,:]) / (np.linalg.norm(rgb_hat[k,:])**2)

    # fit h() to activation vs. v_k
    def errfn(param):
        return ((p - h(vv, *param))**2).sum()
    pinit = np.array((0, 2.2))
    cons = optimize.LinearConstraint(np.array((1,0)), np.array((0,)))  # constrain v0 >= 0
    r = optimize.minimize(errfn, pinit, constraints=cons)
    phat.append(r.x)
    print(r)

    # show the activations and fit
    plt.plot(vv, p, 'rgb'[k] + 'o')
    vvv = np.linspace(0,1,100)
    plt.plot(vvv, h(vvv, *phat[k]), 'rgb'[k] + '-')

plt.xlabel('post-processed $v_k$', fontsize=18)
plt.ylabel('activation $p_k$', fontsize=18)
plt.show()

# define tonemapping function for gamma correction; see equation (25)
def f_k(u_k, k):
    return srgb(hinv((1+w[0,k])*u_k - w[0,k], *(phat[k]), maxout=False), maxout=False)

# create a tonemapping object by applying the tonemapping function f_k to the knot points
tonemap = TonemapCube()
t_knot = [f_k(tonemap.u_knot, k) for k in range(3)]
t_knot = np.column_stack(t_knot)
k1 = (tonemap.u_knot<(1/255)).nonzero()[0][-1]  # first knot point in u_knot below 1/255
k2 = (tonemap.u_knot>1).nonzero()[0][0]         # first knot point in u_knot above 1
t_knot[(k2+1):,:] = 1
tonemap.setchannels(t_knot)

# we can make the tonemapping object's approxmation to f_k a bit better by optimizing t_knot
# - step 1. create an objective function that finds the sum-of-squares error between f_k and
#   the approximation from the tonemapping object
uu = np.linspace(0,1,100)
fuu = [f_k(uu, k) for k in range(3)]
fuu = np.column_stack(fuu)
uu3 = np.column_stack((uu,uu,uu))
def errfn(param):
    t_knot[k1:k2+1,:] = param.reshape((-1,3))
    tonemap.setchannels(t_knot)
    vv = tonemap.apply(uu3)
    return ((vv-fuu)**2).sum()
# - step 2. find the values at knot points that minimize the objective function
pinit = t_knot[k1:k2+1,:].flatten()
r = optimize.minimize(errfn, pinit)
t_knot[k1:k2+1,:] = r.x.reshape((-1,3))
tonemap.setchannels(t_knot)

# check linearization after tonemapping
u = np.linspace(0, 1, 20)
u3 = np.column_stack((u,u,u))
t = tonemap.apply(u3)
v = srgbinv(t)
p = [h(v[:,k], *(phat[k])) for k in range(3)]
p = np.column_stack(p)
plt.plot([0,1], [0,1], 'k-')
plt.plot(u, p + w, 'o-')
plt.xlabel('unprocessed $u_r$')
plt.ylabel('red primary coefficient')
plt.show()

# save the cube file
tonemap.save('cube/linearize_chromatic.cube')
