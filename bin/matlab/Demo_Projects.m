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

% note:   increment by 1 when starting from 0
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
%% 2. load STL file and convert it into 3D data matrix; 
%-----------------------------------------------------------------------%

info = dicominfo('G:\data\dentAL\2022年8月25日\2022年8月25日\上颌\单颗\娄媛媛\cbct-25_25_72_20220614174852498674_892655\MyDentViewer_Demo\Data\0000.dcm'); %% MUST use the first slice for accurate coordination conversion; 

[M,R] = TransMatrix(info);  %% get the affine matrix to convert FOV coords into real-world coords; 

% from FOV coordinates to real-world coords; 
min_coors = M * double([0 0 0 1]'); 
max_coors = M * double([Mx - 1, My - 1, Mz - 1, 1]');

% generated grids for converting STL to 3D data; 
% need additional method to assign which axis is X-axis, which one is Y,
% and which one is Z-; 
gridX = min_coors(1) : (max_coors(1) - min_coors(1))/(Mx - 1) : max_coors(1);
gridY = min_coors(2) : (max_coors(2) - min_coors(2))/(My - 1) : max_coors(2);
gridZ = min_coors(3) : (max_coors(3) - min_coors(3))/(Mz - 1) : max_coors(3);

% Voxelise the STL file one bye one;
ReadData = true; 
while ReadData
    x = input('Read More STL data? Y/N (default: Y). \n', 's');
    if contains(x, 'y') || contains(x, 'Y') || isempty(x)
        [fname, ffolder] = uigetfile('*.stl');  %% get STL files;
        fprintf('Reading and voxelizing STL file "%s" \n ', fname);
%         [OUTPUTgrid] = VOXELISE(gridX,gridY,gridZ,[ffolder, fname],'yxz');  %% from STL to 3D;
        tmp = mystlread([ffolder, fname]);
        OUTPUTgrid = inpolyhedron(tmp,gridX,gridY,gridZ);
        % saving
        fprintf('STL file resaved as NIFTI in Foler: "%s" \n ', WorkingFolder);
        nii = make_nii(single(OUTPUTgrid), [info.PixelSpacing(1), info.PixelSpacing(2), info.SliceThickness]);
        ConvertName = strrep(fname, '.stl', '.nii');
        save_nii(nii, sprintf('%s/%s', WorkingFolder, ConvertName));
    else
        disp('All data resaved!');
        ReadData = false; 
    end
end

%-----------------------------------------------------------------------%
%% 3. Combine all data to generate training datasets; 
%-----------------------------------------------------------------------%
% combine jaw data;
data1 = niftiread('DemoPrjectFolder/lower.nii'); 
data2 = niftiread('DemoPrjectFolder/upperjaw.nii'); 

jawdata = single(data1 + data2); 

nii = make_nii(jawdata, [info.PixelSpacing(1), info.PixelSpacing(2), info.SliceThickness]); 
save_nii(nii, sprintf('%s/Jaw_data_STL.nii', WorkingFolder)); 

plant1 = niftiread('DemoPrjectFolder/16植体.nii');
plant2 = niftiread('DemoPrjectFolder/17植体.nii');

% data = data + plant1 * 2 + plant2 * 3; 
% jawdata = jawdata + plant1 * 2 + plant2 * 3;  

mask1 = plant1 ~= 0; 
mask2 = plant2 ~= 0; 

data = data .* (1 - mask1); 
data = data .* (1 - mask2); 

jawdata = jawdata .* (1 - mask1); 
jawdata = jawdata .* (1 - mask2); 

nii = make_nii(single(jawdata), [info.PixelSpacing(1), info.PixelSpacing(2), info.SliceThickness]); 
save_nii(nii, sprintf('%s/BinaryTraining.nii', WorkingFolder)); 

nii = make_nii(single(data), [info.PixelSpacing(1), info.PixelSpacing(2), info.SliceThickness]); 
save_nii(nii, sprintf('%s/CT_Training.nii', WorkingFolder)); 


tmp = regionprops3(mask1);
RegionBox1 = round(tmp.BoundingBox);

tmp = regionprops3(mask2);
RegionBox2 = round(tmp.BoundingBox);

%-----------------------------------------------------------------------%
% demo one slice; 
data = data + plant1 * 2 + plant2 * 3; 
tmp = data(:,:, round(RegionBox1(3) + 1/2 * RegionBox1(6))); 
tmp = insertShape(squeeze(tmp), 'Rectangle', [RegionBox1(1),RegionBox1(2), RegionBox1(4),RegionBox1(5)], 'LineWidth', 3);
figure, imagesc(squeeze(tmp));


data = data + plant1 * 2 + plant2 * 3; 
tmp = data(:,:, round(RegionBox2(3) + 1/2 * RegionBox2(6))); 
tmp = insertShape(squeeze(tmp), 'Rectangle', [RegionBox2(1),RegionBox2(2), RegionBox2(4),RegionBox2(5)], 'LineWidth', 3);
figure, imagesc(squeeze(tmp)); caxis([0, 0.2]); 



%-----------------------------------------------------------------------%
%% 4. DL prediction (to be finished)
%-----------------------------------------------------------------------%
% codes to be implemented; 


%-----------------------------------------------------------------------%
%% 5. Convert back; 
%-----------------------------------------------------------------------%
res1 = ones(RegionBox1(4), RegionBox1(5),RegionBox1(6));
res2 = ones(RegionBox2(4), RegionBox2(5),RegionBox2(6));
% 
% nii = make_nii(single(res1), [info.PixelSpacing(1), info.PixelSpacing(2), info.SliceThickness]); 
% save_nii(nii, sprintf('%s/solution1.nii', WorkingFolder)); 
% 
% nii = make_nii(single(res2), [info.PixelSpacing(1), info.PixelSpacing(2), info.SliceThickness]); 
% save_nii(nii, sprintf('%s/solution2.nii', WorkingFolder)); 

% minCoors = M * [RegionBox1(1), RegionBox1(2), RegionBox1(3), 1]'; 
% maxCoors = M * [(RegionBox1(1) + RegionBox1(4) - 1), (RegionBox1(2) + RegionBox1(5) -1) ,...
%         (RegionBox1(3) + RegionBox1(6) - 1), 1]'; 
%     
% gridX = minCoors(1) : (maxCoors(1) -  minCoors(1)) / (RegionBox1(4) - 1) : maxCoors(1); 
% gridY = minCoors(1) : (maxCoors(1) -  minCoors(1)) / (RegionBox1(5) - 1) : maxCoors(1); 
% gridZ = minCoors(1) : (maxCoors(1) -  minCoors(1)) / (RegionBox1(6) - 1) : maxCoors(1); 

gridX = 1 : 1 : RegionBox1(4); 
gridY = 1 : 1 : RegionBox1(5); 
gridZ = 1 : 1 : RegionBox1(6); 

CONVERT_voxels_to_stl(sprintf('%s/sol1.stl', WorkingFolder), res1 ,gridX,gridY,gridZ,'binary'); 

% % second data
% minCoors = M * [RegionBox2(1), RegionBox2(2), RegionBox2(3), 1]'; 
% maxCoors = M * [(RegionBox2(1) + RegionBox2(4) - 1), (RegionBox2(2) + RegionBox2(5) -1) ,...
%         (RegionBox2(3) + RegionBox2(6) - 1), 1]'; 
%     
% gridX = minCoors(1) : (maxCoors(1) -  minCoors(1)) / (RegionBox2(4) - 1) : maxCoors(1); 
% gridY = minCoors(1) : (maxCoors(1) -  minCoors(1)) / (RegionBox2(5) - 1) : maxCoors(1); 
% gridZ = minCoors(1) : (maxCoors(1) -  minCoors(1)) / (RegionBox2(6) - 1) : maxCoors(1); 


gridX = 1 : 1 : RegionBox2(4); 
gridY = 1 : 1 : RegionBox2(5); 
gridZ = 1 : 1 : RegionBox2(6); 

CONVERT_voxels_to_stl(sprintf('%s/sol2.stl', WorkingFolder), res2 ,gridX,gridY,gridZ,'binary'); 

% correct coordinates for STL ;
fv = mystlread(sprintf('%s/sol1.stl', WorkingFolder)); 
n_VerticesNum = size(fv.vertices);
TempData=ones(4,1);
for num=1:n_VerticesNum
    TempData(1:3,1) = (fv.vertices(num,:))';
    TempResult = M * (TempData + [RegionBox1(1), RegionBox1(2), RegionBox1(3), 1]' - 1);
    fv.vertices(num,:) = TempResult(1:3, 1);
end
mystlwrite(sprintf('%s/sol1.stl', WorkingFolder), fv);



% correct coordinates for STL ;
fv = mystlread(sprintf('%s/sol2.stl', WorkingFolder)); 
n_VerticesNum = size(fv.vertices);
TempData=ones(4,1);
for num=1:n_VerticesNum
    TempData(1:3,1) = (fv.vertices(num,:))';
    TempResult = M * (TempData + [RegionBox2(1), RegionBox2(2), RegionBox2(3), 1]' - 1);
    fv.vertices(num,:) = TempResult(1:3, 1);
end
mystlwrite(sprintf('%s/sol2.stl', WorkingFolder), fv);





