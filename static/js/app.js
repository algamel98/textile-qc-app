/**
 * Textile QC System - Main Application
 * Version 2.0.0
 */

// ==========================================
// Application State
// ==========================================
var AppState = {
    sessionId: null,
    refFile: null,
    testFile: null,
    shapeType: 'circle',
    shapeSize: 100,
    processFullImage: false,
    pdfFilename: null,
    settings: {}
};

// ==========================================
// Initialize Application
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Textile QC System initialized');
    initFileInputs();
    initShapeControls();
    initButtons();
    initModal();
    initOverlayTracking();
    loadDefaultSettings();
});

// ==========================================
// File Input Handlers
// ==========================================
function initFileInputs() {
    var refInput = document.getElementById('refInput');
    var testInput = document.getElementById('testInput');
    
    if (refInput) {
        refInput.addEventListener('change', function(e) {
            handleFileUpload(e.target.files[0], 'reference');
        });
    }
    
    if (testInput) {
        testInput.addEventListener('change', function(e) {
            handleFileUpload(e.target.files[0], 'sample');
        });
    }
}

function handleFileUpload(file, type) {
    if (!file) return;
    
    var reader = new FileReader();
    reader.onload = function(e) {
        if (type === 'reference') {
            AppState.refFile = file;
            showImagePreview('refPreview', 'refPlaceholder', 'refInfo', e.target.result, file);
        } else {
            AppState.testFile = file;
            showImagePreview('testPreview', 'testPlaceholder', 'testInfo', e.target.result, file);
        }
        updateButtonStates();
    };
    reader.readAsDataURL(file);
}

function showImagePreview(previewId, placeholderId, infoId, src, file) {
    var preview = document.getElementById(previewId);
    var placeholder = document.getElementById(placeholderId);
    var info = document.getElementById(infoId);
    
    if (preview && placeholder) {
        preview.src = src;
        preview.style.display = 'block';
        placeholder.style.display = 'none';
        
        // Get image dimensions
        var img = new Image();
        img.onload = function() {
            if (info) {
                info.textContent = img.width + '×' + img.height;
            }
            updateMaxShapeSize(img.width, img.height);
        };
        img.src = src;
    }
}

function updateMaxShapeSize(width, height) {
    var minDim = Math.min(width, height);
    var slider = document.getElementById('shapeSize');
    if (slider && minDim > 50) {
        slider.max = Math.min(minDim, 800);
    }
}

// ==========================================
// Shape Controls
// ==========================================
function initShapeControls() {
    // Shape type radios
    var radios = document.querySelectorAll('input[name="shapeType"]');
    radios.forEach(function(radio) {
        radio.addEventListener('change', function(e) {
            AppState.shapeType = e.target.value;
            updateShapeOptions();
            updateOverlayShape();
        });
    });
    
    // Full image checkbox
    var fullImageCheckbox = document.getElementById('processFullImage');
    if (fullImageCheckbox) {
        fullImageCheckbox.addEventListener('change', function(e) {
            AppState.processFullImage = e.target.checked;
            toggleShapeControls(!e.target.checked);
        });
    }
    
    // Size slider
    var sizeSlider = document.getElementById('shapeSize');
    var sizeValue = document.getElementById('sizeValue');
    if (sizeSlider && sizeValue) {
        sizeSlider.addEventListener('input', function(e) {
            AppState.shapeSize = parseInt(e.target.value);
            sizeValue.textContent = AppState.shapeSize + ' px';
            updateOverlaySize();
        });
    }
    
    // Initialize shape options visual state
    updateShapeOptions();
}

function updateShapeOptions() {
    var circleOpt = document.getElementById('circleOption');
    var squareOpt = document.getElementById('squareOption');
    
    if (circleOpt && squareOpt) {
        circleOpt.classList.toggle('active', AppState.shapeType === 'circle');
        squareOpt.classList.toggle('active', AppState.shapeType === 'square');
    }
}

function toggleShapeControls(enabled) {
    var circleOpt = document.getElementById('circleOption');
    var squareOpt = document.getElementById('squareOption');
    var sliderContainer = document.getElementById('sizeSliderContainer');
    
    if (circleOpt) circleOpt.classList.toggle('disabled', !enabled);
    if (squareOpt) squareOpt.classList.toggle('disabled', !enabled);
    if (sliderContainer) sliderContainer.classList.toggle('disabled', !enabled);
    
    // Also toggle overlay visibility
    var refOverlay = document.getElementById('refOverlay');
    var testOverlay = document.getElementById('testOverlay');
    if (refOverlay) refOverlay.style.display = enabled ? '' : 'none';
    if (testOverlay) testOverlay.style.display = enabled ? '' : 'none';
}

