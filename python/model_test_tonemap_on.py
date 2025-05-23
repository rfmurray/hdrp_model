# model_test_tonemap_on.py  Test HDRP model predictions with tonemapping

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hdrp import srgb, srgbinv, TonemapCube, cubetag

# choose whether to test results from Unity project render_random with Lambertian or unlit material
testLambertian = True

# choose cube files
cubelist = ['cube/linear_max1.cube', 'cube/square_max1.cube', 'cube/square_root_max1.cube']
cuben = len(cubelist)

# create tonemapping objects and load tonemaps from cube files
tonemap = [TonemapCube(f) for f in cubelist]

# knot points estimated from delta functions (Table 2a)
#u_knot = [0, 1e-09, 0.0002606, 0.003104, 0.007305, 0.01288, 0.02056, 0.03061, 0.04468, 0.06393, 0.09056, 0.1245, 0.1712, 0.2354, 0.3236, 0.4406, 0.5938, 0.8165, 1.111, 1.498, 2.039, 2.776, 3.78, 5.094, 6.935, 9.441, 12.72, 17.32, 23.35, 31.78, 43.27, 58.9]

# knot points estimated from model fitting (Table 2b)
u_knot = [0, 1e-09, 1.657e-09, 0.002830, 0.007137, 0.01269, 0.02051, 0.03086, 0.04479, 0.06444, 0.08989, 0.1252, 0.1726, 0.2370, 0.3253, 0.4422, 0.6039, 0.8207, 1.104, 1.495, 2.032, 2.756, 3.738, 5.083, 6.864, 9.347, 12.62, 17.18, 23.24, 31.48, 42.75, 57.66]

# assign selected knot points to tonemapping objects
for t in tonemap:
    t.u_knot = np.array(u_knot)

# load data files generated by Unity project render_random
df = []
for i, cubefile in enumerate(cubelist):
    fname = f'data/tonemap_on_test/data_L{int(testLambertian)}_T1{cubetag(cubefile)}.txt'
    df2 = pd.read_csv(fname)
    df2['cubenum'] = i
    df.append(df2)
df = pd.concat(df)

# discard samples that may be maxed out
k = (df[['v_r', 'v_g', 'v_b']] <= 0.99).all(axis=1)
df = df[k]

## optionally discard samples with low material color coordinates
#k = (df[['m_r', 'm_g', 'm_b']] >= 0.20).all(axis=1)
#df = df[k]

# create numpy arrays for model parameters
e = df['e'].to_numpy().reshape((-1, 1))  # exposure
m = df[['m_r', 'm_g', 'm_b']].to_numpy()  # material color
d = df[['d_r', 'd_g', 'd_b']].to_numpy()  # directional light color
a = df[['a_r', 'a_g', 'a_b']].to_numpy()  # ambient light color
v = df[['v_r', 'v_g', 'v_b']].to_numpy()  # post-processed color
i_d = df['i_d'].to_numpy().reshape((-1, 1))  # directional light intensity
i_a = df['i_a'].to_numpy().reshape((-1, 1))  # directional light intensity
l = df[['l_x', 'l_y', 'l_z']].to_numpy()  # lighting direction
n = df[['n_x', 'n_y', 'n_z']].to_numpy()  # plane surface normal
costheta = (l * n).sum(axis=1, keepdims=True)  # cosine of angle between lighting direction and plane surface normal
cubenum = df['cubenum']  # number of cube file used

# apply Lambertian or unlit rendering model
if testLambertian:
    c = 0.822
    u_hat = c * srgb(m) * (i_d * srgb(d) * costheta.clip(min=0) / np.pi + i_a * a) / (2 ** e)
else:
    u_hat = srgb(m)

# initialize plot for results
fig = plt.figure(figsize=(13, 5.5))
ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(1, 2, 2)

# step through cube files
handle1 = 3 * [None, ]
handle2 = 3 * [None, ]
err = []
for i in range(cuben):

    # get data for this cube file, and apply post-processing
    k = cubenum == i
    t_hat = tonemap[i].apply(u_hat[k, :])
    v_hat = srgbinv(t_hat)
    vv = v[k, :]
    err.append(v_hat - vv)

    # plot predicted post-processed color coordinates v_k against actual v_k
    kk = np.random.randint(low=0, high=v_hat.shape[0], size=20)
    for j in range(3):
        handle1[i] = ax1.scatter(vv[kk, j], v_hat[kk, j], color='rgb'[i])

    # plot prediction error in v_k against actual v_k
    kk = np.random.randint(low=0, high=v_hat.shape[0], size=50)
    for j in range(3):
        handle2[i] = ax2.scatter(vv[kk, j], v_hat[kk, j] - vv[kk, j], color='rgb'[i])

# find median absolute error
err = np.concatenate(err, axis=0)
mae = np.median(abs(err))
ax2.text(0.1, -0.018, f'error = {255*mae:.2f} / 255', fontsize=12)

# format left panel
xylim = np.array([0, 1.1])
ax1.plot(xylim, xylim, 'k-')
ax1.legend(handle1, ['identity', 'square', 'square root'], frameon=False, loc='upper left')
ax1.set_xlabel('actual $v_k$', fontsize=18)
ax1.set_ylabel('predicted $v_k$', fontsize=18)
ax1.set_xlim(xylim)
ax1.set_ylim(xylim)
ax1.set_aspect(1)
ax1.text(0.85, 0.1, '(a)', fontsize=24)

# format right panel
xlim = np.array([0, 1])
ax2.legend(handle2, ['identity', 'square', 'square root'], frameon=False, loc='upper left')
ax2.plot(xlim, (-1 / 255) * np.ones(2), 'k-')
ax2.plot(xlim, (1 / 255) * np.ones(2), 'k-')
ax2.set_xlabel('actual $v_k$', fontsize=18)
ax2.set_ylabel('prediction error', fontsize=18)
ax2.set_xlim(xlim)
ax2.set_ylim((-0.02, 0.02))
ax2.set_aspect(1. / ax2.get_data_ratio())
ax2.text(0.85, -0.012, '(b)', fontsize=24)

plt.savefig(f'figures/model_test_tonemap_on_L{int(testLambertian)}.pdf', bbox_inches='tight')
plt.show()
