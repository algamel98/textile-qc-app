# -*- coding: utf-8 -*-
"""
Plotting functions for visualization
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2


def save_fig(path):
    """Save current figure to file"""
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_rgb_hist(img_rgb, title, path):
    """Plot RGB histogram"""
    fig, ax = plt.subplots(figsize=(6, 3))
    
    for i, (color, name) in enumerate(zip(['red', 'green', 'blue'], ['R', 'G', 'B'])):
        channel = img_rgb[..., i].flatten()
        if channel.max() <= 1:
            channel = channel * 255
        ax.hist(channel, bins=64, color=color, alpha=0.6, label=name)
    
    ax.set_xlabel('Pixel Value')
    ax.set_ylabel('Frequency')
    ax.set_title(title)
    ax.legend()
    ax.set_xlim(0, 255)
    
    save_fig(path)


def plot_heatmap(de_map, title, path):
    """Plot delta E heatmap"""
    fig, ax = plt.subplots(figsize=(6, 5))
    
    im = ax.imshow(de_map, cmap='RdYlGn_r', vmin=0, vmax=max(5, de_map.max()))
    plt.colorbar(im, ax=ax, label='ΔE')
    ax.set_title(title)
    ax.axis('off')
    
    save_fig(path)


def plot_spectral_proxy(mean_rgb_ref, mean_rgb_test, path):
    """Plot proxy spectral curves from RGB"""
    wl = np.linspace(380, 700, 161)
    
    def gaussian(w, mu, sigma):
        return np.exp(-0.5 * ((w - mu) / sigma) ** 2)
    
    # Create proxy spectra
    spec_ref = (mean_rgb_ref[0] * gaussian(wl, 620, 30) +
                mean_rgb_ref[1] * gaussian(wl, 530, 30) +
                mean_rgb_ref[2] * gaussian(wl, 450, 30))
    
    spec_test = (mean_rgb_test[0] * gaussian(wl, 620, 30) +
                 mean_rgb_test[1] * gaussian(wl, 530, 30) +
                 mean_rgb_test[2] * gaussian(wl, 450, 30))
    
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(wl, spec_ref / max(spec_ref.max(), 1), 'b-', label='Reference', linewidth=2)
    ax.plot(wl, spec_test / max(spec_test.max(), 1), 'r--', label='Sample', linewidth=2)
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Relative Intensity')
    ax.set_title('Proxy Spectral Reflectance')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    save_fig(path)


def plot_ab_scatter(lab_ref, lab_test, path):
    """Plot a*b* scatter diagram"""
    fig, ax = plt.subplots(figsize=(5, 5))
    
    # Flatten and subsample if needed
    a_ref = lab_ref[..., 1].flatten()[::100]
    b_ref = lab_ref[..., 2].flatten()[::100]
    a_test = lab_test[..., 1].flatten()[::100]
    b_test = lab_test[..., 2].flatten()[::100]
    
    ax.scatter(a_ref, b_ref, c='blue', alpha=0.3, s=5, label='Reference')
    ax.scatter(a_test, b_test, c='red', alpha=0.3, s=5, label='Sample')
    
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('a* (green-red)')
    ax.set_ylabel('b* (blue-yellow)')
    ax.set_title('a*b* Chromaticity Diagram')
    ax.legend()
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    save_fig(path)


def plot_lab_bars(lab_ref_mean, lab_test_mean, path):
    """Plot LAB comparison bar chart"""
    fig, ax = plt.subplots(figsize=(6, 4))
    
    labels = ['L*', 'a*', 'b*']
    x = np.arange(len(labels))
    width = 0.35
    
    ax.bar(x - width/2, lab_ref_mean, width, label='Reference', color='#3498DB')
    ax.bar(x + width/2, lab_test_mean, width, label='Sample', color='#E74C3C')
    
    ax.set_xlabel('Component')
    ax.set_ylabel('Value')
    ax.set_title('LAB* Component Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    save_fig(path)


def plot_fft_power_spectrum(power_spectrum, peaks, path):
    """Plot FFT power spectrum with peaks"""
    fig, ax = plt.subplots(figsize=(6, 5))
    
    ax.imshow(power_spectrum, cmap='viridis')
    
    for i, peak in enumerate(peaks[:5]):
        ax.plot(peak['x'], peak['y'], 'ro', markersize=8)
        ax.annotate(f"P{i+1}", (peak['x'], peak['y']), 
                   xytext=(5, 5), textcoords='offset points',
                   color='white', fontsize=8)
    
    ax.set_title('FFT Power Spectrum')
    ax.axis('off')
    
    save_fig(path)


def plot_gabor_montage(energy_maps, frequencies, num_orientations, path):
    """Plot Gabor filter bank responses"""
    n_freq = len(frequencies)
    fig, axes = plt.subplots(n_freq, num_orientations, figsize=(12, 4))
    
    if n_freq == 1:
        axes = axes.reshape(1, -1)
    
    for i, freq in enumerate(frequencies):
        for j in range(num_orientations):
            idx = i * num_orientations + j
            if idx < len(energy_maps):
                axes[i, j].imshow(energy_maps[idx], cmap='hot')
                axes[i, j].axis('off')
                if i == 0:
                    axes[i, j].set_title(f'{j * 180 // num_orientations}°', fontsize=8)
        axes[i, 0].set_ylabel(f'f={freq}', fontsize=8)
    
    plt.suptitle('Gabor Filter Bank Responses')
    plt.tight_layout()
    
    save_fig(path)


def plot_gabor_orientation_histogram(gabor_results, path):
    """Plot Gabor orientation histogram"""
    fig, ax = plt.subplots(figsize=(6, 4), subplot_kw={'projection': 'polar'})
    
    results = gabor_results['results']
    orientations = [r['orientation_deg'] for r in results]
    energies = [r['mean'] for r in results]
    
    # Group by orientation
    unique_orientations = sorted(set(orientations))
    mean_energies = []
    for orient in unique_orientations:
        energy = np.mean([e for o, e in zip(orientations, energies) if o == orient])
        mean_energies.append(energy)
    
    angles = np.radians(unique_orientations + [unique_orientations[0]])
    values = mean_energies + [mean_energies[0]]
    
    ax.plot(angles, values, 'b-', linewidth=2)
    ax.fill(angles, values, alpha=0.3)
    ax.set_title('Gabor Orientation Response')
    
    save_fig(path)


def plot_glcm_radar(glcm_props_ref, glcm_props_sample, path):
    """Plot GLCM properties radar chart"""
    categories = ['contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation']
    
    # Normalize values
    values_ref = []
    values_test = []
    
    for cat in categories:
        ref_val = glcm_props_ref.get(cat, 0)
        test_val = glcm_props_sample.get(cat, 0)
        max_val = max(ref_val, test_val, 1e-10)
        values_ref.append(ref_val / max_val)
        values_test.append(test_val / max_val)
    
    # Close the radar
    values_ref += [values_ref[0]]
    values_test += [values_test[0]]
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += [angles[0]]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    
    ax.plot(angles, values_ref, 'b-', linewidth=2, label='Reference')
    ax.fill(angles, values_ref, alpha=0.25, color='blue')
    ax.plot(angles, values_test, 'r-', linewidth=2, label='Sample')
    ax.fill(angles, values_test, alpha=0.25, color='red')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_title('GLCM Properties Comparison')
    ax.legend(loc='upper right')
    
    save_fig(path)


def plot_lbp_map_and_hist(lbp_map, hist_ref, hist_sample, path):
    """Plot LBP map and histogram comparison"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    ax1.imshow(lbp_map, cmap='gray')
    ax1.set_title('LBP Map (Sample)')
    ax1.axis('off')
    
    x = np.arange(len(hist_ref))
    ax2.bar(x - 0.2, hist_ref, 0.4, label='Reference', alpha=0.7)
    ax2.bar(x + 0.2, hist_sample, 0.4, label='Sample', alpha=0.7)
    ax2.set_xlabel('LBP Pattern')
    ax2.set_ylabel('Normalized Frequency')
    ax2.set_title('LBP Histogram Comparison')
    ax2.legend()
    
    save_fig(path)


