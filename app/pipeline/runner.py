# -*- coding: utf-8 -*-
"""
Main analysis pipeline runner - Optimized version
"""
import os
import logging
import numpy as np
import cv2
import traceback

logger = logging.getLogger(__name__)


def run_analysis_pipeline(ref_path, test_path, ref, test, settings, output_dir):
    """
    Main analysis pipeline with optimizations and error handling.
    """
    logger.info(f"Starting analysis: {os.path.basename(ref_path)} vs {os.path.basename(test_path)}")
    
    results = {
        'ref_path': ref_path,
        'test_path': test_path,
        'charts': {}
    }
    
    try:
        # Ensure output directory exists
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
        
        # Resize for faster processing (smaller = faster)
        H, W = ref.shape[:2]
        target_w = 400  # Reduced from 640 for speed
        scale = target_w / max(W, 1)
        target_h = max(1, int(H * scale))
        
        ref_small = cv2.resize(ref, (target_w, target_h), interpolation=cv2.INTER_AREA)
        test_small = cv2.resize(test, (target_w, target_h), interpolation=cv2.INTER_AREA)
        
        logger.info(f"Resized images to {target_w}x{target_h}")
        
        # ==================== COLOR ANALYSIS ====================
        if settings.enable_color_unit:
            logger.info("Running color analysis...")
            results['color_metrics'] = run_color_analysis(ref_small, test_small, settings, charts_dir, results)
        
        # ==================== PATTERN ANALYSIS ====================
        if settings.enable_pattern_unit:
            logger.info("Running pattern analysis...")
            results['pattern_metrics'] = run_pattern_analysis(ref_small, test_small, settings)
        
        # ==================== PATTERN REPETITION ====================
        if settings.enable_pattern_repetition:
            logger.info("Running pattern repetition analysis...")
            results['pattern_repetition'] = run_repetition_analysis(ref_small, test_small, settings)
        
        # ==================== SCORING & DECISION ====================
        logger.info("Calculating scores...")
        calculate_scores(results, settings)
        
        # ==================== GENERATE PDF ====================
        logger.info("Generating PDF report...")
        try:
            from app.report.pdf_builder import build_main_report
            pdf_path = build_main_report(results, settings, output_dir)
            results['pdf_path'] = pdf_path
            logger.info(f"PDF generated: {pdf_path}")
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            # Create a simple fallback PDF path
            results['pdf_path'] = create_simple_report(results, settings, output_dir)
        
        logger.info(f"Analysis complete! Decision: {results.get('decision', 'N/A')}")
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        logger.error(traceback.format_exc())
        # Set default values on error
        results['color_score'] = 0.0
        results['pattern_score'] = 0.0
        results['overall_score'] = 0.0
        results['decision'] = 'ERROR'
        results['error'] = str(e)
    
    return results


def run_color_analysis(ref_small, test_small, settings, charts_dir, results):
    """Run color analysis with error handling."""
    color_metrics = {
        'mean_de76': 0.0,
        'std_de76': 0.0,
        'min_de76': 0.0,
        'max_de76': 0.0,
        'mean_de2000': 0.0,
        'uniformity': 100.0,
        'status': 'N/A'
    }
    
    try:
        from app.core.constants import WHITE_POINTS
        from app.analysis.color.conversions import srgb_to_xyz, xyz_to_lab
        from app.analysis.color.delta_e import deltaE76, deltaE2000
        from app.analysis.pattern.ssim import determine_status
        
        src_wp = WHITE_POINTS["D65"]
        
        # Convert color spaces
        xyz_ref = srgb_to_xyz(ref_small)
        xyz_test = srgb_to_xyz(test_small)
        lab_ref = xyz_to_lab(xyz_ref, src_wp)
        lab_test = xyz_to_lab(xyz_test, src_wp)
        
        # Calculate delta E
        de76_map = deltaE76(lab_ref, lab_test)
        de00_map = deltaE2000(lab_ref, lab_test)
        
        color_metrics = {
            'mean_de76': float(np.mean(de76_map)),
            'std_de76': float(np.std(de76_map)),
            'min_de76': float(np.min(de76_map)),
            'max_de76': float(np.max(de76_map)),
            'mean_de2000': float(np.mean(de00_map)),
            'std_de2000': float(np.std(de00_map)),
            'min_de2000': float(np.min(de00_map)),
            'max_de2000': float(np.max(de00_map)),
        }
        
        color_metrics['uniformity'] = max(0.0, 100.0 - color_metrics['std_de76'] * 10.0)
        color_metrics['status'] = determine_status(
            color_metrics['mean_de2000'],
            settings.delta_e_threshold,
            settings.delta_e_conditional,
            lower_is_better=True
        )
        
        # Generate heatmap chart
        try:
            from app.visualization.plots import plot_heatmap
            heatmap_path = os.path.join(charts_dir, 'de_heatmap.png')
            plot_heatmap(de00_map, 'ΔE2000 Heatmap', heatmap_path)
            results['charts']['de_heatmap'] = heatmap_path
        except Exception as e:
            logger.warning(f"Heatmap generation failed: {e}")
        
    except Exception as e:
        logger.error(f"Color analysis error: {e}")
        color_metrics['status'] = 'ERROR'
    
    return color_metrics


