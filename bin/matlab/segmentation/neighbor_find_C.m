function vector_neighbor_C = neighbor_find_C(row,col,nn)
total_number=row*col;
now_col= floor(nn/row)+1;
temp=rem(nn,row);
if temp==0
    now_row=row;
else
    now_row=temp;
end
if nn==1
    vector_neighbor_C=[2;row+1;row+2];
else if nn==row
    vector_neighbor_C=[row;row+row;row+row-1];
    else if nn==total_number-row+1
            vector_neighbor_C=[total_number-row+2;total_number-row-row;total_number-row-row+1];
        else if nn==total_number
                vector_neighbor_C=[total_number-1;total_number-row;total_number-row-1];
            else if now_row==1
                    vector_neighbor_C=[nn+row;nn-row;nn+1;nn+row+1;nn-row+1];
                else if now_row==row
                        vector_neighbor_C=[nn+row;nn-row;nn-1;nn+row-1;nn-row-1];
                    else if now_col==1
                            vector_neighbor_C=[nn+1;nn-1;nn+row;nn+row+1;nn+row-1];
                        else if now_col==col
                                vector_neighbor_C=[nn+1;nn-1;nn-row;nn-row+1;nn-row-1];
                            else
                                vector_neighbor_C=[nn+1;nn-1;nn-row;nn+row;nn-row+1;nn-row-1;nn+row+1;nn+row-1];
                            end
                        end
                    end
                end
            end
        end
    end
end
