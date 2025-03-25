import os
import numpy as np
from scipy.interpolate import interpn
import matplotlib.pyplot as plt

# constants in the sRGB nonlinearity
Phi = 12.92
Gamma = 2.4
A = 0.055
X = 0.04045
Y = 0.0031308

def srgb(x, maxout=True):
    'sRGB nonlinearity; maxout determines whether the maximum value is 1.0'
    ub = 1 if maxout else np.inf
    x = np.array(x).clip(0, ub)
    return np.where(x<X, x/Phi, np.power((x+A)/(1+A), Gamma))

def srgbinv(y, maxout=True):
    'inverse of sRGB nonlinearity; maxout determines whether maximum value is 1.0'
    ub = 1 if maxout else np.inf
    y = np.array(y).clip(0, ub)
    return np.where(y<Y, y*Phi, np.power(y, 1/Gamma)*(1+A)-A)

def cubetag(fname):
    'from filename of cube file, return a tag to use in filename of text data files'
    if len(fname) == 0:
        return ''
    _, f = os.path.split(fname)
    return '_' + os.path.splitext(f)[0]

# class for tonemapping model
class TonemapCube:
    
    def __init__(self, filename=''):
        
        # knot point coordinates, estimated empirically
#        self.u_knot = np.array([0, 1e-09, 1.317e-09, 0.002826, 0.007251, 0.01279, 0.02061, 0.03115, 0.04511, 0.06479, 0.0903, 0.1258, 0.1734, 0.238, 0.3264, 0.4434, 0.6056, 0.8231, 1.104, 1.495, 2.032, 2.756, 3.738, 5.083, 6.864, 9.347, 12.62, 17.18, 23.24, 31.48, 42.75, 57.66])
        self.u_knot = np.array([0, 1e-09, 1.657e-09, 0.002830, 0.007137, 0.01269, 0.02051, 0.03086, 0.04479, 0.06444, 0.08989, 0.1252, 0.1726, 0.2370, 0.3253, 0.4422, 0.6039, 0.8207, 1.104, 1.495, 2.032, 2.756, 3.738, 5.083, 6.864, 9.347, 12.62, 17.18, 23.24, 31.48, 42.75, 57.66])

        # 4D array of RGB values; outputs of tonemapping at knot points
        self.cube = None
        
        # interpolation method
        self.method = 'linear'
        
        # filename of cube file
        self.filename = filename
        if self.filename:
            self.load(filename)
    
    def setchannels(self, t_knot):
        'from n x 1 or n x 3 array, create a 4D array for tonemapping that assumes independent channels'

        # from 1D or n x 1 array, make a n x 3 array
        if t_knot.ndim==1 or t_knot.shape[1] == 1:
            t_knot = np.column_stack((t_knot, t_knot, t_knot))

        # create the cube
        n = t_knot.shape[0]
        if n != self.u_knot.size:
            raise Exception('array size does not match number of knot points')
        cubeR = np.tile(t_knot[:,0].reshape((-1,1,1,1)),(1,n,n,1))
        cubeG = np.tile(t_knot[:,1].reshape((1,-1,1,1)),(n,1,n,1))
        cubeB = np.tile(t_knot[:,2].reshape((1,1,-1,1)),(n,n,1,1))
        self.cube = np.concatenate((cubeR, cubeG, cubeB), axis=3)

    def apply(self, u_k):
        'apply tonemapping model to unprocessed values u_k; look up tonemapped values in cube, interpolating if necessary'
        if u_k.shape[1] != 3:
            raise Exception('u_k must be an m x 3 array')
        u_k = u_k.clip(self.u_knot[2], self.u_knot[-1])
        t_k = interpn(3*(self.u_knot,), self.cube, u_k, method=self.method)
        return t_k
        
    def load(self, filename=''):
        'load cube file'
        if filename:
            self.filename = filename
        
        with open(self.filename, 'r') as f:
            cubetext = f.read()
        
        mat = []
        for line in cubetext.split('\n'):
            rgb = np.fromstring(line, sep=' ')
            if rgb.size == 3:
                mat.append(rgb)
        mat = np.array(mat)
        
        n = mat.shape[0] ** (1/3)
        if abs(n-round(n)) > 1e-6:
            raise Exception('number of rows is not a perfect cube')
        n = round(n)
        if n != self.u_knot.size:
            raise Exception('cube size does not match number of knot points')

        self.cube = mat.reshape((n,n,n,3), order='F')

    def save(self, filename=''):
        'save cube file'
        if filename:
            self.filename = filename

        n = self.cube.shape[0]
        mat = self.cube.reshape((n**3,3), order='F')

        f = open(self.filename, 'w')
        f.write(f'TITLE "{self.filename}"\n')
        f.write(f'LUT_3D_SIZE {n}\n')
        f.write('DOMAIN_MIN 0.0 0.0 0.0\n')
        f.write('DOMAIN_MAX 1.0 1.0 1.0\n')
        np.savetxt(f, mat, fmt='%.6f')
        f.close()

    def __repr__(self):
        'string representation of object'
        s = 'u_knot = ' + str(self.u_knot) + '\n'
        s += 'cube.shape = ' + str(self.cube.shape) + '\n'
        s += 'filename = "' + self.filename + '"\n'
        return s
