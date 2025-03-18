# char_chromatic_data.py  Make simulated data for chromatic characterization

import numpy as np

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
p = v ** np.array([1.5, 1.8, 2.0])
xyz = p @ rgb + z
xyz += np.random.normal(scale=1, size=xyz.shape)

# save data to file
f = open('data_chromatic_T0.txt', 'w')
f.write('m_r,m_g,m_b,x,y,z\n')
for i in range(v.shape[0]):
    f.write(f'{v[i,0]:.02f},{v[i,1]:.02f},{v[i,2]:.02f},{xyz[i,0]:.03f},{xyz[i,1]:.03f},{xyz[i,2]:.03f}\n')
f.close()
