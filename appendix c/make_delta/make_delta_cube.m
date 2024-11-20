% make_delta_cube.m

clear; clc;

addtools vrcal

deltan = 32;

subdir = 'delta';
unix(sprintf('rm -fr %s',subdir));
unix(sprintf('mkdir %s',subdir));

for i = 1:deltan

    v = zeros([ deltan 1 ]);
    v(i) = 1;
    c = vec2cube(v);

    fname = sprintf('%s/delta_%02d.cube', subdir, i);
    fprintf('%s\n',fname);
    savecube(fname,c);

end
