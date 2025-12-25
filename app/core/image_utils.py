# -*- coding: utf-8 -*-
"""
Image utility functions for Textile QC System
"""
import os
import logging
import numpy as np
import cv2
from PIL import Image

logger = logging.getLogger(__name__)


def validate_image_file(path):
    """
    Validate that a file is a readable image.
    
    Args:
        path: Path to the image file
        
    Returns:
        bool: True if valid, raises ValueError otherwise
    """
    if not os.path.exists(path):
        raise ValueError(f"File not found: {path}")
    
    valid_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp'}
    ext = os.path.splitext(path)[1].lower()
    if ext not in valid_extensions:
        raise ValueError(f"Invalid image format: {ext}. Supported: {valid_extensions}")
    
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception as e:
        raise ValueError(f"Cannot read image file: {str(e)}")


def validate_image_dimensions(img, min_size=100, max_size=10000):
    """
    Validate image dimensions are within acceptable range.
    
    Args:
        img: Image array (H, W, C) or (H, W)
        min_size: Minimum dimension size
        max_size: Maximum dimension size
        
    Returns:
        bool: True if valid, raises ValueError otherwise
    """
    h, w = img.shape[:2]
    if h < min_size or w < min_size:
        raise ValueError(f"Image too small: {w}x{h}. Minimum size: {min_size}x{min_size}")
    if h > max_size or w > max_size:
        raise ValueError(f"Image too large: {w}x{h}. Maximum size: {max_size}x{max_size}")
    return True


def read_rgb(path):
    """
    Read an image and convert to RGB numpy array.
    
    Args:
        path: Path to the image file
        
    Returns:
        numpy.ndarray: RGB image as float32 in range [0, 1]
    """
    validate_image_file(path)
    
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Failed to read image: {path}")
    
    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Convert to float32 [0, 1]
    img = img.astype(np.float32) / 255.0
    
    validate_image_dimensions(img)
    logger.info(f"Loaded image: {path} ({img.shape[1]}x{img.shape[0]})")
    
    return img


def to_same_size(a, b):
    """
    Resize images to the same dimensions (minimum of both).
    
    Args:
        a: First image array
        b: Second image array
        
    Returns:
        tuple: (resized_a, resized_b)
    """
    h = min(a.shape[0], b.shape[0])
    w = min(a.shape[1], b.shape[1])
    
    a_resized = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA)
    b_resized = cv2.resize(b, (w, h), interpolation=cv2.INTER_AREA)
    
    return a_resized, b_resized


def apply_mask_to_image(img, mask):
    """Apply a binary mask to an image"""
    if len(img.shape) == 3:
        mask_3d = np.stack([mask] * 3, axis=-1)
        return img * mask_3d
    return img * mask


def apply_circular_crop(img, center_x, center_y, diameter):
    """Apply circular crop to image"""
    h, w = img.shape[:2]
    Y, X = np.ogrid[:h, :w]
    radius = diameter / 2
    dist = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
    mask = (dist <= radius).astype(np.float32)
    return apply_mask_to_image(img, mask)


def apply_rectangular_crop(img, center_x, center_y, width, height):
    """Apply rectangular crop to image"""
    h, w = img.shape[:2]
    x1 = max(0, int(center_x - width // 2))
    x2 = min(w, int(center_x + width // 2))
    y1 = max(0, int(center_y - height // 2))
    y2 = min(h, int(center_y + height // 2))
    
    mask = np.zeros((h, w), dtype=np.float32)
    mask[y1:y2, x1:x2] = 1.0
    return apply_mask_to_image(img, mask)


def apply_crop(img, settings, is_test_image=False):
    """
    Apply crop based on settings.
    
    Args:
        img: Image array
        settings: QCSettings object
        is_test_image: Whether this is the test/sample image
        
    Returns:
        numpy.ndarray: Cropped image
    """
    if not settings.use_crop:
        return img
    
    # Determine which position to use
    if settings.crop_mode == "simultaneous" or not is_test_image:
        cx = settings.crop_center_x
        cy = settings.crop_center_y
        diameter = settings.crop_diameter
        width = settings.crop_width
        height = settings.crop_height
    else:
        cx = settings.crop_test_center_x
        cy = settings.crop_test_center_y
        diameter = settings.crop_test_diameter
        width = settings.crop_test_width
        height = settings.crop_test_height
    
    if settings.crop_shape == "circle":
        return apply_circular_crop(img, cx, cy, diameter)
    else:
        return apply_rectangular_crop(img, cx, cy, width, height)


def draw_circle_on_image(img, center_x, center_y, diameter, color=(255, 0, 0), thickness=3):
    """Draw a circle overlay on image for visualization"""
    img_copy = (img * 255).astype(np.uint8).copy()
    radius = int(diameter / 2)
    cv2.circle(img_copy, (int(center_x), int(center_y)), radius, color, thickness)
    return img_copy


def draw_rectangle_on_image(img, center_x, center_y, width, height, color=(255, 0, 0), thickness=3):
    """Draw a rectangle overlay on image for visualization"""
    img_copy = (img * 255).astype(np.uint8).copy()
    x1 = int(center_x - width // 2)
    y1 = int(center_y - height // 2)
    x2 = int(center_x + width // 2)
    y2 = int(center_y + height // 2)
    cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, thickness)
    return img_copy


def grid_points(h, w, n=5):
    """
    Generate n sample points in a grid pattern.
    
    Args:
        h: Image height
        w: Image width
        n: Number of points
        
    Returns:
        list: List of (y, x) tuples
    """
    margin_y = h // 6
    margin_x = w // 6
    inner_h = h - 2 * margin_y
    inner_w = w - 2 * margin_x
    
    pts = []
    if n == 1:
        pts.append((h // 2, w // 2))
    elif n <= 4:
        step_y = inner_h // 2
        step_x = inner_w // 2
        for i in range(2):
            for j in range(2):
                if len(pts) < n:
                    pts.append((margin_y + i * step_y, margin_x + j * step_x))
    else:
        # 5+ points: center + corners
        pts.append((h // 2, w // 2))  # Center
        pts.append((margin_y, margin_x))  # Top-left
        pts.append((margin_y, w - margin_x))  # Top-right
        pts.append((h - margin_y, margin_x))  # Bottom-left
        pts.append((h - margin_y, w - margin_x))  # Bottom-right
        
        # Add more points if needed
        while len(pts) < n:
            pts.append((
                np.random.randint(margin_y, h - margin_y),
                np.random.randint(margin_x, w - margin_x)
            ))
    
    return pts[:n]


def overlay_regions(img, pts, radius=12):
    """
    Draw sample region circles on image.
    
    Args:
        img: Image array (float32, 0-1)
        pts: List of (y, x) points
        radius: Circle radius
        
    Returns:
        numpy.ndarray: Image with overlays (uint8)
    """
    img_uint8 = (img * 255).astype(np.uint8).copy()
    
    for i, (y, x) in enumerate(pts):
        # Draw circle
        cv2.circle(img_uint8, (int(x), int(y)), radius, (255, 0, 0), 2)
        # Draw label
        cv2.putText(img_uint8, str(i + 1), (int(x) + radius + 2, int(y) + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    
    return img_uint8


def ensure_dir(path):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)
    return path

