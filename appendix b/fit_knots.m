% fit_knots.m

clear; clc;

% addpath ../tools
addpath tools

% data1 = readtable('model_test/data_lambertian_notonemap.txt');
% data2 = readtable('model_test/data_lambertian_tonemap.txt');

data1 = readtable('model_test/data_unlit_notonemap.txt');
data2 = readtable('model_test/data_unlit_tonemap.txt');

tonemap = TonemapCube('model_test/Assets/square_root.cube');
tonemap.u_knot = [ 0 1e-09 1.402e-05 0.003089 0.007417 0.01272 0.021 0.03146 0.04521 0.06482 0.09131 0.126 0.1736 0.2381 0.3303 0.4483 0.6096 0.8295 1.124 1.498 2.039 2.766 3.76 5.072 6.871 9.398 12.65 17.25 23.25 31.41 43.01 57.74 ];
tonemap.u_knot(3:19) = linspace(0.01,1,17);
tonemap.makecoord;

v1 = [ data1.renderR data1.renderG data1.renderB ];
v2 = [ data2.renderR data2.renderG data2.renderB ];

u1 = srgb(v1);
t2_hat = tonemap.apply(u1);
v2_hat = srgbinv(t2_hat);

figure(1);
plot(v2(:), v2_hat(:), 'ro', 'MarkerFaceColor' ,'r');
hold on
plot([0 1],[0 1],'k-');
hold off
axis square
xlabel 'actual v_k'
ylabel 'predicted v_k'
set(gca,'FontSize',18);

figure(2);
plot(v2(:), v2_hat(:) - v2(:),'ro', 'MarkerFaceColor', 'r');
hold on
plot([0 1],(1/255)*[1 1],'k-');
plot([0 1],-(1/255)*[1 1],'k-');
hold off
axis square
axis([0 1 -0.015 0.015 ]);
xlabel 'actual v_k'
ylabel 'prediction error in v_k'
set(gca,'FontSize',18);

nknot = numel(tonemap.u_knot(3:19));

A = eye(nknot) + diag(repmat(-1,[1 nknot-1]),1);
A = A(1:end-1,:);
B = zeros([ size(A,1) 1]);

LB = -Inf([ nknot 1]);
LB(1) = 1e-5;

UB = Inf([ nknot 1]);
UB(end) = 1.4;

errfn2 = @(p) errfn(p, u1, v2, tonemap, A, B, LB, UB);
pinit = tonemap.u_knot(3:19)';
phat = fmincon(errfn2, pinit, A, B, [], [], LB, UB);

tonemap.u_knot(3:19) = phat;
tonemap.makecoord;

t2_hat = tonemap.apply(u1);
v2_hat = srgbinv(t2_hat);

fprintf('%.4g ',tonemap.u_knot);
fprintf('\n');

figure(3);
plot(v2(:), v2_hat(:) - v2(:),'ro', 'MarkerFaceColor', 'r');
hold on
plot([0 1],(1/255)*[1 1],'k-');
plot([0 1],-(1/255)*[1 1],'k-');
hold off
axis square
axis([0 1 -0.015 0.015 ]);
xlabel 'actual v_k'
ylabel 'prediction error in v_k'
set(gca,'FontSize',18);


function e = errfn(param, u1, v2, tonemap, A, B, LB, UB)

constraintsAB = A * param <= B;
constraintsLB = param >= LB;
constraintsUB = param <= UB;
if ~all(constraintsAB) || ~all(constraintsLB) || ~all(constraintsUB)
    e = Inf;
    return
end

tonemap.u_knot(3:19) = param;
tonemap.makecoord;

% fprintf('%.9f\n',tonemap.u_knot);
% fprintf('\n');

t2_hat = tonemap.apply(u1);
v2_hat = srgbinv(t2_hat);
e = sum( (v2_hat - v2).^2, "all" );

end