// ==========================================
// Overlay Tracking
// ==========================================
function initOverlayTracking() {
    var refPanel = document.getElementById('refPanelContent');
    var testPanel = document.getElementById('testPanelContent');
    
    [refPanel, testPanel].forEach(function(panel) {
        if (!panel) return;
        
        panel.addEventListener('mousemove', function(e) {
            if (AppState.processFullImage) return;
            
            var rect = panel.getBoundingClientRect();
            var x = e.clientX - rect.left;
            var y = e.clientY - rect.top;
            
            moveOverlays(x, y);
        });
        
        panel.addEventListener('mouseenter', function() {
            if (!AppState.processFullImage) {
                setOverlaysOpacity(1);
            }
        });
        
        panel.addEventListener('mouseleave', function() {
            setOverlaysOpacity(0);
        });
    });
}

function moveOverlays(x, y) {
    var refOverlay = document.getElementById('refOverlay');
    var testOverlay = document.getElementById('testOverlay');
    
    [refOverlay, testOverlay].forEach(function(overlay) {
        if (overlay) {
            overlay.style.left = x + 'px';
            overlay.style.top = y + 'px';
        }
    });
}

function setOverlaysOpacity(opacity) {
    var refOverlay = document.getElementById('refOverlay');
    var testOverlay = document.getElementById('testOverlay');
    
    [refOverlay, testOverlay].forEach(function(overlay) {
        if (overlay) {
            overlay.style.opacity = opacity;
        }
    });
}

function updateOverlayShape() {
    var refOverlay = document.getElementById('refOverlay');
    var testOverlay = document.getElementById('testOverlay');
    var isCircle = AppState.shapeType === 'circle';
    
    [refOverlay, testOverlay].forEach(function(overlay) {
        if (overlay) {
            overlay.classList.toggle('circle', isCircle);
            overlay.classList.remove(isCircle ? 'square' : 'circle');
            if (!isCircle) {
                overlay.style.borderRadius = '0';
            } else {
                overlay.style.borderRadius = '50%';
            }
        }
    });
}

function updateOverlaySize() {
    var size = AppState.shapeSize;
    var refOverlay = document.getElementById('refOverlay');
    var testOverlay = document.getElementById('testOverlay');
    
    [refOverlay, testOverlay].forEach(function(overlay) {
        if (overlay) {
            overlay.style.width = size + 'px';
            overlay.style.height = size + 'px';
        }
    });
}

// ==========================================
// Button Handlers
// ==========================================
function initButtons() {
    // Advanced Settings
    var btnSettings = document.getElementById('btnAdvancedSettings');
    if (btnSettings) {
        btnSettings.addEventListener('click', openModal);
    }
    
    // Start Processing
    var btnProcess = document.getElementById('btnStartProcessing');
    if (btnProcess) {
        btnProcess.addEventListener('click', startProcessing);
    }
    
    // Delete Images
    var btnDelete = document.getElementById('btnDeleteImages');
    if (btnDelete) {
        btnDelete.addEventListener('click', deleteImages);
    }
    
    // Download Report
    var btnDownload = document.getElementById('btnDownload');
    if (btnDownload) {
        btnDownload.addEventListener('click', downloadReport);
    }
    
    // Download Settings
    var btnDownloadSettings = document.getElementById('btnDownloadSettings');
    if (btnDownloadSettings) {
        btnDownloadSettings.addEventListener('click', downloadSettings);
    }
}

function updateButtonStates() {
    var hasImages = AppState.refFile && AppState.testFile;
    var btnProcess = document.getElementById('btnStartProcessing');
    var btnDelete = document.getElementById('btnDeleteImages');
    
    if (btnProcess) btnProcess.disabled = !hasImages;
    if (btnDelete) btnDelete.disabled = !hasImages;
}

// ==========================================
// Processing
// ==========================================
function startProcessing() {
    if (!AppState.refFile || !AppState.testFile) {
        alert('Please upload both reference and sample images');
        return;
    }
    
    showLoading('Uploading Images...', 'Preparing files for analysis');
    
    // Upload images
    var formData = new FormData();
    formData.append('reference', AppState.refFile);
    formData.append('sample', AppState.testFile);
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.error) throw new Error(data.error);
        
        AppState.sessionId = data.session_id;
        updateLoading('Analyzing Images...', 'Running color and pattern analysis');
        
        // Run analysis
        var settings = collectSettings();
        settings.use_crop = !AppState.processFullImage;
        settings.crop_shape = AppState.shapeType;
        settings.crop_diameter = AppState.shapeSize;
        settings.crop_width = AppState.shapeSize;
        settings.crop_height = AppState.shapeSize;
        
        return fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: AppState.sessionId,
                settings: settings
            })
        });
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.error) throw new Error(data.error);
        
        AppState.pdfFilename = data.pdf_filename;
        hideLoading();
        displayResults(data);
    })
    .catch(function(error) {
        hideLoading();
        alert('Error: ' + error.message);
        console.error('Processing error:', error);
    });
}

