#! python3
"""
Created on Mon Feb 24 14:19:41 2020

@author: bharvey2
"""


def breach_depressions_00(in_dem_path, dist=50):
    """
    
    
    Parameters
    ----------
    :param in_dem_path: string
        Path to the input dem .tif
    :param output_path: string
        Path to save the new file
    :param dist: integer
    
    """
    
    import os
    import re
    
    from whitebox_tools import WhiteboxTools
    
    wbt = WhiteboxTools()
    
    in_dsm_path = os.path.dirname(in_dem_path)
    in_dsm_parent = os.path.dirname(in_dsm_path)    
    in_file_name = os.path.basename(in_dem_path)
    huc = in_file_name.split('_')[0]
    
    # Get highest numbered group
    grps = os.listdir(in_dsm_parent)
    grpRegex = re.compile(r'DSM(\d\d)_.*')
    mo = grpRegex.search(re.escape(in_dsm_path))
    in_grpno = mo.group(1)
        
    #TODO: Replace this with a list comprehension
    grpnos = []
    for g in grps:
        new_mo = grpRegex.search(g)
        grpno = new_mo.group(1)
        grpnos.append(int(grpno))
    
    out_grpno = ('0' + str(max(grpnos) + 1))[-2:]
    out_dsm = "DSM{}_DEM{}".format(out_grpno, in_grpno)
    out_dsm_path = os.path.join(in_dsm_parent, out_dsm)
    os.mkdir(out_dsm_path)
    
    out_file_name = "{}_DEM{}_DEM{}.tif".format(huc.upper(), out_grpno, in_grpno)    
    output_path = os.path.join(out_dsm_path, out_file_name)
    
    wbt.breach_depressions_least_cost(in_dem_path, output_path, dist)
