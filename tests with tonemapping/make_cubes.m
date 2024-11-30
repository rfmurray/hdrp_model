% make_cube.m  Make a few cube files

clear; clc;

addpath hdrp

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

t_knot = t.u_knot;
t.setchannels(t_knot);
t.save('identity.cube');

t_knot = NaN(size(t.u_knot));
t_knot(1:2:end) = 0.1;
t_knot(2:2:end) = 0.9;
t.setchannels(t_knot);
t.save('sawtooth.cube');
