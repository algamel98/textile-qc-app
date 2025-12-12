# -*- coding: utf-8 -*-
"""
Defect detection functions
"""
import numpy as np
import cv2
from skimage.morphology import disk, white_tophat, black_tophat, opening, closing
from skimage.measure import label, regionprops
from skimage.filters import threshold_otsu
from skimage.util import img_as_ubyte


def analyze_defects(gray, min_area=50, morph_kernel_size=5, saliency_strength=1.0):
    """
    Detect defects using morphological operations and saliency.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        min_area: Minimum defect area in pixels
        morph_kernel_size: Size of morphological kernel
        saliency_strength: Strength of saliency detection
        
    Returns:
        dict: Defect detection results
    """
    gray_8bit = img_as_ubyte(gray)
    
    # Create morphological kernel
    kernel = disk(morph_kernel_size)
    
    # White and black top-hat transforms
    w_tophat = white_tophat(gray_8bit, kernel)
    b_tophat = black_tophat(gray_8bit, kernel)
    
    # Combine for saliency
    saliency = (w_tophat.astype(float) + b_tophat.astype(float)) * saliency_strength
    saliency = np.clip(saliency, 0, 255).astype(np.uint8)
    
    # Threshold
    if saliency.max() > saliency.min():
        thresh = threshold_otsu(saliency)
        binary = saliency > thresh
    else:
        binary = np.zeros_like(saliency, dtype=bool)
    
    # Clean up
    binary = opening(binary, disk(2))
    binary = closing(binary, disk(2))
    
    # Label connected components
    labeled = label(binary)
    regions = regionprops(labeled)
    
    # Filter by area and collect defects
    defects = []
    for region in regions:
        if region.area >= min_area:
            y0, x0, y1, x1 = region.bbox
            defects.append({
                'id': region.label,
                'area': int(region.area),
                'centroid': (int(region.centroid[1]), int(region.centroid[0])),
                'bbox': (int(x0), int(y0), int(x1), int(y1)),
                'perimeter': float(region.perimeter),
                'eccentricity': float(region.eccentricity),
                'solidity': float(region.solidity)
            })
    
    # Calculate defect metrics
    total_defect_area = sum(d['area'] for d in defects)
    defect_density = total_defect_area / gray.size * 10000  # per 10000 pixels
    
    return {
        'defects': defects,
        'count': len(defects),
        'total_area': int(total_defect_area),
        'defect_density': float(defect_density),
        'saliency_map': saliency,
        'binary_map': binary.astype(np.uint8) * 255,
        'labeled_map': labeled
    }


def classify_defect(defect):
    """
    Classify defect type based on properties.
    
    Args:
        defect: Defect dictionary
        
    Returns:
        str: Defect classification
    """
    eccentricity = defect.get('eccentricity', 0)
    solidity = defect.get('solidity', 1)
    area = defect.get('area', 0)
    
    if eccentricity > 0.9:
        return "Linear defect (scratch, thread)"
    elif solidity < 0.6:
        return "Irregular defect (hole, tear)"
    elif area > 500:
        return "Large spot/stain"
    else:
        return "Point defect (spot, knot)"


def defect_severity_score(defects, image_area):
    """
    Calculate overall defect severity score.
    
    Args:
        defects: List of defect dictionaries
        image_area: Total image area in pixels
        
    Returns:
        dict: Severity assessment
    """
    if not defects:
        return {
            'score': 100,
            'level': 'NONE',
            'description': 'No defects detected'
        }
    
    # Calculate metrics
    total_area = sum(d['area'] for d in defects)
    area_ratio = total_area / image_area * 100
    count = len(defects)
    
    # Severity score (100 = perfect, 0 = heavily defective)
    score = max(0, 100 - area_ratio * 10 - count * 2)
    
    if score >= 90:
        level = 'MINOR'
        description = 'Minor defects, acceptable quality'
    elif score >= 70:
        level = 'MODERATE'
        description = 'Moderate defects, may require inspection'
    elif score >= 50:
        level = 'SIGNIFICANT'
        description = 'Significant defects, quality concern'
    else:
        level = 'SEVERE'
        description = 'Severe defects, likely reject'
    
    return {
        'score': score,
        'level': level,
        'description': description,
        'area_ratio': area_ratio,
        'count': count
    }

