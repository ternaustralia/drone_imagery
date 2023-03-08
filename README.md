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

## translate_tiff_cog
This was put together for a very specific use case: to convert orthomosaic TIFF generated in the Calperum campaign (May 2022) ~30 files to COG format for upload to the TERN portal.


**Funding**: This project was funded by TERN Landscapes  
**Authors**: Poornima Sivanandam, Emiliano Cimoli, Arko Lucieer, School of Geography, Planning and Spatial Sciences, University of Tasmania  
**Acknowledgements**: TERN Landscapes, TERN Surveillance, TERN Data Services
