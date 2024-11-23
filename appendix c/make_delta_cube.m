% make_delta_cube.m

clear; clc;

addpath ../tools

! rm -fr delta
! mkdir delta

t = TonemapCube;

for i = 1:32

    t_knot = zeros(size(t.u_knot));
    t_knot(i) = 1;
    t.setchannels(t_knot);
    
    filename = sprintf('delta/delta_%02d.cube',i);
    fprintf('%s\n',filename);
    t.save(filename);

end
