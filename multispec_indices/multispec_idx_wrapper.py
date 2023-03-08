# -*- coding: utf-8 -*-
"""
Created on Feb 7 2022

@authors: Poornima Sivanandam (wrapper decorator and functions)
          Emiliano Cimoli (Dask to compute indices and index formulae are from HSS)


"""
import numpy as np
import functools


# Functions to calculate spectral indices
def f_ARI1(spectral_array, w1):
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    ARI1 = 1 / w1
    return(ARI1)


def f_ARI2(spectral_array, w1, w2, w3):
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    w2 = spectral_array.sel(wavelength=w2, method='nearest')
    w3 = spectral_array.sel(wavelength=w3, method='nearest')
    ARI2 = w3 * (1 / w1 - 1 / w2)
    return(ARI2)


def f_CCCI(spectral_array, w1, w2, w3):
    """Canopy Chlorophyll concentration index: ((NIR-RE)/(NIR+RE))/NDVI
    """
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    w2 = spectral_array.sel(wavelength=w2, method='nearest')
    w3 = spectral_array.sel(wavelength=w3, method='nearest')
    CCCI = ((w3 - w2)/(w3 + w2))/((w3 - w1)/(w3 + w1))
    return(CCCI)


def f_CI(spectral_array, w1, w2):
    w2 = spectral_array.sel(wavelength=w2, method='nearest')
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    CI = w2/w1 -1
    return(CI)


def f_CRI(spectral_array, w1, w2):
    w2 = spectral_array.sel(wavelength=w2, method='nearest')
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    CRI = 1 / w1 - 1 / w2
    return(CRI)


def f_EVI2(spectral_array, w1, w2):
    w2 = spectral_array.sel(wavelength=w2, method='nearest')
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    EVI2 = 2.5 * (w2 - w1) / (w2 + (2.4 * w1) + 1)
    return(EVI2)


def f_MSAVI2(spectral_array, w1, w2):
    w2 = spectral_array.sel(wavelength=w2, method='nearest')
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    MSAVI2 = 0.5 * (2 * w2 + 1 - np.sqrt((2 * w2 + 1) ** 2 - 8 * (w2 - w1)))
    return(MSAVI2)


def f_MTVI2(spectral_array, w1, w2, w3):
    w3 = spectral_array.sel(wavelength=w3, method='nearest')
    w2 = spectral_array.sel(wavelength=w2, method='nearest')
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    nominator = 1.5 * (1.2 * (w3 - w1) - 2.5 * (w2 - w1))
    denominator = (((2 * w3 + 1) ** 2) - (6 * w3 - 5 * w2 ** 0.5) - 0.5)
    MTVI2 = nominator / denominator
    return(MTVI2)


def f_PSRI(spectral_array, w1, w2, w3):
    w3 = spectral_array.sel(wavelength=w3, method='nearest')
    w2 = spectral_array.sel(wavelength=w2, method='nearest')
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    PSRI = (w2 - w1) / w3
    return(PSRI)


def f_SIPI(spectral_array, w1, w2, w3):
    w3 = spectral_array.sel(wavelength=w3, method='nearest')
    w2 = spectral_array.sel(wavelength=w2, method='nearest')
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    SIPI = (w3 - w1) / (w3 - w2)
    return(SIPI)


def f_SR(spectral_array, w1, w2):
    w2 = spectral_array.sel(wavelength=w2, method='nearest')
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    SR = w2 / w1
    return(SR)


def f_TO(spectral_array, w1, w2, w3, w4):
    w4 = spectral_array.sel(wavelength=w4, method='nearest')
    w3 = spectral_array.sel(wavelength=w3, method='nearest')
    w2 = spectral_array.sel(wavelength=w2, method='nearest')
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    TCARI = 3 * ((w3 - w2) - 0.2 * (w3 - w1) * (w3 / w2))
    OSAVI = (1.16 * (w4 - w2) / (w4 + w2 + 0.16))
    TO = (TCARI / OSAVI)
    return(TO)


def f_VI(spectral_array, w1, w2):
    """

    """
    w1 = spectral_array.sel(wavelength=w1, method='nearest')
    w2 = spectral_array.sel(wavelength=w2, method='nearest')
    VI = (w2 - w1)/(w2 + w1)
    return(VI)


# Dictionary of index and function with index formula
# TODO: if adding more indices, automate this
dict_spec_idx_formula = {
    'ARI1': f_ARI1,
    'ARI2': f_ARI2,
    'CCI': f_VI,
    'CCCI': f_CCCI,
    'CI':  f_CI,
    'CRI1': f_CRI,
    'CRI2': f_CRI,
    'EVI2': f_EVI2,
    'MSAVI2': f_MSAVI2,
    'MTVI2': f_MTVI2,
    'NDI': f_VI,
    'NDVI': f_VI,
    'PSRI': f_PSRI,
    'PSSRb': f_SR,
    'RGRI': f_SR,
    'SIPI': f_SIPI,
    'TO': f_TO
    }


def decorator_calc_spec_idx(func):
    @functools.wraps(func)
    def wrapper_decorator(idx_str, spectral_array, bands=None, client=None, *args, **kwargs):
        # Call calc_spec_idx
        spec_idx = func(idx_str, spectral_array, *args, **kwargs)
        # Run the index computation
        spec_idx_xda = client.compute(spec_idx)
        spec_idx_xda = spec_idx_xda.result()
        spec_idx_xda.rio.write_crs(spectral_array.rio.crs, inplace=True)
        # spec_idx_xda.rio.update_attrs(spec_idx_xda.attrs, inplace=True)
        spec_idx_xda.rio.update_encoding(spectral_array.encoding, inplace=True)
        return spec_idx_xda
    return wrapper_decorator


@decorator_calc_spec_idx
def calc_spec_idx(idx_str, spectral_array, bands=None, client=None, *args, **kwargs):
    # Calculate index using the function in dict_spec_idx_formula
    # Index is computed in wrapper_decorator()
    return(dict_spec_idx_formula[idx_str](spectral_array, *args, **kwargs))
