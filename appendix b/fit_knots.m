% fit_knots.m

clear; clc;

% addpath ../tools
addpath tools

data1 = readtable('data_L1_T0_F1_A1_S05000_M1.txt');
data2 = readtable('data_L1_T1_F1_A1_S05000_M1.txt');

% data1 = readtable('data_L0_T0_F1_A1_S05000_M1.txt');
% data2 = readtable('data_L0_T1_F1_A1_S05000_M1.txt');

v1 = [ data1.renderR data1.renderG data1.renderB ];
v2 = [ data2.renderR data2.renderG data2.renderB ];

tonemap = TonemapCube('square_root.cube');

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
LB(1) = 1e-8;

UB = Inf([ nknot 1]);
UB(end) = 1.4;

errfn2 = @(p) errfn(p, u1, v2, tonemap, A, B, LB, UB);
pinit = tonemap.u_knot(3:19)';

A * pinit <= B
pinit >= LB
pinit <= UB

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
