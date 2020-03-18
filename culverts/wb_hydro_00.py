#! python3
"""
From initial DEM and pipe files, create 3 new DSM groups:
- DEM with culverts
- DEM with breached depressions
- DEM with culverts and breached depressions

@author: bharvey2
"""

def new_group_00(in_file_path, source_name=None):
    """ Create the next group in the input file's class
    
    Parameters
    ----------
    in_file_path: str
        Path to input file
    source_name: str
    
    """
    import os
    import re

    in_file_name = os.path.basename(in_file_path)
    source = in_file_name.split("_")[1]
    if source_name == None:
        source_name = source[:-2]
    
    in_grp_path = os.path.dirname(in_file_path)
    in_grp_parent = os.path.dirname(in_grp_path)
    
    grpRegex = re.compile(r'(\w{2,8})(\d{2})_(\w{2,9})$')
    mo = grpRegex.search(re.escape(in_grp_path))
    grp_name = mo.group(1)
    in_grpno = mo.group(2)
    
    grps = os.listdir(in_grp_parent)
    #TODO: Replace this with a list comprehension
    grpnos = []
    for g in grps:
        new_mo = grpRegex.search(g)
        grpno = new_mo.group(2)
        grpnos.append(int(grpno))
    
    out_grpno = ('0' + str(max(grpnos) + 1))[-2:]
    out_grp = "{}{}_{}{}".format(grp_name, out_grpno, source_name, in_grpno)
    out_grp_path = os.path.join(in_grp_parent, out_grp)
    os.mkdir(out_grp_path)
    
    return(out_grp_path)
    
def out_file_00(in_file_path, name, out_ext, out_grp_path=None):
    """
    
    Parameters
    ----------
    in_file_path: string
        Path to input file
    name: string
        Example: "DEM"
    out_ext: string
        File extension for the output file. Example: "shp"
    out_grp_path: string
        Path to output directory. If none given, same as input directory.
    """
    
    import os
    import re
    
    in_file_name = os.path.basename(in_file_path)
    in_grp_path = os.path.dirname(in_file_path)
    
    fileRegex = re.compile(r'(\w{2,9}\d{2})_(\w{2,9})(\d{2})_\w{2,12}_?\w*\.\w{1,5}')
    mo = fileRegex.search(in_file_name)
    huc = mo.group(1)
    source_name = mo.group(2)
    in_grpno = mo.group(3)
    
    if out_grp_path != None:
        grpnoRegex = re.compile(r'(\w{2,9})(\d{2})_\w{2,9}$')
        grp_mo = grpnoRegex.search(out_grp_path)
        out_grpno = grp_mo.group(2)
    else:
        out_grp_path = in_grp_path
        out_grpno = in_grpno
    
    out_file_name = "{}_{}{}_{}{}.{}".format(huc, name, out_grpno, source_name, in_grpno, out_ext)
    out_file_path = os.path.join(out_grp_path, out_file_name)
    
    return(out_file_path)


# def extract_pipes_00(in_pipes_paths, dem):
#    """ Clip pipe features to map extent
#    
#    Parameters
#    ----------
#    in_pipes_paths: list
    #     List of paths to pipe files
    # dem: str
    #     Path to DEM
        
#    """
#    pass()


def merge_pipes_00(in_pipe_paths):
    """ Merge culvert features from multiple files
    
    Parameters
    ----------
    in_pipe_paths: list
        List of pipe files to merge
    """
    
    from whitebox_tools import WhiteboxTools
    
    wbt = WhiteboxTools()
    
    out_group = new_group_00(in_pipe_paths[-1])
    output_path = out_file_00(in_pipe_paths[-1], "PIPES", "shp", out_group)
    
    wbt.merge_vectors(';'.join(in_pipe_paths), output_path)
    
    return(output_path)


def extend_pipes_00(in_pipe_path, dist='10.0'):
    """ Extend individual culvert lines at each end, by the specified distance.
    
    Parameters
    ----------
    in_pipe_path: str
        Path to pipe file
    dist: str
        Distance to extend each line in both directions
    """
    
    from whitebox_tools import WhiteboxTools
    wbt = WhiteboxTools()
    
    output_path = out_file_00(in_pipe_path, "XTPIPE", "shp")
    
    wbt.extend_vector_lines(in_pipe_path, output_path, dist)
    
    return(output_path)
    
    
