# -*- coding: utf-8 -*-
"""
Main analysis pipeline runner
"""
import os
import logging
import numpy as np
import cv2
from skimage.color import rgb2gray
from skimage.metrics import structural_similarity as ssim

from app.core.settings import QCSettings
from app.core.constants import WHITE_POINTS
from app.core.image_utils import apply_crop, grid_points, overlay_regions, ensure_dir

from app.analysis.color.conversions import srgb_to_xyz, xyz_to_lab, rgb_to_cmyk, adapt_white_xyz
from app.analysis.color.delta_e import deltaE76, deltaE94, deltaE2000, deltaE_CMC
from app.analysis.color.whiteness import cie_whiteness_tint, astm_e313_yellowness
from app.analysis.color.metamerism import compute_metamerism_index

from app.analysis.pattern.ssim import ssim_percent, symmetry_score, repeat_period_estimate, determine_status
from app.analysis.pattern.fft import analyze_fft
from app.analysis.pattern.gabor import analyze_gabor
from app.analysis.pattern.glcm import analyze_glcm, compute_glcm_zscores
from app.analysis.pattern.lbp import analyze_lbp, lbp_chi2_distance, lbp_bhattacharyya_distance
from app.analysis.pattern.wavelet import analyze_wavelet
from app.analysis.pattern.edges import edge_definition, analyze_structure_tensor, compute_hog_density
from app.analysis.pattern.defects import analyze_defects

from app.analysis.repetition.blob_detection import analyze_blob_patterns
from app.analysis.repetition.connected import analyze_connected_components
from app.analysis.repetition.keypoints import analyze_keypoint_matching
from app.analysis.repetition.autocorrelation import analyze_autocorrelation
from app.analysis.repetition.spatial import analyze_spatial_distribution
from app.analysis.repetition.integrity import assess_pattern_integrity, detect_missing_extra_patterns

from app.visualization.plots import (
    plot_rgb_hist, plot_heatmap, plot_spectral_proxy, plot_ab_scatter, plot_lab_bars,
    plot_fft_power_spectrum, plot_gabor_montage, plot_glcm_radar, plot_lbp_map_and_hist,
    plot_wavelet_energy_bars, plot_defect_saliency, plot_metamerism_illuminants,
    plot_pattern_detection_map, plot_pattern_count_comparison, plot_pattern_density_heatmap,
    plot_autocorrelation_surface, plot_keypoint_matching, plot_pattern_integrity_radar
)

from app.report.pdf_builder import build_main_report

logger = logging.getLogger(__name__)


