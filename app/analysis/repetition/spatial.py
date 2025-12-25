# -*- coding: utf-8 -*-
"""
Spatial distribution analysis
"""
import numpy as np


def analyze_spatial_distribution(gray, patterns, cell_size=50):
    """
    Analyze spatial distribution of detected patterns.
    
    Args:
        gray: Grayscale image
        patterns: List of pattern dictionaries
        cell_size: Grid cell size
        
    Returns:
        dict: Spatial distribution analysis results
    """
    try:
        h, w = gray.shape
        
        # Create grid
        grid_h = h // cell_size
        grid_w = w // cell_size
        
        if grid_h == 0 or grid_w == 0:
            return {
                'density_grid': np.zeros((1, 1)),
                'uniformity_score': 0.0,
                'coverage_ratio': 0.0,
                'clustering_index': 0.0
            }
        
        # Count patterns in each cell
        density_grid = np.zeros((grid_h, grid_w))
        
        for pattern in patterns:
            cx, cy = pattern['centroid']
            cell_x = min(cx // cell_size, grid_w - 1)
            cell_y = min(cy // cell_size, grid_h - 1)
            density_grid[cell_y, cell_x] += 1
        
        # Calculate metrics
        total_patterns = len(patterns)
        occupied_cells = np.sum(density_grid > 0)
        total_cells = grid_h * grid_w
        
        # Coverage ratio
        coverage_ratio = occupied_cells / total_cells * 100
        
        # Uniformity score (based on coefficient of variation)
        if density_grid.mean() > 0:
            cv = density_grid.std() / density_grid.mean()
            uniformity_score = max(0, 100 - cv * 50)
        else:
            uniformity_score = 0
        
        # Clustering index (ratio of patterns in high-density cells)
        if total_patterns > 0:
            mean_density = density_grid[density_grid > 0].mean() if occupied_cells > 0 else 0
            high_density_cells = density_grid > mean_density * 1.5
            clustering_index = np.sum(density_grid[high_density_cells]) / total_patterns * 100
        else:
            clustering_index = 0
        
        return {
            'density_grid': density_grid,
            'uniformity_score': float(uniformity_score),
            'coverage_ratio': float(coverage_ratio),
            'clustering_index': float(clustering_index),
            'grid_shape': (grid_h, grid_w),
            'cell_size': cell_size
        }
        
    except Exception as e:
        print(f"⚠️ Spatial distribution analysis failed: {e}")
        return {
            'density_grid': np.zeros((1, 1)),
            'uniformity_score': 0.0,
            'coverage_ratio': 0.0,
            'clustering_index': 0.0
        }