def buffer_pipes_raster_00(in_pipe_path, in_dem_path, size='1'):
    """ Convert the pipes feature to a raster and then buffer each culvert
    
    Parameters
    ----------
    in_pipe_path: str
        Path to the pipe file to buffer
    size: str
        Size of buffer, in grid cells    
    """
    
    from whitebox_tools import WhiteboxTools
    wbt = WhiteboxTools()
    
    # Create pipe raster file
    pipe_raster = out_file_00(in_pipe_path, "LINES", "tif")
    wbt.vector_lines_to_raster(in_pipe_path, pipe_raster, field="FID", nodata=False, base=in_dem_path) #If this doesn't work, check on the nodata value?
    
    # Create buffered pipe raster file
    output_path = out_file_00(in_pipe_path, "BUF", "tif")    
    wbt.buffer_raster(pipe_raster, output_path, size, gridcells=True)

    return(output_path)

    
def zone_min_00(in_dem_path, in_buffer_path):
    """
    Parameters
    ----------
    in_dem_path: str
        Path to input DEM file
    in_buffer_path: str
        Path to buffered culvert raster file
    """
    
    from whitebox_tools import WhiteboxTools
    wbt = WhiteboxTools()
   
    output_path = out_file_00(in_buffer_path, "MIN", "tif")
    wbt.zonal_statistics(in_dem_path, in_buffer_path, output_path, stat="minimum", out_table=None)
   
    return(output_path)


def burn_min_dem_00(in_dem_path, in_zones_path):
    """
    
    Parameters
    ----------
    in_dem_path: str
        Path to the DEM input file
    in_zones_path: str
        Path to raster file resulting from zonal statistics minimum tool
    """
    
    from whitebox_tools import WhiteboxTools
    wbt = WhiteboxTools() 

    out_group = new_group_00(in_dem_path)
    
    # Create position raster
    pos = out_file_00(in_dem_path, "POS", "tif", out_group)
    wbt.is_no_data(in_zones_path, pos)
    
    output_path = out_file_00(in_dem_path, "DEM", "tif", out_group)
    inputs = "{};{}".format(in_zones_path, in_dem_path)
    # Use nodata results to pick from rasters (0=min zones, 1=DEM)
    wbt.pick_from_list(inputs, pos, output_path)

    return(output_path)
    
    
def breach_depressions_00(in_dem_path, breach_dist):
    """
    
    Parameters
    ----------
    in_dem_path: str
    
    breach_dist: str
        Max distance to breach
    
    """
    
    from whitebox_tools import WhiteboxTools
    wbt = WhiteboxTools() 
    
    out_group = new_group_00(in_dem_path)
    out_path = out_file_00(in_dem_path, "DEM", "tif", out_group)   
    
    
    wbt.breach_depressions_least_cost(in_dem_path, out_path, breach_dist)


# ========================== #
# === Combined functions === #
# ========================== #

def process_pipe_vectors_00(in_pipe_paths, dist='10.0'):
    """Create a vector file of merged pipe files, with pipes extended by dist from each end.
    
    Parameters
    ----------
    in_pipe_paths: list
        List of paths to pipe shapefiles
    dist: str
        Distance in feet to extend the pipe lines from each end.
    """
    #pipes = extract_pipes_00(in_pipe_paths, clip_path)
    pipes = in_pipe_paths
    merge = merge_pipes_00(pipes)
    extend = extend_pipes_00(merge)
    
    return(extend)
    

def burn_culverts_00(in_pipe_path, in_dem_path, buffer_dist):
    """
    
    Parameters
    ----------
    in_pipe_path: str
        Path to pipe file
    in_dem_path: str
        Path to input DEM file
    buffer_dist: str
        Buffer size in grid cells
    """
    
    buf = buffer_pipes_raster_00(in_pipe_path, in_dem_path, buffer_dist)
    min = zone_min_00(in_dem_path, buf)
    burn = burn_min_dem_00(in_dem_path, min)


def process_dems_00(in_pipe_paths, in_dem_path, extend_dist='10', buffer_dist='1', breach_dist='50'):
    """Create 3 new DSM groups from initial DEM and pipe shapefiles
    1. Burn in culverts
    2. Breach Depressions
    3. Culverts + Breach Depressions
    
    Parameters
    ----------
    in_pipe_paths: list
        List of paths to pipe shapefiles
    in_dem_path: str
        Path to initial DEM file
    extend_dist: str
        Distance (in feet) to extend the pipe lines from each end
    buffer_dist: str
        Size of buffer around each pipe, in grid cells. (Depends on DEM resolution)
    breach_dist: str
        Maximum distance to breach depressions
    """
    
    # DEM01: Add culverts
    pipes = process_pipe_vectors_00(in_pipe_paths, extend_dist)
    burn = burn_culverts_00(pipes, in_dem_path, buffer_dist)
    
    # DEM02: Breach depressions
    breach_depressions_00(in_dem_path, breach_dist)
    
    # DEM03: Culverts + breach depressions
    breach_depressions_00(burn, breach_dist)
    
    
    
