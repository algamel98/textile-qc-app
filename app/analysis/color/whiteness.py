# -*- coding: utf-8 -*-
"""
Whiteness and yellowness calculations
"""
import numpy as np


def cie_whiteness_tint(xyz, illuminant='D65'):
    """
    CIE Whiteness and Tint (ISO 11475) for illuminant D65 with 10° observer.
    
    Args:
        xyz: XYZ array
        illuminant: Illuminant name (default D65)
        
    Returns:
        tuple: (Whiteness, Tint)
    """
    xyz = np.asarray(xyz, dtype=np.float64)
    
    X, Y, Z = xyz[..., 0], xyz[..., 1], xyz[..., 2]
    
    # Chromaticity coordinates
    sum_XYZ = np.maximum(X + Y + Z, 1e-8)
    x = X / sum_XYZ
    y = Y / sum_XYZ
    
    # CIE Whiteness (D65, 10°) - ISO 11475
    # Reference white point for D65/10°: xn=0.3138, yn=0.3310
    xn, yn = 0.3138, 0.3310
    W = Y + 800 * (xn - x) + 1700 * (yn - y)
    
    # Tint
    T = 900 * (xn - x) - 650 * (yn - y)
    
    return W, T


def astm_e313_yellowness(xyz):
    """
    ASTM E313 Yellowness Index.
    
    Args:
        xyz: XYZ array
        
    Returns:
        numpy.ndarray: Yellowness Index values
    """
    xyz = np.asarray(xyz, dtype=np.float64)
    
    X, Y, Z = xyz[..., 0], xyz[..., 1], xyz[..., 2]
    
    # Coefficients for D65/10° (newer standard)
    C_x = 1.3013
    C_z = 1.1498
    
    YI = 100 * (C_x * X - C_z * Z) / np.maximum(Y, 1e-8)
    
    return YI


def hunter_whiteness(xyz):
    """
    Hunter Whiteness Index.
    
    Args:
        xyz: XYZ array
        
    Returns:
        numpy.ndarray: Hunter Whiteness values
    """
    xyz = np.asarray(xyz, dtype=np.float64)
    
    X, Y, Z = xyz[..., 0], xyz[..., 1], xyz[..., 2]
    
    # Hunter L, a, b
    L = 10 * np.sqrt(Y)
    a = 17.5 * (1.02 * X - Y) / np.sqrt(np.maximum(Y, 1e-8))
    b = 7.0 * (Y - 0.847 * Z) / np.sqrt(np.maximum(Y, 1e-8))
    
    # Hunter Whiteness
    WI = L - 3 * b
    
    return WI


# Alias for compatibility
astm_yellowness = astm_e313_yellowness


def berger_whiteness(xyz):
    """
    Berger Whiteness Index.
    
    Args:
        xyz: XYZ array
        
    Returns:
        numpy.ndarray: Berger Whiteness values
    """
    xyz = np.asarray(xyz, dtype=np.float64)
    
    X, Y, Z = xyz[..., 0], xyz[..., 1], xyz[..., 2]
    
    # Berger formula
    WI = 3.388 * Z - 3 * Y
    
    return WI