function displayResults(data) {
    var resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Decision badge
    var badge = document.getElementById('decisionBadge');
    if (badge) {
        badge.textContent = data.decision;
        badge.className = 'decision-badge';
        if (data.decision === 'ACCEPT') {
            badge.classList.add('accept');
        } else if (data.decision.indexOf('CONDITIONAL') >= 0) {
            badge.classList.add('conditional');
        } else {
            badge.classList.add('reject');
        }
    }
    
    // Scores
    animateScore('colorScore', 'colorBar', data.color_score);
    animateScore('patternScore', 'patternBar', data.pattern_score);
    animateScore('overallScore', 'overallBar', data.overall_score);
    
    // Enable download
    var btnDownload = document.getElementById('btnDownload');
    if (btnDownload) btnDownload.disabled = false;
}

function animateScore(valueId, barId, score) {
    var valueEl = document.getElementById(valueId);
    var barEl = document.getElementById(barId);
    
    if (valueEl) {
        var current = 0;
        var step = score / 30;
        var interval = setInterval(function() {
            current += step;
            if (current >= score) {
                current = score;
                clearInterval(interval);
            }
            valueEl.textContent = current.toFixed(1);
        }, 20);
    }
    
    if (barEl) {
        setTimeout(function() {
            barEl.style.width = score + '%';
            barEl.className = 'bar-fill';
            if (score >= 70) barEl.classList.add('success');
            else if (score >= 50) barEl.classList.add('warning');
            else barEl.classList.add('danger');
        }, 100);
    }
}

function deleteImages() {
    if (!confirm('Are you sure you want to delete all images?')) return;
    
    // Reset state
    AppState.sessionId = null;
    AppState.refFile = null;
    AppState.testFile = null;
    AppState.pdfFilename = null;
    
    // Reset UI
    ['ref', 'test'].forEach(function(type) {
        var preview = document.getElementById(type + 'Preview');
        var placeholder = document.getElementById(type + 'Placeholder');
        var info = document.getElementById(type + 'Info');
        var input = document.getElementById(type + 'Input');
        
        if (preview) preview.style.display = 'none';
        if (placeholder) placeholder.style.display = 'flex';
        if (info) info.textContent = 'No image';
        if (input) input.value = '';
    });
    
    // Hide results
    var resultsSection = document.getElementById('resultsSection');
    if (resultsSection) resultsSection.style.display = 'none';
    
    // Reset scores
    ['colorScore', 'patternScore', 'overallScore'].forEach(function(id) {
        var el = document.getElementById(id);
        if (el) el.textContent = '--';
    });
    
    ['colorBar', 'patternBar', 'overallBar'].forEach(function(id) {
        var el = document.getElementById(id);
        if (el) el.style.width = '0%';
    });
    
    var btnDownload = document.getElementById('btnDownload');
    if (btnDownload) btnDownload.disabled = true;
    
    updateButtonStates();
}

function downloadReport() {
    if (AppState.sessionId && AppState.pdfFilename) {
        window.open('/api/download/' + AppState.sessionId + '/' + AppState.pdfFilename, '_blank');
    }
}

