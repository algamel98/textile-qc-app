# -*- coding: utf-8 -*-
"""
Comprehensive Analysis Pipeline Runner
Matches PDFSAMPLE.py functionality for complete textile quality control analysis
"""
import os
import logging
import numpy as np
import cv2
import traceback
import pandas as pd
from PIL import Image

logger = logging.getLogger(__name__)


def run_analysis_pipeline(ref_path, test_path, ref, test, settings, output_dir):
    """
    Comprehensive analysis pipeline matching PDFSAMPLE.py functionality.
    
    Args:
        ref_path: Path to reference image
        test_path: Path to test image  
        ref: Reference image array (RGB)
        test: Test image array (RGB)
        settings: QCSettings object
        output_dir: Output directory for charts and PDF
        
    Returns:
        dict: Complete analysis results
    """
    logger.info(f"Starting comprehensive analysis: {os.path.basename(ref_path)} vs {os.path.basename(test_path)}")
    
    results = {
        'ref_path': ref_path,
        'test_path': test_path,
        'charts': {},
        'error': None
    }
    
    try:
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        charts_dir = os.path.join(output_dir, 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        
        # Apply crop if enabled
        if settings.use_crop:
            logger.info(f"Applying {settings.crop_shape} crop")
            try:
                from app.core.image_utils import apply_crop
                ref = apply_crop(ref, settings, is_test_image=False)
                test = apply_crop(test, settings, is_test_image=True)
            except Exception as e:
                logger.warning(f"Crop failed, using full images: {e}")
        
        # Resize for analysis (640px width for good balance of speed and quality)
        H, W = ref.shape[:2]
        target_w = 640
        scale = target_w / max(W, 1)
        target_h = max(1, int(H * scale))
        
        ref_small = cv2.resize(ref, (target_w, target_h), interpolation=cv2.INTER_AREA)
        test_small = cv2.resize(test, (target_w, target_h), interpolation=cv2.INTER_AREA)
        
        logger.info(f"Resized images to {target_w}x{target_h}")
        
        # Store resized images in results
        results['ref_small'] = ref_small
        results['test_small'] = test_small
        results['original_size'] = (H, W)
        results['analysis_size'] = (target_h, target_w)
        
        # ==================== COLOR ANALYSIS ====================
        if settings.enable_color_unit:
            logger.info("Running color analysis...")
            color_results = run_comprehensive_color_analysis(
                ref_small, test_small, settings, charts_dir, results
            )
            results['color_metrics'] = color_results['metrics']
            results['color_data'] = color_results
        
        # ==================== PATTERN ANALYSIS ====================
        if settings.enable_pattern_unit:
            logger.info("Running pattern analysis...")
            pattern_results = run_comprehensive_pattern_analysis(
                ref_small, test_small, settings, charts_dir, results
            )
            results['pattern_metrics'] = pattern_results['metrics']
            results['pattern_data'] = pattern_results
        
        # ==================== PATTERN REPETITION ====================
        if settings.enable_pattern_repetition:
            logger.info("Running pattern repetition analysis...")
            repetition_results = run_comprehensive_repetition_analysis(
                ref_small, test_small, settings, charts_dir, results
            )
            results['pattern_repetition'] = repetition_results
        
        # ==================== SPECTROPHOTOMETER ANALYSIS ====================
        if settings.enable_spectrophotometer:
            logger.info("Running spectrophotometer analysis...")
            spectro_results = run_spectrophotometer_analysis(
                ref_small, test_small, settings, charts_dir, results
            )
            results['spectrophotometer'] = spectro_results
        
        # ==================== REGIONAL SAMPLES ====================
        logger.info("Computing regional samples...")
        results['regional_samples'] = compute_regional_samples(
            ref_small, test_small, settings
        )
        
        # ==================== SCORING & DECISION ====================
        logger.info("Calculating scores and decision...")
        calculate_comprehensive_scores(results, settings)
        
        # ==================== GENERATE PDF ====================
        logger.info("Generating comprehensive PDF report...")
        try:
            from app.report.pdf_builder import build_comprehensive_report
            pdf_path = build_comprehensive_report(results, settings, output_dir)
            results['pdf_path'] = pdf_path
            logger.info(f"PDF generated: {pdf_path}")
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            logger.error(traceback.format_exc())
            # Try simple fallback
            results['pdf_path'] = create_simple_report(results, settings, output_dir)
        
        logger.info(f"Analysis complete! Decision: {results.get('decision', 'N/A')}")
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        logger.error(traceback.format_exc())
        results['color_score'] = 0.0
        results['pattern_score'] = 0.0
        results['overall_score'] = 0.0
        results['decision'] = 'ERROR'
        results['error'] = str(e)
    
    return results


def run_comprehensive_color_analysis(ref_small, test_small, settings, charts_dir, results):
    """Run comprehensive color analysis matching PDFSAMPLE.py"""
    from app.core.constants import WHITE_POINTS
    from app.analysis.color.conversions import srgb_to_xyz, xyz_to_lab, rgb_to_cmyk
    from app.analysis.color.delta_e import deltaE76, deltaE94, deltaE2000, deltaE_CMC
    
    color_results = {
        'metrics': {},
        'lab_ref': None,
        'lab_test': None,
        'de_maps': {}
    }
    
    try:
        src_wp = WHITE_POINTS["D65"]
        
        # Convert to XYZ and LAB
        xyz_ref = srgb_to_xyz(ref_small)
        xyz_test = srgb_to_xyz(test_small)
        lab_ref = xyz_to_lab(xyz_ref, src_wp)
        lab_test = xyz_to_lab(xyz_test, src_wp)
        
        color_results['xyz_ref'] = xyz_ref
        color_results['xyz_test'] = xyz_test
        color_results['lab_ref'] = lab_ref
        color_results['lab_test'] = lab_test
        
        # Calculate all delta E metrics
        de76_map = deltaE76(lab_ref, lab_test)
        de94_map = deltaE94(lab_ref, lab_test)
        de00_map = deltaE2000(lab_ref, lab_test)
        
        color_results['de_maps'] = {
            'de76': de76_map,
            'de94': de94_map,
            'de00': de00_map
        }
        
        # CMC delta E
        if settings.use_delta_e_cmc:
            l_val, c_val = (2, 1) if settings.cmc_l_c_ratio == "2:1" else (1, 1)
            de_cmc_map = deltaE_CMC(lab_ref, lab_test, l=l_val, c=c_val)
            color_results['de_maps']['cmc'] = de_cmc_map
        
        # Statistics
        color_results['metrics'] = {
            # DE76
            'mean_de76': float(np.mean(de76_map)),
            'std_de76': float(np.std(de76_map)),
            'min_de76': float(np.min(de76_map)),
            'max_de76': float(np.max(de76_map)),
            # DE94
            'mean_de94': float(np.mean(de94_map)),
            'std_de94': float(np.std(de94_map)),
            'min_de94': float(np.min(de94_map)),
            'max_de94': float(np.max(de94_map)),
            # DE2000
            'mean_de2000': float(np.mean(de00_map)),
            'std_de2000': float(np.std(de00_map)),
            'min_de2000': float(np.min(de00_map)),
            'max_de2000': float(np.max(de00_map)),
        }
        
        # CMC
        if settings.use_delta_e_cmc and 'cmc' in color_results['de_maps']:
            color_results['metrics']['mean_de_cmc'] = float(np.mean(color_results['de_maps']['cmc']))
        
        # LAB means
        lab_ref_mean = lab_ref.reshape(-1, 3).mean(axis=0)
        lab_test_mean = lab_test.reshape(-1, 3).mean(axis=0)
        color_results['lab_ref_mean'] = lab_ref_mean
        color_results['lab_test_mean'] = lab_test_mean
        
        # LAB differences
        color_results['metrics']['dL'] = float(lab_test_mean[0] - lab_ref_mean[0])
        color_results['metrics']['da'] = float(lab_test_mean[1] - lab_ref_mean[1])
        color_results['metrics']['db'] = float(lab_test_mean[2] - lab_ref_mean[2])
        
        # Uniformity index
        color_results['metrics']['uniformity'] = max(0.0, 100.0 - color_results['metrics']['std_de76'] * settings.uniformity_std_multiplier)
        
        # Status
        color_results['metrics']['status'] = determine_status(
            color_results['metrics']['mean_de2000'],
            settings.delta_e_threshold,
            settings.delta_e_conditional,
            lower_is_better=True
        )
        
        # Generate charts
        generate_color_charts(ref_small, test_small, color_results, charts_dir, results)
        
    except Exception as e:
        logger.error(f"Color analysis error: {e}")
        color_results['metrics']['status'] = 'ERROR'
    
    return color_results


def run_comprehensive_pattern_analysis(ref_small, test_small, settings, charts_dir, results):
    """Run comprehensive pattern analysis with advanced texture features"""
    from skimage.color import rgb2gray
    from skimage.metrics import structural_similarity as ssim_func
    
    pattern_results = {
        'metrics': {},
        'fft': {},
        'gabor': {},
        'glcm': {},
        'lbp': {},
        'wavelet': {},
        'defects': {}
    }
    
    try:
        # Convert to grayscale
        gray_ref = rgb2gray(ref_small)
        gray_test = rgb2gray(test_small)
        pattern_results['gray_ref'] = gray_ref
        pattern_results['gray_test'] = gray_test
        
        # Basic SSIM
        ssim_val = float(ssim_func(gray_ref, gray_test, data_range=1.0))
        
        # Symmetry
        try:
            from app.analysis.pattern.ssim import symmetry_score
            sym_ref = symmetry_score(gray_ref)
            sym_test = symmetry_score(gray_test)
            symmetry = (sym_ref + sym_test) / 2
        except:
            symmetry = 50.0
        
        # Edge definition
        try:
            from app.analysis.pattern.edges import edge_definition
            edge_def = edge_definition(gray_test)
        except:
            edge_def = 50.0
        
        # Repeat period
        try:
            from app.analysis.pattern.ssim import repeat_period_estimate
            px, py = repeat_period_estimate(gray_test)
        except:
            px, py = 0, 0
        
        pattern_results['metrics'] = {
            'ssim': ssim_val,
            'symmetry': symmetry,
            'edge_definition': edge_def,
            'repeat_period_x': px,
            'repeat_period_y': py,
        }
        
        # Advanced texture analysis (if enabled)
        if settings.enable_pattern_advanced:
            # FFT Analysis
            try:
                from app.analysis.pattern.fft import analyze_fft
                pattern_results['fft']['ref'] = analyze_fft(gray_ref, settings.fft_num_peaks, settings.fft_enable_notch)
                pattern_results['fft']['test'] = analyze_fft(gray_test, settings.fft_num_peaks, settings.fft_enable_notch)
            except Exception as e:
                logger.warning(f"FFT analysis failed: {e}")
            
            # Gabor Analysis
            try:
                from app.analysis.pattern.gabor import analyze_gabor
                pattern_results['gabor']['ref'] = analyze_gabor(gray_ref, settings.gabor_frequencies, settings.gabor_num_orientations)
                pattern_results['gabor']['test'] = analyze_gabor(gray_test, settings.gabor_frequencies, settings.gabor_num_orientations)
            except Exception as e:
                logger.warning(f"Gabor analysis failed: {e}")
            
            # GLCM Analysis
            try:
                from app.analysis.pattern.glcm import analyze_glcm
                pattern_results['glcm']['ref'] = analyze_glcm(gray_ref, settings.glcm_distances, settings.glcm_angles)
                pattern_results['glcm']['test'] = analyze_glcm(gray_test, settings.glcm_distances, settings.glcm_angles)
            except Exception as e:
                logger.warning(f"GLCM analysis failed: {e}")
            
            # LBP Analysis
            try:
                from app.analysis.pattern.lbp import analyze_lbp, lbp_chi2_distance
                pattern_results['lbp']['ref'] = analyze_lbp(gray_ref, settings.lbp_points, settings.lbp_radius)
                pattern_results['lbp']['test'] = analyze_lbp(gray_test, settings.lbp_points, settings.lbp_radius)
                pattern_results['lbp']['chi2_distance'] = lbp_chi2_distance(
                    pattern_results['lbp']['ref']['histogram'],
                    pattern_results['lbp']['test']['histogram']
                )
            except Exception as e:
                logger.warning(f"LBP analysis failed: {e}")
            
            # Wavelet Analysis
            try:
                from app.analysis.pattern.wavelet import analyze_wavelet
                pattern_results['wavelet']['ref'] = analyze_wavelet(gray_ref, settings.wavelet_type, settings.wavelet_levels)
                pattern_results['wavelet']['test'] = analyze_wavelet(gray_test, settings.wavelet_type, settings.wavelet_levels)
            except Exception as e:
                logger.warning(f"Wavelet analysis failed: {e}")
            
            # Defect Detection
            try:
                from app.analysis.pattern.defects import analyze_defects
                pattern_results['defects'] = analyze_defects(
                    gray_test, 
                    settings.defect_min_area,
                    settings.morph_kernel_size,
                    settings.saliency_strength
                )
            except Exception as e:
                logger.warning(f"Defect detection failed: {e}")
        
        # Status
        pattern_results['metrics']['status'] = determine_status(
            ssim_val,
            settings.ssim_pass_threshold,
            settings.ssim_conditional_threshold,
            lower_is_better=False
        )
        
        # Generate charts
        generate_pattern_charts(ref_small, test_small, pattern_results, settings, charts_dir, results)
        
    except Exception as e:
        logger.error(f"Pattern analysis error: {e}")
        pattern_results['metrics']['status'] = 'ERROR'
    
    return pattern_results


def run_comprehensive_repetition_analysis(ref_small, test_small, settings, charts_dir, results):
    """Run comprehensive pattern repetition analysis"""
    from skimage.color import rgb2gray
    
    rep_results = {
        'connected_ref': {},
        'connected_test': {},
        'blob_ref': {},
        'blob_test': {},
        'keypoint_matching': {},
        'autocorr_ref': {},
        'autocorr_test': {},
        'spatial_ref': {},
        'spatial_test': {},
        'integrity': {},
        'missing_extra': {},
        'status': 'N/A'
    }
    
    try:
        gray_ref = rgb2gray(ref_small)
        gray_test = rgb2gray(test_small)
        
        # Connected Components
        try:
            from app.analysis.repetition.connected import analyze_connected_components
            rep_results['connected_ref'] = analyze_connected_components(
                gray_ref, settings.pattern_min_area, settings.pattern_max_area
            )
            rep_results['connected_test'] = analyze_connected_components(
                gray_test, settings.pattern_min_area, settings.pattern_max_area
            )
        except Exception as e:
            logger.warning(f"Connected components failed: {e}")
        
        # Blob Detection
        try:
            from app.analysis.repetition.blob_detection import analyze_blob_patterns
            rep_results['blob_ref'] = analyze_blob_patterns(
                gray_ref, settings.pattern_min_area, settings.pattern_max_area,
                settings.blob_min_circularity, settings.blob_min_convexity
            )
            rep_results['blob_test'] = analyze_blob_patterns(
                gray_test, settings.pattern_min_area, settings.pattern_max_area,
                settings.blob_min_circularity, settings.blob_min_convexity
            )
        except Exception as e:
            logger.warning(f"Blob detection failed: {e}")
        
        # Keypoint Matching
        try:
            from app.analysis.repetition.keypoints import analyze_keypoint_matching
            rep_results['keypoint_matching'] = analyze_keypoint_matching(
                gray_ref, gray_test,
                settings.keypoint_detector,
                settings.pattern_match_threshold
            )
        except Exception as e:
            logger.warning(f"Keypoint matching failed: {e}")
        
        # Autocorrelation
        try:
            from app.analysis.repetition.autocorrelation import analyze_autocorrelation
            rep_results['autocorr_ref'] = analyze_autocorrelation(gray_ref)
            rep_results['autocorr_test'] = analyze_autocorrelation(gray_test)
        except Exception as e:
            logger.warning(f"Autocorrelation failed: {e}")
        
        # Spatial Distribution
        try:
            from app.analysis.repetition.spatial import analyze_spatial_distribution
            patterns_ref = rep_results['connected_ref'].get('patterns', [])
            patterns_test = rep_results['connected_test'].get('patterns', [])
            rep_results['spatial_ref'] = analyze_spatial_distribution(
                gray_ref, patterns_ref, settings.grid_cell_size
            )
            rep_results['spatial_test'] = analyze_spatial_distribution(
                gray_test, patterns_test, settings.grid_cell_size
            )
        except Exception as e:
            logger.warning(f"Spatial analysis failed: {e}")
        
        # Pattern Integrity
        try:
            from app.analysis.repetition.integrity import assess_pattern_integrity, detect_missing_extra_patterns
            patterns_ref = rep_results['connected_ref'].get('patterns', [])
            patterns_test = rep_results['connected_test'].get('patterns', [])
            rep_results['integrity'] = assess_pattern_integrity(patterns_ref, patterns_test)
            rep_results['missing_extra'] = detect_missing_extra_patterns(
                patterns_ref, patterns_test, rep_results['spatial_ref'], tolerance=50
            )
        except Exception as e:
            logger.warning(f"Integrity assessment failed: {e}")
        
        # Summary metrics
        count_ref = rep_results['connected_ref'].get('count', 0)
        count_test = rep_results['connected_test'].get('count', 0)
        count_diff = abs(count_ref - count_test)
        
        rep_results['count_ref'] = count_ref
        rep_results['count_test'] = count_test
        rep_results['count_diff'] = count_diff
        rep_results['mean_area_ref'] = rep_results['connected_ref'].get('mean_area', 0)
        rep_results['mean_area_test'] = rep_results['connected_test'].get('mean_area', 0)
        
        # Status determination
        if count_diff <= settings.pattern_count_tolerance:
            rep_results['status'] = 'PASS'
        elif count_diff <= settings.pattern_count_tolerance * 2:
            rep_results['status'] = 'CONDITIONAL'
        else:
            rep_results['status'] = 'FAIL'
        
        # Generate charts
        generate_repetition_charts(ref_small, test_small, rep_results, settings, charts_dir, results)
        
    except Exception as e:
        logger.error(f"Repetition analysis error: {e}")
        rep_results['status'] = 'ERROR'
    
    return rep_results


def run_spectrophotometer_analysis(ref_small, test_small, settings, charts_dir, results):
    """Run spectrophotometer-related analysis (metamerism, whiteness, yellowness)"""
    from app.core.constants import WHITE_POINTS
    from app.analysis.color.conversions import srgb_to_xyz, xyz_to_lab
    from app.analysis.color.delta_e import deltaE2000
    
    spectro_results = {
        'metamerism': [],
        'whiteness_ref': 0.0,
        'whiteness_test': 0.0,
        'yellowness_ref': 0.0,
        'yellowness_test': 0.0,
        'metamerism_index': 0.0
    }
    
    try:
        src_wp = WHITE_POINTS["D65"]
        xyz_ref = srgb_to_xyz(ref_small)
        xyz_test = srgb_to_xyz(test_small)
        
        # Metamerism analysis under different illuminants
        de_values = []
        for illuminant in settings.metamerism_illuminants:
            if illuminant in WHITE_POINTS:
                try:
                    from app.analysis.color.metamerism import compute_metamerism_de
                    de_val = compute_metamerism_de(xyz_ref, xyz_test, src_wp, WHITE_POINTS[illuminant])
                    spectro_results['metamerism'].append({
                        'illuminant': illuminant,
                        'delta_e': float(de_val)
                    })
                    de_values.append(de_val)
                except Exception as e:
                    logger.warning(f"Metamerism for {illuminant} failed: {e}")
        
        # Metamerism index
        if len(de_values) >= 2:
            spectro_results['metamerism_index'] = float(np.std(de_values) * 10)
        
        # Whiteness and yellowness
        try:
            from app.analysis.color.whiteness import cie_whiteness_tint, astm_yellowness
            xyz_ref_mean = xyz_ref.reshape(-1, 3).mean(axis=0)
            xyz_test_mean = xyz_test.reshape(-1, 3).mean(axis=0)
            
            w_ref, t_ref = cie_whiteness_tint(xyz_ref_mean)
            w_test, t_test = cie_whiteness_tint(xyz_test_mean)
            spectro_results['whiteness_ref'] = float(w_ref)
            spectro_results['whiteness_test'] = float(w_test)
            spectro_results['tint_ref'] = float(t_ref)
            spectro_results['tint_test'] = float(t_test)
            
            spectro_results['yellowness_ref'] = float(astm_yellowness(xyz_ref_mean))
            spectro_results['yellowness_test'] = float(astm_yellowness(xyz_test_mean))
        except Exception as e:
            logger.warning(f"Whiteness/yellowness failed: {e}")
        
        # Generate metamerism chart
        if spectro_results['metamerism']:
            try:
                from app.visualization.plots import plot_metamerism_illuminants
                illuminants = [m['illuminant'] for m in spectro_results['metamerism']]
                de_vals = [m['delta_e'] for m in spectro_results['metamerism']]
                chart_path = os.path.join(charts_dir, 'metamerism.png')
                plot_metamerism_illuminants(illuminants, de_vals, chart_path)
                results['charts']['metamerism'] = chart_path
            except Exception as e:
                logger.warning(f"Metamerism chart failed: {e}")
        
    except Exception as e:
        logger.error(f"Spectrophotometer analysis error: {e}")
    
    return spectro_results


def compute_regional_samples(ref_small, test_small, settings):
    """Compute 5-point regional color samples"""
    from app.core.constants import WHITE_POINTS
    from app.analysis.color.conversions import srgb_to_xyz, xyz_to_lab, rgb_to_cmyk
    from app.analysis.color.delta_e import deltaE76, deltaE94, deltaE2000
    
    samples = []
    h, w = ref_small.shape[:2]
    src_wp = WHITE_POINTS["D65"]
    
    try:
        # Grid points
        n = settings.num_sample_points
        pts = grid_points(h, w, n)
        
        for i, (y, x) in enumerate(pts, start=1):
            # RGB values
            ref_rgb = ref_small[y, x].astype(float)
            test_rgb = test_small[y, x].astype(float)
            
            # XYZ
            xyz_r = srgb_to_xyz(np.array([[ref_rgb]]))[0, 0]
            xyz_t = srgb_to_xyz(np.array([[test_rgb]]))[0, 0]
            
            # LAB
            lab_r = xyz_to_lab(xyz_r.reshape(1, 1, 3), src_wp)[0, 0]
            lab_t = xyz_to_lab(xyz_t.reshape(1, 1, 3), src_wp)[0, 0]
            
            # CMYK
            cmyk_r = rgb_to_cmyk(np.array([[ref_rgb / 255.0]]))[0, 0] * 100
            cmyk_t = rgb_to_cmyk(np.array([[test_rgb / 255.0]]))[0, 0] * 100
            
            # Delta E
            de76 = float(deltaE76(lab_r.reshape(1, 3), lab_t.reshape(1, 3))[0])
            de94 = float(deltaE94(lab_r.reshape(1, 3), lab_t.reshape(1, 3))[0])
            de00 = float(deltaE2000(lab_r.reshape(1, 3), lab_t.reshape(1, 3))[0])
            
            samples.append({
                'region': i,
                'x': int(x),
                'y': int(y),
                'ref_rgb': ref_rgb.tolist(),
                'test_rgb': test_rgb.tolist(),
                'ref_lab': lab_r.tolist(),
                'test_lab': lab_t.tolist(),
                'ref_xyz': xyz_r.tolist(),
                'test_xyz': xyz_t.tolist(),
                'ref_cmyk': cmyk_r.tolist(),
                'test_cmyk': cmyk_t.tolist(),
                'de76': de76,
                'de94': de94,
                'de00': de00
            })
    except Exception as e:
        logger.error(f"Regional samples error: {e}")
    
    return samples


def grid_points(h, w, n=5):
    """Generate grid sample points"""
    ys = np.linspace(0.2, 0.8, n)
    xs = np.linspace(0.2, 0.8, n)
    pts = [(int(y * h), int(x * w)) for y, x in zip(ys, xs)]
    return pts[:n]


def determine_status(value, pass_threshold, conditional_threshold, lower_is_better=True):
    """Determine PASS/CONDITIONAL/FAIL status"""
    if lower_is_better:
        if value < pass_threshold:
            return "PASS"
        elif value <= conditional_threshold:
            return "CONDITIONAL"
        else:
            return "FAIL"
    else:
        if value > pass_threshold:
            return "PASS"
        elif value > conditional_threshold:
            return "CONDITIONAL"
        else:
            return "FAIL"


def calculate_comprehensive_scores(results, settings):
    """Calculate comprehensive scores and final decision"""
    # Color score
    color_score = 100.0
    if settings.enable_color_unit and 'color_metrics' in results:
        mean_de = results['color_metrics'].get('mean_de76', 0)
        color_score = max(0.0, 100.0 - mean_de * settings.color_score_multiplier)
    
    # Pattern score
    pattern_score = 100.0
    if settings.enable_pattern_unit and 'pattern_metrics' in results:
        pattern_score = results['pattern_metrics'].get('ssim', 1.0) * 100.0
    
    # Pattern repetition factor
    pattern_rep_ok = True
    pattern_rep_conditional = False
    if settings.enable_pattern_repetition and 'pattern_repetition' in results:
        rep_status = results['pattern_repetition'].get('status', 'N/A')
        if rep_status == 'FAIL':
            pattern_rep_ok = False
        elif rep_status == 'CONDITIONAL':
            pattern_rep_conditional = True
    
    # Overall score
    overall_score = (color_score + pattern_score) / 2.0
    
    results['color_score'] = color_score
    results['pattern_score'] = pattern_score
    results['overall_score'] = overall_score
    
    # Decision logic
    if (color_score >= settings.color_score_threshold and
        pattern_score >= settings.pattern_score_threshold and
        pattern_rep_ok and not pattern_rep_conditional):
        decision = 'ACCEPT'
    elif not pattern_rep_ok:
        decision = 'REJECT'
    elif overall_score >= settings.overall_score_threshold or pattern_rep_conditional:
        decision = 'CONDITIONAL ACCEPT'
    else:
        decision = 'REJECT'
    
    results['decision'] = decision


def generate_color_charts(ref_small, test_small, color_results, charts_dir, results):
    """Generate all color analysis charts"""
    from app.visualization.plots import (
        plot_rgb_hist, plot_heatmap, plot_spectral_proxy,
        plot_ab_scatter, plot_lab_bars
    )
    
    try:
        # RGB Histograms
        hist_ref_path = os.path.join(charts_dir, 'hist_ref.png')
        hist_test_path = os.path.join(charts_dir, 'hist_test.png')
        plot_rgb_hist(ref_small, 'Reference RGB Histogram', hist_ref_path)
        plot_rgb_hist(test_small, 'Sample RGB Histogram', hist_test_path)
        results['charts']['hist_ref'] = hist_ref_path
        results['charts']['hist_test'] = hist_test_path
    except Exception as e:
        logger.warning(f"RGB histogram failed: {e}")
    
    try:
        # Delta E Heatmap
        if 'de00' in color_results['de_maps']:
            heatmap_path = os.path.join(charts_dir, 'de_heatmap.png')
            plot_heatmap(color_results['de_maps']['de00'], 'ΔE2000 Heatmap', heatmap_path)
            results['charts']['de_heatmap'] = heatmap_path
    except Exception as e:
        logger.warning(f"Heatmap failed: {e}")
    
    try:
        # Spectral proxy
        mean_rgb_ref = ref_small.reshape(-1, 3).mean(axis=0) / 255.0
        mean_rgb_test = test_small.reshape(-1, 3).mean(axis=0) / 255.0
        spectral_path = os.path.join(charts_dir, 'spectral_proxy.png')
        plot_spectral_proxy(mean_rgb_ref, mean_rgb_test, spectral_path)
        results['charts']['spectral_proxy'] = spectral_path
    except Exception as e:
        logger.warning(f"Spectral proxy failed: {e}")
    
    try:
        # a*b* scatter
        if color_results['lab_ref'] is not None:
            ab_path = os.path.join(charts_dir, 'ab_scatter.png')
            plot_ab_scatter(color_results['lab_ref'], color_results['lab_test'], ab_path)
            results['charts']['ab_scatter'] = ab_path
    except Exception as e:
        logger.warning(f"a*b* scatter failed: {e}")
    
    try:
        # LAB bars
        if color_results['lab_ref_mean'] is not None:
            lab_bars_path = os.path.join(charts_dir, 'lab_bars.png')
            plot_lab_bars(color_results['lab_ref_mean'], color_results['lab_test_mean'], lab_bars_path)
            results['charts']['lab_bars'] = lab_bars_path
    except Exception as e:
        logger.warning(f"LAB bars failed: {e}")
    
    # Save overlay images
    try:
        from PIL import Image, ImageDraw
        pts = grid_points(ref_small.shape[0], ref_small.shape[1], 5)
        
        # Reference overlay
        ref_pil = Image.fromarray(ref_small)
        draw = ImageDraw.Draw(ref_pil)
        for y, x in pts:
            draw.ellipse([(x-10, y-10), (x+10, y+10)], outline='red', width=3)
        overlay_ref_path = os.path.join(charts_dir, 'overlay_ref.png')
        ref_pil.save(overlay_ref_path)
        results['charts']['overlay_ref'] = overlay_ref_path
        
        # Test overlay
        test_pil = Image.fromarray(test_small)
        draw = ImageDraw.Draw(test_pil)
        for y, x in pts:
            draw.ellipse([(x-10, y-10), (x+10, y+10)], outline='red', width=3)
        overlay_test_path = os.path.join(charts_dir, 'overlay_test.png')
        test_pil.save(overlay_test_path)
        results['charts']['overlay_test'] = overlay_test_path
    except Exception as e:
        logger.warning(f"Overlay images failed: {e}")


def generate_pattern_charts(ref_small, test_small, pattern_results, settings, charts_dir, results):
    """Generate pattern analysis charts"""
    from app.visualization.plots import (
        plot_fft_power_spectrum, plot_gabor_montage, plot_gabor_orientation_histogram,
        plot_glcm_radar, plot_lbp_map_and_hist, plot_wavelet_energy_bars,
        plot_defect_saliency
    )
    
    # FFT chart
    if 'test' in pattern_results['fft'] and pattern_results['fft']['test']:
        try:
            fft_path = os.path.join(charts_dir, 'fft_spectrum.png')
            fft_data = pattern_results['fft']['test']
            if 'power_spectrum' in fft_data and 'peaks' in fft_data:
                plot_fft_power_spectrum(fft_data['power_spectrum'], fft_data['peaks'], fft_path)
                results['charts']['fft_spectrum'] = fft_path
        except Exception as e:
            logger.warning(f"FFT chart failed: {e}")
    
    # Gabor charts
    if 'test' in pattern_results['gabor'] and pattern_results['gabor']['test']:
        try:
            gabor_data = pattern_results['gabor']['test']
            if 'energy_maps' in gabor_data:
                gabor_path = os.path.join(charts_dir, 'gabor_montage.png')
                plot_gabor_montage(gabor_data['energy_maps'], settings.gabor_frequencies,
                                  settings.gabor_num_orientations, gabor_path)
                results['charts']['gabor_montage'] = gabor_path
        except Exception as e:
            logger.warning(f"Gabor montage failed: {e}")
    
    # GLCM radar
    if pattern_results['glcm'].get('ref') and pattern_results['glcm'].get('test'):
        try:
            glcm_path = os.path.join(charts_dir, 'glcm_radar.png')
            plot_glcm_radar(pattern_results['glcm']['ref'], pattern_results['glcm']['test'], glcm_path)
            results['charts']['glcm_radar'] = glcm_path
        except Exception as e:
            logger.warning(f"GLCM radar failed: {e}")
    
    # LBP chart
    if pattern_results['lbp'].get('ref') and pattern_results['lbp'].get('test'):
        try:
            lbp_path = os.path.join(charts_dir, 'lbp_map.png')
            plot_lbp_map_and_hist(
                pattern_results['lbp']['test']['lbp_map'],
                pattern_results['lbp']['ref']['histogram'],
                pattern_results['lbp']['test']['histogram'],
                lbp_path
            )
            results['charts']['lbp_map'] = lbp_path
        except Exception as e:
            logger.warning(f"LBP chart failed: {e}")
    
    # Wavelet chart
    if pattern_results['wavelet'].get('ref') and pattern_results['wavelet'].get('test'):
        try:
            wavelet_path = os.path.join(charts_dir, 'wavelet_energy.png')
            plot_wavelet_energy_bars(
                pattern_results['wavelet']['ref']['energies'],
                pattern_results['wavelet']['test']['energies'],
                wavelet_path
            )
            results['charts']['wavelet_energy'] = wavelet_path
        except Exception as e:
            logger.warning(f"Wavelet chart failed: {e}")
    
    # Defect saliency
    if pattern_results['defects']:
        try:
            defect_path = os.path.join(charts_dir, 'defect_saliency.png')
            plot_defect_saliency(
                pattern_results['defects'].get('saliency_map', np.zeros((10, 10))),
                pattern_results['defects'].get('binary_map', np.zeros((10, 10))),
                pattern_results['defects'].get('defects', []),
                pattern_results['gray_test'].shape,
                defect_path
            )
            results['charts']['defect_saliency'] = defect_path
        except Exception as e:
            logger.warning(f"Defect chart failed: {e}")


def generate_repetition_charts(ref_small, test_small, rep_results, settings, charts_dir, results):
    """Generate pattern repetition charts"""
    from app.visualization.plots import (
        plot_pattern_detection_map, plot_pattern_count_comparison,
        plot_pattern_density_heatmap, plot_pattern_size_distribution,
        plot_pattern_integrity_radar
    )
    
    # Pattern detection maps
    try:
        patterns_ref = rep_results['connected_ref'].get('patterns', [])
        patterns_test = rep_results['connected_test'].get('patterns', [])
        
        if patterns_ref:
            det_ref_path = os.path.join(charts_dir, 'pattern_detection_ref.png')
            plot_pattern_detection_map(ref_small, patterns_ref, 'Reference', det_ref_path)
            results['charts']['pattern_detection_ref'] = det_ref_path
        
        if patterns_test:
            det_test_path = os.path.join(charts_dir, 'pattern_detection_test.png')
            plot_pattern_detection_map(test_small, patterns_test, 'Sample', det_test_path)
            results['charts']['pattern_detection_test'] = det_test_path
    except Exception as e:
        logger.warning(f"Pattern detection charts failed: {e}")
    
    # Count comparison
    try:
        count_path = os.path.join(charts_dir, 'pattern_count.png')
        plot_pattern_count_comparison(
            rep_results.get('count_ref', 0),
            rep_results.get('count_test', 0),
            count_path
        )
        results['charts']['pattern_count'] = count_path
    except Exception as e:
        logger.warning(f"Count comparison chart failed: {e}")
    
    # Density heatmaps
    try:
        if rep_results['spatial_ref'].get('density_grid') is not None:
            density_ref_path = os.path.join(charts_dir, 'density_ref.png')
            plot_pattern_density_heatmap(rep_results['spatial_ref']['density_grid'], density_ref_path)
            results['charts']['density_ref'] = density_ref_path
        
        if rep_results['spatial_test'].get('density_grid') is not None:
            density_test_path = os.path.join(charts_dir, 'density_test.png')
            plot_pattern_density_heatmap(rep_results['spatial_test']['density_grid'], density_test_path)
            results['charts']['density_test'] = density_test_path
    except Exception as e:
        logger.warning(f"Density heatmap failed: {e}")
    
    # Integrity radar
    try:
        if rep_results['integrity']:
            integrity_path = os.path.join(charts_dir, 'integrity_radar.png')
            plot_pattern_integrity_radar({}, rep_results['integrity'], integrity_path)
            results['charts']['integrity_radar'] = integrity_path
    except Exception as e:
        logger.warning(f"Integrity radar failed: {e}")


def create_simple_report(results, settings, output_dir):
    """Create a simple fallback text report"""
    from datetime import datetime
    
    filename = f"TextileQC_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w') as f:
            f.write("TEXTILE QC ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Decision: {results.get('decision', 'N/A')}\n")
            f.write(f"Color Score: {results.get('color_score', 0):.1f}/100\n")
            f.write(f"Pattern Score: {results.get('pattern_score', 0):.1f}/100\n")
            f.write(f"Overall Score: {results.get('overall_score', 0):.1f}/100\n")
            
            if results.get('error'):
                f.write(f"\nError: {results['error']}\n")
    except:
        pass
    
    return filepath
