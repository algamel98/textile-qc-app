# -*- coding: utf-8 -*-
"""
FFT (Fourier Transform) analysis functions
"""
import numpy as np
import cv2


def analyze_fft(gray, num_peaks=5, enable_notch=False):
    """
    2D FFT analysis with peak detection.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        num_peaks: Number of peaks to detect
        enable_notch: Whether to apply notch filter
        
    Returns:
        dict: FFT analysis results
    """
    h, w = gray.shape
    
    # Compute FFT
    f = np.fft.fft2(gray)
    f_shift = np.fft.fftshift(f)
    magnitude = np.abs(f_shift)
    power_spectrum = np.log(magnitude + 1)
    
    # Find peaks (excluding DC component)
    cy, cx = h // 2, w // 2
    magnitude_copy = magnitude.copy()
    magnitude_copy[cy-5:cy+5, cx-5:cx+5] = 0  # Mask DC
    
    peaks = []
    for _ in range(num_peaks):
        y, x = np.unravel_index(np.argmax(magnitude_copy), magnitude_copy.shape)
        if magnitude_copy[y, x] < 1e-5:
            break
        
        r = np.sqrt((y - cy)**2 + (x - cx)**2)
        angle = np.degrees(np.arctan2(y - cy, x - cx))
        peaks.append({
            'radius': float(r),
            'angle': float(angle),
            'magnitude': float(magnitude_copy[y, x]),
            'x': int(x),
            'y': int(y)
        })
        
        # Mask region around peak
        magnitude_copy[max(0, y-3):min(h, y+3), max(0, x-3):min(w, x+3)] = 0
    
    # Fundamental period and orientation
    if peaks:
        fund_r = peaks[0]['radius']
        fund_period = min(h, w) / max(fund_r, 1e-5)
        fund_orientation = peaks[0]['angle']
    else:
        fund_period = 0
        fund_orientation = 0
    
    # Anisotropy ratio
    radial_profile = []
    for r in range(1, min(cx, cy)):
        mask = (((np.arange(h)[:, None] - cy)**2 + (np.arange(w) - cx)**2 < (r+1)**2) &
                ((np.arange(h)[:, None] - cy)**2 + (np.arange(w) - cx)**2 >= r**2))
        radial_profile.append(np.mean(magnitude[mask]) if mask.any() else 0)
    
    anisotropy = np.std(radial_profile) / (np.mean(radial_profile) + 1e-8) if radial_profile else 0
    
    # Optional notch filter
    residual = None
    if enable_notch and peaks:
        f_filtered = f_shift.copy()
        for peak in peaks[:3]:
            y = int(cy + peak['radius'] * np.sin(np.radians(peak['angle'])))
            x = int(cx + peak['radius'] * np.cos(np.radians(peak['angle'])))
            cv2.circle(f_filtered.real, (x, y), 10, 0, -1)
            cv2.circle(f_filtered.imag, (x, y), 10, 0, -1)
        
        f_ishift = np.fft.ifftshift(f_filtered)
        filtered = np.fft.ifft2(f_ishift)
        residual = np.abs(filtered).real
    
    return {
        'power_spectrum': power_spectrum,
        'peaks': peaks,
        'fundamental_period': float(fund_period),
        'fundamental_orientation': float(fund_orientation),
        'anisotropy': float(anisotropy),
        'residual': residual
    }

