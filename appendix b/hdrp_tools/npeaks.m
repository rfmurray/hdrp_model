function y = npeaks(x, k, xmax)

xmax = sort(xmax);
n = numel(xmax);

if k<1 || k>n
    error('k out of range');
end

y = NaN(size(x));

if k==1

    flow = x<=xmax(1);
    y(flow) = 1;

    fhigh = x>=xmax(2);
    y(fhigh) = 0;

    p = polyfit( xmax([ 1 2 ]), [ 1 0 ], 1 );
    fmid = ~(flow|fhigh);
    y(fmid) = polyval(p,x(fmid));

elseif k==n

    flow = x<=xmax(n-1);
    y(flow) = 0;

    fhigh = x>=xmax(n);
    y(fhigh) = 1;

    p = polyfit( xmax([ n-1 n ]), [ 0 1 ], 1 );
    fmid = ~(flow|fhigh);
    y(fmid) = polyval(p,x(fmid));

else

    flow = x<=xmax(k-1);
    y(flow) = 0;

    fhigh = x>=xmax(k+1);
    y(fhigh) = 0;

    p1 = polyfit( xmax([ k-1 k ]), [ 0 1 ], 1 );
    fmid1 = x>xmax(k-1) & x<=xmax(k);
    y(fmid1) = polyval(p1,x(fmid1));

    p2 = polyfit( xmax([ k k+1 ]), [ 1 0 ], 1 );
    fmid2 = x>xmax(k) & x<xmax(k+1);
    y(fmid2) = polyval(p2,x(fmid2));

end

if any(isnan(y),'all')
    warning('NaN values remaining');
end

end
