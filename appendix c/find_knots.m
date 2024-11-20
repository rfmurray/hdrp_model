% fit_knots.m

clear; clc; clf;

addtools vrcal

data = load('find_knots/data_knots.txt');
data = data(data(:,1)>=3,:);
data(:,1) = data(:,1)-2;
% data(:,3) = data(:,3)/pi;

% 1. get initial estimates of peak locations

figure(1);
hold on
xlabel 'light intensity'
ylabel 'tonemapped k_t'
set(gca,'FontSize',18);
xlim = [ min(data(:,2)) max(data(:,2)) ];
axis([ xlim 0 1.1 ]);
set(gca,'XScale','log');
box on

n = max(data(:,1));
k_i_knot_init = NaN([ n 1 ]);

for i = 1:n
    
    d = data(data(:,1)==i,:);
    % trialnum = d(:,2);
    k_i = d(:,2);
    % k_m = d(:,4)/255;
    % theta = d(:,5);
    k_f = d(:,3)/255;
    k_t = srgb(k_f);
    
    if i==1
        k_i_knot_init(i) = 0;
    elseif i==n
        j = find(k_t==1,1,'first');
        k_i_knot_init(i) = k_i(j);
    else
        [~,j] = max(k_t);
        k_i_knot_init(i) = k_i(j);
    end
    
    plot(k_i, k_t, 'ro-', 'MarkerSize', 4, 'MarkerFaceColor', 'r');
    plot([ k_i_knot_init(i) k_i_knot_init(i) ],[ 0 255 ],'k-');
    drawnow;
    % pause;

end

return

% 2. get better estimates of peak locations

err_pre = errfn(k_i_knot_init,data)

errfn2 = @(p) errfn(p,data);
k_i_knot = fminsearch(errfn2,k_i_knot_init);

err_post = errfn(k_i_knot,data,true)

% convert k_i to k_d and save
% k_d_knot = 0.2622 * k_i_knot * 1.0 * cosd(0) / (2^0);
% save k_d_knot.mat k_d_knot


function err = errfn(p, data, plotit)

if nargin<3, plotit=false; end

if plotit
    k_i = data(:,3);
    xx = logspace(log10(min(k_i)),log10(max(k_i)),10000);
end

n = max(data(:,1));
err = 0;
for k = 1:n
    d = data(data(:,1)==k,:);
    k_i = d(:,3);
    k_f = d(:,6)/255;
    k_t = srgb(k_f);
    k_t_hat = npeaks(k_i,k,p);
    err = err + sum((k_t_hat-k_t).^2);

    if plotit
        plot(xx,npeaks(xx,k,p),'b-');
    end

end

if plotit
    drawnow;
end

end
