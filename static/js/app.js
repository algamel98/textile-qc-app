/**
 * Textile QC System - Main Application JavaScript
 * Version 2.0.0 - Light Theme Edition
 */

// ==========================================
// Global State
// ==========================================
const state = {
    sessionId: null,
    refImage: null,
    testImage: null,
    refImageData: null,
    testImageData: null,
    settings: {},
    shapeType: 'circle',
    shapeSize: 100,
    processFullImage: false,
    minShapeSize: 20,
    maxShapeSize: 500,
    pdfFilename: null
};

// ==========================================
// DOM Elements
// ==========================================
const elements = {};

// ==========================================
// Initialization
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    initElements();
    initUploadHandlers();
    initShapeControls();
    initButtonHandlers();
    initModalHandlers();
    loadDefaultSettings();
});

function initElements() {
    // Panels
    elements.refPanel = document.getElementById('refPanel');
    elements.testPanel = document.getElementById('testPanel');
    elements.refPanelContent = document.getElementById('refPanelContent');
    elements.testPanelContent = document.getElementById('testPanelContent');
    elements.refPlaceholder = document.getElementById('refPlaceholder');
    elements.testPlaceholder = document.getElementById('testPlaceholder');
    
    // Inputs
    elements.refInput = document.getElementById('refInput');
    elements.testInput = document.getElementById('testInput');
    
    // Canvases
    elements.refCanvas = document.getElementById('refCanvas');
    elements.testCanvas = document.getElementById('testCanvas');
    
    // Overlays
    elements.refOverlay = document.getElementById('refOverlay');
    elements.testOverlay = document.getElementById('testOverlay');
    
    // Info
    elements.refInfo = document.getElementById('refInfo');
    elements.testInfo = document.getElementById('testInfo');
    
    // Shape Controls
    elements.circleOption = document.getElementById('circleOption');
    elements.squareOption = document.getElementById('squareOption');
    elements.fullImageOption = document.getElementById('fullImageOption');
    elements.processFullImage = document.getElementById('processFullImage');
    elements.sizeSliderContainer = document.getElementById('sizeSliderContainer');
    elements.shapeSize = document.getElementById('shapeSize');
    elements.sizeValue = document.getElementById('sizeValue');
    
    // Buttons
    elements.btnAdvancedSettings = document.getElementById('btnAdvancedSettings');
    elements.btnStartProcessing = document.getElementById('btnStartProcessing');
    elements.btnDeleteImages = document.getElementById('btnDeleteImages');
    elements.btnDownload = document.getElementById('btnDownload');
    elements.btnDownloadSettings = document.getElementById('btnDownloadSettings');
    
    // Results
    elements.resultsSection = document.getElementById('resultsSection');
    elements.decisionBadge = document.getElementById('decisionBadge');
    elements.colorScore = document.getElementById('colorScore');
    elements.patternScore = document.getElementById('patternScore');
    elements.overallScore = document.getElementById('overallScore');
    elements.colorBar = document.getElementById('colorBar');
    elements.patternBar = document.getElementById('patternBar');
    elements.overallBar = document.getElementById('overallBar');
    
    // Loading
    elements.loadingOverlay = document.getElementById('loadingOverlay');
    elements.loadingTitle = document.getElementById('loadingTitle');
    elements.loadingText = document.getElementById('loadingText');
    
    // Modal
    elements.settingsModal = document.getElementById('settingsModal');
    elements.closeModal = document.getElementById('closeModal');
    elements.btnApplySettings = document.getElementById('btnApplySettings');
    elements.btnCancelSettings = document.getElementById('btnCancelSettings');
    elements.btnResetSettings = document.getElementById('btnResetSettings');
    elements.modalTabs = document.querySelectorAll('.tab');
    elements.tabContents = document.querySelectorAll('.tab-content');
}

