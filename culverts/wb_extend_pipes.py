#! python3

"""
Created on Thu Jan 23 15:54:14 2020

@author: bharvey2
"""


def extend_pipes_00(in_pipe_paths, dist='10.0'):
    """
    Extend pipe lines in vector files by the specified distance.
    
    Parameters
    ----------
    :param in_pipe_paths: list
        List of paths to the pipe files.
    :param dist: string
        Length (in feet) to extend the pipe lines from each end.
    """
    
    import os
    
    from whitebox_tools import WhiteboxTools
    
    wbt = WhiteboxTools()
        
    for p in in_pipe_paths:
        group_path = os.path.dirname(p)    
        in_file_name = os.path.basename(p)
        
        huc = in_file_name.split("_")[0]
        source = in_file_name.split("_")[1]
        grpno = source[-2:]
        out_file = "{}_XTPIPE{}_{}.shp".format(huc, grpno, source)        
        out_path = os.path.join(group_path, out_file)

        wbt.extend_vector_lines(p, out_path, dist)