def plot_wavelet_energy_bars(energies_ref, energies_sample, path):
    """Plot wavelet energy distribution comparison"""
    fig, ax = plt.subplots(figsize=(8, 4))
    
    levels = len(energies_ref)
    x = np.arange(levels)
    width = 0.35
    
    lh_ref = [e['LH'] for e in energies_ref]
    lh_test = [e['LH'] for e in energies_sample]
    
    ax.bar(x - width/2, lh_ref, width, label='Reference', color='#3498DB')
    ax.bar(x + width/2, lh_test, width, label='Sample', color='#E74C3C')
    
    ax.set_xlabel('Decomposition Level')
    ax.set_ylabel('Energy')
    ax.set_title('Wavelet LH (Horizontal Detail) Energy')
    ax.set_xticks(x)
    ax.set_xticklabels([f'Level {i+1}' for i in range(levels)])
    ax.legend()
    
    save_fig(path)


def plot_defect_saliency(saliency_map, binary_map, defects, original_shape, path):
    """Plot defect detection results"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    ax1.imshow(saliency_map, cmap='hot')
    ax1.set_title('Saliency Map')
    ax1.axis('off')
    
    ax2.imshow(binary_map, cmap='gray')
    for defect in defects[:20]:  # Show up to 20 defects
        cx, cy = defect['centroid']
        ax2.plot(cx, cy, 'r+', markersize=10, markeredgewidth=2)
    ax2.set_title(f'Detected Defects (n={len(defects)})')
    ax2.axis('off')
    
    save_fig(path)


def plot_metamerism_illuminants(illuminants, delta_e_values, path):
    """Plot metamerism under different illuminants"""
    fig, ax = plt.subplots(figsize=(8, 4))
    
    colors = ['#3498DB', '#E74C3C', '#27AE60', '#F39C12', '#9B59B6', '#1ABC9C']
    
    bars = ax.bar(illuminants, delta_e_values, color=colors[:len(illuminants)])
    
    # Add threshold lines
    ax.axhline(2.0, color='green', linestyle='--', label='Pass threshold')
    ax.axhline(3.5, color='orange', linestyle='--', label='Conditional threshold')
    
    ax.set_xlabel('Illuminant')
    ax.set_ylabel('ΔE2000')
    ax.set_title('Color Difference Under Different Illuminants')
    ax.legend()
    
    # Add value labels
    for bar, val in zip(bars, delta_e_values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
               f'{val:.2f}', ha='center', va='bottom', fontsize=9)
    
    save_fig(path)


def plot_spectral_curve(wavelengths, reflectance_ref, reflectance_sample, path):
    """Plot spectral reflectance curves"""
    fig, ax = plt.subplots(figsize=(8, 4))
    
    ax.plot(wavelengths, reflectance_ref, 'b-', linewidth=2, label='Reference')
    ax.plot(wavelengths, reflectance_sample, 'r--', linewidth=2, label='Sample')
    
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Reflectance (%)')
    ax.set_title('Spectral Reflectance Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(380, 700)
    
    save_fig(path)


def plot_line_angle_histogram(orientation_degrees, path):
    """Plot orientation angle histogram"""
    fig, ax = plt.subplots(figsize=(6, 4))
    
    ax.hist(orientation_degrees.flatten(), bins=36, range=(-90, 90), 
            color='#3498DB', edgecolor='white')
    ax.set_xlabel('Angle (degrees)')
    ax.set_ylabel('Frequency')
    ax.set_title('Line Orientation Distribution')
    ax.set_xlim(-90, 90)
    
    save_fig(path)


def plot_pattern_detection_map(img_rgb, patterns, title, path):
    """Plot detected patterns on image"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if img_rgb.max() <= 1:
        img_rgb = (img_rgb * 255).astype(np.uint8)
    
    ax.imshow(img_rgb)
    
    for pattern in patterns[:50]:  # Limit to 50 patterns
        cx, cy = pattern['centroid']
        ax.plot(cx, cy, 'r+', markersize=8, markeredgewidth=2)
        
        if 'bbox' in pattern:
            x0, y0, x1, y1 = pattern['bbox']
            rect = plt.Rectangle((x0, y0), x1-x0, y1-y0,
                                fill=False, edgecolor='red', linewidth=1)
            ax.add_patch(rect)
    
    ax.set_title(f'{title} (n={len(patterns)})')
    ax.axis('off')
    
    save_fig(path)


