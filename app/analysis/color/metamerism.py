# -*- coding: utf-8 -*-
"""
Metamerism analysis functions
"""
import numpy as np
from app.core.constants import WHITE_POINTS
from app.analysis.color.conversions import adapt_white_xyz, xyz_to_lab
from app.analysis.color.delta_e import deltaE2000


def compute_metamerism_index(xyz_ref, xyz_test, illuminants=None):
    """
    Compute metamerism index across multiple illuminants.
    
    Args:
        xyz_ref: Reference XYZ values (under D65)
        xyz_test: Test XYZ values (under D65)
        illuminants: List of illuminant names to test
        
    Returns:
        dict: Metamerism analysis results
    """
    if illuminants is None:
        illuminants = ["D65", "TL84", "A"]
    
    src_wp = WHITE_POINTS["D65"]
    delta_e_values = []
    results = []
    
    for ill_name in illuminants:
        if ill_name not in WHITE_POINTS:
            continue
            
        dst_wp = WHITE_POINTS[ill_name]
        
        # Adapt to target illuminant
        xyz_ref_adapted = adapt_white_xyz(xyz_ref, src_wp, dst_wp)
        xyz_test_adapted = adapt_white_xyz(xyz_test, src_wp, dst_wp)
        
        # Convert to LAB
        lab_ref = xyz_to_lab(xyz_ref_adapted, dst_wp)
        lab_test = xyz_to_lab(xyz_test_adapted, dst_wp)
        
        # Calculate color difference
        de = float(np.mean(deltaE2000(lab_ref, lab_test)))
        delta_e_values.append(de)
        
        results.append({
            'illuminant': ill_name,
            'delta_e': de,
            'lab_ref': lab_ref.mean(axis=tuple(range(lab_ref.ndim - 1))).tolist() if lab_ref.ndim > 1 else lab_ref.tolist(),
            'lab_test': lab_test.mean(axis=tuple(range(lab_test.ndim - 1))).tolist() if lab_test.ndim > 1 else lab_test.tolist()
        })
    
    # Calculate metamerism index (standard deviation of ΔE values)
    metamerism_index = float(np.std(delta_e_values) * 10) if delta_e_values else 0
    
    # Find worst case
    worst_case = max(results, key=lambda x: x['delta_e']) if results else None
    
    return {
        'results': results,
        'metamerism_index': metamerism_index,
        'worst_case': worst_case,
        'mean_delta_e': float(np.mean(delta_e_values)) if delta_e_values else 0
    }


def compute_metamerism_de(xyz_ref, xyz_test, src_wp, dst_wp):
    """
    Compute delta E for a specific illuminant adaptation.
    
    Args:
        xyz_ref: Reference XYZ values
        xyz_test: Test XYZ values
        src_wp: Source white point (typically D65)
        dst_wp: Destination white point
        
    Returns:
        float: Mean delta E 2000 value
    """
    # Adapt to target illuminant
    xyz_ref_adapted = adapt_white_xyz(xyz_ref, src_wp, dst_wp)
    xyz_test_adapted = adapt_white_xyz(xyz_test, src_wp, dst_wp)
    
    # Convert to LAB
    lab_ref = xyz_to_lab(xyz_ref_adapted, dst_wp)
    lab_test = xyz_to_lab(xyz_test_adapted, dst_wp)
    
    # Calculate color difference
    de = deltaE2000(lab_ref, lab_test)
    
    return float(np.mean(de))


def assess_metamerism_risk(metamerism_index):
    """
    Assess metamerism risk level.
    
    Args:
        metamerism_index: Calculated metamerism index
        
    Returns:
        dict: Risk assessment
    """
    if metamerism_index < 1.0:
        level = "LOW"
        description = "Minimal color shift across illuminants"
        color = "#27AE60"
    elif metamerism_index < 3.0:
        level = "MODERATE"
        description = "Noticeable color shift under different lighting"
        color = "#F39C12"
    else:
        level = "HIGH"
        description = "Significant color shift - may cause quality issues"
        color = "#E74C3C"
    
    return {
        'level': level,
        'description': description,
        'color': color,
        'index': metamerism_index
    }

