#! python

"""

"""

def merge_pipes_00(in_pipes_paths):
    """
    Merges extended pipe features and saves merged file in new HYDRTE group.
    
    Parameters
    ----------
    :param in_pipes_paths: List of paths to extended pipe files
    """
    
    import arcpy

    import HSSD_02.File_Sys.fso_00 as fso

    # Add a new group for the merged files
    last_pipes = fso.create_file_10(in_pipes_paths[-1])
    prj = last_pipes.create_prj()
    hydro_rt_class = prj.create_class('Hydro_Route')
    hydrte0 = hydro_rt_class.create_next_group(source=last_pipes)
    hydrte0.write_group()
    merge = hydrte0.create_file_00('MERGE', None, 'shp', source_fso=last_pipes)

    # Remove known mismatched fields
    fm = arcpy.FieldMappings()
    for p in in_pipes_paths:
        fm.addTable(p)
    fm.removeFieldMap(fm.findFieldMapIndex("InCrwnToBe"))
    fm.removeFieldMap(fm.findFieldMapIndex("OutCrwnToB"))

    # Merge files
    arcpy.Merge_management(in_pipes_paths, merge.path, fm)

    return merge.path


def buffer_pipes_00(in_pipes_path, buffer="5"):
    """
    Create a buffer around each culvert pipe

    Parameters
    ----------
    :param in_pipes_path: string
        Path to pipe file
    :param buffer: string
        Buffer distance, in feet
    """

    import arcpy

    import HSSD_02.File_Sys.fso_00 as fso

    pipes = fso.create_file_10(in_pipes_path)
    grp = fso.create_group_10(pipes.directory)
    buf = grp.create_file_00('BUF', None, 'shp', source_fso=pipes)
       
    arcpy.Buffer_analysis(in_pipes_path, buf.path, buffer)

    return buf.path


def find_min_elev_00(in_buf_path, in_dem_path):
    """
    Create a raster file with the zones covered by the buffers set to the minimum elevation

    Parameters
    ----------
    :param in_buf_path: string
        Path to the pipe buffer file
    :param in_dem_path: string
        Path to the DEM file
    """

    import arcpy
    from arcpy import sa

    import HSSD_02.File_Sys.fso_00 as fso

    zones = fso.create_file_10(in_buf_path)
    grp = fso.create_group_10(zones.directory)
    min = grp.create_file_00('MIN', None, 'tif', source_fso=zones)

    arcpy.CheckOutExtension("Spatial")

    minRas = sa.ZonalStatistics(in_buf_path, "PipeId", in_dem_path, "Minimum", "DATA")
    minRas.save(min.path)

    return min.path

    
def burn_min_elev_00(min_zones_path, in_dem_path):
    """
    Combine minimum elevations from the buffered pipes with the original DEM, creates a new Surface group.
    
    Parameters
    ----------
    :param min_zones_path: string
        Path to min elevation zones file
    :param in_dem_path: string
        Original DEM file path
    """

    import arcpy
    from arcpy.sa import *

    import HSSD_02.File_Sys.fso_00 as fso

    arcpy.env.extent = "MAXOF"

    # Add a new DSM group
    dem = fso.create_file_10(in_dem_path)
    prj = dem.create_prj()
    surface_class = prj.create_class('Surface')
    dsm0 = surface_class.create_next_group(source=dem)
    dsm0.write_group()
    burn = dsm0.create_file_00('DEM', None, 'tif', source_fso=dem)

    # Raster calculation
    arcpy.CheckOutExtension("Spatial")
    minRas = Raster(min_zones_path)
    demRas = Raster(in_dem_path)
    burnRas = Con(IsNull(minRas), demRas, minRas)
    burnRas.save(burn.path)

    return burn.path


    
def add_culverts(in_pipes_paths, in_dem_path, buffer="5"):
    """
    
    Parameters
    ----------
    :param in_pipes_paths: list
        List of paths to the pipe files
    :param in_dem_path: string
        Path to the DEM
    :param extend: integer
        Distance to extend the pipes from each end (in feet)
    :param buffer: string
        Width of buffer (in feet)
    """

    xt_pipes = in_pipes_paths

    # Merge extended pipes files
    merge = merge_pipes_00(xt_pipes)
    
    # Buffer merged pipes file
    buf = buffer_pipes_00(merge, buffer)

    # Create a file with minimum elevations for zones covered by the buffers
    min = find_min_elev_00(buf, in_dem_path)

    # Create a new dem with minimum elevations burned in
    burn = burn_min_elev_00(min, in_dem_path)




def main():
    pass

if __name__ == "__main__":
    main()
