#! python3
"""
:Date: 2020-03-19

From initial DEM and pipe files, create 3 new DSM groups:
- DEM with culverts
- DEM with breached depressions
- DEM with culverts and breached depressions
"""


def new_group_00(source_path):
    """ Create the next group in the input file's class
    Parameters
    ----------
    source_path : str
        Path to source file
    """

    import os
    import re

    in_file_name = os.path.basename(source_path)
    source_str = in_file_name.split("_")[1]
    source_str = source_str[:-2]

    in_grp_path = os.path.dirname(source_path)
    in_grp_parent = os.path.dirname(in_grp_path)

    grpRegex = re.compile(r'(\w{2,8})(\d{2})_(\w{2,9})$')
    mo = grpRegex.search(re.escape(in_grp_path))
    grp_name = mo.group(1)
    in_grpno = mo.group(2)

    grps = os.listdir(in_grp_parent)

    grpnos = []
    for g in grps:
        new_mo = grpRegex.search(g)
        grpno = new_mo.group(2)
        grpnos.append(int(grpno))

    out_grpno = ('0' + str(max(grpnos) + 1))[-2:]
    out_grp = "{}{}_{}{}".format(grp_name, out_grpno, source_str, in_grpno)
    out_grp_path = os.path.join(in_grp_parent, out_grp)
    os.mkdir(out_grp_path)

    return out_grp_path


def new_file_00(in_file_path, name, out_ext, out_grp_path=None):
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

    if out_grp_path is not None:
        grpnoRegex = re.compile(r'(\w{2,9})(\d{2})_\w{2,9}$')
        grp_mo = grpnoRegex.search(out_grp_path)
        out_grpno = grp_mo.group(2)
    else:
        out_grp_path = in_grp_path
        out_grpno = in_grpno

    out_file_name = "{}_{}{}_{}{}.{}".format(huc, name, out_grpno, source_name, in_grpno, out_ext)
    out_file_path = os.path.join(out_grp_path, out_file_name)

    return out_file_path


def merge_pipes_00(in_pipe_paths):
    """ Merge culvert features from multiple files
    Parameters
    ----------
    in_pipe_paths : list
        List of pipe files to merge
    """

    from WBT.whitebox_tools import WhiteboxTools

    wbt = WhiteboxTools()

    out_group = new_group_00(in_pipe_paths[-1])
    output_path = new_file_00(in_pipe_paths[-1], "PIPES", "shp", out_group)

    wbt.merge_vectors(';'.join(in_pipe_paths), output_path)

    return output_path


def extend_pipes_00(in_pipe_path, dist='20.0'):
    """ Extend individual culvert lines at each end, by the specified distance.
    Parameters
    ----------
    in_pipe_path : str
        Path to pipe file
    dist : str
        Distance to extend each line in both directions
    """

    from WBT.whitebox_tools import WhiteboxTools
    wbt = WhiteboxTools()

    output_path = new_file_00(in_pipe_path, "XTPIPE", "shp")
    wbt.extend_vector_lines(in_pipe_path, output_path, dist)

    return output_path


def pipes_to_raster_00(in_pipe_path, in_dem_path):
    """ Convert the pipes feature to a raster. Lines will be 1 cell wide.
    Parameters
    ----------
    in_pipe_path : str
        Path to the pipe file to buffer
    in_dem_path : str
        Path to the base DEM
    """

    from WBT.whitebox_tools import WhiteboxTools
    wbt = WhiteboxTools()

    # Create pipe raster file
    output_path = new_file_00(in_pipe_path, "PIPR", "tif")
    wbt.vector_lines_to_raster(in_pipe_path, output_path, field="FID", nodata=True,
                               base=in_dem_path)

    return output_path


def zone_min_00(in_dem_path, in_zones_path):
    """
    Parameters
    ----------
    in_dem_path : str
        Path to input DEM file
    in_zones_path : str
        Path to culvert raster file
    """

    from WBT.whitebox_tools import WhiteboxTools
    wbt = WhiteboxTools()

    output_path = new_file_00(in_zones_path, "MIN", "tif")
    wbt.zonal_statistics(in_dem_path, in_zones_path, output_path, stat="minimum", out_table=None)

    return output_path