def plot_pattern_count_comparison(count_ref, count_test, path):
    """Plot pattern count comparison"""
    fig, ax = plt.subplots(figsize=(5, 4))
    
    categories = ['Reference', 'Sample']
    counts = [count_ref, count_test]
    colors = ['#3498DB', '#E74C3C']
    
    bars = ax.bar(categories, counts, color=colors)
    
    # Add value labels
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
               str(count), ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Pattern Count')
    ax.set_title('Pattern Count Comparison')
    
    # Add difference annotation
    diff = count_test - count_ref
    diff_text = f'+{diff}' if diff > 0 else str(diff)
    ax.annotate(f'Difference: {diff_text}', xy=(0.5, 0.95), xycoords='axes fraction',
               ha='center', fontsize=10, color='gray')
    
    save_fig(path)


def plot_pattern_density_heatmap(density_grid, path):
    """Plot pattern density heatmap"""
    fig, ax = plt.subplots(figsize=(6, 5))
    
    im = ax.imshow(density_grid, cmap='YlOrRd', interpolation='nearest')
    plt.colorbar(im, ax=ax, label='Pattern Count')
    ax.set_title('Pattern Density Distribution')
    ax.set_xlabel('Grid X')
    ax.set_ylabel('Grid Y')
    
    save_fig(path)


