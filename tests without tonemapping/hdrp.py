import numpy as np
from scipy.interpolate import interpn

Phi = 12.92
Gamma = 2.4
A = 0.055
X = 0.04045
Y = 0.0031308

def srgb(x):
    y = np.empty(x.shape)
    f = x < X
    y[f] = x[f] / Phi
    y[~f] = np.power((x[~f]+A)/(1+A), Gamma)
    return y

def srgbinv(y):
    x = np.empty(y.shape)
    f = y < Y
    x[f] = y[f] * Phi
    x[~f] = np.power(y[~f], 1/Gamma)*(1+A)-A
    return x

class TonemapCube:
    
    def __init__(self, filename=''):
        
        # knot point coordinates
        self.u_knot = np.array([ 0, 1e-09, 2.034e-07, 0.002628, 0.006926, 0.0126, 0.02031, 0.03085, 0.04499, 0.06423, 0.08987, 0.1254, 0.1732, 0.2377, 0.3267, 0.4419, 0.6092, 0.824, 1.109, 1.492, 2.034, 2.759, 3.738, 5.083, 6.881, 9.342, 12.61, 17.2, 23.25, 31.5, 42.75, 57.81 ])
        
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

#        % save a .cube file
#        function save(obj, filename)
#            if nargin >= 2
#                obj.filename = filename;
#            end
#            mat = [ obj.cubeR(:) obj.cubeG(:) obj.cubeB(:) ];
#
#            fid = fopen(obj.filename,'w');
#            fprintf(fid,'TITLE "%s"\n', obj.filename);
#            fprintf(fid,'LUT_3D_SIZE %d\n', size(obj.cubeR,1));
#            fprintf(fid,'DOMAIN_MIN 0.0 0.0 0.0\n');
#            fprintf(fid,'DOMAIN_MAX 1.0 1.0 1.0\n');
#            fprintf(fid,'%.6f %.6f %.6f\n', mat');
#            fclose(fid);
#        end
