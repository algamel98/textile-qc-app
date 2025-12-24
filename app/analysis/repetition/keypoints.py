# -*- coding: utf-8 -*-
"""
Keypoint-based pattern matching
"""
import numpy as np
import cv2
from skimage.util import img_as_ubyte


def analyze_keypoint_matching(gray_ref, gray_test, detector_type='ORB', match_threshold=0.7):
    """
    Match patterns using keypoint detection (SIFT, ORB, AKAZE).
    
    Args:
        gray_ref: Reference grayscale image
        gray_test: Test grayscale image
        detector_type: Detector type ('SIFT', 'ORB', 'AKAZE')
        match_threshold: Lowe's ratio test threshold
        
    Returns:
        dict: Keypoint matching results
    """
    try:
        # Convert to 8-bit
        gray_ref_8bit = img_as_ubyte(gray_ref)
        gray_test_8bit = img_as_ubyte(gray_test)
        
        # Create detector based on type
        if detector_type == 'SIFT':
            try:
                detector = cv2.SIFT_create()
            except AttributeError:
                detector = cv2.xfeatures2d.SIFT_create()
        elif detector_type == 'AKAZE':
            detector = cv2.AKAZE_create()
        else:  # ORB (default, patent-free)
            detector = cv2.ORB_create(nfeatures=1000)
        
        # Detect keypoints and compute descriptors
        kp_ref, desc_ref = detector.detectAndCompute(gray_ref_8bit, None)
        kp_test, desc_test = detector.detectAndCompute(gray_test_8bit, None)
        
        if desc_ref is None or desc_test is None or len(kp_ref) == 0 or len(kp_test) == 0:
            return {
                'keypoints_ref': [],
                'keypoints_test': [],
                'matches': [],
                'good_matches': [],
                'match_count': 0,
                'match_ratio': 0.0,
                'homography': None,
                'inliers': 0,
                'matching_score': 0.0
            }
        
        # Match descriptors
        if detector_type == 'ORB':
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        else:
            bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        
        matches = bf.knnMatch(desc_ref, desc_test, k=2)
        
        # Apply ratio test (Lowe's ratio test)
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < match_threshold * n.distance:
                    good_matches.append(m)
        
        match_ratio = len(good_matches) / len(kp_ref) if len(kp_ref) > 0 else 0
        
        # Compute homography if enough matches
        homography = None
        inliers = 0
        if len(good_matches) >= 4:
            src_pts = np.float32([kp_ref[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp_test[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            
            homography, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            inliers = int(np.sum(mask)) if mask is not None else 0
        
        # Matching score based on inliers and match ratio
        matching_score = (match_ratio * 50 + (inliers / max(len(good_matches), 1)) * 50) if good_matches else 0
        
        return {
            'keypoints_ref': kp_ref,
            'keypoints_test': kp_test,
            'matches': matches,
            'good_matches': good_matches,
            'match_count': len(good_matches),
            'match_ratio': float(match_ratio),
            'homography': homography,
            'inliers': inliers,
            'matching_score': float(matching_score)
        }
        
    except Exception as e:
        print(f"⚠️ Keypoint matching failed: {e}")
        return {
            'keypoints_ref': [],
            'keypoints_test': [],
            'matches': [],
            'good_matches': [],
            'match_count': 0,
            'match_ratio': 0.0,
            'homography': None,
            'inliers': 0,
            'matching_score': 0.0
        }