def plot_missing_extra_patterns(img_rgb, missing_patterns, extra_patterns, path):
    """Plot missing and extra patterns"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if img_rgb.max() <= 1:
        img_rgb = (img_rgb * 255).astype(np.uint8)
    
    ax.imshow(img_rgb)
    
    # Plot missing patterns (blue)
    for pattern in missing_patterns[:20]:
        cx, cy = pattern['centroid']
        circle = plt.Circle((cx, cy), 15, fill=False, 
                           edgecolor='blue', linewidth=2, linestyle='--')
        ax.add_patch(circle)
    
    # Plot extra patterns (red)
    for pattern in extra_patterns[:20]:
        cx, cy = pattern['centroid']
        circle = plt.Circle((cx, cy), 15, fill=False,
                           edgecolor='red', linewidth=2)
        ax.add_patch(circle)
    
    ax.set_title(f'Missing: {len(missing_patterns)} (blue), Extra: {len(extra_patterns)} (red)')
    ax.axis('off')
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='blue', linestyle='--', label=f'Missing ({len(missing_patterns)})'),
        Line2D([0], [0], color='red', label=f'Extra ({len(extra_patterns)})')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    save_fig(path)


def plot_pattern_size_distribution(areas_ref, areas_test, path):
    """Plot pattern size distribution comparison"""
    fig, ax = plt.subplots(figsize=(6, 4))
    
    if len(areas_ref) > 0:
        ax.hist(areas_ref, bins=20, alpha=0.6, label='Reference', color='#3498DB')
    if len(areas_test) > 0:
        ax.hist(areas_test, bins=20, alpha=0.6, label='Sample', color='#E74C3C')
    
    ax.set_xlabel('Pattern Area (pixels)')
    ax.set_ylabel('Frequency')
    ax.set_title('Pattern Size Distribution')
    ax.legend()
    
    save_fig(path)


def plot_autocorrelation_surface(autocorr, peaks, path):
    """Plot autocorrelation surface with peaks"""
    fig, ax = plt.subplots(figsize=(6, 5))
    
    ax.imshow(autocorr, cmap='viridis')
    
    for i, peak in enumerate(peaks[:5]):
        ax.plot(peak['x'], peak['y'], 'ro', markersize=8)
        ax.annotate(f"P{i+1}\n{peak['period']:.0f}px", 
                   (peak['x'], peak['y']),
                   xytext=(5, 5), textcoords='offset points',
                   color='white', fontsize=8)
    
    ax.set_title('Autocorrelation Surface')
    ax.axis('off')
    
    save_fig(path)


def plot_keypoint_matching(img_ref, img_test, kp_ref, kp_test, good_matches, path):
    """Plot keypoint matches between images"""
    # Convert images
    if img_ref.max() <= 1:
        img_ref = (img_ref * 255).astype(np.uint8)
    if img_test.max() <= 1:
        img_test = (img_test * 255).astype(np.uint8)
    
    # Draw matches
    img_matches = cv2.drawMatches(
        img_ref, kp_ref, img_test, kp_test,
        good_matches[:50], None,
        matchColor=(0, 255, 0),
        singlePointColor=(255, 0, 0),
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.imshow(img_matches)
    ax.set_title(f'Keypoint Matches ({len(good_matches)} matches)')
    ax.axis('off')
    
    save_fig(path)


def plot_blob_detection(img_rgb, keypoints, path):
    """Plot blob detection results"""
    if img_rgb.max() <= 1:
        img_rgb = (img_rgb * 255).astype(np.uint8)
    
    img_with_blobs = cv2.drawKeypoints(
        img_rgb, keypoints, None,
        (255, 0, 0),
        cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    )
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(img_with_blobs)
    ax.set_title(f'Blob Detection ({len(keypoints)} blobs)')
    ax.axis('off')
    
    save_fig(path)


def plot_pattern_integrity_radar(integrity_data_ref, integrity_data_test, path):
    """Plot pattern integrity radar chart"""
    categories = ['Size\nConsistency', 'Shape\nConsistency', 'Position\nConsistency']
    
    values_ref = [100, 100, 100]  # Reference is always 100%
    values_test = [
        integrity_data_test.get('size_consistency', 0),
        integrity_data_test.get('shape_consistency', 0),
        integrity_data_test.get('position_consistency', 0)
    ]
    
    # Close the radar
    values_ref += [values_ref[0]]
    values_test += [values_test[0]]
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += [angles[0]]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    
    ax.plot(angles, values_ref, 'b-', linewidth=2, label='Reference')
    ax.fill(angles, values_ref, alpha=0.1, color='blue')
    ax.plot(angles, values_test, 'r-', linewidth=2, label='Sample')
    ax.fill(angles, values_test, alpha=0.25, color='red')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 100)
    ax.set_title('Pattern Integrity Assessment')
    ax.legend(loc='upper right')
    
    save_fig(path)

