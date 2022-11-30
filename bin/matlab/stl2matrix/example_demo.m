clear
clc

[stlcoords, coordNORMALS] = READ_stl('/Volumes/Samsung_T5/data/dentAL/rawdata/data/Single/upper/xurongnan/implant_23.stl');

cx1 = squeeze( stlcoords(:,1,:) );
cy1 = squeeze( stlcoords(:,2,:) );
cz1 = squeeze( stlcoords(:,3,:) );


gridX = min(cx1) : (max(cx1) - min(cx1))/511 : max(cx1);
gridY = min(cy1) : (max(cy1) - min(cy1))/511 : max(cy1);
gridZ = min(cz1) : (max(cz1) - min(cz1))/511 : max(cz1);

%Voxelise the STL:
[OUTPUTgrid] = VOXELISE(gridX,gridY,gridZ,'/Volumes/Samsung_T5/data/dentAL/rawdata/data/Single/upper/xurongnan/implant_23.stl','xyz');

niftiwrite(single(OUTPUTgrid), 'lower_converted.nii')


[OUTPUTgrid2] = VOXELISE(gridX,gridY,gridZ,'upper.stl','xyz');

niftiwrite(single(OUTPUTgrid2), 'upper_converted.nii')

niftiwrite(single(OUTPUTgrid2 + OUTPUTgrid), 'combined_converted.nii')

% 
% gridX = min(cx1) : (max(cx1) - min(cx1))/511 : max(cx1);
% gridY = min(cy1) : (max(cy1) - min(cy1))/511 : max(cy1);
% gridZ = min(cz1) : (max(cz1) - min(cz1))/511 : max(cz1);


% OUTPUTgrid = imresize3(OUTPUTgrid, [1024, 1024, 1024]); 
% OUTPUTgrid2 = imresize3(OUTPUTgrid2, [1024, 1024, 1024]); 
% 
% gridX = min(cx) : (max(cx) - min(cx))/1023 : max(cx);
% gridY = min(cy) : (max(cy) - min(cy))/1023 : max(cy);
% gridZ = min(cz) : (max(cz) - min(cz))/1023 : max(cz);

tic
CONVERT_voxels_to_stl('lower_convert_back.stl',OUTPUTgrid,gridX,gridY,gridZ,'binary');
toc 

% gridX = min(cx2) : (max(cx2) - min(cx2))/511 : max(cx2);
% gridY = min(cy2) : (max(cy2) - min(cy2))/511 : max(cy2);
% gridZ = min(cz2) : (max(cz2) - min(cz2))/511 : max(cz2);

tic
CONVERT_voxels_to_stl('upper_convert_back.stl',OUTPUTgrid2,gridX,gridY,gridZ,'binary');
toc 




