# char_chromatic_1.py  Characterize chromatic stimulus display and generate a cube file
#                      for gamma correction

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize
from hdrp import srgb, srgbinv, TonemapCube
from charfit import CharXYZ

# load color characterization measurements, made with tonemapping off
df = pd.read_csv('data/characterize/data_chromatic_T0.txt')
m = df[['m_r', 'm_g', 'm_b']].to_numpy()
xyz = df[['x', 'y', 'z']].to_numpy()
v = m

# fit a characterization model to xyz vs. v
char = CharXYZ(v=v, xyz=xyz)
char.fit()

# express the background term as a weighted sum of the primaries; solve z = w @ rgb for w
w = (char.z @ np.linalg.inv(char.rgb)).reshape((1, 3))

# find the primary coefficients; solve xyz = coef @ rgb for coef
coef = char.xyz @ np.linalg.inv(char.rgb)

# plot primary coefficients vs. unprocessed values u_k
# - the CharXYZ class has a method plot() that plots primary activation vs.
#   post-processed values v_k, which is what is of interest for viewing
#   the fit of the characterization model; here, instead, we want to show
#   that without tonemapping for gamma correction, primary coefficients are
#   a nonlinear function of u_k; so we'll plot that ourselves here.
u_fit = np.linspace(0, 1, 100)
v_fit = srgbinv(u_fit)
for k in range(3):
    coef_fit = char.h(v_fit, v0=char.v0[k], gamma=char.gamma[k]) + w[0,k]
    plt.plot(u_fit, coef_fit, 'rgb'[k] + '-')
u_data = srgb(char.v)
for k in range(3):
    plt.plot(u_data[:, k], coef[:, k], 'rgb'[k] + 'o')
plt.xlabel('unprocessed $u_k$', fontsize=18)
plt.ylabel('primary coefficient', fontsize=18)
plt.legend(labels=['red','green','blue'], frameon=False)
plt.savefig('figures/char_chromatic_1.pdf');
plt.show()

# define tonemapping function for gamma correction; see equation (24);
# also see comments on definition of f(u_k) in char_achromatic_1.py, which
# apply to this definition as well
def f_k(u_k, k):
    return srgb(char.hinv((1+w[0,k])*u_k - w[0,k], k=k, maxout=False), maxout=False)

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

# save the cube file
tonemap.save('cube/linearize_chromatic.cube')
