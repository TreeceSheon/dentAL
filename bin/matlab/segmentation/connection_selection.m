function outline = connection_selection(map)
    
    while true
        
        areas = bwlabel(map, 4);
        
        if sum(areas(areas == 10)) ~= 0
            
            se = strel('square', 10);

            map = imfill(map, 'hole');

            map = imdilate(map, se);
        
        else
            break
        
        end
    end
        

    ii = 1;
    count = 0;
    idx = 0;

    while(true)
        
        new_count = areas == ii;
        new_count = sum(new_count(:));

        if new_count == 0

            break;
        
        end

        count = max(count, new_count);

        if count == new_count
            
            idx = ii;
        
        end

       ii = ii + 1;
    
    end
    
    outline = zeros(size(areas));

    outline(areas == idx) = -1000;

    outline = edge(outline,'sobel');


end


    