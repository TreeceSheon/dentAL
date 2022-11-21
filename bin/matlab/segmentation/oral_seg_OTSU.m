
function [background, gum] = oral_seg_OTSU(slice)

    idx = otsu(slice, 2);
    
    background = zeros(size(slice));
    gum = zeros(size(slice));
    
    
    background(idx == 1) = 1;
    gum(idx == 2) = 1;
end
