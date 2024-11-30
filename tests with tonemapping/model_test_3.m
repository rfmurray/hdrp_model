% model_test_3.m  Test effect of tonemapping

clear; clc;

addpath hdrp

data0 = readtable('data_L1_T0.txt');
data1 = readtable('data_L1_T1.txt');

plot(data0.v_r, data1.v_r, 'ro', 'MarkerFaceColor' ,'r');
hold on
plot(data0.v_g, data1.v_g, 'go', 'MarkerFaceColor' ,'g');
plot(data0.v_b, data1.v_b, 'bo', 'MarkerFaceColor' ,'b');
hold off
axis square
axis([0 1 0 1]);
xlabel v1_k
ylabel v2_k
set(gca,'FontSize',18);

t = TonemapCube('sawtooth.cube');
v1_k = linspace(0,1,1000)';
u1_k = srgb(v1_k);
t_k = t.apply(repmat(u1_k,[1 3]));
t_k = t_k(:,1);
v2_k = srgbinv(t_k);

hold on
plot(v1_k,v2_k,'r-','LineWidth',2);

% vv1 = linspace(0,1,100);
% uu1 = srgb(vv1);
% uu2 = uu1.^2;
% vv2 = srgbinv(uu2);
% plot(vv1, vv2, 'r--','LineWidth',2);

hold off
