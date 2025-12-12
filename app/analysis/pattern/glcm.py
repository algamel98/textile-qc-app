# -*- coding: utf-8 -*-
"""
GLCM (Gray-Level Co-occurrence Matrix) analysis
"""
import numpy as np
from skimage.feature import graycomatrix, graycoprops
from skimage.util import img_as_ubyte


def analyze_glcm(gray, distances=None, angles=None):
    """
    GLCM texture features (Haralick features).
    
    Args:
        gray: Grayscale image (float32, 0-1)
        distances: List of pixel distances
        angles: List of angles in degrees
        
    Returns:
        dict: GLCM properties
    """
    if distances is None:
        distances = [1, 3, 5]
    if angles is None:
        angles = [0, 45, 90, 135]
    
    # Convert to 8-bit
    gray_8bit = img_as_ubyte(gray)
    
    # Convert angles to radians
    angles_rad = [np.radians(a) for a in angles]
    
    # Compute GLCM
    glcm = graycomatrix(gray_8bit, distances=distances, angles=angles_rad,
                        levels=256, symmetric=True, normed=True)
    
    # Extract properties
    props = {}
    for prop in ['contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation']:
        props[prop] = float(graycoprops(glcm, prop).mean())
    
    # ASM (Angular Second Moment) = energy squared
    props['ASM'] = float(graycoprops(glcm, 'energy').mean())
    
    # Calculate entropy manually
    glcm_mean = glcm.mean(axis=(2, 3))
    entropy = -np.sum(glcm_mean * np.log(glcm_mean + 1e-10))
    props['entropy'] = float(entropy)
    
    return props


def compute_glcm_zscores(glcm_ref, glcm_test):
    """
    Compute z-scores for GLCM feature differences.
    
    Args:
        glcm_ref: Reference GLCM properties
        glcm_test: Test GLCM properties
        
    Returns:
        dict: Z-scores for each feature
    """
    # Typical standard deviations for GLCM features (empirical values)
    typical_stds = {
        'contrast': 50.0,
        'dissimilarity': 5.0,
        'homogeneity': 0.1,
        'energy': 0.05,
        'correlation': 0.1,
        'ASM': 0.05,
        'entropy': 0.5
    }
    
    zscores = {}
    for feat in glcm_ref.keys():
        diff = glcm_test[feat] - glcm_ref[feat]
        std = typical_stds.get(feat, 1.0)
        zscores[feat] = float(diff / std)
    
    return zscores

