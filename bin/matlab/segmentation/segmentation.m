clc;
clear;

oral_model = niftiread('G:\dentAL\data\down\single\0001\0001.nii');

% thers_map = oral_model > 500 & oral_model < 2500;
% 
% mask = zeros(size(oral_model));
% mask(thers_map) = 1;
% 
% oral_model(mask ~= 1) = 0;


slice_no = 460;

slice = squeeze(oral_model(slice_no, :, :));

normed_slice = int32(normalize(slice));


%% dilation

se = strel('square', 10);

slice = imfill(slice, 'hole');


dilated_slice = imdilate(slice, se);

% imshow(dilated_slice)

%% 2D cluster segmentation

[cluster1, cluster2] = oral_seg_cluster(dilated_slice);

%% 2D OTSU segmentation

[OTSU_background, OTSU_gum] = oral_seg_OTSU(dilated_slice);

%% outline selection

OTSU_outline_gum = connection_selection(OTSU_gum);
cluster_outline1 = connection_selection(cluster1);
cluster_outline2 = connection_selection(cluster2);


niftiwrite(int32(OTSU_outline_gum), 'OTSU_gum');
niftiwrite(int32(cluster_outline1), 'cluster1');
niftiwrite(int32(cluster_outline2), 'cluster2');


% niftiwrite(int32(OTSU_outline_gum) + int32(slice), 'OTSU_gum');
% niftiwrite(int32(cluster_outline1) + int32(slice), 'cluster1');
% niftiwrite(int32(cluster_outline2) + int32(slice), 'cluster2');




