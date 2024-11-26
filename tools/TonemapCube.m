classdef TonemapCube < handle

    properties

        % u_k values of knot points
        u_knot = [ 0 1e-09 2.606e-04 3.104e-03 7.157e-03 1.270e-02 2.027e-02 3.049e-02 4.443e-02 6.334e-02 8.883e-02 1.236e-01 1.702e-01 2.338e-01 3.209e-01 4.368e-01 5.966e-01 8.106e-01 1.105e+00 1.492e+00 2.034e+00 2.759e+00 3.738e+00 5.083e+00 6.881e+00 9.342e+00 1.261e+01 1.720e+01 2.325e+01 3.150e+01 4.275e+01 5.781e+01 ];
        
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
        end
        
        % save a .cube file
        function save(obj, filename)
            if nargin >= 2
                obj.filename = filename;
            end
            mat = [ obj.cubeR(:) obj.cubeG(:) obj.cubeB(:) ];

            fid = fopen(obj.filename,'w');
            fprintf(fid,'TITLE "%s"\n', obj.filename);
            fprintf(fid,'LUT_3D_SIZE %d\n', size(obj.cubeR,1));
            fprintf(fid,'DOMAIN_MIN 0.0 0.0 0.0\n');
            fprintf(fid,'DOMAIN_MAX 1.0 1.0 1.0\n');
            fprintf(fid,'%.6f %.6f %.6f\n', mat');
            fclose(fid);
        end

        % make independent rgb channels with specified values at knot points
        function setchannels(obj, t_knot)
            n = numel(t_knot);
            if n ~= numel(obj.u_knot)
                error('vector size does not match number of knot points');
            end
            t_knot = t_knot(:);
            obj.cubeR = repmat(t_knot,[1 n n]);
            obj.cubeG = repmat(t_knot',[n 1 n]);
            obj.cubeB = repmat(reshape(t_knot,[1 1 n]),[n n 1]);
        end

        % apply tonemapping to rendered values u_k
        function t_k = apply(obj, u_k)
            if size(u_k,2)~=3
                error('u_k must be an m x 3 array');
            end
            u_k = max(min(u_k,obj.u_knot(end)),obj.u_knot(3));
            t_r = interpn(obj.u_knot,obj.u_knot,obj.u_knot,obj.cubeR,u_k(:,1),u_k(:,2),u_k(:,3),obj.method);
            t_g = interpn(obj.u_knot,obj.u_knot,obj.u_knot,obj.cubeG,u_k(:,1),u_k(:,2),u_k(:,3),obj.method);
            t_b = interpn(obj.u_knot,obj.u_knot,obj.u_knot,obj.cubeB,u_k(:,1),u_k(:,2),u_k(:,3),obj.method);
            t_k = [t_r t_g t_b];
        end

    end

end
