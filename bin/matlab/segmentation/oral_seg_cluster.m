function [background, gum] = oral_seg_cluster(slice)


    [L, centres] = imsegkmeans(single(slice), 2);

    background = zeros(size(slice));
    gum = zeros(size(slice));

    background(L == 1) = 1;
    gum(L == 2) = 2;
end