// ==========================================
// Upload Handlers
// ==========================================
function initUploadHandlers() {
    // Reference image upload
    elements.refPlaceholder.addEventListener('click', () => elements.refInput.click());
    elements.refInput.addEventListener('change', (e) => handleFileSelect(e, 'reference'));
    
    // Sample image upload
    elements.testPlaceholder.addEventListener('click', () => elements.testInput.click());
    elements.testInput.addEventListener('change', (e) => handleFileSelect(e, 'sample'));
    
    // Drag and drop for reference
    setupDragDrop(elements.refPanelContent, 'reference');
    setupDragDrop(elements.testPanelContent, 'sample');
    
    // Shape overlay mouse tracking
    setupOverlayTracking(elements.refPanelContent, elements.refOverlay);
    setupOverlayTracking(elements.testPanelContent, elements.testOverlay);
}

function setupDragDrop(element, type) {
    element.addEventListener('dragover', (e) => {
        e.preventDefault();
        element.style.background = 'rgba(0, 102, 204, 0.1)';
    });
    
    element.addEventListener('dragleave', () => {
        element.style.background = '';
    });
    
    element.addEventListener('drop', (e) => {
        e.preventDefault();
        element.style.background = '';
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleFile(file, type);
        }
    });
}

function setupOverlayTracking(panel, overlay) {
    panel.addEventListener('mousemove', (e) => {
        if (state.processFullImage) return;
        
        const rect = panel.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Update both overlays simultaneously
        const size = state.shapeSize;
        
        elements.refOverlay.style.left = `${x}px`;
        elements.refOverlay.style.top = `${y}px`;
        elements.refOverlay.style.width = `${size}px`;
        elements.refOverlay.style.height = `${size}px`;
        
        elements.testOverlay.style.left = `${x}px`;
        elements.testOverlay.style.top = `${y}px`;
        elements.testOverlay.style.width = `${size}px`;
        elements.testOverlay.style.height = `${size}px`;
    });
    
    panel.addEventListener('mouseenter', () => {
        if (!state.processFullImage) {
            elements.refOverlay.style.opacity = '1';
            elements.testOverlay.style.opacity = '1';
        }
    });
    
    panel.addEventListener('mouseleave', () => {
        elements.refOverlay.style.opacity = '0';
        elements.testOverlay.style.opacity = '0';
    });
}

function handleFileSelect(event, type) {
    const file = event.target.files[0];
    if (file) {
        handleFile(file, type);
    }
}

function handleFile(file, type) {
    const reader = new FileReader();
    
    reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
            if (type === 'reference') {
                state.refImage = file;
                state.refImageData = img;
                drawImageToCanvas(img, elements.refCanvas);
                elements.refPlaceholder.style.display = 'none';
                elements.refCanvas.style.display = 'block';
                elements.refInfo.textContent = `${img.width}×${img.height}`;
                elements.refPanelContent.classList.add('has-image');
            } else {
                state.testImage = file;
                state.testImageData = img;
                drawImageToCanvas(img, elements.testCanvas);
                elements.testPlaceholder.style.display = 'none';
                elements.testCanvas.style.display = 'block';
                elements.testInfo.textContent = `${img.width}×${img.height}`;
                elements.testPanelContent.classList.add('has-image');
            }
            
            updateButtonStates();
            updateMaxShapeSize();
        };
        img.src = e.target.result;
    };
    
    reader.readAsDataURL(file);
}

function drawImageToCanvas(img, canvas) {
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to match container while maintaining aspect ratio
    const container = canvas.parentElement;
    const containerWidth = container.clientWidth - 40;
    const containerHeight = container.clientHeight - 40;
    
    const scale = Math.min(containerWidth / img.width, containerHeight / img.height);
    const width = img.width * scale;
    const height = img.height * scale;
    
    canvas.width = width;
    canvas.height = height;
    canvas.style.display = 'block';
    
    ctx.drawImage(img, 0, 0, width, height);
}

// ==========================================
// Shape Controls
// ==========================================
function initShapeControls() {
    // Shape type radio buttons
    document.querySelectorAll('input[name="shapeType"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            state.shapeType = e.target.value;
            updateOverlayShape();
        });
    });
    
    // Process full image checkbox
    elements.processFullImage.addEventListener('change', (e) => {
        state.processFullImage = e.target.checked;
        updateShapeControlsState();
    });
    
    // Size slider
    elements.shapeSize.addEventListener('input', (e) => {
        state.shapeSize = parseInt(e.target.value);
        elements.sizeValue.textContent = `${state.shapeSize} px`;
        updateOverlaySize();
    });
    
    // Initialize overlay shape
    updateOverlayShape();
}

