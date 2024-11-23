% fit_knots.m

clear; clc;

% addpath ../tools
addpath tools

% d1 = readtable('model_test/data_lambertian_notonemap.txt');
% d2 = readtable('model_test/data_lambertian_tonemap.txt');

d1 = readtable('model_test/data_unlit_notonemap.txt');
d2 = readtable('model_test/data_unlit_tonemap.txt');

tonemap = TonemapCube('model_test/Assets/square_root.cube');

v1_rgb = [ d1.renderR d1.renderG d1.renderB ];
v2_rgb = [ d2.renderR d2.renderG d2.renderB ];

u1_rgb = srgb(v1_rgb);
t2_rgb_hat = tonemap.apply(u1_rgb);
v2_rgb_hat = srgbinv(t2_rgb_hat);

figure(1);
plot(v2_rgb(:), v2_rgb_hat(:), 'ro', 'MarkerFaceColor' ,'r');
hold on
plot([0 1],[0 1],'k-');
hold off
axis square
xlabel 'actual v_k'
ylabel 'predicted v_k'
set(gca,'FontSize',18);

figure(2);
plot(v2_rgb(:), v2_rgb_hat(:) - v2_rgb(:),'ro', 'MarkerFaceColor', 'r');
hold on
plot([0 1],(1/255)*[1 1],'k-');
plot([0 1],-(1/255)*[1 1],'k-');
hold off
axis square
xlabel 'actual v_k'
ylabel 'prediction error in v_k'
set(gca,'FontSize',18);

errfn2 = @(p) errfn(p, u1_rgb, v2_rgb, tonemap);

k1 = tonemap.u_knot(3:19);
err1 = errfn2(k1)

phat = fminsearch(errfn2, tonemap.u_knot(3:19) + 1);
% *** use fmincon to constrain order of knot points

nknot = numel(t.u_knot(3:19));
A = eye(nknot) + diag(repmat(-1,[1 nknot-1]),1);
A = A(1:end-1,:);
B = zeros([ size(A,1) 1]);

tonemap.u_knot(3:19) = phat;
tonemap.makecoord;

k2 = tonemap.u_knot(3:19);
err2 = errfn2(k2)

t2_rgb_hat = tonemap.apply(u1_rgb);
v2_rgb_hat = srgbinv(t2_rgb_hat);

figure(3);
plot(v2_rgb(:), v2_rgb_hat(:) - v2_rgb(:),'ro', 'MarkerFaceColor', 'r');
hold on
plot([0 1],(1/255)*[1 1],'k-');
plot([0 1],-(1/255)*[1 1],'k-');
hold off
axis square
xlabel 'actual v_k'
ylabel 'prediction error in v_k'
set(gca,'FontSize',18);

function e = errfn(u_knot, u1_rgb, v2_rgb, tonemap)
tonemap.u_knot(3:19) = u_knot;
tonemap.makecoord;
t2_rgb_hat = tonemap.apply(u1_rgb);
v2_rgb_hat = srgbinv(t2_rgb_hat);
e = sum( (v2_rgb_hat - v2_rgb).^2, "all" );
end
