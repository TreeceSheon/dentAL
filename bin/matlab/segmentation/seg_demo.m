clear 
clc 
close all 

addpath('../stl2matrix')
WorkingFolder = 'DemoPrjectFolder';
if ~exist(WorkingFolder, 'dir')
    mkdir(WorkingFolder)
end
%-----------------------------------------------------------------------%
%% 1. load DICOM data;  
%-----------------------------------------------------------------------%
CT_folder = uigetdir();  %% get dicom data folder; 
imds = imageDatastore(sprintf('%s/*.dcm', CT_folder), 'FileExtensions', '.dcm');

if length(imds.Files) < 1
    fprintf('No DICOM data found in foder \n "%s" \n ', CT_folder); 
end

fprintf('Start reading ct data in folder \n "%s" \n ', CT_folder); 

info = dicominfo(imds.Files{end}); %% get dicom information; 

Mx = single(info.Rows); 
My = single(info.Columns); 
% Mz = single(info.ImagesInAcquisition); 
Mz = single(info.InstanceNumber); 

data = zeros(Mx, My, Mz); 

% read all dicom data one by one;
for i = 1 : length(imds.Files)
    tmp_file = imds.Files{i}; 
    tmp_file = split(tmp_file, '/'); 
    tmp_file = tmp_file{end}; 
    
    if strncmpi('.', tmp_file, 1)
        continue; 
    end 
    
    tmp_info = dicominfo(imds.Files{i}); 
    tmp_data = dicomread(imds.Files{i}); 
    
    data(:,:,tmp_info.InstanceNumber) = tmp_data; 
end 

disp('Performing data normlization!')

data = single(data); 
% data normalization; 
data = data - min(data(:)); 
data = data / max(data(:)); 

nii = make_nii(single(data), [info.PixelSpacing(1), info.PixelSpacing(2), info.SliceThickness]); 
save_nii(nii, sprintf('%s/PatientCT.nii', WorkingFolder)); 

fprintf('CT data resaved as NIFTI in foder: "%s" \n', WorkingFolder); 

%-----------------------------------------------------------------------%
%% 2. Find appropriate slice & do the segmentation
%-----------------------------------------------------------------------%

I = data(:,:,196);
figure,
imshow(I)


[~,threshold] = edge(I,'sobel');
fudgeFactor = 0.8;
BWs = edge(I,'sobel',threshold * fudgeFactor); % create binary image

imshow(BWs)
title('Binary Gradient Mask')

imageSize = size(BWs);
ci = [549/2,549/2,540/2];     % center and radius of circle ([c_row, c_col, r])
[xx,yy] = ndgrid((1:imageSize(1))-ci(1),(1:imageSize(2))-ci(2));
mask = single((xx.^2 + yy.^2)<ci(3)^2);
croppedImage = single(zeros(size(BWs)));
croppedImage(:,:) = BWs(:,:).*mask;
imshow(croppedImage);

se90 = strel('line',6,90);
se0 = strel('line',6,0);
BWsdil = imdilate(croppedImage,[se90 se0]); % Dilation to fill the empty 
figure, imshow(BWsdil);


BWdfill = imfill(BWsdil,'holes'); % Fill the holes
imshow(BWdfill)
title('Binary Image with Filled Holes')


BW2 = bwareaopen(BWdfill, 6000); % Delete all parts below 6000 pixels
imshow(BW2)
title('Cleared Image1')

seD = strel('diamond',9);
se3 = strel('disk', 15);
BWfinal = imdilate(BW2,seD);
BWfinal = imdilate(BWfinal,seD);
BWfinal = imerode(BWfinal,seD);
BWfinal = imerode(BWfinal,se3); 
BWfinal = imerode(BWfinal,se3); % Final refine using dilation and erodtion 

imshow(BWfinal)
title('Segmented Image');

imshow(labeloverlay(I,BWfinal))
title('Mask Over Original Image')


