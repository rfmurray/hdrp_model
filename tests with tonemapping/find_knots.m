% find_knots.m

clear; clc; clf;

addpath hdrp

data = readtable('render_delta.txt');
data = data(data.delta>=3,:);
data.delta = data.delta - 2;
data.u_k = 0.822 * data.i_d / pi;
data.t_k = srgb(data.v_r);

% 1. get initial estimates of peak locations

figure(1);
hold on
xlabel 'rendered u_k'
ylabel 'tonemapped t_k'
set(gca,'FontSize',18);
xlim = [ min(data.u_k) max(data.u_k) ];
axis([ xlim 0 1.1 ]);
set(gca,'XScale','log');
box on

n = max(data.delta);
u_knot_init = NaN([ n 1 ]);

figure(1);
set(gcf,'Position',[50 500 1400 400]);

for i = 1:n
    
    d = data(data.delta==i,:);
    
    if i==1
        j = find(d.t_k>0.99,1,'last');
    elseif i==n
        j = find(d.t_k==1,1,'first');
    else
        [~,j] = max(d.t_k);
    end
    u_knot_init(i) = d.u_k(j);
    
    plot(d.u_k, d.t_k, 'ro', 'MarkerSize', 4, 'MarkerFaceColor', 'r');
    plot(u_knot_init(i)*[ 1 1 ],[ 0 1.1 ],'k-');
    h = text(u_knot_init(i)*0.95, 1.05, sprintf('%d',i+2));
    h.FontSize = 14;
    drawnow;

end

% 2. refine estimates of peak locations

errfn2 = @(p) errfn(p,data);
u_knot = fminsearch(errfn2,u_knot_init);

% u_knot = u_knot_init;

% interpolation between these knot points works differently, so the
% initial estimates are more accurate
u_knot(1:2) = u_knot_init(1:2);

% check that the new knot points are better
err_pre = errfn(u_knot_init,data)
err_post = errfn(u_knot,data,true)

fprintf('%.3e ',u_knot);
fprintf('\n');

hold off

function err = errfn(p, data, plotit)

if nargin<3, plotit=false; end

if plotit
    xx = logspace(log10(min(data.u_k)),log10(max(data.u_k)),10000);
end

n = max(data.delta);
err = 0;
for i = 1:n
    d = data(data.delta==i,:);
    t_k_hat = npeaks(d.u_k,i,p);
    err = err + sum((t_k_hat-d.t_k).^2);
    
    if plotit
        plot(xx,npeaks(xx,i,p),'b-');
    end

end

if plotit
    drawnow;
end

end
