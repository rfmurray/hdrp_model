function c = vec2cube( v )

n = numel(v);

vr = reshape(v,[ n 1 ]);
r = repmat(vr,[ 1 n n ]);

vg = reshape(v,[ 1 n ]);
g = repmat(vg,[ n 1 n ]);

vb = reshape(v,[ 1 1 n ]);
b = repmat(vb,[ n n 1 ]);

c = [ r(:) g(:) b(:) ];

end
