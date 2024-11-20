function y = srgb( x )

Phi = 12.9232102;
Gamma = 2.4;
A = 0.055;
X = 0.0392857;

y = NaN(size(x));
f = (x<X);
y(f) = x(f)/Phi;
y(~f) = power((x(~f)+A)/(1+A),Gamma);

end
