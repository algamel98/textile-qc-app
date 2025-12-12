# -*- coding: utf-8 -*-
"""
Visualization module for generating charts and plots
"""
from app.visualization.plots import (
    save_fig, plot_rgb_hist, plot_heatmap, plot_spectral_proxy,
    plot_ab_scatter, plot_lab_bars, plot_fft_power_spectrum,
    plot_gabor_montage, plot_gabor_orientation_histogram,
    plot_glcm_radar, plot_lbp_map_and_hist, plot_wavelet_energy_bars,
    plot_defect_saliency, plot_metamerism_illuminants, plot_spectral_curve,
    plot_line_angle_histogram, plot_pattern_detection_map,
    plot_pattern_count_comparison, plot_pattern_density_heatmap,
    plot_missing_extra_patterns, plot_pattern_size_distribution,
    plot_autocorrelation_surface, plot_keypoint_matching,
    plot_blob_detection, plot_pattern_integrity_radar
)

__all__ = [
    'save_fig', 'plot_rgb_hist', 'plot_heatmap', 'plot_spectral_proxy',
    'plot_ab_scatter', 'plot_lab_bars', 'plot_fft_power_spectrum',
    'plot_gabor_montage', 'plot_gabor_orientation_histogram',
    'plot_glcm_radar', 'plot_lbp_map_and_hist', 'plot_wavelet_energy_bars',
    'plot_defect_saliency', 'plot_metamerism_illuminants', 'plot_spectral_curve',
    'plot_line_angle_histogram', 'plot_pattern_detection_map',
    'plot_pattern_count_comparison', 'plot_pattern_density_heatmap',
    'plot_missing_extra_patterns', 'plot_pattern_size_distribution',
    'plot_autocorrelation_surface', 'plot_keypoint_matching',
    'plot_blob_detection', 'plot_pattern_integrity_radar'
]

