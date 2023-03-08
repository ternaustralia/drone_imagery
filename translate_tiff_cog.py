# -*- coding: utf-8 -*-
"""
@author:  Poornima Sivanandam

@detail: _translate() from https://cogeotiff.github.io/rio-cogeo/API/ used to convert tiff to Cloud Optimised Geotiff (COG)

The main code was written with a very specific use case to convert all ortho TIFF generated in the Calperum campaign ~30 files
to COG for upload to the TERN portal.
Note: PREDICTOR and ZLEVEL values not tested exhaustively.
But PREDICTOR is set differently for float. The string "micasense" in the dir structure is used to identify multispectral tiff.
https://kokoalberti.com/articles/geotiff-compression-optimization-guide/

"""

import os
from pathlib import Path

from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles

def _translate(src_path, dst_path, profile="deflate", profile_options={}, **options):
    """
    From https://cogeotiff.github.io/rio-cogeo/API/
    Convert image to COG.
    
    # Tested this first: _translate(file, cog_file, profile_options={("PREDICTOR", 3)})

    """

    # Format creation option (see gdalwarp `-co` option)
    output_profile = cog_profiles.get(profile)
    output_profile.update(dict(BIGTIFF="IF_SAFER"))
    output_profile.update(profile_options)

    # TODO: update this as required
    config = dict(
        GDAL_NUM_THREADS="ALL_CPUS",
        GDAL_TIFF_INTERNAL_MASK=True,
        GDAL_TIFF_OVR_BLOCKSIZE="128",
    )

    cog_translate(
        src_path,
        dst_path,
        output_profile,
        config=config,
        in_memory=False,
        quiet=True,
        **options,
    )
    return True


###############
## Main code
###############
# Aim here was very specific: to convert all ortho TIFF in this folder to COG for upload to TERN
# TODO enter dir path
dir_name = r""
level_1_list = []

# DO not convert all .tiff to COG. Skip files from 2021 or those with cog or dem in file name
level_1_list = [dirs for dirs, subdirs, files in os.walk(dir_name) if ("level_1" in dirs) and ("2021" not in dirs)]

# micasense: predictor 3 float
# p1: predictor 2 int
PRED = 2

tif_ext = [".tiff", ".tif"]
skip_list = ["cog", "dem", "tmp", "l1"]

tif_file_list = []
for subdir in level_1_list:
    for file in os.listdir(subdir):
        if file.endswith(tuple(tif_ext)):
            if any(chk in file for chk in skip_list):
                continue
            else:
                 tif_file_list.append(Path(subdir)/file)


# use list to run translate.
# parse src_path to get dst_path. same as src path without filename. append cog to filename+".tif"
for file in tif_file_list:
    print(Path(file).stem)
    cog_file = Path(file).parent / (Path(file).stem + "_cog.tif")
    if "micasense" in str(file):
        # floating point predictor
        print("micasense")
        PRED = 3
    else:
        PRED = 2
    _translate(file, cog_file, profile_options={("PREDICTOR", PRED), ("ZLEVEL", 9)})

