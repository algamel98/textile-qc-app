# -*- coding: utf-8 -*-
"""
Pattern integrity assessment
"""
import numpy as np
from scipy.spatial.distance import cdist


def assess_pattern_integrity(patterns_ref, patterns_test, tolerance=0.15):
    """
    Assess pattern integrity by comparing reference and test patterns.
    
    Args:
        patterns_ref: Reference patterns list
        patterns_test: Test patterns list
        tolerance: Tolerance for comparison (fraction)
        
    Returns:
        dict: Pattern integrity assessment
    """
    try:
        if not patterns_ref or not patterns_test:
            return {
                'size_consistency': 0.0,
                'shape_consistency': 0.0,
                'position_consistency': 0.0,
                'overall_integrity': 0.0,
                'status': 'FAIL' if not patterns_ref and not patterns_test else 'CONDITIONAL'
            }
        
        # Size consistency
        areas_ref = np.array([p['area'] for p in patterns_ref])
        areas_test = np.array([p['area'] for p in patterns_test])
        
        mean_area_ref = areas_ref.mean()
        mean_area_test = areas_test.mean()
        
        size_diff = abs(mean_area_ref - mean_area_test) / max(mean_area_ref, 1)
        size_consistency = max(0, 100 - size_diff * 100)
        
        # Shape consistency (using eccentricity and solidity)
        ecc_ref = np.mean([p['eccentricity'] for p in patterns_ref])
        ecc_test = np.mean([p['eccentricity'] for p in patterns_test])
        sol_ref = np.mean([p['solidity'] for p in patterns_ref])
        sol_test = np.mean([p['solidity'] for p in patterns_test])
        
        ecc_diff = abs(ecc_ref - ecc_test)
        sol_diff = abs(sol_ref - sol_test)
        shape_consistency = max(0, 100 - (ecc_diff + sol_diff) * 100)
        
        # Position consistency (using nearest neighbor matching)
        centroids_ref = np.array([p['centroid'] for p in patterns_ref])
        centroids_test = np.array([p['centroid'] for p in patterns_test])
        
        # Calculate distances
        if len(centroids_ref) > 0 and len(centroids_test) > 0:
            distances = cdist(centroids_ref, centroids_test)
            
            # For each ref pattern, find closest test pattern
            min_distances_ref = distances.min(axis=1)
            min_distances_test = distances.min(axis=0)
            
            # Normalize by image diagonal (approximate)
            max_dist = np.sqrt(centroids_ref.max()**2 + centroids_test.max()**2)
            if max_dist > 0:
                position_consistency = max(0, 100 - np.mean(min_distances_ref) / max_dist * 200)
            else:
                position_consistency = 100
        else:
            position_consistency = 0
        
        # Overall integrity
        overall_integrity = (size_consistency + shape_consistency + position_consistency) / 3
        
        # Status
        if overall_integrity >= 80:
            status = 'PASS'
        elif overall_integrity >= 60:
            status = 'CONDITIONAL'
        else:
            status = 'FAIL'
        
        return {
            'size_consistency': float(size_consistency),
            'shape_consistency': float(shape_consistency),
            'position_consistency': float(position_consistency),
            'overall_integrity': float(overall_integrity),
            'status': status,
            'ref_mean_area': float(mean_area_ref),
            'test_mean_area': float(mean_area_test)
        }
        
    except Exception as e:
        print(f"⚠️ Pattern integrity assessment failed: {e}")
        return {
            'size_consistency': 0.0,
            'shape_consistency': 0.0,
            'position_consistency': 0.0,
            'overall_integrity': 0.0,
            'status': 'ERROR'
        }


def detect_missing_extra_patterns(patterns_ref, patterns_test, spatial_dist, tolerance=50):
    """
    Detect missing and extra patterns.
    
    Args:
        patterns_ref: Reference patterns
        patterns_test: Test patterns
        spatial_dist: Spatial distribution data
        tolerance: Distance tolerance for matching
        
    Returns:
        dict: Missing and extra pattern analysis
    """
    try:
        if not patterns_ref or not patterns_test:
            return {
                'missing': patterns_ref if patterns_ref else [],
                'extra': patterns_test if patterns_test else [],
                'missing_count': len(patterns_ref) if patterns_ref else 0,
                'extra_count': len(patterns_test) if patterns_test else 0,
                'matched_count': 0
            }
        
        centroids_ref = np.array([p['centroid'] for p in patterns_ref])
        centroids_test = np.array([p['centroid'] for p in patterns_test])
        
        # Calculate distances
        distances = cdist(centroids_ref, centroids_test)
        
        # Find matches (within tolerance)
        matched_ref = set()
        matched_test = set()
        
        for i in range(len(patterns_ref)):
            min_idx = distances[i].argmin()
            if distances[i, min_idx] < tolerance:
                matched_ref.add(i)
                matched_test.add(min_idx)
        
        # Missing patterns (in ref but not matched)
        missing_indices = set(range(len(patterns_ref))) - matched_ref
        missing = [patterns_ref[i] for i in missing_indices]
        
        # Extra patterns (in test but not matched)
        extra_indices = set(range(len(patterns_test))) - matched_test
        extra = [patterns_test[i] for i in extra_indices]
        
        return {
            'missing': missing,
            'extra': extra,
            'missing_count': len(missing),
            'extra_count': len(extra),
            'matched_count': len(matched_ref)
        }
        
    except Exception as e:
        print(f"⚠️ Missing/extra pattern detection failed: {e}")
        return {
            'missing': [],
            'extra': [],
            'missing_count': 0,
            'extra_count': 0,
            'matched_count': 0
        }

