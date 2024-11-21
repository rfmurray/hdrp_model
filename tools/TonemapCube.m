classdef TonemapCube < handle

    properties

        % u_k values of knot points
        u_knot = [ 0 1e-9 2.592e-04 3.121e-03 7.183e-03 1.271e-02 2.033e-02 3.056e-02 4.461e-02 6.358e-02 8.881e-02 1.241e-01 1.699e-01 2.346e-01 3.210e-01 4.384e-01 5.995e-01 8.069e-01 1.107e+00 1.498e+00 2.039e+00 2.766e+00 3.760e+00 5.072e+00 6.871e+00 9.398e+00 1.265e+01 1.725e+01 2.325e+01 3.141e+01 4.301e+01 5.774e+01 ];

        % 3D arrays of RGB coordinates
        coordR, coordG, coordB
        
        % 3D arrays of RGB values
        cubeR, cubeG, cubeB

        % filename of .cube file
        filename = ''

        % interpolation method for interpn
        method = 'linear'

    end
    
    methods

        % constructor
        function obj = TonemapCube(filename)
            if nargin > 0
                obj.filename = filename;
                obj.load(filename);
            end
        end

        % load a .cube file
        function load(obj, filename)
            if nargin >= 2
                obj.filename = filename;
            end

            % load cube file as m x 3 matrix
            fid = fopen(obj.filename,'r');
            mat = [];
            while ~feof(fid)
                s = fgetl(fid);
                rgb = sscanf(s,'%f %f %f');
                if ~isempty(rgb)
                    mat(end+1,:) = rgb;
                end
            end
            fclose(fid);

            % convert matrix to 3D arrays
            n = size(mat,1) ^ (1/3);
            if abs(n-round(n)) > 1e-6
                error('number of rows is not a perfect cube');
            end
            n = round(n);
            if n ~= numel(obj.u_knot)
                error('cube size does not match number of knot points');
            end
            obj.cubeR = reshape(mat(:,1),[n n n]);
            obj.cubeG = reshape(mat(:,2),[n n n]);
            obj.cubeB = reshape(mat(:,3),[n n n]);
            obj.makecoord;
        end

        % create coordinate matrices
        function makecoord(obj, u_knot)
            if nargin >= 2
                obj.u_knot = u_knot;
            end
            [obj.coordR,obj.coordG,obj.coordB] = ndgrid(obj.u_knot);
        end
        
        % apply tonemapping to rendered values u_k
        function t_k = apply(obj, u_k)
            u_k = max(min(u_k,obj.u_knot(end)),obj.u_knot(3));
            r = interpn(obj.coordR,obj.coordG,obj.coordB,obj.cubeR,u_k(1),u_k(2),u_k(3),obj.method);
            g = interpn(obj.coordR,obj.coordG,obj.coordB,obj.cubeG,u_k(1),u_k(2),u_k(3),obj.method);
            b = interpn(obj.coordR,obj.coordG,obj.coordB,obj.cubeB,u_k(1),u_k(2),u_k(3),obj.method);
            t_k = reshape([r g b],size(u_k));
        end

    end

end
