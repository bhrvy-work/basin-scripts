#! python3

"""

"""

def grass_setup_00(gisdb = r'C:\Users\betha\Work\grassdata', location='script_testing_chown05', mapset='mapset_01'):

    import os
    import sys
    import subprocess

    # Location of GRASS binary
    grass7bin = r'C:\OSGeo4W64\bin\grass78.bat'

    ############## Copied section
    # query GRASS GIS itself for its GISBASE
    startcmd = [grass7bin, '--config', 'path']
    try:
        p = subprocess.Popen(startcmd, shell=False,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
    except OSError as error:
        sys.exit("ERROR: Cannot find GRASS GIS start script"
                 " {cmd}: {error}".format(cmd=startcmd[0], error=error))
    if p.returncode != 0:
        sys.exit("ERROR: Issues running GRASS GIS start script"
                 " {cmd}: {error}"
                 .format(cmd=' '.join(startcmd), error=err))
    gisbase = out.strip(os.linesep)

    # set GISBASE environment variable
    os.environ['GISBASE'] = gisbase

    # define GRASS-Python environment
    grass_pydir = os.path.join(gisbase, "etc", "python")
    sys.path.append(grass_pydir)

    # Import GRASS Python bindings
    import grass.script as script

    # Launch session
    rcfile = script.setup.init(gisbase, gisdb, location, mapset)

    # Example calls
    script.message('Current GRASS GIS 7 environment:')
    print(script.gisenv())

    script.message('Available raster maps:')
    for rast in script.list_strings(type='raster'):
        print(rast)

    script.message('Available vector maps:')
    for vect in script.list_strings(type='vector'):
        print(vect)

############

# mapcalc parameters:
# exp (str): expression
# quiet (bool): true to run quietly
# verbose (bool): true to run verbosely
# overwrite (bool): true to enable overwriting the output
# seed (int): integer to seed the random-number generator for the rand() function
# env (dict): dictionary of environment variables for child process
# kwargs (dict): more arguments


def import_dem_00(in_dem_path):
    """

    Parameters
    ----------
    in_dem_path : str
        Path to the DEM

    Returns
    -------
    in_raster : str
        Name of the imported raster
    """
    #TODO: Import dem to GRASS raster, keep basename and group number in name



    return in_raster



def watershed_00(in_raster):
    """Runs r.watershed

    Parameters
    ----------
    in_raster : str
        Name of imported dem file

    Returns
    -------
    out_rasters : dict
        Output rasters {type: name}
    """
    #TODO: Run r.watershed

    pass
    # Get base name and group number from input raster name
    basename =
    num =

    accumulation = "{b}_acc_{n}".format(b=basename, n=num)
    tci = "{b}_tci_{n}".format(b=basename, n=num)
    spi = "{b}_spi_{n}".format(b=basename, n=num)
    drainage = "{b}_flowdir_{n}".format(b=basename, n=num)
    basin = "{b}_basin_{n}".format(b=basename, n=num)
    stream = "{b}_stream_{n}".format(b=basename, n=num)
    length_slope = "{b}_slplen_{n}".format(b=basename, n=num)
    slope_steepness = "{b}_slpstp_{n}".format(b=basename, n=num)

    #Assign output files to a dictionary out_rasters
    #out_rasters['accumulation'] = accumulation



    #return out_rasters

def flowdir_to_p(flowdir):
    """Converts a flow direction file produced by r.watershed for use by TauDem.

    Parameters
    ----------
    flowdir : str
        Name of GRASS flow direction raster
    """

    dir_conv = "if({i} == 8, 1, {i}+1))".format(i=in_raster)
    expr = "if({i} < 1, nodata, {d}".format(i=in_raster, d=dir_conv)
    script.raster.mapcalc(expr)

def stream_to_src(stream):
    """

    Parameters
    ----------
    stream :

    Returns
    -------

    """
    #TODO: Write mapcalc function to convert a stream file to match the taudem src file.

    export_raster_00(stream_src, 'SRC', grp)

def export_raster_00(in_raster, name, out_dir):
    """

    Parameters
    ----------
    in_raster : str
        Name of GRASS raster to export
    name : str
        Model file abbreviation
    out_dir : str
        Path to output group directory
    """
    #TODO: Write function to export the raster to a geotiff file.

    pass

def watershed_batch_00(in_dem_path, gisdb, location, mapset):
    """

    Parameters
    ----------
    in_dem_path : str
        path to the DEM to import
    gisdb : str
        path to the root directory to store the GRASS files
    location : str
        name of the subfolder to store this GRASS project
    mapset : str
        name of the mapset
    """
    grass_setup_00(gisdb, location, mapset)
    elev_raster = import_dem_00(in_dem_path)

    str_rasters = watershed_00(elev_raster)
    stream = str_rasters['stream']
    flowdir = str_rasters['flowdir']

    stream_to_src(stream)
    flowdir_to_p(flowdir)


    ########### Copied
    # Clean up at the end
    gsetup.cleanup()
    ###########



if __name__ == '__main__':

    ### Testing inputs ###
    in_dem_path = r'C:\Users\betha\Work\Data\CHOWN05\Surface\DSM00_LDR2014\CHOWN05_DEM00_LDR2014_D20.tif'
    gisdb = os.path.join(os.path.expanduser("~"), "Work", "grass_test")
    location = "chown05"
    mapset = "mapset_01"

    grass7bin = r'C:\OSGeo4W64\bin\grass78.bat'

    ######


    watershed_batch_00(in_dem_path, gisdb, location, mapset)


