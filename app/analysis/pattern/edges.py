# -*- coding: utf-8 -*-
"""
Edge detection and structure analysis
"""
import numpy as np
import cv2
from scipy import ndimage
from skimage.feature import hog


def edge_definition(gray):
    """
    Calculate edge definition score using Laplacian variance.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        
    Returns:
        float: Edge definition score (0-100)
    """
    lap = cv2.Laplacian((gray * 255).astype(np.uint8), cv2.CV_64F)
    var = np.var(lap)
    return float(min(100.0, var / 50.0))


def analyze_structure_tensor(gray):
    """
    Structure tensor analysis for coherency and line orientation.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        
    Returns:
        dict: Structure tensor analysis results
    """
    # Gradients
    Iy, Ix = np.gradient(gray)
    
    # Structure tensor components
    Ixx = ndimage.gaussian_filter(Ix * Ix, sigma=1.5)
    Iyy = ndimage.gaussian_filter(Iy * Iy, sigma=1.5)
    Ixy = ndimage.gaussian_filter(Ix * Iy, sigma=1.5)
    
    # Eigenvalues
    trace = Ixx + Iyy
    det = Ixx * Iyy - Ixy**2
    
    lambda1 = trace / 2 + np.sqrt(np.maximum((trace/2)**2 - det, 0))
    lambda2 = trace / 2 - np.sqrt(np.maximum((trace/2)**2 - det, 0))
    
    # Coherency: How oriented the texture is (0 = isotropic, 1 = perfectly oriented)
    coherency = np.where(
        lambda1 + lambda2 > 1e-8,
        (lambda1 - lambda2) / (lambda1 + lambda2),
        0
    )
    
    # Orientation angle
    orientation = 0.5 * np.arctan2(2 * Ixy, Ixx - Iyy)
    orientation_degrees = np.degrees(orientation)
    
    # Dominant orientation (circular mean)
    orientation_flat = orientation_degrees.flatten()
    weights = coherency.flatten()
    
    # Calculate weighted circular mean
    sin_sum = np.sum(weights * np.sin(2 * np.radians(orientation_flat)))
    cos_sum = np.sum(weights * np.cos(2 * np.radians(orientation_flat)))
    dominant_orientation = 0.5 * np.degrees(np.arctan2(sin_sum, cos_sum))
    
    return {
        'coherency_map': coherency,
        'orientation_map': orientation_degrees,
        'mean_coherency': float(np.mean(coherency)),
        'dominant_orientation': float(dominant_orientation),
        'lambda1': lambda1,
        'lambda2': lambda2
    }


def compute_hog_density(gray):
    """
    Compute HOG (Histogram of Oriented Gradients) features.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        
    Returns:
        dict: HOG analysis results
    """
    # Ensure valid dimensions for HOG
    h, w = gray.shape
    cell_size = 8
    block_size = 2
    
    # Resize if needed
    new_h = (h // cell_size) * cell_size
    new_w = (w // cell_size) * cell_size
    
    if new_h != h or new_w != w:
        gray_resized = cv2.resize(gray, (new_w, new_h))
    else:
        gray_resized = gray
    
    # Compute HOG
    hog_features, hog_image = hog(
        gray_resized,
        orientations=9,
        pixels_per_cell=(cell_size, cell_size),
        cells_per_block=(block_size, block_size),
        visualize=True,
        feature_vector=True
    )
    
    # Orientation histogram
    hist_bins = 9
    hist, _ = np.histogram(hog_features, bins=hist_bins, density=True)
    
    # Dominant orientation index
    dominant_idx = np.argmax(hist)
    dominant_angle = dominant_idx * (180 / hist_bins)
    
    return {
        'features': hog_features,
        'hog_image': hog_image,
        'histogram': hist.tolist(),
        'dominant_orientation': float(dominant_angle),
        'mean_magnitude': float(np.mean(hog_features)),
        'std_magnitude': float(np.std(hog_features))
    }


def canny_edge_analysis(gray, low_threshold=50, high_threshold=150):
    """
    Canny edge detection analysis.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        low_threshold: Lower threshold for edge detection
        high_threshold: Upper threshold for edge detection
        
    Returns:
        dict: Edge analysis results
    """
    gray_8bit = (gray * 255).astype(np.uint8)
    edges = cv2.Canny(gray_8bit, low_threshold, high_threshold)
    
    # Calculate edge density
    edge_density = np.sum(edges > 0) / edges.size * 100
    
    return {
        'edge_map': edges,
        'edge_density': float(edge_density),
        'edge_count': int(np.sum(edges > 0))
    }

