function savecube(fname, cubemat)

fid = fopen(fname,'w');
fprintf(fid,'TITLE "%s"\n', fname);
fprintf(fid,'LUT_3D_SIZE %d\n', round(power(size(cubemat,1),1/3)));
fprintf(fid,'DOMAIN_MIN 0.0 0.0 0.0\n');
fprintf(fid,'DOMAIN_MAX 1.0 1.0 1.0\n');
fprintf(fid,'%.6f %.6f %.6f\n', cubemat');
fclose(fid);

end