def burn_min_00(in_dem_path, in_zones_path):
    """
    Parameters
    ----------
    in_dem_path : str
        Path to the DEM input file
    in_zones_path : str
        Path to raster file resulting from zonal statistics minimum tool
    """

    from WBT.whitebox_tools import WhiteboxTools
    wbt = WhiteboxTools()

    out_group = new_group_00(in_dem_path)

    # Create position raster
    pos_path = new_file_00(in_dem_path, "POS", "tif", out_group)
    wbt.is_no_data(in_zones_path, pos_path)

    new_dem_path = new_file_00(in_dem_path, "DEM", "tif", out_group)

    inputs = "{};{}".format(in_zones_path, in_dem_path)

    # If position (isnodata) file = 0, use value from zones. If = 1, use value from dem.
    wbt.pick_from_list(inputs, pos_path, new_dem_path)

    return new_dem_path


def breach_depressions_00(in_dem_path, breach_dist):
    """
    Parameters
    ----------
    in_dem_path : str
        Path to the DEM
    breach_dist : str
        Max distance to breach
    """

    from WBT.whitebox_tools import WhiteboxTools
    wbt = WhiteboxTools()

    out_group = new_group_00(in_dem_path)
    out_path = new_file_00(in_dem_path, "DEM", "tif", out_group)

    wbt.breach_depressions_least_cost(in_dem_path, out_path, breach_dist)


# === Combined functions === #

def process_pipe_vectors_00(in_pipe_paths, dist='20.0'):
    """Merge pipe vector files and extend lines by dist from each end.
    Parameters
    ----------
    in_pipe_paths : list
        List of paths to pipe shapefiles
    dist : str
        Distance in feet to extend the pipe lines from each end.
    """

    merge = merge_pipes_00(in_pipe_paths)
    extend = extend_pipes_00(merge, str(dist))

    return extend


def burn_culverts_00(in_pipe_path, in_dem_path):
    """
    Parameters
    ----------
    in_pipe_path : str
        Path to pipe shapefile
    in_dem_path : str
        Path to input DEM file
    """

    pipe_ras = pipes_to_raster_00(in_pipe_path, in_dem_path)
    min_zones = zone_min_00(in_dem_path, pipe_ras)
    burn_dem = burn_min_00(in_dem_path, min_zones)

    return burn_dem


def process_dems_00(in_pipe_paths, in_dem_path, extend_dist='20', breach_dist='50'):
    """Create 3 new DSM groups from initial DEM and pipe shapefiles
    For example, from DEM00, the following groups will be created:
    DSM01_DEM00: Burn in culverts
    DSM02_DEM00: Breach depressions
    DSM03_DEM01: Burn in culverts, then breach depressions
    
    Parameters
    ----------
    in_pipe_paths : list
        List of paths to pipe shapefiles
    in_dem_path : str
        Path to initial DEM file
    extend_dist : str
        Distance (in feet) to extend the pipe lines from each end
    breach_dist : str
        Maximum distance to breach depressions
    """

    # Add culverts
    pipes = process_pipe_vectors_00(in_pipe_paths, str(extend_dist))
    dem_01 = burn_culverts_00(pipes, in_dem_path)

    # Breach depressions on original DEM file
    breach_depressions_00(in_dem_path, str(breach_dist))

    # Breach depressions on file with culverts
    breach_depressions_00(dem_01, str(breach_dist))



if __name__ == '__main__':
    in_pipes = [r'C:\Users\betha\Work\Data\WBTEST00\Hydro_Route\HYDRTE00_NCDOT00\CHOWN05_PIPES00_NCDOT00_NNBIS.shp', r'C:\Users\betha\Work\Data\WBTEST00\Hydro_Route\HYDRTE01_NCDOT01\CHOWN05_PIPES01_NCDOT01_MNTNC.shp']
    in_dem = r'C:\Users\betha\Work\Data\WBTEST00\Surface\DSM00_LDR2014\CHOWN05_DEM00_LDR2014_D20.tif'
    process_dems_00(in_pipes, in_dem)
