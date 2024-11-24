classdef TonemapCube < handle

    properties

        % u_k values of knot points
        % u_knot = [ 0 1e-9 0.0002592 0.003121 0.007183 0.01271 0.02033 0.03056 0.04461 0.06358 0.08881 0.1241 0.1699 0.2346 0.3210 0.4384 0.5995 0.8069 1.107 1.498 2.039 2.766 3.760 5.072 6.871 9.398 12.65 17.25 23.25 31.41 43.01 57.74 ];
        u_knot = [ 0 1e-09 1.355e-05 0.003138 0.007366 0.01298 0.02089 0.03124 0.04545 0.06475 0.09134 0.1263 0.1741 0.2388 0.3312 0.4477 0.6092 0.8301 1.106 1.498 2.039 2.766 3.76 5.072 6.871 9.398 12.65 17.25 23.25 31.41 43.01 57.74 ];
        
        % % 3D arrays of RGB coordinates
        % coordR, coordG, coordB
        
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
            % obj.makecoord;
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

        % make independent rgb channels with specified tonemapping knot points
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

        % create coordinate matrices
        function makecoord(obj, u_knot)
            if nargin >= 2
                obj.u_knot = u_knot;
            end
            % [obj.coordR,obj.coordG,obj.coordB] = ndgrid(obj.u_knot);
        end
        
        % apply tonemapping to rendered values u_k
        function t_k = apply(obj, u_k)
            if size(u_k,2)~=3
                error('u_k must be an m x 3 array');
            end
            u_k = max(min(u_k,obj.u_knot(end)),obj.u_knot(3));
            % t_r = interpn(obj.coordR,obj.coordG,obj.coordB,obj.cubeR,u_k(:,1),u_k(:,2),u_k(:,3),obj.method);
            % t_g = interpn(obj.coordR,obj.coordG,obj.coordB,obj.cubeG,u_k(:,1),u_k(:,2),u_k(:,3),obj.method);
            % t_b = interpn(obj.coordR,obj.coordG,obj.coordB,obj.cubeB,u_k(:,1),u_k(:,2),u_k(:,3),obj.method);
            t_r = interpn(obj.u_knot,obj.u_knot,obj.u_knot,obj.cubeR,u_k(:,1),u_k(:,2),u_k(:,3),obj.method);
            t_g = interpn(obj.u_knot,obj.u_knot,obj.u_knot,obj.cubeG,u_k(:,1),u_k(:,2),u_k(:,3),obj.method);
            t_b = interpn(obj.u_knot,obj.u_knot,obj.u_knot,obj.cubeB,u_k(:,1),u_k(:,2),u_k(:,3),obj.method);
            t_k = [t_r t_g t_b];
        end

    end

end
