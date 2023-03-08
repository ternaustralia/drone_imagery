# multispec_indices
Script to generate spectral indices in Cloud optimised Geotiff format (COG) from multispectral orthomosaic TIFF

Authors:
        Poornima Sivanandam,
        Emiliano Cimoli (dask/xarray code)

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
