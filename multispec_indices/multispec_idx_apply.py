"""
Created Feb 2022

@authors:
        Poornima Sivanandam, Emiliano Cimoli (dask/xarray code)

Script to generate spectral indices in Cloud optimised Geotiff format (COG) from multispectral orthomosaic TIFF.
Indices available:
    * Indices relevant from Spyndex package (see spyndex_idx_* below)
    * Implement any new index through multispec_idx_wrapper
        1. In dict_spec_idx_args: add index and wavelengths
        2. In multispec_idx_wrapper: add index in dict_spec_idx_formula and create function f_<index> to calculate index

Script arguments:
    -i : input multispectral tiff
    -o : path to save outputs

optional (generates default_idx_list  if none specified):
    -idx: list of indices.

Example: multispec_idx_apply.py -i F:\test_MS_spectral_indices\20211012_RedEdgeMX_ortho_05_80m.tif \
                                -o F:\test_MS_spectral_indices\202203_out \
                                -idx NDYI NDVI CIG CIRE ARI1
"""
import argparse
import spyndex
import time
import xarray as xr
import rioxarray as rioxr
from dask.distributed import Client
from dask.distributed import performance_report
from pathlib import Path
from multispec_idx_wrapper import *
import webbrowser
from util import *

# dask dashboard on browser
WAIT_DASHBOARD = True

# multi_bands = [475, 560, 668, 717, 842]  # MicaSense RedEdge-MX bands
# dual_bands = [444, 475, 531, 560, 650, 668, 705, 717, 740, 842]  # MicaSense RedEdge-MX Dual bands

# Indices implemented in spyndex separated by RedEdge/Dual bands
# Complete list at https://github.com/davemlz/awesome-spectral-indices
# TODO: keep this updated
spyndex_idx_rededge = ['ARI', 'BAI', 'BCC', 'BNDVI', 'CIG', 'CIRE', 'CVI', 'DVI',
                       'ExG', 'FCVI', 'GARI', 'GBNDVI', 'GCC', 'GLI', 'GNDVI', 'GRNDVI',
                       'MCARI1', 'MGRVI', 'MTVI1', 'MTVI2', 'MSAVI', 'MSR',
                       'NDDI', 'NDVI', 'NDYI', 'NDWI', 'NGRDI', 'NIRv', 'NLI',
                       'OSAVI', 'RCC', 'RDVI', 'RVI', 'SR555', 'TGI', 'TRRVI', 'TVI', 'VIG']
spyndex_idx_dual = ['IRECI', 'MCARI', 'MCARI705', 'MCARIOSAVI', 'MCARIOSAVI705', 'MSR705', 'MTCI',
                    'NDREI', 'NDVI705', 'SR705', 'TCARI', 'TCARIOSAVI', 'TCARIOSAVI705', 'TCI']

# Indices that are not in Spyndex are calculated in multispec_idx_wrapper.py
# Wavelengths for these indices
dict_spec_idx_args = {
    'ARI1': {'w1': 550},
    'ARI2': {'w1': 550, 'w2': 700, 'w3': 800},
    'CCI': {'w1': 531, 'w2': 645},
    'CCCI': {'w1': 668, 'w2': 717, 'w3': 842},
    'CRI1': {'w1': 510, 'w2': 550},
    'CRI2': {'w1': 510, 'w2': 670},
    # 'NDI': {'w1': 587, 'w2': 621}, # NGRDI
    # 'MSAVI2': {'w1': 670, 'w2': 800}, # MSAVI
    'PSRI': {'w1': 500, 'w2': 678, 'w3': 750},
    'PSSRb': {'w1': 652, 'w2': 800},
    # 'RGRI': {'w1': 699, 'w2': 599}, # inverse of SR555
    'SIPI': {'w1': 445, 'w2': 680, 'w3': 800},
    # 'TO': {'w1': 550, 'w2': 670, 'w3': 700, 'w4': 800} # TCARIOSAVI
}
wrapper_idx_list = list(dict_spec_idx_args.keys())

# TODO: update this as required. Used if no values passed for '-idx' argument
default_idx_list = ['CIG', 'CIRE', 'MSAVI', 'NDVI']


# Function definitions
def load_tif_rioxr(hdr_file, data_file, band=None, x=None, y=None) -> xr.DataArray:
    """
    Author: Emiliano Cimoli
    Description: Load tif using rasterio xarray. Add relevant metadata to the xarray.
    """
    header = read_header(hdr_file, process=True)
    cube = rioxr.open_rasterio(data_file, chunks={'band': band, 'x': x, 'y': y}, masked=True)

    cube.coords['wavelength'] = ('band', header['wavelength'])
    cube = cube.swap_dims({'band': 'wavelength'})
    cube.attrs['long_name'] = 'reflectance'
    return cube


