% make_cube.m

clear; clc;

addpath tools

t = TonemapCube;
t_knot = t.u_knot .^ 2;
t.setchannels(t_knot);
t.save('square.cube');
