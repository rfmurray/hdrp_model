# model_test_2.py  Test rendering and post-processing models for Lambertian
#                  and unlit materials

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tools import srgb, srgbinv

# choose whether to test results from model_test Unity project with
# Lambertian or unlit material
testLambertian = True

# choose whether to test results with or without tonemapping
testTonemapping = False
cubefile = 'square_root.cube'

# load data generated by Unity project render_random for this condition
fname = f'data_L{int(testLambertian)}_T{int(testTonemapping)}.txt'
df = pd.read_csv(fname)

# discard samples that may be maxed out
k = (df[['v_r','v_g','v_b']] <= 0.99).all(axis=1)
df = df.loc[k,:]

# tranform data frame into numpy arrays for model parameters
e = df['e'].to_numpy().reshape((-1,1))      # exposure
m = df[['m_r','m_g','m_b']].to_numpy()      # material color
d = df[['d_r','d_g','d_b']].to_numpy()      # directional light color
a = df[['a_r','a_g','a_b']].to_numpy()      # ambient light color
v = df[['v_r','v_g','v_b']].to_numpy()      # post-processed color
i_d = df['i_d'].to_numpy().reshape((-1,1))  # directional light intensity
i_a = df['i_a'].to_numpy().reshape((-1,1))  # directional light intensity
l = df[['l_x','l_y','l_z']].to_numpy()      # lighting direction
n = df[['n_x','n_y','n_z']].to_numpy()      # plane normal
costheta = (l*n).sum(axis=1, keepdims=True)

# apply Lambertian rendering model to get predicted rendered color
# coordinates u_k, without rendering scale constant c
if testLambertian:
    c = 0.822
    u_hat = c * srgb(m) * ( i_d * srgb(d) * costheta.clip(min=0) / np.pi + i_a * a ) / (2**e)
else:
    u_hat = srgb(m)

# apply tonemapping
if testTonemapping:
    t_hat = u_hat  # *** apply tonemapping here
else:
    t_hat = u_hat

# apply sRGB nonlinearity to get post-processed color coordinates v_k
v_hat = srgbinv(t_hat)

## plot predicted post-processed color coordinates v_k against actual v_k
#xylim = np.array([0,1.1])
k = np.random.randint(low=0, high=v.shape[0], size=200)
#for i in range(3):
#    plt.scatter(v[k,i], v_hat[k,i], color=['r','g','b'][i])
#plt.plot(xylim, xylim, 'k-')
#plt.legend(['red channel','green channel','blue channel'], frameon=False)
#plt.xlabel('actual v_k', fontsize=18)
#plt.ylabel('predicted v_k', fontsize=18)
#plt.xlim(xylim)
#plt.ylim(xylim)
#plt.gca().set_aspect(1)
#plt.show()

# plot prediction error in v_k against actual v_k
xlim = np.array([0,1])
for i in range(3):
    plt.scatter(v[k,i], v_hat[k,i]-v[k,i], color=['r','g','b'][i])
plt.legend(['red channel','green channel','blue channel'], frameon=False)
plt.plot(xlim,(-1/255)*np.ones(2),'k-')
plt.plot(xlim,(1/255)*np.ones(2),'k-')
plt.xlabel('actual v_k', fontsize=18)
plt.ylabel('prediction error', fontsize=18)
plt.xlim(xlim)
#axis([ xlim (5/255)*[ -1 1 ] ]);
plt.show()