#####################################
# Main code
#####################################
# Parse arguments
parser = argparse.ArgumentParser(description='Calculate vegetation indices from input multispectral orthomosaic')
parser.add_argument('-i', help='input orthomosaic tiff file', required=True)
parser.add_argument('-o', help='path to save output files', required=True)
parser.add_argument('-idx', nargs="+", default=None)
args = parser.parse_args()

img_file = args.i
out_dir = Path(args.o)

daskreport_name = out_dir / 'multispec_dask_report.html'
# Note that the header file must have 'wavelength' field updated
hdr_file = Path(img_file).parent / str(Path(img_file).stem + ".hdr")

# initialise lists for spectral indices
spyn_idx_list = []
other_idx_list = []

# dask web interface: http://distributed.dask.org/en/latest/web.html
client = Client(processes=False)
if WAIT_DASHBOARD:
    print(client)
    print("Dask dashboard should automatically open. If not, open browser and enter the following URL: "
          + str(client.dashboard_link))
    webbrowser.open(client.dashboard_link, new=2)

# TODO wrap main() in timing decorator instead?
t0 = time.perf_counter()

# Load orthomosaic
if str(img_file).endswith(('.tif', '.TIFF')):
    # import image and geodata from GeoTif format into a chunked datarray
    # TODO chunk size hardcoded. tested 1000
    img_array = load_tif_rioxr(hdr_file, img_file, band=1, x=2560, y=2560)
    img_bands = img_array.coords['wavelength'].values
else:
    raise ValueError("Expecting tiff file input, found:" + str(img_file))

# Get list of indices to be calculated
if args.idx is not None:
    # input through '-idx'
    idx_list = args.idx
else:
    # if no indices specified, use default list
    idx_list = default_idx_list
    print("'-idx' argument not specified. Calculating default list of indices.")

# create separate lists for spyndex and other indices
spyndex_list = spyndex_idx_rededge
# HARDCODED: include dual_band indices if 10-band input
if img_array.shape[0] == 10:
    spyndex_list += spyndex_idx_dual
spyn_idx_list = list(filter(lambda x: x in spyndex_list, idx_list))

# remaining indices from the original list
other_idx_list = list(filter(lambda x: x not in spyn_idx_list, idx_list))
# check if the remaining indices are implemented in the wrapper
idx_not_found = [x for x in other_idx_list if x not in wrapper_idx_list]
if idx_not_found:
    raise ValueError("Following indices not found " + str(idx_not_found))

print("Calculating indices:" + str(idx_list))

# Calculate indices: spyndex using computeIndex(), and others using calc_spec_idx()
# Save tiffs in output directory
with performance_report(filename=daskreport_name):
    # 1. Compute spyndex indices
    if spyn_idx_list:
        indices = spyndex.computeIndex(
            index=spyn_idx_list,
            online=True,
            params={
                "N": img_array.sel(wavelength=842, method='nearest'),
                "RE3": img_array.sel(wavelength=740, method='nearest'),
                "RE2": img_array.sel(wavelength=717, method='nearest'),
                "RE1": img_array.sel(wavelength=705, method='nearest'),
                "R": img_array.sel(wavelength=668, method='nearest'),
                "G": img_array.sel(wavelength=560, method='nearest'),
                "B": img_array.sel(wavelength=475, method='nearest'),
                "A": img_array.sel(wavelength=444, method='nearest')
            }
        ).compute()

        # Write crs
        indices.rio.write_crs(img_array.rio.crs, inplace=True)
        # Spyndex: index coordinate added only when more than 1 index calculated
        # Manually add "index" dim/coord when 1 index was computed
        if len(spyn_idx_list) == 1:  # or if "index" not in indices.coords:
            indices = indices.expand_dims(dim={"index": 1})
            indices = indices.assign_coords(index=("index", spyn_idx_list))

        for idx in spyn_idx_list:
            idx_data = indices.sel(index=idx)
            file_out = Path.joinpath(out_dir, idx + ".TIFF")
            idx_data.rio.to_raster(file_out, driver="COG", COMPRESS="DEFLATE", LEVEL=9, PREDICTOR=3)

    # 2. Calculate indices that are not in spyndex through spectral_indices_wrapper
    for idx in other_idx_list:
        idx_proc = calc_spec_idx(idx, img_array, bands=img_bands, client=client,
                                 **dict_spec_idx_args[idx])
        file_out = Path.joinpath(out_dir, idx + ".TIFF")
        idx_proc.rio.to_raster(file_out, driver="COG", COMPRESS="DEFLATE", LEVEL=9, PREDICTOR=3)

t2 = time.perf_counter()
tdiff = t2 - t0
print("Code took %.3f seconds to run. Indices written to %s." % (tdiff, str(out_dir)))
