% make_cube.m

clear; clc;

addpath tools

t = TonemapCube;
t_knot = t.u_knot .^ 2;
t.setchannels(t_knot);
t.save('square.cube');

t_knot = t.u_knot .^ 0.5;
t.setchannels(t_knot);
t.save('square_root.cube');

t_knot = zeros(size(t.u_knot));
t_knot(16) = 1;
t.setchannels(t_knot);
t.save('delta_16.cube');
