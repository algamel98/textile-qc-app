# -*- coding: utf-8 -*-
"""
Connected components analysis
"""
import numpy as np
from skimage.measure import label, regionprops
from skimage.filters import threshold_otsu
from skimage.util import img_as_ubyte


def analyze_connected_components(gray, min_area=100, max_area=5000):
    """
    Analyze connected components for pattern counting.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        min_area: Minimum pattern area
        max_area: Maximum pattern area
        
    Returns:
        dict: Connected components analysis results
    """
    try:
        # Convert to 8-bit and threshold
        gray_8bit = img_as_ubyte(gray)
        
        # Use Otsu thresholding
        thresh_val = threshold_otsu(gray_8bit)
        binary = gray_8bit > thresh_val
        
        # Label connected components
        labeled = label(binary)
        regions = regionprops(labeled)
        
        # Filter by area
        patterns = []
        for region in regions:
            if min_area <= region.area <= max_area:
                y0, x0, y1, x1 = region.bbox
                patterns.append({
                    'label': int(region.label),
                    'area': int(region.area),
                    'bbox': (int(x0), int(y0), int(x1), int(y1)),
                    'centroid': (int(region.centroid[1]), int(region.centroid[0])),
                    'perimeter': float(region.perimeter),
                    'eccentricity': float(region.eccentricity),
                    'solidity': float(region.solidity)
                })
        
        # Calculate statistics
        if patterns:
            areas = [p['area'] for p in patterns]
            mean_area = float(np.mean(areas))
            std_area = float(np.std(areas))
            cv_area = float((std_area / mean_area * 100) if mean_area > 0 else 0)
        else:
            mean_area = std_area = cv_area = 0.0
        
        return {
            'patterns': patterns,
            'count': len(patterns),
            'labeled_image': labeled,
            'binary_image': binary.astype(np.uint8) * 255,
            'mean_area': mean_area,
            'std_area': std_area,
            'cv_area': cv_area
        }
        
    except Exception as e:
        print(f"⚠️ Connected components analysis failed: {e}")
        return {
            'patterns': [],
            'count': 0,
            'labeled_image': None,
            'binary_image': None,
            'mean_area': 0.0,
            'std_area': 0.0,
            'cv_area': 0.0
        }