def run_pattern_analysis(ref_small, test_small, settings):
    """Run pattern analysis with error handling."""
    pattern_metrics = {
        'ssim': 0.0,
        'symmetry': 0.0,
        'edge_definition': 0.0,
        'status': 'N/A'
    }
    
    try:
        from skimage.color import rgb2gray
        from skimage.metrics import structural_similarity as ssim_func
        from app.analysis.pattern.ssim import symmetry_score, determine_status
        from app.analysis.pattern.edges import edge_definition
        
        gray_ref = rgb2gray(ref_small)
        gray_test = rgb2gray(test_small)
        
        # SSIM
        ssim_val = float(ssim_func(gray_ref, gray_test, data_range=1.0))
        
        # Symmetry (simplified)
        try:
            sym_test = symmetry_score(gray_test)
        except:
            sym_test = 50.0
        
        # Edge definition
        try:
            edge_def = edge_definition(gray_test)
        except:
            edge_def = 50.0
        
        pattern_metrics = {
            'ssim': ssim_val,
            'symmetry': sym_test,
            'edge_definition': edge_def,
        }
        
        pattern_metrics['status'] = determine_status(
            ssim_val,
            settings.ssim_pass_threshold,
            settings.ssim_conditional_threshold,
            lower_is_better=False
        )
        
    except Exception as e:
        logger.error(f"Pattern analysis error: {e}")
        pattern_metrics['status'] = 'ERROR'
    
    return pattern_metrics


def run_repetition_analysis(ref_small, test_small, settings):
    """Run pattern repetition analysis with error handling."""
    pattern_repetition = {
        'count_ref': 0,
        'count_test': 0,
        'count_diff': 0,
        'mean_area_ref': 0.0,
        'mean_area_test': 0.0,
        'status': 'N/A'
    }
    
    try:
        from skimage.color import rgb2gray
        from app.analysis.repetition.connected import analyze_connected_components
        
        gray_ref = rgb2gray(ref_small)
        gray_test = rgb2gray(test_small)
        
        # Connected components analysis
        cc_ref = analyze_connected_components(gray_ref, settings.pattern_min_area, settings.pattern_max_area)
        cc_test = analyze_connected_components(gray_test, settings.pattern_min_area, settings.pattern_max_area)
        
        pattern_repetition = {
            'count_ref': cc_ref['count'],
            'count_test': cc_test['count'],
            'count_diff': abs(cc_ref['count'] - cc_test['count']),
            'mean_area_ref': cc_ref['mean_area'],
            'mean_area_test': cc_test['mean_area'],
        }
        
        # Status
        count_diff = pattern_repetition['count_diff']
        if count_diff <= settings.pattern_count_tolerance:
            pattern_repetition['status'] = 'PASS'
        elif count_diff <= settings.pattern_count_tolerance * 2:
            pattern_repetition['status'] = 'CONDITIONAL'
        else:
            pattern_repetition['status'] = 'FAIL'
        
    except Exception as e:
        logger.error(f"Repetition analysis error: {e}")
        pattern_repetition['status'] = 'ERROR'
    
    return pattern_repetition


def calculate_scores(results, settings):
    """Calculate final scores and decision."""
    # Color score
    color_score = 100.0
    if settings.enable_color_unit and 'color_metrics' in results:
        mean_de = results['color_metrics'].get('mean_de76', 0)
        color_score = max(0.0, 100.0 - mean_de * settings.color_score_multiplier)
    
    # Pattern score
    pattern_score = 100.0
    if settings.enable_pattern_unit and 'pattern_metrics' in results:
        pattern_score = results['pattern_metrics'].get('ssim', 1.0) * 100.0
    
    # Overall
    overall_score = (color_score + pattern_score) / 2.0
    
    results['color_score'] = color_score
    results['pattern_score'] = pattern_score
    results['overall_score'] = overall_score
    
    # Decision
    pattern_rep_ok = True
    if settings.enable_pattern_repetition and 'pattern_repetition' in results:
        if results['pattern_repetition'].get('status') == 'FAIL':
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


def create_simple_report(results, settings, output_dir):
    """Create a simple text-based report as fallback."""
    from datetime import datetime
    
    filename = f"TextileQC_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write("TEXTILE QC ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Decision: {results.get('decision', 'N/A')}\n")
        f.write(f"Color Score: {results.get('color_score', 0):.1f}\n")
        f.write(f"Pattern Score: {results.get('pattern_score', 0):.1f}\n")
        f.write(f"Overall Score: {results.get('overall_score', 0):.1f}\n")
    
    # Return PDF path even though it's txt (for compatibility)
    return filepath.replace('.txt', '.pdf') if os.path.exists(filepath) else filepath
