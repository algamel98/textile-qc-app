# -*- coding: utf-8 -*-
"""
Wavelet analysis functions
"""
import numpy as np
import pywt


def analyze_wavelet(gray, wavelet='db4', levels=3):
    """
    Wavelet multiresolution analysis.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        wavelet: Wavelet type (e.g., 'db4', 'haar', 'sym4')
        levels: Number of decomposition levels
        
    Returns:
        dict: Wavelet analysis results
    """
    # Perform wavelet decomposition
    coeffs = pywt.wavedec2(gray, wavelet, level=levels)
    
    # Calculate energies for each level
    energies = []
    for i, detail in enumerate(coeffs[1:], start=1):
        cH, cV, cD = detail
        
        energy_LL = float(np.sum(coeffs[0]**2)) if i == 1 else 0
        energy_LH = float(np.sum(cH**2))  # Horizontal details
        energy_HL = float(np.sum(cV**2))  # Vertical details
        energy_HH = float(np.sum(cD**2))  # Diagonal details
        
        energies.append({
            'level': i,
            'LL': energy_LL,
            'LH': energy_LH,
            'HL': energy_HL,
            'HH': energy_HH,
            'total': energy_LL + energy_LH + energy_HL + energy_HH
        })
    
    # Calculate total energy distribution
    total_energy = sum(e['total'] for e in energies)
    if total_energy > 0:
        for e in energies:
            e['percentage'] = e['total'] / total_energy * 100
    
    return {
        'coeffs': coeffs,
        'energies': energies,
        'wavelet': wavelet,
        'levels': levels
    }


def compare_wavelet_energies(energies_ref, energies_test):
    """
    Compare wavelet energy distributions.
    
    Args:
        energies_ref: Reference energy dict
        energies_test: Test energy dict
        
    Returns:
        dict: Comparison results
    """
    differences = []
    
    for ref, test in zip(energies_ref, energies_test):
        level_diff = {
            'level': ref['level'],
            'LH_diff': abs(test['LH'] - ref['LH']) / (ref['LH'] + 1e-10) * 100,
            'HL_diff': abs(test['HL'] - ref['HL']) / (ref['HL'] + 1e-10) * 100,
            'HH_diff': abs(test['HH'] - ref['HH']) / (ref['HH'] + 1e-10) * 100,
        }
        differences.append(level_diff)
    
    # Overall similarity
    total_diff = sum(d['LH_diff'] + d['HL_diff'] + d['HH_diff'] for d in differences) / (len(differences) * 3)
    similarity = max(0, 100 - total_diff)
    
    return {
        'differences': differences,
        'similarity': similarity
    }

