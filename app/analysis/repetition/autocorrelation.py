# -*- coding: utf-8 -*-
"""
Autocorrelation analysis for pattern repetition detection
"""
import numpy as np
from scipy import signal


def analyze_autocorrelation(gray):
    """
    Analyze pattern repetition using autocorrelation.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        
    Returns:
        dict: Autocorrelation analysis results
    """
    try:
        # Compute 2D autocorrelation
        autocorr = signal.correlate2d(gray, gray, mode='same', boundary='wrap')
        
        # Normalize
        autocorr = autocorr / autocorr.max()
        
        h, w = autocorr.shape
        cy, cx = h // 2, w // 2
        
        # Find peaks (excluding center)
        peaks = []
        threshold = 0.3  # Minimum correlation threshold
        window = 5  # Window for local maxima detection
        
        for y in range(window, h - window):
            for x in range(window, w - window):
                if y == cy and x == cx:
                    continue
                    
                val = autocorr[y, x]
                if val < threshold:
                    continue
                
                # Check if local maximum
                local_region = autocorr[y-window:y+window+1, x-window:x+window+1]
                if val >= local_region.max():
                    # Calculate distance from center (period)
                    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                    angle = np.degrees(np.arctan2(y - cy, x - cx))
                    
                    peaks.append({
                        'x': int(x),
                        'y': int(y),
                        'correlation': float(val),
                        'period': float(dist),
                        'angle': float(angle)
                    })
        
        # Sort by correlation strength
        peaks.sort(key=lambda p: p['correlation'], reverse=True)
        peaks = peaks[:10]  # Keep top 10 peaks
        
        # Find primary period (strongest peak)
        if peaks:
            primary_peak = peaks[0]
            primary_period = primary_peak['period']
            primary_angle = primary_peak['angle']
            peak_strength = primary_peak['correlation']
        else:
            primary_period = 0.0
            primary_angle = 0.0
            peak_strength = 0.0
        
        # Calculate periodicity score
        if peaks:
            periodicity_score = float(np.mean([p['correlation'] for p in peaks]) * 100)
        else:
            periodicity_score = 0.0
        
        return {
            'autocorr': autocorr,
            'peaks': peaks,
            'primary_period': float(primary_period),
            'primary_angle': float(primary_angle),
            'peak_strength': float(peak_strength),
            'periodicity_score': periodicity_score
        }
        
    except Exception as e:
        print(f"Warning: Autocorrelation analysis failed: {e}")
        return {
            'autocorr': np.zeros((10, 10)),
            'peaks': [],
            'primary_period': 0.0,
            'primary_angle': 0.0,
            'peak_strength': 0.0,
            'periodicity_score': 0.0
        }

