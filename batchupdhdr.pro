PRO BatchUpdHdr
  COMPILE_OPT IDL2

  ; Start the application
  e = ENVI(/HEADLESS)

  ; Select input files - example below. Replace directory path and recursive pattern

  FileDir = Filepath('', Subdir=['Calperum'], Root_Dir = "R:\SET\Spatial Science\UAV\_data\")
  Rasters = File_Search(FileDir, 'micasense\level_1\*ortho_05.tif')
  PRINT, Rasters

  ; Update Wavelength and Bands Names fields
  For i=0, N_Elements(Rasters)-1 DO BEGIN
    tmp = Rasters[i]
    Raster = e.OpenRaster(tmp)

    metadata = Raster.METADATA
    PRINT, metadata
    num_bands = Raster.NBANDS
    IF (num_bands EQ 10) THEN BEGIN
      metadata.UpdateItem, 'BAND NAMES', ['Blue-444', 'Blue', 'Green-531', 'Green', 'Red-650', 'Red', 'Red edge-705', 'Red edge', 'Red edge-740', 'NIR']
      ; Update Wavelength if already exists, else AddField
      IF (metadata.HasTag ('WAVELENGTH')) THEN BEGIN
        metadata.UpdateItem, 'WAVELENGTH', [444.0 , 475.0 , 531.0 , 560.0 , 650.0 , 668.0 , 705.0 , 717.0 , 740.0 , 842.0]
      ENDIF ELSE BEGIN
        metadata.AddItem, 'WAVELENGTH', [444.0 , 475.0 , 531.0 , 560.0 , 650.0 , 668.0 , 705.0 , 717.0 , 740.0 , 842.0]
      ENDELSE
    ENDIF ELSE BEGIN
      IF (num_bands EQ 5) THEN BEGIN
        metadata.UpdateItem, 'BAND NAMES', ['Blue', 'Green', 'Red', 'Red edge', 'NIR']
        ; Update Wavelength if already exists, else AddField
        IF (metadata.HasTag ('WAVELENGTH')) THEN BEGIN
          metadata.UpdateItem, 'WAVELENGTH', [475.0, 560.0, 668.0, 717.0, 842.0]
        ENDIF ELSE BEGIN
          metadata.AddItem, 'WAVELENGTH', [475.0, 560.0, 668.0, 717.0, 842.0]
        ENDELSE
      ENDIF
    ENDELSE
    ;metadata.UpdateItem, 'BAND NAMES', ['Red', 'Green', 'Blue']
    ;metadata.UpdateItem, 'BAND NAMES', ['Blue', 'Green',  'Red', 'Red edge', 'NIR']
    ;metadata.UpdateItem, 'BAND NAMES', ['Blue-444', 'Blue', 'Green-531', 'Green', 'Red-650', 'Red', 'Red edge-705','Red edge', 'Red edge-740','NIR']
    ;metadata.AddItem, 'WAVELENGTH', [444.0 , 475.0 , 531.0 , 560.0 , 650.0 , 668.0 , 705.0 , 717.0 , 740.0 , 842.0]
    PRINT, metadata
    Raster.WriteMetadata
    Raster.Close
  Endfor

  e.Close
END