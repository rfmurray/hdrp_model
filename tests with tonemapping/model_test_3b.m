% model_test_3b.m  Test effect of tonemapping

clear; clc;

addpath hdrp

data0 = readtable('data_L1_T0.txt');
data1 = readtable('data_L1_T1.txt');

vmax = 0.98;
k = data0.v_r < vmax & data0.v_g < vmax & data0.v_b < vmax & data1.v_r < vmax & data1.v_g < vmax & data1.v_b;
data0 = data0(k,:);
data1 = data1(k,:);

data0.t_r = srgb(data0.v_r);
data0.t_g = srgb(data0.v_g);
data0.t_b = srgb(data0.v_b);
data1.t_r = srgb(data1.v_r);
data1.t_g = srgb(data1.v_g);
data1.t_b = srgb(data1.v_b);

plot(data0.t_r, data1.t_r, 'ro', 'MarkerFaceColor' ,'r');
hold on
plot(data0.t_g, data1.t_g, 'go', 'MarkerFaceColor' ,'g');
plot(data0.t_b, data1.t_b, 'bo', 'MarkerFaceColor' ,'b');
hold off
axis([0 1 0 1]);
xlabel t1_k
ylabel t2_k
set(gca,'FontSize',18);

tonemap = TonemapCube('sawtooth.cube');
u1_k = linspace(0,1,1000)';
t1_k = u1_k;
t2_k = tonemap.apply(repmat(u1_k,[1 3]));
t2_k = t2_k(:,1);
hold on
plot(t1_k,t2_k,'r-','LineWidth',2);
hold off


nknot = numel(tonemap.u_knot(3:19));

A = eye(nknot) + diag(repmat(-1,[1 nknot-1]),1);
A = A(1:end-1,:);
B = zeros([ size(A,1) 1]);

LB = -Inf([ nknot 1]);
LB(1) = 1e-8;

UB = Inf([ nknot 1]);
UB(end) = 1.4;

u0 = [ data0.t_r data0.t_g data0.t_b ];
t1 = [ data1.t_r data1.t_g data1.t_b ];

errfn2 = @(p) errfn(p, u0, t1, tonemap, A, B, LB, UB);
pinit = tonemap.u_knot(3:19)';
phat = fmincon(errfn2, pinit, A, B, [], [], LB, UB);
tonemap.u_knot(3:19) = phat;


t2_k = tonemap.apply(repmat(u1_k,[1 3]));
t2_k = t2_k(:,1);
hold on
plot(t1_k,t2_k,'g-','LineWidth',2);
hold off

fprintf('u_knot = [ ');
fprintf('%.6e, ',tonemap.u_knot);
fprintf(']\n');


% t2_hat = tonemap.apply(u1);
% v2_hat = srgbinv(t2_hat);
% 
% fprintf('%.4g ',tonemap.u_knot);
% fprintf('\n');
% 
% figure(3);
% plot(v2(:), v2_hat(:) - v2(:),'ro', 'MarkerFaceColor', 'r');
% hold on
% plot([0 1],(1/255)*[1 1],'k-');
% plot([0 1],-(1/255)*[1 1],'k-');
% hold off
% axis square
% axis([0 1 -0.015 0.015 ]);
% xlabel 'actual v_k'
% ylabel 'prediction error in v_k'
% set(gca,'FontSize',18);


function err = errfn(param, u0, t1, tonemap, A, B, LB, UB)

constraintsAB = A * param <= B;
constraintsLB = param >= LB;
constraintsUB = param <= UB;
if ~all(constraintsAB) || ~all(constraintsLB) || ~all(constraintsUB)
    err = Inf;
    return
end

tonemap.u_knot(3:19) = param;
t1_hat = tonemap.apply(u0);
err = sum( (t1_hat - t1).^2, "all" );

end