function updateShapeControlsState() {
    const disabled = state.processFullImage;
    
    elements.circleOption.classList.toggle('disabled', disabled);
    elements.squareOption.classList.toggle('disabled', disabled);
    elements.sizeSliderContainer.classList.toggle('disabled', disabled);
    
    elements.circleOption.querySelector('input').disabled = disabled;
    elements.squareOption.querySelector('input').disabled = disabled;
    elements.shapeSize.disabled = disabled;
    
    // Hide/show overlays
    if (disabled) {
        elements.refOverlay.classList.add('disabled');
        elements.testOverlay.classList.add('disabled');
    } else {
        elements.refOverlay.classList.remove('disabled');
        elements.testOverlay.classList.remove('disabled');
    }
}

function updateOverlayShape() {
    const isCircle = state.shapeType === 'circle';
    
    elements.refOverlay.classList.toggle('circle', isCircle);
    elements.refOverlay.classList.toggle('square', !isCircle);
    elements.testOverlay.classList.toggle('circle', isCircle);
    elements.testOverlay.classList.toggle('square', !isCircle);
}

function updateOverlaySize() {
    const size = state.shapeSize;
    elements.refOverlay.style.width = `${size}px`;
    elements.refOverlay.style.height = `${size}px`;
    elements.testOverlay.style.width = `${size}px`;
    elements.testOverlay.style.height = `${size}px`;
}

function updateMaxShapeSize() {
    let minDimension = 500;
    
    if (state.refImageData) {
        minDimension = Math.min(minDimension, state.refImageData.width, state.refImageData.height);
    }
    if (state.testImageData) {
        minDimension = Math.min(minDimension, state.testImageData.width, state.testImageData.height);
    }
    
    state.maxShapeSize = Math.max(minDimension, 100);
    elements.shapeSize.max = state.maxShapeSize;
    
    // Adjust current size if needed
    if (state.shapeSize > state.maxShapeSize) {
        state.shapeSize = state.maxShapeSize;
        elements.shapeSize.value = state.shapeSize;
        elements.sizeValue.textContent = `${state.shapeSize} px`;
    }
}

// ==========================================
// Button Handlers
// ==========================================
function initButtonHandlers() {
    elements.btnAdvancedSettings.addEventListener('click', openSettingsModal);
    elements.btnStartProcessing.addEventListener('click', startProcessing);
    elements.btnDeleteImages.addEventListener('click', deleteImages);
    elements.btnDownload.addEventListener('click', downloadReport);
    elements.btnDownloadSettings.addEventListener('click', downloadSettings);
}

function updateButtonStates() {
    const hasImages = state.refImage && state.testImage;
    elements.btnStartProcessing.disabled = !hasImages;
    elements.btnDeleteImages.disabled = !hasImages;
}

async function startProcessing() {
    if (!state.refImage || !state.testImage) {
        alert('Please upload both reference and sample images');
        return;
    }
    
    // Show loading
    showLoading('Uploading Images...', 'Preparing files for analysis');
    
    try {
        // Upload images
        const formData = new FormData();
        formData.append('reference', state.refImage);
        formData.append('sample', state.testImage);
        
        const uploadResponse = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const uploadData = await uploadResponse.json();
        
        if (!uploadResponse.ok) {
            throw new Error(uploadData.error || 'Upload failed');
        }
        
        state.sessionId = uploadData.session_id;
        
        // Update loading message
        updateLoading('Analyzing Images...', 'Running color and pattern analysis');
        
        // Prepare settings with crop info
        const analysisSettings = {
            ...state.settings,
            use_crop: !state.processFullImage,
            crop_shape: state.shapeType,
            crop_diameter: state.shapeSize,
            crop_width: state.shapeSize,
            crop_height: state.shapeSize
        };
        
        // Run analysis
        const analyzeResponse = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                settings: analysisSettings
            })
        });
        
        const analyzeData = await analyzeResponse.json();
        
        if (!analyzeResponse.ok) {
            throw new Error(analyzeData.error || 'Analysis failed');
        }
        
        // Store PDF filename
        state.pdfFilename = analyzeData.pdf_filename;
        
        // Display results
        displayResults(analyzeData);
        
        hideLoading();
        
    } catch (error) {
        hideLoading();
        alert('Error: ' + error.message);
        console.error('Processing error:', error);
    }
}