def run_analysis_pipeline(ref_path, test_path, ref, test, settings, output_dir):
    """
    Main analysis pipeline.
    
    Args:
        ref_path: Path to reference image
        test_path: Path to test image
        ref: Reference image array (float32, 0-1)
        test: Test image array (float32, 0-1)
        settings: QCSettings object
        output_dir: Output directory for charts and reports
        
    Returns:
        dict: Analysis results including PDF path
    """
    logger.info(f"Starting analysis pipeline: {os.path.basename(ref_path)} vs {os.path.basename(test_path)}")
    
    results = {
        'ref_path': ref_path,
        'test_path': test_path,
        'charts': {}
    }
    
    # Apply crop if enabled
    if settings.use_crop:
        logger.info(f"Applying {settings.crop_shape} crop")
        ref = apply_crop(ref, settings, is_test_image=False)
        test = apply_crop(test, settings, is_test_image=True)
    
    # Resize for processing
    H, W = ref.shape[:2]
    small_w = 640
    scale = small_w / W
    small_h = max(1, int(H * scale))
    ref_small = cv2.resize(ref, (small_w, small_h), interpolation=cv2.INTER_AREA)
    test_small = cv2.resize(test, (small_w, small_h), interpolation=cv2.INTER_AREA)
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    charts_dir = ensure_dir(os.path.join(output_dir, 'charts'))
    
    # ==================== COLOR ANALYSIS ====================
    if settings.enable_color_unit:
        logger.info("Running color analysis...")
        
        src_wp = WHITE_POINTS["D65"]
        xyz_ref = srgb_to_xyz(ref_small)
        xyz_test = srgb_to_xyz(test_small)
        
        # Convert to LAB
        lab_ref = xyz_to_lab(xyz_ref, src_wp)
        lab_test = xyz_to_lab(xyz_test, src_wp)
        
        # Calculate delta E maps
        de76_map = deltaE76(lab_ref, lab_test)
        de94_map = deltaE94(lab_ref, lab_test)
        de00_map = deltaE2000(lab_ref, lab_test)
        
        # Statistics
        color_metrics = {
            'mean_de76': float(np.mean(de76_map)),
            'std_de76': float(np.std(de76_map)),
            'min_de76': float(np.min(de76_map)),
            'max_de76': float(np.max(de76_map)),
            'mean_de94': float(np.mean(de94_map)),
            'std_de94': float(np.std(de94_map)),
            'min_de94': float(np.min(de94_map)),
            'max_de94': float(np.max(de94_map)),
            'mean_de2000': float(np.mean(de00_map)),
            'std_de2000': float(np.std(de00_map)),
            'min_de2000': float(np.min(de00_map)),
            'max_de2000': float(np.max(de00_map)),
        }
        
        # CMC if enabled
        if settings.use_delta_e_cmc:
            l_val, c_val = (2, 1) if settings.cmc_l_c_ratio == "2:1" else (1, 1)
            de_cmc_map = deltaE_CMC(lab_ref, lab_test, l=l_val, c=c_val)
            color_metrics['mean_de_cmc'] = float(np.mean(de_cmc_map))
        
        # Uniformity
        color_metrics['uniformity'] = max(0.0, 100.0 - color_metrics['std_de76'] * settings.uniformity_std_multiplier)
        
        # Status
        color_metrics['status'] = determine_status(
            color_metrics['mean_de2000'],
            settings.delta_e_threshold,
            settings.delta_e_conditional,
            lower_is_better=True
        )
        
        results['color_metrics'] = color_metrics
        
        # Metamerism
        metamerism = compute_metamerism_index(
            xyz_ref.mean(axis=(0, 1)),
            xyz_test.mean(axis=(0, 1)),
            settings.metamerism_illuminants
        )
        results['metamerism'] = metamerism
        
        # Generate color charts
        if settings.enable_color_visual_diff:
            heatmap_path = os.path.join(charts_dir, 'de_heatmap.png')
            plot_heatmap(de00_map, 'ΔE2000 Heatmap', heatmap_path)
            results['charts']['de_heatmap'] = heatmap_path
        
        if settings.enable_color_lab_viz:
            scatter_path = os.path.join(charts_dir, 'ab_scatter.png')
            plot_ab_scatter(lab_ref, lab_test, scatter_path)
            results['charts']['ab_scatter'] = scatter_path
            
            bars_path = os.path.join(charts_dir, 'lab_bars.png')
            lab_ref_mean = lab_ref.reshape(-1, 3).mean(axis=0)
            lab_test_mean = lab_test.reshape(-1, 3).mean(axis=0)
            plot_lab_bars(lab_ref_mean, lab_test_mean, bars_path)
            results['charts']['lab_bars'] = bars_path
        
        # RGB histograms
        hist_ref_path = os.path.join(charts_dir, 'hist_ref.png')
        hist_test_path = os.path.join(charts_dir, 'hist_test.png')
        plot_rgb_hist(ref_small, 'Reference RGB Histogram', hist_ref_path)
        plot_rgb_hist(test_small, 'Sample RGB Histogram', hist_test_path)
        results['charts']['hist_ref'] = hist_ref_path
        results['charts']['hist_test'] = hist_test_path
    
    # ==================== PATTERN ANALYSIS ====================
    if settings.enable_pattern_unit:
        logger.info("Running pattern analysis...")
        
        gray_ref = rgb2gray(ref_small)
        gray_test = rgb2gray(test_small)
        
        # Basic pattern metrics
        ssim_val = float(ssim(gray_ref, gray_test, data_range=1.0))
        sym_ref = symmetry_score(gray_ref)
        sym_test = symmetry_score(gray_test)
        px, py = repeat_period_estimate(gray_test)
        edge_def = edge_definition(gray_test)
        
        pattern_metrics = {
            'ssim': ssim_val,
            'symmetry': (sym_ref + sym_test) / 2,
            'repeat_period_x': px,
            'repeat_period_y': py,
            'edge_definition': edge_def,
        }
        
        # Advanced texture analysis
        if settings.enable_pattern_advanced:
            # FFT
            fft_ref = analyze_fft(gray_ref, settings.fft_num_peaks, settings.fft_enable_notch)
            fft_test = analyze_fft(gray_test, settings.fft_num_peaks, settings.fft_enable_notch)
            pattern_metrics['fft_period'] = fft_test['fundamental_period']
            pattern_metrics['fft_anisotropy'] = fft_test['anisotropy']
            
            # Gabor
            gabor_ref = analyze_gabor(gray_ref, settings.gabor_frequencies, settings.gabor_num_orientations)
            gabor_test = analyze_gabor(gray_test, settings.gabor_frequencies, settings.gabor_num_orientations)
            pattern_metrics['gabor_dominant_orientation'] = gabor_test['dominant_orientation']
            pattern_metrics['gabor_coherency'] = gabor_test['coherency']
            
            # GLCM
            glcm_ref = analyze_glcm(gray_ref, settings.glcm_distances, settings.glcm_angles)
            glcm_test = analyze_glcm(gray_test, settings.glcm_distances, settings.glcm_angles)
            pattern_metrics['glcm_contrast'] = glcm_test['contrast']
            pattern_metrics['glcm_homogeneity'] = glcm_test['homogeneity']
            
            # LBP
            lbp_ref = analyze_lbp(gray_ref, settings.lbp_points, settings.lbp_radius)
            lbp_test = analyze_lbp(gray_test, settings.lbp_points, settings.lbp_radius)
            pattern_metrics['lbp_chi2'] = lbp_chi2_distance(lbp_ref['histogram'], lbp_test['histogram'])
            
            # Wavelet
            wavelet_ref = analyze_wavelet(gray_ref, settings.wavelet_type, settings.wavelet_levels)
            wavelet_test = analyze_wavelet(gray_test, settings.wavelet_type, settings.wavelet_levels)
            
            # Defects
            defects = analyze_defects(gray_test, settings.defect_min_area, 
                                     settings.morph_kernel_size, settings.saliency_strength)
            pattern_metrics['defect_count'] = defects['count']
            pattern_metrics['defect_density'] = defects['defect_density']
            
            # Generate advanced charts
            if fft_test['power_spectrum'] is not None:
                fft_path = os.path.join(charts_dir, 'fft_spectrum.png')
                plot_fft_power_spectrum(fft_test['power_spectrum'], fft_test['peaks'], fft_path)
                results['charts']['fft_spectrum'] = fft_path
            
            glcm_path = os.path.join(charts_dir, 'glcm_radar.png')
            plot_glcm_radar(glcm_ref, glcm_test, glcm_path)
            results['charts']['glcm_radar'] = glcm_path
            
            lbp_path = os.path.join(charts_dir, 'lbp_comparison.png')
            plot_lbp_map_and_hist(lbp_test['lbp_map'], lbp_ref['histogram'], 
                                 lbp_test['histogram'], lbp_path)
            results['charts']['lbp_comparison'] = lbp_path
        
        # Pattern status
        pattern_metrics['status'] = determine_status(
            ssim_val,
            settings.ssim_pass_threshold,
            settings.ssim_conditional_threshold,
            lower_is_better=False
        )
        
        results['pattern_metrics'] = pattern_metrics
    
    # ==================== PATTERN REPETITION ====================
    if settings.enable_pattern_repetition:
        logger.info("Running pattern repetition analysis...")
        
        gray_ref = rgb2gray(ref_small)
        gray_test = rgb2gray(test_small)
        
        # Connected components
        cc_ref = analyze_connected_components(gray_ref, settings.pattern_min_area, settings.pattern_max_area)
        cc_test = analyze_connected_components(gray_test, settings.pattern_min_area, settings.pattern_max_area)
        
        # Blob detection
        blob_ref = analyze_blob_patterns(gray_ref, settings.pattern_min_area, settings.pattern_max_area,
                                        settings.blob_min_circularity, settings.blob_min_convexity)
        blob_test = analyze_blob_patterns(gray_test, settings.pattern_min_area, settings.pattern_max_area,
                                         settings.blob_min_circularity, settings.blob_min_convexity)
        
        # Keypoint matching
        keypoint_matching = analyze_keypoint_matching(gray_ref, gray_test, settings.keypoint_detector,
                                                      settings.pattern_match_threshold)
        
        # Autocorrelation
        autocorr_test = analyze_autocorrelation(gray_test)
        
        # Spatial distribution
        spatial_test = analyze_spatial_distribution(gray_test, cc_test['patterns'], settings.grid_cell_size)
        
        # Pattern integrity
        integrity = assess_pattern_integrity(cc_ref['patterns'], cc_test['patterns'])
        
        # Missing/extra patterns
        missing_extra = detect_missing_extra_patterns(cc_ref['patterns'], cc_test['patterns'], 
                                                      spatial_test, tolerance=50)
        
        # Compile results
        pattern_repetition = {
            'count_ref': cc_ref['count'],
            'count_test': cc_test['count'],
            'count_diff': abs(cc_ref['count'] - cc_test['count']),
            'mean_area_ref': cc_ref['mean_area'],
            'mean_area_test': cc_test['mean_area'],
            'blob_count_ref': blob_ref['count'],
            'blob_count_test': blob_test['count'],
            'keypoint_matches': keypoint_matching['match_count'],
            'matching_score': keypoint_matching['matching_score'],
            'autocorr_period': autocorr_test['primary_period'],
            'spatial_uniformity': spatial_test['uniformity_score'],
            'integrity': integrity,
            'missing_count': missing_extra['missing_count'],
            'extra_count': missing_extra['extra_count'],
        }
        
        # Status
        count_diff = pattern_repetition['count_diff']
        if count_diff <= settings.pattern_count_tolerance:
            pattern_repetition['status'] = 'PASS'
        elif count_diff <= settings.pattern_count_tolerance * 2:
            pattern_repetition['status'] = 'CONDITIONAL'
        else:
            pattern_repetition['status'] = 'FAIL'
        
        results['pattern_repetition'] = pattern_repetition
        
        # Generate charts
        count_path = os.path.join(charts_dir, 'pattern_count.png')
        plot_pattern_count_comparison(cc_ref['count'], cc_test['count'], count_path)
        results['charts']['pattern_count'] = count_path
        
        if spatial_test['density_grid'] is not None:
            density_path = os.path.join(charts_dir, 'pattern_density.png')
            plot_pattern_density_heatmap(spatial_test['density_grid'], density_path)
            results['charts']['pattern_density'] = density_path
    
    # ==================== SCORING & DECISION ====================
    logger.info("Calculating scores and decision...")
    
    # Calculate scores
    color_score = 100.0
    if settings.enable_color_unit and 'color_metrics' in results:
        mean_de = results['color_metrics'].get('mean_de76', 0)
        color_score = max(0.0, 100.0 - mean_de * settings.color_score_multiplier)
    
    pattern_score = 100.0
    if settings.enable_pattern_unit and 'pattern_metrics' in results:
        pattern_score = results['pattern_metrics'].get('ssim', 1.0) * 100.0
    
    overall_score = (color_score + pattern_score) / 2.0
    
    results['color_score'] = color_score
    results['pattern_score'] = pattern_score
    results['overall_score'] = overall_score
    
    # Decision logic
    pattern_rep_ok = True
    if settings.enable_pattern_repetition and 'pattern_repetition' in results:
        if results['pattern_repetition']['status'] == 'FAIL':
            pattern_rep_ok = False
    
    if (color_score >= settings.color_score_threshold and 
        pattern_score >= settings.pattern_score_threshold and 
        pattern_rep_ok):
        decision = 'ACCEPT'
    elif not pattern_rep_ok:
        decision = 'REJECT'
    elif overall_score >= settings.overall_score_threshold:
        decision = 'CONDITIONAL ACCEPT'
    else:
        decision = 'REJECT'
    
    results['decision'] = decision
    
    # ==================== GENERATE PDF ====================
    logger.info("Generating PDF report...")
    
    pdf_path = build_main_report(results, settings, output_dir)
    results['pdf_path'] = pdf_path
    
    logger.info(f"Analysis complete! Decision: {decision}, PDF: {pdf_path}")
    
    return results

