classdef TonemapCube < handle

    properties

        nsample = 32
        u_knot
        cubeR
        cubeG
        cubeB
        filename = ''

    end
    
    methods

        function obj = TonemapCube(filename)
            obj.u_knot = linspace(0,1,obj.nsample);
            if nargin > 0
                obj.filename = filename;
                obj.load(filename);
            end
        end

        function load(obj, filename)
            if nargin < 2
                filename = obj.filename;
            end

            % load cube file as n x 3 matrix
            mat = [];
            fid = fopen(filename,'r');
            row = 0;
            while ~feof(fid)
                s = fgetl(fid);
                rgb = sscanf(s,'%f %f %f');
                if ~isempty(rgb)
                    row = row + 1;
                    mat(row,:) = rgb;
                end
            end
            fclose(fid);

            % convert to 3D arrays
            n = size(mat,1) ^ (1/3);
            if abs(n-round(n)) > 1e-6
                error('number of rows is not a perfect cube');
            end
            n = round(n);
            obj.cubeR = reshape(mat(:,1),[n n n]);
            obj.cubeG = reshape(mat(:,2),[n n n]);
            obj.cubeB = reshape(mat(:,3),[n n n]);
        end

        function save(obj, filename)
            if nargin < 2
                filename = obj.filename;
            end
        end

        function t_k = apply(obj, u_k)
            r = interp3(obj.u_knot,obj.u_knot,obj.u_knot,obj.cubeR,u_k(1),u_k(2),u_k(3));
            g = interp3(obj.u_knot,obj.u_knot,obj.u_knot,obj.cubeG,u_k(1),u_k(2),u_k(3));
            b = interp3(obj.u_knot,obj.u_knot,obj.u_knot,obj.cubeB,u_k(1),u_k(2),u_k(3));
            t_k = reshape([r g b],size(u_k));
        end

    end

end
