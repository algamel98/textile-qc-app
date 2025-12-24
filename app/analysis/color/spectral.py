# -*- coding: utf-8 -*-
"""
Spectral data processing functions
"""
import os
import logging
import numpy as np
import pandas as pd
from app.core.constants import CIE_2DEG_WAVELENGTHS, CIE_2DEG_CMF, D65_SPD

logger = logging.getLogger(__name__)


def parse_spectral_csv(csv_path):
    """
    Parse spectral CSV file (wavelength, reflectance).
    
    Args:
        csv_path: Path to CSV file with spectral data
        
    Returns:
        tuple: (wavelengths, reflectance) arrays, or (None, None) on error
    """
    try:
        if not os.path.exists(csv_path):
            logger.error(f"Spectral CSV file not found: {csv_path}")
            return None, None
        
        df = pd.read_csv(csv_path)
        
        if df.empty:
            logger.error(f"Spectral CSV file is empty: {csv_path}")
            return None, None
        
        # Try common column name variations
        wl_cols = [c for c in df.columns if 'wave' in c.lower() or 'nm' in c.lower() or 'λ' in c.lower()]
        ref_cols = [c for c in df.columns if 'ref' in c.lower() or 'r(' in c.lower() or '%' in c.lower()]
        
        if not wl_cols or not ref_cols:
            # Assume first two columns
            if len(df.columns) < 2:
                logger.error(f"Spectral CSV must have at least 2 columns: {csv_path}")
                return None, None
            wavelengths = df.iloc[:, 0].values
            reflectance = df.iloc[:, 1].values
        else:
            wavelengths = df[wl_cols[0]].values
            reflectance = df[ref_cols[0]].values
        
        # Validate data ranges
        if np.any(wavelengths < 300) or np.any(wavelengths > 800):
            logger.warning(f"Wavelengths outside typical range (300-800nm) in {csv_path}")
        
        if np.any(reflectance < 0) or np.any(reflectance > 100):
            logger.warning(f"Reflectance values outside 0-100% range in {csv_path}")
            reflectance = np.clip(reflectance, 0, 100)
        
        # Filter to 380-700nm range
        mask = (wavelengths >= 380) & (wavelengths <= 700)
        filtered_wl = wavelengths[mask]
        filtered_ref = reflectance[mask]
        
        if len(filtered_wl) == 0:
            logger.error(f"No data in valid wavelength range (380-700nm) in {csv_path}")
            return None, None
        
        logger.info(f"Parsed spectral CSV: {len(filtered_wl)} data points")
        return filtered_wl, filtered_ref
        
    except Exception as e:
        logger.error(f"Error parsing spectral CSV {csv_path}: {str(e)}")
        return None, None


def spectral_to_xyz(wavelengths, reflectance, illuminant='D65', observer='2'):
    """
    Compute XYZ tristimulus values from spectral reflectance.
    
    Args:
        wavelengths: Wavelength array (nm)
        reflectance: Reflectance array (0-100%)
        illuminant: Illuminant name
        observer: Observer angle ('2' or '10')
        
    Returns:
        numpy.ndarray: XYZ values
    """
    # Interpolate spectral data to match CIE wavelengths
    cie_wl = CIE_2DEG_WAVELENGTHS
    
    # Interpolate reflectance to CIE wavelengths
    reflectance_interp = np.interp(cie_wl, wavelengths, reflectance)
    
    # Convert reflectance from percentage to fraction
    if reflectance_interp.max() > 1:
        reflectance_interp = reflectance_interp / 100.0
    
    # Get CMF
    x_bar = CIE_2DEG_CMF['x_bar']
    y_bar = CIE_2DEG_CMF['y_bar']
    z_bar = CIE_2DEG_CMF['z_bar']
    
    # Get illuminant SPD
    spd = D65_SPD
    
    # Compute tristimulus values
    delta_lambda = 5  # 5nm step
    
    # Normalization factor
    k = 100.0 / np.sum(y_bar * spd * delta_lambda)
    
    X = k * np.sum(reflectance_interp * x_bar * spd) * delta_lambda
    Y = k * np.sum(reflectance_interp * y_bar * spd) * delta_lambda
    Z = k * np.sum(reflectance_interp * z_bar * spd) * delta_lambda
    
    return np.array([X, Y, Z])


def find_spectral_peaks_valleys(wavelengths, reflectance, n_peaks=3):
    """
    Find peaks and valleys in spectral curve.
    
    Args:
        wavelengths: Wavelength array
        reflectance: Reflectance array
        n_peaks: Number of peaks/valleys to find
        
    Returns:
        list: List of dicts with peak/valley info
    """
    from scipy.signal import find_peaks
    
    features = []
    
    # Find peaks
    peaks, properties = find_peaks(reflectance, prominence=5, distance=10)
    for i, idx in enumerate(peaks[:n_peaks]):
        features.append({
            'type': 'peak',
            'wavelength': float(wavelengths[idx]),
            'reflectance': float(reflectance[idx]),
            'prominence': float(properties['prominences'][i]) if 'prominences' in properties else 0
        })
    
    # Find valleys (peaks in inverted signal)
    valleys, properties = find_peaks(-reflectance, prominence=5, distance=10)
    for i, idx in enumerate(valleys[:n_peaks]):
        features.append({
            'type': 'valley',
            'wavelength': float(wavelengths[idx]),
            'reflectance': float(reflectance[idx]),
            'prominence': float(properties['prominences'][i]) if 'prominences' in properties else 0
        })
    
    # Sort by prominence
    features.sort(key=lambda x: x.get('prominence', 0), reverse=True)
    
    return features[:n_peaks * 2]

