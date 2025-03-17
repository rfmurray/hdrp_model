import os
import numpy as np
from scipy.interpolate import interpn
import matplotlib.pyplot as plt

Phi = 12.92
Gamma = 2.4
A = 0.055
X = 0.04045
Y = 0.0031308

def srgb(x, maxout=True):
    ub = 1 if maxout else np.inf
    x = np.array(x).clip(0, ub)
    return np.where(x<X, x/Phi, np.power((x+A)/(1+A), Gamma))

def srgbinv(y, maxout=True):
    ub = 1 if maxout else np.inf
    y = np.array(y).clip(0, ub)
    return np.where(y<Y, y*Phi, np.power(y, 1/Gamma)*(1+A)-A)

def h(v, v0, gamma, maxout=True):
    ub = 1 if maxout else np.inf
    v = np.array(v).clip(v0, ub)
    return ((v-v0)/(1-v0)) ** gamma

def hinv(p, v0, gamma, maxout=True):
    ub = 1 if maxout else np.inf
    p = np.array(p).clip(0, ub)
    return v0 + (1-v0)*(p ** (1/gamma))

def cubetag(fname):
    if len(fname) == 0:
        return ''
    _, f = os.path.split(fname)
    return '_' + os.path.splitext(f)[0]

class TonemapCube:
    
    def __init__(self, filename=''):
        
        # knot point coordinates
        self.u_knot = np.array([0, 1e-09, 1.317e-09, 0.002826, 0.007251, 0.01279, 0.02061, 0.03115, 0.04511, 0.06479, 0.0903, 0.1258, 0.1734, 0.238, 0.3264, 0.4434, 0.6056, 0.8231, 1.104, 1.495, 2.032, 2.756, 3.738, 5.083, 6.864, 9.347, 12.62, 17.18, 23.24, 31.48, 42.75, 57.66])

        # 4D array of RGB values
        self.cube = None
        
        # interpolation method
        self.method = 'linear'
        
        # filename of .cube file
        self.filename = filename
        if self.filename:
            self.load(filename)
    
    def setchannels(self, t_knot):
        if t_knot.ndim==1 or t_knot.shape[1] == 1:
            t_knot = np.column_stack((t_knot, t_knot, t_knot))

        n = t_knot.shape[0]
        if n != self.u_knot.size:
            raise Exception('array size does not match number of knot points')
        cubeR = np.tile(t_knot[:,0].reshape((-1,1,1,1)),(1,n,n,1))
        cubeG = np.tile(t_knot[:,1].reshape((1,-1,1,1)),(n,1,n,1))
        cubeB = np.tile(t_knot[:,2].reshape((1,1,-1,1)),(n,n,1,1))
        self.cube = np.concatenate((cubeR, cubeG, cubeB), axis=3)

    def apply(self, u_k):
        if u_k.shape[1] != 3:
            raise Exception('u_k must be an m x 3 array')
        u_k = u_k.clip(self.u_knot[2], self.u_knot[-1])
        t_k = interpn(3*(self.u_knot,), self.cube, u_k, method=self.method)
        return t_k
        
    def load(self, filename=''):
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
        s = 'u_knot = ' + str(self.u_knot) + '\n'
        s += 'cube.shape = ' + str(self.cube.shape) + '\n'
        s += 'filename = "' + self.filename + '"\n'
        return s
