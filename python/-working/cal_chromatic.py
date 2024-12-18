# cal_chromatic.py

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from hdrp import srgb, srgbinv, h, hinv, TonemapCube

# make an array of the post-processed values v_k that we displayed for the characterization measurements
mat = np.array([[1,0,0],[0,1,0],[0,0,1],[1,1,1]])
v = [np.array((0,0,0)).reshape(1,3)] + [k * mat for k in np.linspace(0.1,1,10)]
v = np.vstack(v)

# make an array of the XYZ coordinates that we recorded during the characterization measurements
# - here we'll make up some measurements; alternatively, replace 'xyz' below with an array of real measurements
# - step 1. make up XYZ coordinates for rgb primaries and the ambient background term
r = np.array((90,50,10)).reshape((1,3))
g = np.array((20,100,10)).reshape((1,3))
b = np.array((10,20,70)).reshape((1,3))
rgb = np.vstack((r,g,b))
z = np.array((4,8,5)).reshape((1,3))
# - step 2. use v_k, the primaries, and the ambient term to make up some XYZ measurements
p = v ** 1.5
xyz = p @ rgb + z
# xyz += np.random.normal(scale=1, size=xyz.shape)

# estimate the primaries and background term from the characterization measurements
def lookup(row):
    'find the entry in xyz corresponding to a given row of v_k'
    return xyz[(v==row).all(axis=1).nonzero()[0],:].reshape((1,3))
z_hat = lookup((0,0,0))
r_hat = lookup((1,0,0)) - z_hat
g_hat = lookup((0,1,0)) - z_hat
b_hat = lookup((0,0,1)) - z_hat
rgb_hat = np.vstack((r_hat,g_hat,b_hat))

print(abs(rgb-rgb_hat).max())
print(abs(z-z_hat).max())
# zero

# express the background term as a weighted sum of the primaries; solve z_hat = w @ rgb_hat for w
w = (z_hat @ np.linalg.inv(rgb_hat)).flatten()

z_test = w @ rgb_hat
print(abs(z_hat-z_test).max())
# negligible

# step through the primaries
phat = []
for k in range(3):

    # estimate the activation as a function of v_k
    # - step 1. find the rows of v where the other primaries are not activated
    kk = (v[:,[i for i in range(3) if i != k]] == 0).all(axis=1)
    vv = v[kk,k]
    # - step 2. estimate the activations for those rows
    xx = xyz[kk,:] - z_hat
    p = xx.dot(rgb_hat[k,:]) / (np.linalg.norm(rgb_hat[k,:])**2)
    # *** check this

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

# h gives a practically perfect fit
# *** check calculation of activation noted above

# *** seems exact up to here

# define tonemapping function for gamma correction; see equation (26)
def f(u_k, k):
    return srgb(hinv((1+w[k])*u_k - w[k], *phat[k]))

# *** check that f does what it's supposed to

def ptest(u_k, k):
    v = srgbinv(f(u_k, k))
    p = v ** 1.5
    return p

u_k = np.linspace(0, 1, 11)
p_k = ptest(u_k, 0)
plt.plot(u_k, p_k, 'ro-')
plt.show()
# also plot line showing what we expect here

exit()

# create a tonemapping object by applying the tonemapping function f to the knot points
tonemap = TonemapCube()
t_knot = [f_k(tonemap.u_knot, k) for k in range(3)]
t_knot = np.column_stack(t_knot)
tonemap.setchannels(t_knot)
tonemap.save('cube/linearize_chromatic.cube')

# *** plot the tonemapping knot points; should we set the outputs to 1 for points
# more than one sample beyond u_k in [0, 1], like we did for achromatic gamma correction?

# optimize model parameters

# check linearization
u = v

# t = tonemap.apply(u)
t = [ f_k(u[:,k],k) for k in range(3) ]
t = np.column_stack(t)
# t = np.empty(u.shape)
# for k in range(3):
#     t[:,k] = f_k(u[:,k],k)

v = srgbinv(t)
p = np.empty(v.shape)
for i in range(3):
    p[:,i] = h(v[:,i], *phat[i])
p = v ** 1.5
xyz_pred = p @ rgb + z
# - express each xyz_pred as a sum of the three primaries
coef = p + w  # right?
# - for each primary, plot the coefficient as a function of u_k for that primary; should be linear
# - it's approximately linear, but why not exactly? try simulating measurements without noise, and seeing where
#   the approximation comes from
plt.plot([0,1],[0,1],'k-')
plt.plot(u, coef, 'o')
plt.xlabel('unprocessed $u_k$', fontsize=18)
plt.ylabel('primary coefficient', fontsize=18)
plt.show()
