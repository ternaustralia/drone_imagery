"""
@authors:        Emiliano Cimoli
@description:    Functions to read ENVI header files (source: HSS package).

"""
import logging
import numpy as np

logger = logging.getLogger(__name__)

FIELDS = [
    'samples',
    'lines',
    'bands',
    'wavelength',
    'interleave',
    'data type'
]

def read_header(fpath, process=True) -> dict:
    """
    Author: Emiliano Cimoli
    Description: subfunctions used to read header file information
    """
    with open(fpath, 'r') as fp:
        lines = fp.readlines()

    HDR = {}
    reading = False

    for line in lines:
        # logger.debug(f'Line: {line}')
        if not reading:
            parts = [s.strip() for s in line.split('=')]
            try:
                key, value = parts
                if key not in FIELDS:
                    continue

                if value.startswith('{'):
                    reading = True
                    reading_vals = [value.strip()]
                    reading_key = key
                    logger.info(f"Reading {key}={reading} from {value}")
                else:
                    HDR[key] = value
                    logger.info(f'Read "{key}" = "{value}"')
            except ValueError:
                logger.debug('Invalid header entry')

        else:
            line = line.strip()
            reading_vals.append(line.strip())
            if line.endswith('}'):
                HDR[reading_key] = ' '.join(reading_vals)
                logger.info(f'Done reading "{key}" = "{value}"')
                reading = False
                del reading_key, reading_vals

    if process:
        return _process_envi_fields(HDR)
    else:
        return HDR


def _process_envi_fields(HDR: dict) -> dict:
    """
    Author: Emiliano Cimoli
    Description: subfunctions used to read header file information
    """
    lines, samples, bands = [int(HDR[_]) for _ in (
        'lines',
        'samples',
        'bands')
                             ]
    interleave = HDR['interleave']

    if interleave == 'bil':
        shape = (lines, bands, samples)
        dims = ('y', 'wavelength', 'x')

    elif interleave == 'bip':
        shape = (lines, samples, bands)
        dims = ('y', 'x', 'wavelength')

    elif interleave == 'bsq':
        shape = (bands, lines, samples)
        dims = ('wavelength', 'y', 'x')

    data_type = int(HDR['data type'])
    if data_type == 4:
        dtype = 'float32'
    elif data_type == 8:
        dtype = 'uint8'
    elif data_type > 8:
        dtype = 'uint16'
    elif data_type == 2:
        dtype = 'int16'

    wavelength_arr = HDR['wavelength']
    # remove the { & } at the start and end, and interpret as float
    wavelengths = np.array([
        float(_) for _ in wavelength_arr[1:-1].split(',')])

    HDR['wavelength'] = wavelengths
    HDR['shape'] = shape
    HDR['dtype'] = dtype
    HDR['dims'] = dims

    return HDR