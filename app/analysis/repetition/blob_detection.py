# -*- coding: utf-8 -*-
"""
Blob detection for pattern analysis
"""
import numpy as np
import cv2
from skimage.util import img_as_ubyte


def analyze_blob_patterns(gray, min_area=100, max_area=5000, min_circularity=0.5, min_convexity=0.8):
    """
    Detect repeating patterns using blob detection.
    
    Args:
        gray: Grayscale image (float32, 0-1)
        min_area: Minimum blob area
        max_area: Maximum blob area
        min_circularity: Minimum circularity (0-1)
        min_convexity: Minimum convexity (0-1)
        
    Returns:
        dict: Blob detection results
    """
    try:
        # Convert to 8-bit
        gray_8bit = img_as_ubyte(gray)
        
        # Setup SimpleBlobDetector parameters
        params = cv2.SimpleBlobDetector_Params()
        
        # Filter by Area
        params.filterByArea = True
        params.minArea = min_area
        params.maxArea = max_area
        
        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = min_circularity
        
        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = min_convexity
        
        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0.01
        
        # Create detector
        detector = cv2.SimpleBlobDetector_create(params)
        
        # Detect blobs
        keypoints = detector.detect(gray_8bit)
        
        # Extract blob properties
        blobs = []
        for kp in keypoints:
            blobs.append({
                'center': (int(kp.pt[0]), int(kp.pt[1])),
                'size': float(kp.size),
                'area': float(np.pi * (kp.size / 2) ** 2)
            })
        
        # Calculate statistics
        if blobs:
            areas = [b['area'] for b in blobs]
            sizes = [b['size'] for b in blobs]
            mean_area = float(np.mean(areas))
            std_area = float(np.std(areas))
            cv_area = float((std_area / mean_area * 100) if mean_area > 0 else 0)
            mean_size = float(np.mean(sizes))
            std_size = float(np.std(sizes))
        else:
            mean_area = std_area = cv_area = mean_size = std_size = 0.0
        
        return {
            'blobs': blobs,
            'count': len(blobs),
            'keypoints': keypoints,
            'mean_area': mean_area,
            'std_area': std_area,
            'cv_area': cv_area,
            'mean_size': mean_size,
            'std_size': std_size
        }
        
    except Exception as e:
        print(f"⚠️ Blob detection failed: {e}")
        return {
            'blobs': [],
            'count': 0,
            'keypoints': [],
            'mean_area': 0.0,
            'std_area': 0.0,
            'cv_area': 0.0,
            'mean_size': 0.0,
            'std_size': 0.0
        }

