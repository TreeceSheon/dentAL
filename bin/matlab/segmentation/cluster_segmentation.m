clc;
clear;
close all;

oral_model = niftiread('G:\dentAL\data\down\single\0001\0001.nii');

% thers_map = oral_model > 500 & oral_model < 2500;
% 
% mask = zeros(size(oral_model));
% mask(thers_map) = 1;
% 
% oral_model(mask ~= 1) = 0;

niftiwrite(oral_model, 'tmodel')


slice_no = 450;

slice = squeeze(oral_model(slice_no, :, :));

lap_operator = [0 1 0; 1 -4 1;0 1 0];


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

figure, imshow(OTSU_outline_gum);
figure, imshow(cluster_outline1);

%% Down Side (185-208)

% se90 = strel('line',6,90);
% se0 = strel('line',6,0);
% BWsdil = imdilate(OTSU_outline_gum,[se90 se0]); % Dilation to fill the empty 
% figure, imshow(BWsdil);
% 
% BW2 = bwareaopen(BWsdil, 1000); % Delete all parts below 6000 pixels
% figure, imshow(BW2)
% title('Cleared Image1')
% 
% se90 = strel('line',5,90);
% se0 = strel('line',5,0);
% se1 = strel('diamond',7);
% BW3 = imdilate(BW2,se1);
% BW3 = imerode(BW3,se1);
% BW3 = imerode(BW3,[se90 se0]);
% figure, imshow(BW3);
% 
% BWdfill = imfill(BW3,'holes'); % Fill the holes
% figure, imshow(BWdfill)
% title('Binary Image with Filled Holes')
% 
% BW1 = edge(BWdfill,'sobel');
% figure, imshow(BW1)
% title('Smooth result')


%% Upper Side (52-70)

se90 = strel('line',20,90);
se0 = strel('line',45,0);
BWsdil = imdilate(OTSU_outline_gum,[se90 se0]); % Dilation to fill the empty 
% figure, imshow(BWsdil);

BW2 = bwareaopen(BWsdil, 1000); % Delete all parts below 6000 pixels
% figure, imshow(BW2)
% title('Cleared Image1')

se90 = strel('line',5,90);
se0 = strel('line',25,0);
BW3 = imerode(BW2,[se90 se0]);
% figure, imshow(BW3);

BWdfill = imfill(BW3,'holes'); % Fill the holes
% figure, imshow(BWdfill)
% title('Binary Image with Filled Holes')

BW1 = edge(BWdfill,'sobel');
figure, imshow(BW1)
title('Smooth result')


% niftiwrite(OTSU_outline_gum, 'OTSU_gum');
% niftiwrite(cluster_outline1, 'cluster1');
% niftiwrite(cluster_outline2, 'cluster2')





