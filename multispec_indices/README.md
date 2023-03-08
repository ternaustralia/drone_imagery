## multispec_indices
Script to generate spectral indices in Cloud optimised Geotiff format (COG) from multispectral orthomosaic TIFF. This script has been tested with multispectral data from MicaSense RedEdge-MX and RedEdge-MX Dual sensors (please see [Drone Protocols](https://www.tern.org.au/field-survey-apps-and-protocols/) for more information). 

Indices available:
   * Implement any new index through multispec_idx_wrapper
       1. In dict_spec_idx_args: add index and wavelengths
       2. In multispec_idx_wrapper: add index in dict_spec_idx_formula and create function f_<index> to calculate index
   * Relevant indices from Spyndex package. 
    
Script arguments:
   * -i : input multispectral tiff
   *  -o : path to save outputs
   * -idx: list of indices (generates default_idx_list if none specified)
