import os
import numpy as np
from scipy.interpolate import interpn

Phi = 12.92
Gamma = 2.4
A = 0.055
X = 0.04045
Y = 0.0031308

def srgb(x):
    if ~isinstance(x, np.ndarray):
        x = np.array(x)
    y = np.empty(x.shape)
    f = x < X
    y[f] = x[f] / Phi
    y[~f] = np.power((x[~f]+A)/(1+A), Gamma)
    return y

def srgbinv(y):
    if ~isinstance(y, np.ndarray):
        y = np.array(y)
    x = np.empty(y.shape)
    f = y < Y
    x[f] = y[f] * Phi
    x[~f] = np.power(y[~f], 1/Gamma)*(1+A)-A
    return x

def cubetag(fname):
    if len(fname) == 0:
        return ''
    _, f = os.path.split(fname)
    return '_' + os.path.splitext(f)[0]

class TonemapCube:
    
    def __init__(self, filename=''):
        
        # knot point coordinates
        # - estimates from delta fits
        self.u_knot = np.array([ 0, 1e-9, 2.615089e-04, 3.078970e-03, 7.122111e-03, 1.268338e-02, 2.026181e-02, 3.048614e-02, 4.439802e-02, 6.322072e-02, 8.877536e-02, 1.233599e-01, 1.704276e-01, 2.337193e-01, 3.207782e-01, 4.362458e-01, 5.968221e-01, 8.089089e-01, 1.103839e+00, 1.494589e+00, 2.032118e+00, 2.756492e+00, 3.738142e+00, 5.082894e+00, 6.864276e+00, 9.347126e+00, 1.261947e+01, 1.717960e+01, 2.324054e+01, 3.148071e+01, 4.275218e+01, 5.766443e+01 ])
        # - estimates from optimizing model predictions
        # self.u_knot = np.array([ 0.000000000, 0.000000001, 0.000000010, 0.002904932, 0.007022516, 0.012769628, 0.020355035, 0.030692471, 0.044981780, 0.064149374, 0.089930606, 0.125204496, 0.172865536, 0.237020901, 0.326773047, 0.440772325, 0.607139173, 0.824515244, 1.103839000, 1.494589000, 2.032118000, 2.756492000, 3.738142000, 5.082894000, 6.864276000, 9.347126000, 12.619470000, 17.179600000, 23.240540000, 31.480710000, 42.752180000, 57.664430000])
        
        # 3D arrays of RGB values
        self.cubeR = self.cubeG = self.cubeB = None
        
        # interpolation method
        self.method = 'linear'
        
        # filename of .cube file
        self.filename = filename
        if self.filename:
            self.load(filename)
    
    def setchannels(self, t_knot):
        n = t_knot.size
        if n != self.u_knot.size:
            raise Exception('array size does not match number of knot points')
        self.cubeR = np.tile(t_knot.reshape((-1,1,1)),(1,n,n))
        self.cubeG = np.tile(t_knot.reshape((1,-1,1)),(n,1,n))
        self.cubeB = np.tile(t_knot.reshape((1,1,-1)),(n,n,1))

    def apply(self, u_k):
        if u_k.shape[1] != 3:
            raise Exception('u_k must be an m x 3 array')
        u_k = u_k.clip(self.u_knot[0], self.u_knot[-1])
        t_r = interpn(3*(self.u_knot,), self.cubeR, u_k, method=self.method)
        t_g = interpn(3*(self.u_knot,), self.cubeG, u_k, method=self.method)
        t_b = interpn(3*(self.u_knot,), self.cubeB, u_k, method=self.method)
        return np.column_stack((t_r, t_g, t_b))
        
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
        
        self.cubeR = mat[:,0].reshape((n,n,n), order='F')
        self.cubeG = mat[:,1].reshape((n,n,n), order='F')
        self.cubeB = mat[:,2].reshape((n,n,n), order='F')
    
    def save(self, filename=''):
        if filename:
            self.filename = filename
        
        mat = np.column_stack([ self.cubeR.flatten(order='F'), self.cubeG.flatten(order='F'), self.cubeB.flatten(order='F') ])
        
        f = open(self.filename, 'w')
        f.write(f'TITLE "{self.filename}"\n')
        f.write(f'LUT_3D_SIZE {self.cubeR.shape[0]}\n')
        f.write('DOMAIN_MIN 0.0 0.0 0.0\n')
        f.write('DOMAIN_MAX 1.0 1.0 1.0\n')
        np.savetxt(f, mat, fmt='%.6f')
        f.close()
