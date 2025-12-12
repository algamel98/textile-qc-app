# -*- coding: utf-8 -*-
"""
Color space conversion functions
"""
import numpy as np
from app.core.constants import SRGB_TO_XYZ_MATRIX, WHITE_POINTS


def srgb_to_xyz(rgb):
    """
    Convert sRGB to CIE XYZ (D65).
    
    Args:
        rgb: RGB array with values in [0, 1] or [0, 255]
        
    Returns:
        numpy.ndarray: XYZ values
    """
    rgb = np.asarray(rgb, dtype=np.float64)
    
    # Normalize if in 0-255 range
    if rgb.max() > 1.0:
        rgb = rgb / 255.0
    
    # Linearize sRGB (inverse gamma)
    linear = np.where(
        rgb <= 0.04045,
        rgb / 12.92,
        ((rgb + 0.055) / 1.055) ** 2.4
    )
    
    # Matrix multiplication
    xyz = np.tensordot(linear, SRGB_TO_XYZ_MATRIX.T, axes=([-1], [0]))
    
    return xyz


def xyz_to_lab(xyz, wp):
    """
    Convert XYZ to CIELAB.
    
    Args:
        xyz: XYZ array
        wp: White point array [Xn, Yn, Zn]
        
    Returns:
        numpy.ndarray: LAB values
    """
    xyz = np.asarray(xyz, dtype=np.float64)
    wp = np.asarray(wp, dtype=np.float64)
    
    # Normalize by white point
    xyz_n = xyz / wp
    
    def f(t):
        delta = 6 / 29
        return np.where(t > delta ** 3, t ** (1/3), t / (3 * delta ** 2) + 4 / 29)
    
    fx, fy, fz = f(xyz_n[..., 0]), f(xyz_n[..., 1]), f(xyz_n[..., 2])
    
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    
    return np.stack([L, a, b], axis=-1)


def lab_to_xyz(lab, wp):
    """
    Convert CIELAB to XYZ.
    
    Args:
        lab: LAB array
        wp: White point array
        
    Returns:
        numpy.ndarray: XYZ values
    """
    lab = np.asarray(lab, dtype=np.float64)
    wp = np.asarray(wp, dtype=np.float64)
    
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    
    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200
    
    delta = 6 / 29
    
    def f_inv(t):
        return np.where(t > delta, t ** 3, 3 * delta ** 2 * (t - 4 / 29))
    
    X = wp[0] * f_inv(fx)
    Y = wp[1] * f_inv(fy)
    Z = wp[2] * f_inv(fz)
    
    return np.stack([X, Y, Z], axis=-1)


def adapt_white_xyz(xyz, src_wp, dst_wp):
    """
    Bradford chromatic adaptation transform.
    
    Args:
        xyz: XYZ array
        src_wp: Source white point
        dst_wp: Destination white point
        
    Returns:
        numpy.ndarray: Adapted XYZ values
    """
    # Bradford matrix
    M = np.array([
        [ 0.8951,  0.2664, -0.1614],
        [-0.7502,  1.7135,  0.0367],
        [ 0.0389, -0.0685,  1.0296]
    ])
    M_inv = np.linalg.inv(M)
    
    # Convert white points to cone response
    src_lms = M @ src_wp
    dst_lms = M @ dst_wp
    
    # Scaling matrix
    scale = dst_lms / src_lms
    S = np.diag(scale)
    
    # Full transform matrix
    transform = M_inv @ S @ M
    
    return np.tensordot(xyz, transform.T, axes=([-1], [0]))


def rgb_to_cmyk(rgb):
    """
    Convert RGB to CMYK.
    
    Args:
        rgb: RGB array with values in [0, 1] or [0, 255]
        
    Returns:
        numpy.ndarray: CMYK values in [0, 1]
    """
    rgb = np.asarray(rgb, dtype=np.float64)
    
    # Normalize if in 0-255 range
    if rgb.max() > 1.0:
        rgb = rgb / 255.0
    
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    
    k = 1 - np.maximum(np.maximum(r, g), b)
    
    # Avoid division by zero
    denom = np.maximum(1 - k, 1e-10)
    
    c = (1 - r - k) / denom
    m = (1 - g - k) / denom
    y = (1 - b - k) / denom
    
    return np.stack([c, m, y, k], axis=-1)


def cmyk_to_rgb(cmyk):
    """
    Convert CMYK to RGB.
    
    Args:
        cmyk: CMYK array with values in [0, 1]
        
    Returns:
        numpy.ndarray: RGB values in [0, 1]
    """
    cmyk = np.asarray(cmyk, dtype=np.float64)
    
    c, m, y, k = cmyk[..., 0], cmyk[..., 1], cmyk[..., 2], cmyk[..., 3]
    
    r = (1 - c) * (1 - k)
    g = (1 - m) * (1 - k)
    b = (1 - y) * (1 - k)
    
    return np.stack([r, g, b], axis=-1)

