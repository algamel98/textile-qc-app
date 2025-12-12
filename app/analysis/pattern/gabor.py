# -*- coding: utf-8 -*-
"""
Gabor filter bank analysis
"""
import numpy as np
from scipy import ndimage
from skimage.filters import gabor_kernel


def analyze_gabor(gray, frequencies=None, num_orientations=8):
    """
    Multi-scale, multi-orientation Gabor analysis.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        frequencies: List of spatial frequencies
        num_orientations: Number of orientation bands
        
    Returns:
        dict: Gabor analysis results
    """
    if frequencies is None:
        frequencies = [0.1, 0.2, 0.3]
    
    results = []
    energy_maps = []
    
    for freq in frequencies:
        for i in range(num_orientations):
            theta = i * np.pi / num_orientations
            
            # Create Gabor kernel
            kernel = gabor_kernel(freq, theta=theta, sigma_x=3, sigma_y=3)
            
            # Apply filter
            filtered_real = ndimage.convolve(gray, kernel.real, mode='wrap')
            filtered_imag = ndimage.convolve(gray, kernel.imag, mode='wrap')
            
            # Calculate energy
            energy = np.sqrt(filtered_real**2 + filtered_imag**2)
            energy_maps.append(energy)
            
            results.append({
                'frequency': float(freq),
                'orientation_deg': float(np.degrees(theta)),
                'mean': float(np.mean(energy)),
                'variance': float(np.var(energy)),
                'max': float(np.max(energy))
            })
    
    # Dominant orientation
    mean_energies = [r['mean'] for r in results]
    dom_idx = np.argmax(mean_energies)
    dominant_orientation = results[dom_idx]['orientation_deg']
    
    # Coherency (ratio of max to mean energy)
    coherency = np.max(mean_energies) / (np.mean(mean_energies) + 1e-8)
    
    return {
        'results': results,
        'energy_maps': energy_maps,
        'dominant_orientation': float(dominant_orientation),
        'coherency': float(coherency)
    }

