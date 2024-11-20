classdef CubeTonemap < handle

    properties

        u_knot
        cubeR
        cubeG
        cubeB
        filename = ''

    end

    methods

        function obj = CubeTonemap(filename)
            if nargin > 0
                obj.filename = filename;
                obj.load(filename);
            end
        end

        function load(obj, filename)
            if nargin < 2
                filename = obj.filename;
            end
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
