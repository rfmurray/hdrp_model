% model_test_3.m  Test effect of tonemapping

clear; clc;

% addpath ../tools
addpath tools

data1 = readtable('model_test/data_lambertian_notonemap.txt');
data2 = readtable('model_test/data_lambertian_tonemap.txt');

% data1 = readtable('model_test/data_unlit_notonemap.txt');
% data2 = readtable('model_test/data_unlit_tonemap.txt');

plot(data1.renderR, data2.renderR, 'ro', 'MarkerFaceColor' ,'r');
hold on
plot(data1.renderG, data2.renderG, 'go', 'MarkerFaceColor' ,'g');
plot(data1.renderB, data2.renderB, 'bo', 'MarkerFaceColor' ,'b');
hold off
axis square
axis([0 1 0 1]);
xlabel v1_k
ylabel v2_k
set(gca,'FontSize',18);

t = TonemapCube('model_test/Assets/delta_16.cube');
t.method = 'linear';
v1_k = linspace(0,1,100)';
u1_k = srgb(v1_k);
t_k = t.apply(repmat(u1_k,[1 3]));
t_k = t_k(:,1);
v2_k = srgbinv(t_k);

hold on
plot(v1_k,v2_k,'c-','LineWidth',2);

% vv1 = linspace(0,1,100);
% uu1 = srgb(vv1);
% uu2 = uu1.^2;
% vv2 = srgbinv(uu2);
% plot(vv1, vv2, 'r--','LineWidth',2);

hold off
