function x = srgbinv( y )

Phi = 12.9232102;
Gamma = 2.4;
A = 0.055;
Y = 0.0030399;

x = NaN(size(y));
f = (y<Y);
x(f) = y(f)*Phi;
x(~f) = power(y(~f),1/Gamma)*(1+A)-A;

end
