# -*- coding: utf-8 -*-
"""
LBP (Local Binary Patterns) analysis
"""
import numpy as np
from skimage.feature import local_binary_pattern


def analyze_lbp(gray, P=24, R=3):
    """
    Local Binary Patterns analysis.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        P: Number of circularly symmetric neighbor points
        R: Radius of circle
        
    Returns:
        dict: LBP results
    """
    # Compute LBP
    lbp = local_binary_pattern(gray, P, R, method='uniform')
    
    # Histogram
    n_bins = int(lbp.max() + 1)
    hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins), density=True)
    
    return {
        'lbp_map': lbp,
        'histogram': hist,
        'n_bins': n_bins
    }


def lbp_chi2_distance(hist1, hist2):
    """
    Chi-squared distance between LBP histograms.
    
    Args:
        hist1: First histogram
        hist2: Second histogram
        
    Returns:
        float: Chi-squared distance
    """
    return float(0.5 * np.sum((hist1 - hist2)**2 / (hist1 + hist2 + 1e-10)))


def lbp_bhattacharyya_distance(hist1, hist2):
    """
    Bhattacharyya distance between LBP histograms.
    
    Args:
        hist1: First histogram
        hist2: Second histogram
        
    Returns:
        float: Bhattacharyya distance
    """
    bc = np.sum(np.sqrt(hist1 * hist2))
    return float(-np.log(bc + 1e-10))


def lbp_similarity(hist1, hist2):
    """
    Calculate similarity between LBP histograms.
    
    Args:
        hist1: First histogram
        hist2: Second histogram
        
    Returns:
        float: Similarity score (0-100)
    """
    # Use histogram intersection
    intersection = np.minimum(hist1, hist2).sum()
    return float(intersection * 100)