function displayResults(data) {
    // Show results section
    elements.resultsSection.hidden = false;
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Update decision badge
    const decision = data.decision;
    elements.decisionBadge.textContent = decision;
    elements.decisionBadge.className = 'decision-badge';
    
    if (decision === 'ACCEPT') {
        elements.decisionBadge.classList.add('accept');
    } else if (decision.includes('CONDITIONAL')) {
        elements.decisionBadge.classList.add('conditional');
    } else {
        elements.decisionBadge.classList.add('reject');
    }
    
    // Update scores with animation
    animateScore(elements.colorScore, elements.colorBar, data.color_score);
    animateScore(elements.patternScore, elements.patternBar, data.pattern_score);
    animateScore(elements.overallScore, elements.overallBar, data.overall_score);
    
    // Enable download buttons
    elements.btnDownload.disabled = false;
    elements.btnDownloadSettings.disabled = false;
}

function animateScore(valueEl, barEl, score) {
    // Animate number
    let currentScore = 0;
    const step = score / 30;
    const interval = setInterval(() => {
        currentScore += step;
        if (currentScore >= score) {
            currentScore = score;
            clearInterval(interval);
        }
        valueEl.textContent = currentScore.toFixed(1);
    }, 20);
    
    // Animate bar
    setTimeout(() => {
        barEl.style.width = `${score}%`;
        
        barEl.className = 'bar-fill';
        if (score >= 70) {
            barEl.classList.add('success');
        } else if (score >= 50) {
            barEl.classList.add('warning');
        } else {
            barEl.classList.add('danger');
        }
    }, 100);
}

function deleteImages() {
    if (!confirm('Are you sure you want to delete all images and start over?')) {
        return;
    }
    
    // Reset state
    state.sessionId = null;
    state.refImage = null;
    state.testImage = null;
    state.refImageData = null;
    state.testImageData = null;
    state.pdfFilename = null;
    
    // Reset UI
    elements.refPlaceholder.style.display = 'flex';
    elements.testPlaceholder.style.display = 'flex';
    elements.refCanvas.style.display = 'none';
    elements.testCanvas.style.display = 'none';
    elements.refInfo.textContent = 'No image';
    elements.testInfo.textContent = 'No image';
    elements.refPanelContent.classList.remove('has-image');
    elements.testPanelContent.classList.remove('has-image');
    elements.refInput.value = '';
    elements.testInput.value = '';
    
    // Hide results
    elements.resultsSection.hidden = true;
    
    // Reset scores
    elements.decisionBadge.textContent = 'PENDING';
    elements.decisionBadge.className = 'decision-badge';
    elements.colorScore.textContent = '--';
    elements.patternScore.textContent = '--';
    elements.overallScore.textContent = '--';
    elements.colorBar.style.width = '0%';
    elements.patternBar.style.width = '0%';
    elements.overallBar.style.width = '0%';
    
    // Disable buttons
    elements.btnDownload.disabled = true;
    elements.btnDownloadSettings.disabled = true;
    
    updateButtonStates();
}

function downloadReport() {
    if (state.sessionId && state.pdfFilename) {
        window.open(`/api/download/${state.sessionId}/${state.pdfFilename}`, '_blank');
    }
}

