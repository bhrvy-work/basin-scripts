#! python3
"""



"""

#TODO: Rewrite these to use pathlib, clean up any unnecessary stuff, make them more versatile.

def new_group_00(in_file_path):
    """ Create the next group in the input file's class
    Parameters
    ----------
    in_file_path : str
        Path to input file
    source_name : str
        (Optional) If different from the input file
    """

    import os
    from pathlib import Path
    import re

    in_file_name = os.path.basename(in_file_path)
    source_str = in_file_name.split("_")[1]
    source_str = source_str[:-2]

    in_grp_path = os.path.dirname(in_file_path)
    in_grp_parent = os.path.dirname(in_grp_path)

    grpRegex = re.compile(r'(\w{2,8})(\d{2})_(\w{2,9})$')
    mo = grpRegex.search(re.escape(in_grp_path))
    grp_name = mo.group(1)
    in_grpno = mo.group(2)

    grps = os.listdir(in_grp_parent)

    # TODO: Replace this with a list comprehension
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