function downloadSettings() {
    var settings = collectSettings();
    var blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'textile_qc_settings.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ==========================================
// Loading Overlay
// ==========================================
function showLoading(title, text) {
    var overlay = document.getElementById('loadingOverlay');
    var titleEl = document.getElementById('loadingTitle');
    var textEl = document.getElementById('loadingText');
    
    if (titleEl) titleEl.textContent = title || 'Processing...';
    if (textEl) textEl.textContent = text || 'Please wait';
    if (overlay) overlay.style.display = 'flex';
}

function updateLoading(title, text) {
    var titleEl = document.getElementById('loadingTitle');
    var textEl = document.getElementById('loadingText');
    
    if (titleEl) titleEl.textContent = title;
    if (textEl) textEl.textContent = text;
}

function hideLoading() {
    var overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = 'none';
}

// ==========================================
// Modal
// ==========================================
function initModal() {
    var closeBtn = document.getElementById('closeModal');
    var cancelBtn = document.getElementById('btnCancelSettings');
    var applyBtn = document.getElementById('btnApplySettings');
    var resetBtn = document.getElementById('btnResetSettings');
    var overlay = document.getElementById('settingsModal');
    
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    if (applyBtn) applyBtn.addEventListener('click', function() {
        AppState.settings = collectSettings();
        closeModal();
    });
    if (resetBtn) resetBtn.addEventListener('click', loadDefaultSettings);
    
    // Close on backdrop click
    if (overlay) {
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) closeModal();
        });
    }
    
    // Tab switching
    var tabs = document.querySelectorAll('.modal-tabs .tab');
    tabs.forEach(function(tab) {
        tab.addEventListener('click', function() {
            var tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeModal();
    });
}

function openModal() {
    var modal = document.getElementById('settingsModal');
    if (modal) modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    var modal = document.getElementById('settingsModal');
    if (modal) modal.style.display = 'none';
    document.body.style.overflow = '';
}

function switchTab(tabName) {
    // Update tab buttons
    var tabs = document.querySelectorAll('.modal-tabs .tab');
    tabs.forEach(function(tab) {
        tab.classList.toggle('active', tab.getAttribute('data-tab') === tabName);
    });
    
    // Update tab contents
    var contents = document.querySelectorAll('.tab-content');
    contents.forEach(function(content) {
        content.classList.toggle('active', content.id === 'tab-' + tabName);
    });
}

// ==========================================
// Settings
// ==========================================
function collectSettings() {
    return {
        delta_e_threshold: getNumberValue('delta_e_threshold', 2.0),
        delta_e_conditional: getNumberValue('delta_e_conditional', 3.5),
        ssim_pass_threshold: getNumberValue('ssim_pass_threshold', 0.95),
        ssim_conditional_threshold: getNumberValue('ssim_conditional_threshold', 0.90),
        color_score_threshold: getNumberValue('color_score_threshold', 70),
        pattern_score_threshold: getNumberValue('pattern_score_threshold', 90),
        overall_score_threshold: getNumberValue('overall_score_threshold', 70),
        use_delta_e_cmc: getCheckboxValue('use_delta_e_cmc', true),
        cmc_l_c_ratio: getSelectValue('cmc_l_c_ratio', '2:1'),
        observer_angle: getSelectValue('observer_angle', '2'),
        geometry_mode: getSelectValue('geometry_mode', 'd/8 SCI'),
        lbp_points: getNumberValue('lbp_points', 24),
        lbp_radius: getNumberValue('lbp_radius', 3),
        wavelet_type: getSelectValue('wavelet_type', 'db4'),
        wavelet_levels: getNumberValue('wavelet_levels', 3),
        pattern_min_area: getNumberValue('pattern_min_area', 100),
        pattern_max_area: getNumberValue('pattern_max_area', 5000),
        keypoint_detector: getSelectValue('keypoint_detector', 'ORB'),
        enable_color_unit: getCheckboxValue('enable_color_unit', true),
        enable_pattern_unit: getCheckboxValue('enable_pattern_unit', true),
        enable_pattern_repetition: getCheckboxValue('enable_pattern_repetition', true),
        enable_spectrophotometer: getCheckboxValue('enable_spectrophotometer', true),
        enable_analysis_settings: getCheckboxValue('enable_analysis_settings', false),
        operator_name: getTextValue('operator_name', 'Operator')
    };
}

function getNumberValue(id, defaultVal) {
    var el = document.getElementById(id);
    return el ? parseFloat(el.value) || defaultVal : defaultVal;
}

function getCheckboxValue(id, defaultVal) {
    var el = document.getElementById(id);
    return el ? el.checked : defaultVal;
}

function getSelectValue(id, defaultVal) {
    var el = document.getElementById(id);
    return el ? el.value : defaultVal;
}

function getTextValue(id, defaultVal) {
    var el = document.getElementById(id);
    return el ? el.value : defaultVal;
}

function loadDefaultSettings() {
    fetch('/api/settings/default')
        .then(function(response) { return response.json(); })
        .then(function(defaults) {
            Object.keys(defaults).forEach(function(key) {
                var el = document.getElementById(key);
                if (el) {
                    if (el.type === 'checkbox') {
                        el.checked = defaults[key];
                    } else {
                        el.value = defaults[key];
                    }
                }
            });
            AppState.settings = defaults;
        })
        .catch(function(error) {
            console.error('Error loading settings:', error);
        });
}
