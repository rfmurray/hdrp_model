% model_test_2.m  Test rendering and post-processing models for Lambertian
%                 and unlit materials

% See readme_appendix_b.txt for details about how to run this test.

clear; clc;

addpath ../tools

% choose whether to test results from model_test Unity project with
% a Lambertian or an unlit material
testLambertian = true;
tonemapping = false;

if tonemapping
    tonemap = TonemapCube('linearize.cube');
end

if testLambertian

    % load data generated by Unity project model_test with a Lambertian
    % material
    d = readtable('model_test/data_lambertian.txt');

    % use dot product to find cosine of angle between lighting direction
    % and test plane surface normal
    costheta = d.lightDirX .* d.planeNormalX + d.lightDirY .* d.planeNormalY + d.lightDirZ .* d.planeNormalZ;

    % find rendering model's predictions for rendered color coordinates u_k
    % (exposure in Unity project model_test is set to zero)
    c = 0.822;
    uR = c * srgb(d.planeColorR) .* ( d.directionalIntensity .* srgb(d.directionalColorR) .* max(costheta, 0) / pi + d.ambientMultiplier .* d.ambientColorR );
    uG = c * srgb(d.planeColorG) .* ( d.directionalIntensity .* srgb(d.directionalColorG) .* max(costheta, 0) / pi + d.ambientMultiplier .* d.ambientColorG );
    uB = c * srgb(d.planeColorB) .* ( d.directionalIntensity .* srgb(d.directionalColorB) .* max(costheta, 0) / pi + d.ambientMultiplier .* d.ambientColorB );

    % apply tonemapping
    if tonemapping
        tR = NaN(size(uR));
        tG = NaN(size(uG));
        tB = NaN(size(uB));
        for i = 1:numel(uR)
            tRGB = tonemap.apply([uR(i) uG(i) uB(i)]);
            tR(i) = tRGB(1);
            tG(i) = tRGB(2);
            tB(i) = tRGB(3);
        end
    else
        tR = uR;
        tG = uG;
        tB = uB;
    end

    % apply sRGB nonlinearity to get predictions for post-processed color
    % coordinates v_k
    vR = srgbinv(tR);
    vG = srgbinv(tG);
    vB = srgbinv(tB);

else

    % load data generated by Unity project model_test with an unlit material
    d = readtable('model_test/data_unlit.txt');

    % predicted post-processed color coordinates are simply the unlit
    % material coordinates
    vR = d.planeColorR;
    vG = d.planeColorG;
    vB = d.planeColorB;

    % *** apply tonemapping in this case too

end

% plot predicted post-processed color coordinates v_k against actual,
% rendered coordinates; just plot a subset, so that results for the blue
% channel (which are plotted last) don't cover up results for the red
% and green channels
figure(1);
xylim = [ 0 1.2 ];
plot(xylim, xylim, 'k-');
hold on
hr = plot(d.renderR(1:30), vR(1:30), 'ro', 'MarkerFaceColor', 'r', 'MarkerSize', 8);
hg = plot(d.renderG(1:30), vG(1:30), 'go', 'MarkerFaceColor', 'g', 'MarkerSize', 8);
hb = plot(d.renderB(1:30), vB(1:30), 'bo', 'MarkerFaceColor', 'b', 'MarkerSize', 8);
hold off
axis square
axis([ xylim xylim ]);
xlabel 'actual v_k'
ylabel 'predicted v_k'
legend([hr hg hb], 'red channel', 'green channel', 'blue channel', 'location', 'northwest', 'box', 'off');
set(gca,'FontSize',18);
print -dpdf model_test_2a.pdf
print -depsc2 model_test_2a.eps

figure(2);
xlim = [ 0 1 ];
hr = plot(d.renderR,vR-d.renderR, 'ro', 'MarkerFaceColor', 'r', 'MarkerSize', 8);
hold on
hg = plot(d.renderG,vG-d.renderG,'go', 'MarkerFaceColor', 'g', 'MarkerSize', 8);
hb = plot(d.renderB,vB-d.renderB,'bo', 'MarkerFaceColor', 'b', 'MarkerSize', 8);
plot(xlim,(-1/255)*[ 1 1 ],'k-');
plot(xlim,(1/255)*[ 1 1 ],'k-');
hold off
axis square
axis([ xlim (5/255)*[ -1 1 ] ]);
xlabel 'actual v_k'
ylabel 'prediction error for v_k'
legend([hr hg hb], 'red channel', 'green channel', 'blue channel', 'location', 'northwest', 'box', 'off');
set(gca,'FontSize',18);
print -dpdf model_test_2b.pdf
print -depsc2 model_test_2b.eps