function downloadSettings() {
    const settings = collectSettings();
    const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'textile_qc_settings.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ==========================================
// Modal Handlers
// ==========================================
function initModalHandlers() {
    // Close modal buttons
    elements.closeModal.addEventListener('click', closeSettingsModal);
    elements.btnCancelSettings.addEventListener('click', closeSettingsModal);
    
    // Backdrop click
    elements.settingsModal.querySelector('.modal-backdrop').addEventListener('click', closeSettingsModal);
    
    // Tab switching
    elements.modalTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            
            elements.modalTabs.forEach(t => t.classList.remove('active'));
            elements.tabContents.forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(`tab-${tabName}`).classList.add('active');
        });
    });
    
    // Apply settings
    elements.btnApplySettings.addEventListener('click', () => {
        state.settings = collectSettings();
        closeSettingsModal();
    });
    
    // Reset settings
    elements.btnResetSettings.addEventListener('click', loadDefaultSettings);
}

function openSettingsModal() {
    elements.settingsModal.hidden = false;
    document.body.style.overflow = 'hidden';
}

function closeSettingsModal() {
    elements.settingsModal.hidden = true;
    document.body.style.overflow = '';
}

function collectSettings() {
    return {
        // Thresholds
        delta_e_threshold: parseFloat(document.getElementById('delta_e_threshold').value),
        delta_e_conditional: parseFloat(document.getElementById('delta_e_conditional').value),
        ssim_pass_threshold: parseFloat(document.getElementById('ssim_pass_threshold').value),
        ssim_conditional_threshold: parseFloat(document.getElementById('ssim_conditional_threshold').value),
        color_score_threshold: parseFloat(document.getElementById('color_score_threshold').value),
        pattern_score_threshold: parseFloat(document.getElementById('pattern_score_threshold').value),
        overall_score_threshold: parseFloat(document.getElementById('overall_score_threshold').value),
        
        // Color settings
        use_delta_e_cmc: document.getElementById('use_delta_e_cmc').checked,
        cmc_l_c_ratio: document.getElementById('cmc_l_c_ratio').value,
        observer_angle: document.getElementById('observer_angle').value,
        geometry_mode: document.getElementById('geometry_mode').value,
        
        // Pattern settings
        lbp_points: parseInt(document.getElementById('lbp_points').value),
        lbp_radius: parseInt(document.getElementById('lbp_radius').value),
        wavelet_type: document.getElementById('wavelet_type').value,
        wavelet_levels: parseInt(document.getElementById('wavelet_levels').value),
        pattern_min_area: parseInt(document.getElementById('pattern_min_area').value),
        pattern_max_area: parseInt(document.getElementById('pattern_max_area').value),
        keypoint_detector: document.getElementById('keypoint_detector').value,
        
        // Report sections
        enable_color_unit: document.getElementById('enable_color_unit').checked,
        enable_pattern_unit: document.getElementById('enable_pattern_unit').checked,
        enable_pattern_repetition: document.getElementById('enable_pattern_repetition').checked,
        enable_spectrophotometer: document.getElementById('enable_spectrophotometer').checked,
        enable_analysis_settings: document.getElementById('enable_analysis_settings').checked,
        
        // Operator
        operator_name: document.getElementById('operator_name').value
    };
}

async function loadDefaultSettings() {
    try {
        const response = await fetch('/api/settings/default');
        const defaults = await response.json();
        
        // Populate form fields
        Object.keys(defaults).forEach(key => {
            const el = document.getElementById(key);
            if (el) {
                if (el.type === 'checkbox') {
                    el.checked = defaults[key];
                } else {
                    el.value = defaults[key];
                }
            }
        });
        
        state.settings = defaults;
        
    } catch (error) {
        console.error('Error loading default settings:', error);
    }
}

// ==========================================
// Loading Overlay
// ==========================================
function showLoading(title = 'Processing...', text = 'Please wait') {
    elements.loadingTitle.textContent = title;
    elements.loadingText.textContent = text;
    elements.loadingOverlay.hidden = false;
}

function updateLoading(title, text) {
    elements.loadingTitle.textContent = title;
    elements.loadingText.textContent = text;
}

function hideLoading() {
    elements.loadingOverlay.hidden = true;
}

// ==========================================
// Keyboard Shortcuts
// ==========================================
document.addEventListener('keydown', (e) => {
    // Escape closes modal
    if (e.key === 'Escape' && !elements.settingsModal.hidden) {
        closeSettingsModal();
    }
});
