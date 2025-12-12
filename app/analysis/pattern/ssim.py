# -*- coding: utf-8 -*-
"""
SSIM and structural similarity functions
"""
import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.color import rgb2gray


def ssim_percent(ref_rgb, test_rgb):
    """
    Calculate SSIM between two images as percentage.
    
    Args:
        ref_rgb: Reference RGB image (float32, 0-1)
        test_rgb: Test RGB image (float32, 0-1)
        
    Returns:
        float: SSIM percentage (0-100)
    """
    gr1 = rgb2gray(ref_rgb)
    gr2 = rgb2gray(test_rgb)
    return float(ssim(gr1, gr2, data_range=1.0) * 100.0)


def symmetry_score(gray):
    """
    Calculate symmetry score (horizontal and vertical).
    
    Args:
        gray: Grayscale image (float32, 0-1)
        
    Returns:
        float: Symmetry score (0-100)
    """
    h, w = gray.shape
    
    # Horizontal symmetry
    left = gray[:, :w//2]
    right = np.fliplr(gray[:, w - w//2:])
    
    # Vertical symmetry
    top = gray[:h//2, :]
    bottom = np.flipud(gray[h - h//2:, :])
    
    # Calculate SSIM for both directions
    sh = ssim(left, right, data_range=1.0)
    sv = ssim(top, bottom, data_range=1.0)
    
    return float((sh + sv) / 2 * 100)


def repeat_period_estimate(gray):
    """
    Estimate pattern repeat period using FFT.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        
    Returns:
        tuple: (period_x, period_y) in pixels
    """
    f = np.fft.fftshift(np.fft.fft2(gray))
    mag = np.log(np.abs(f) + 1e-8)
    
    cy, cx = np.array(mag.shape) // 2
    
    # Mask DC component
    window = 10
    mag[cy-window:cy+window, cx-window:cx+window] = 0
    
    # Find peak
    y_idx, x_idx = np.unravel_index(np.argmax(mag), mag.shape)
    
    # Calculate frequency
    fy = abs(y_idx - cy) / gray.shape[0]
    fx = abs(x_idx - cx) / gray.shape[1]
    
    # Convert to period
    px = int(round(1/fx)) if fx > 1e-4 else 0
    py = int(round(1/fy)) if fy > 1e-4 else 0
    
    return px, py


def color_uniformity_index(de_map):
    """
    Calculate color uniformity index from delta E map.
    
    Args:
        de_map: Delta E map array
        
    Returns:
        float: Uniformity index (0-100, higher is more uniform)
    """
    std = float(np.std(de_map))
    return max(0.0, 100.0 - std * 10.0)


def pass_status(mean_de, threshold=2.0, conditional=3.5):
    """
    Determine pass/fail status based on mean delta E.
    
    Args:
        mean_de: Mean delta E value
        threshold: Pass threshold
        conditional: Conditional threshold
        
    Returns:
        str: "PASS", "CONDITIONAL", or "FAIL"
    """
    if mean_de < threshold:
        return "PASS"
    elif mean_de <= conditional:
        return "CONDITIONAL"
    else:
        return "FAIL"


def determine_status(value, pass_threshold, conditional_threshold, lower_is_better=True):
    """
    Unified status determination function.
    
    Args:
        value: Metric value
        pass_threshold: Threshold for pass
        conditional_threshold: Threshold for conditional
        lower_is_better: If True, lower values are better
        
    Returns:
        str: "PASS", "CONDITIONAL", or "FAIL"
    """
    if lower_is_better:
        if value < pass_threshold:
            return "PASS"
        elif value <= conditional_threshold:
            return "CONDITIONAL"
        else:
            return "FAIL"
    else:
        if value >= pass_threshold:
            return "PASS"
        elif value >= conditional_threshold:
            return "CONDITIONAL"
        else:
            return "FAIL"

