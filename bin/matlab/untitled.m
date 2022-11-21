
clc;
clear;
CT_folder = 'G:\data\dentAL\2022年8月25日\2022年8月25日\上颌\单颗\史娜娜\ct';  %% get dicom data folder; 
imds = imageDatastore(sprintf('%s/*.dcm', CT_folder), 'FileExtensions', '.dcm');

if length(imds.Files) < 1
    fprintf('No DICOM data found in foder \n "%s" \n ', CT_folder); 
end

fprintf('Start reading ct data in folder \n "%s" \n ', CT_folder); 

info = dicominfo(imds.Files{end}); %% get dicom information; 

Mx = single(info.Rows); 
My = single(info.Columns); 
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

mask = data > 1500 & data < 3000;

data = data .* mask;

% 2D

% slice_no = 120;
% slice = squeeze(data(:, :, slice_no));
% slice = (slice - min(slice)) ./ (max(slice) - min(slice));
% slice(isnan(slice)) = 0;

% 3D

% data = (data - min(data)) ./ (max(data) - min(data));
% data(isnan(data)) = 0;

[L, centres] = imsegkmeans3(single(data), 3);

type1 = zeros(size(data));
type2 = zeros(size(data));
type3 = zeros(size(data));

type1(L==1) = 1;
type2(L==2) = 1;
type3(L==3) = 1;

niftiwrite(type1, 'type1');
niftiwrite(type2, 'type2');
niftiwrite(type3, 'type3');
niftiwrite(data, 'data');