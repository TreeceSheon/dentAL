function vector_neighbor = area_neighbor_find_C(row,col,area_index)
I = zeros(row,col);
se=ones(3);
I(area_index) = 1;
I2 = imfilter(I,se);  % 滤波
I2=I2-I.*9;
vector_neighbor = find(I2>0);
