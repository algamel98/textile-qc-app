/**
 * Textile QC System - Main Application
 * Version 2.0.0 - With Progress Tracking
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
    settings: {},
    isProcessing: false
};

// ==========================================
// Progress Steps Configuration
// ==========================================
var ProgressSteps = {
    upload: { name: 'Uploading Images', weight: 10 },
    color: { name: 'Color Analysis', weight: 25 },
    pattern: { name: 'Pattern Analysis', weight: 25 },
    repetition: { name: 'Pattern Repetition', weight: 20 },
    scoring: { name: 'Calculating Scores', weight: 10 },
    report: { name: 'Generating Report', weight: 10 }
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
            if (e.target.files[0]) handleFileUpload(e.target.files[0], 'reference');
        });
    }
    
    if (testInput) {
        testInput.addEventListener('change', function(e) {
            if (e.target.files[0]) handleFileUpload(e.target.files[0], 'sample');
        });
    }
}

function handleFileUpload(file, type) {
    if (!file) return;
    
    var reader = new FileReader();
    reader.onload = function(e) {
        if (type === 'reference') {
            AppState.refFile = file;
            showImagePreview('refPreview', 'refPlaceholder', 'refInfo', e.target.result);
        } else {
            AppState.testFile = file;
            showImagePreview('testPreview', 'testPlaceholder', 'testInfo', e.target.result);
        }
        updateButtonStates();
    };
    reader.onerror = function() {
        alert('Error reading file');
    };
    reader.readAsDataURL(file);
}

function showImagePreview(previewId, placeholderId, infoId, src) {
    var preview = document.getElementById(previewId);
    var placeholder = document.getElementById(placeholderId);
    var info = document.getElementById(infoId);
    
    if (preview && placeholder) {
        var img = new Image();
        img.onload = function() {
            preview.src = src;
            preview.style.display = 'block';
            placeholder.style.display = 'none';
            if (info) info.textContent = img.width + '×' + img.height;
        };
        img.src = src;
    }
}

// ==========================================
// Shape Controls
// ==========================================
function initShapeControls() {
    var radios = document.querySelectorAll('input[name="shapeType"]');
    radios.forEach(function(radio) {
        radio.addEventListener('change', function(e) {
            AppState.shapeType = e.target.value;
            updateShapeOptions();
            updateOverlayShape();
        });
    });
    
    var fullImageCheckbox = document.getElementById('processFullImage');
    if (fullImageCheckbox) {
        fullImageCheckbox.addEventListener('change', function(e) {
            AppState.processFullImage = e.target.checked;
            toggleShapeControls(!e.target.checked);
        });
    }
    
    var sizeSlider = document.getElementById('shapeSize');
    var sizeValue = document.getElementById('sizeValue');
    if (sizeSlider && sizeValue) {
        sizeSlider.addEventListener('input', function(e) {
            AppState.shapeSize = parseInt(e.target.value);
            sizeValue.textContent = AppState.shapeSize + ' px';
            updateOverlaySize();
        });
    }
    
    updateShapeOptions();
}

function updateShapeOptions() {
    var circleOpt = document.getElementById('circleOption');
    var squareOpt = document.getElementById('squareOption');
    
    if (circleOpt) circleOpt.classList.toggle('active', AppState.shapeType === 'circle');
    if (squareOpt) squareOpt.classList.toggle('active', AppState.shapeType === 'square');
}

function toggleShapeControls(enabled) {
    var circleOpt = document.getElementById('circleOption');
    var squareOpt = document.getElementById('squareOption');
    var sliderContainer = document.getElementById('sizeSliderContainer');
    
    if (circleOpt) circleOpt.classList.toggle('disabled', !enabled);
    if (squareOpt) squareOpt.classList.toggle('disabled', !enabled);
    if (sliderContainer) sliderContainer.classList.toggle('disabled', !enabled);
    
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
            moveOverlays(e.clientX - rect.left, e.clientY - rect.top);
        });
        
        panel.addEventListener('mouseenter', function() {
            if (!AppState.processFullImage) setOverlaysOpacity(1);
        });
        
        panel.addEventListener('mouseleave', function() {
            setOverlaysOpacity(0);
        });
    });
}

function moveOverlays(x, y) {
    ['refOverlay', 'testOverlay'].forEach(function(id) {
        var overlay = document.getElementById(id);
        if (overlay) {
            overlay.style.left = x + 'px';
            overlay.style.top = y + 'px';
        }
    });
}

function setOverlaysOpacity(opacity) {
    ['refOverlay', 'testOverlay'].forEach(function(id) {
        var overlay = document.getElementById(id);
        if (overlay) overlay.style.opacity = opacity;
    });
}

function updateOverlayShape() {
    var isCircle = AppState.shapeType === 'circle';
    ['refOverlay', 'testOverlay'].forEach(function(id) {
        var overlay = document.getElementById(id);
        if (overlay) {
            overlay.style.borderRadius = isCircle ? '50%' : '0';
        }
    });
}

function updateOverlaySize() {
    var size = AppState.shapeSize;
    ['refOverlay', 'testOverlay'].forEach(function(id) {
        var overlay = document.getElementById(id);
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
    var btnSettings = document.getElementById('btnAdvancedSettings');
    if (btnSettings) btnSettings.addEventListener('click', openModal);
    
    var btnProcess = document.getElementById('btnStartProcessing');
    if (btnProcess) btnProcess.addEventListener('click', startProcessing);
    
    var btnDelete = document.getElementById('btnDeleteImages');
    if (btnDelete) btnDelete.addEventListener('click', deleteImages);
    
    var btnDownload = document.getElementById('btnDownload');
    if (btnDownload) btnDownload.addEventListener('click', downloadReport);
    
    var btnDownloadSettings = document.getElementById('btnDownloadSettings');
    if (btnDownloadSettings) btnDownloadSettings.addEventListener('click', downloadSettings);
}

function updateButtonStates() {
    var hasImages = AppState.refFile && AppState.testFile;
    var btnProcess = document.getElementById('btnStartProcessing');
    var btnDelete = document.getElementById('btnDeleteImages');
    
    if (btnProcess) btnProcess.disabled = !hasImages || AppState.isProcessing;
    if (btnDelete) btnDelete.disabled = !hasImages || AppState.isProcessing;
}

// ==========================================
// Processing with Progress
// ==========================================
function startProcessing() {
    if (!AppState.refFile || !AppState.testFile) {
        alert('Please upload both reference and sample images');
        return;
    }
    
    if (AppState.isProcessing) return;
    AppState.isProcessing = true;
    updateButtonStates();
    
    // Show progress modal
    showProgressModal();
    
    // Start upload
    updateProgress('upload', 0, 'Uploading images...');
    
    var formData = new FormData();
    formData.append('reference', AppState.refFile);
    formData.append('sample', AppState.testFile);
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(function(response) {
        if (!response.ok) {
            return response.json().then(function(data) {
                throw new Error(data.error || 'Upload failed');
            });
        }
        return response.json();
    })
    .then(function(data) {
        if (data.error) throw new Error(data.error);
        
        AppState.sessionId = data.session_id;
        completeStep('upload');
        
        // Start analysis
        return runAnalysis();
    })
    .then(function(data) {
        if (data.error) throw new Error(data.error);
        
        AppState.pdfFilename = data.pdf_filename;
        AppState.isProcessing = false;
        
        // Complete all steps
        completeAllSteps();
        
        // Show completion
        setTimeout(function() {
            hideProgressModal();
            displayResults(data);
            updateButtonStates();
        }, 1000);
    })
    .catch(function(error) {
        console.error('Processing error:', error);
        AppState.isProcessing = false;
        hideProgressModal();
        updateButtonStates();
        
        // Show more detailed error message
        var errorMsg = error.message || 'Unknown error occurred';
        if (errorMsg.includes('timeout')) {
            errorMsg = 'The analysis is taking too long. Please try with smaller images or fewer analysis options.';
        } else if (errorMsg.includes('Empty response') || errorMsg.includes('Invalid response')) {
            errorMsg = 'Server did not respond correctly. Please try again or check server logs.';
        }
        
        alert('Analysis Error:\n\n' + errorMsg);
    });
}

function runAnalysis() {
    return new Promise(function(resolve, reject) {
        var settings = collectSettings();
        // Don't use crop - process full image by default
        settings.use_crop = false;
        settings.crop_shape = AppState.shapeType;
        settings.crop_diameter = AppState.shapeSize;
        settings.crop_width = AppState.shapeSize;
        settings.crop_height = AppState.shapeSize;
        
        // Simulate progress for each enabled section
        var currentProgress = 10;
        
        if (settings.enable_color_unit) {
            updateProgress('color', currentProgress, 'Analyzing colors...');
            currentProgress += 25;
        }
        
        setTimeout(function() {
            if (settings.enable_pattern_unit) {
                updateProgress('pattern', currentProgress, 'Analyzing patterns...');
                currentProgress += 25;
            }
        }, 500);
        
        setTimeout(function() {
            if (settings.enable_pattern_repetition) {
                updateProgress('repetition', currentProgress, 'Analyzing repetition...');
                currentProgress += 20;
            }
        }, 1000);
        
        setTimeout(function() {
            updateProgress('scoring', currentProgress, 'Calculating scores...');
        }, 1500);
        
        setTimeout(function() {
            updateProgress('report', 90, 'Generating report...');
        }, 2000);
        
        // Make the actual API call with timeout handling
        var controller = new AbortController();
        var timeoutId = setTimeout(function() {
            controller.abort();
        }, 300000); // 5 minute timeout
        
        fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: AppState.sessionId,
                settings: settings
            }),
            signal: controller.signal
        })
        .then(function(response) {
            clearTimeout(timeoutId);
            // First, try to get the text content
            return response.text().then(function(text) {
                if (!text || text.trim() === '') {
                    throw new Error('Empty response from server');
                }
                try {
                    var data = JSON.parse(text);
                    // Check for error in response
                    if (data.error && data.decision === 'ERROR') {
                        throw new Error(data.error);
                    }
                    return data;
                } catch (parseError) {
                    console.error('JSON parse error:', parseError, 'Response:', text.substring(0, 200));
                    throw new Error('Invalid response from server');
                }
            });
        })
        .then(resolve)
        .catch(function(error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                reject(new Error('Analysis timeout - server is taking too long'));
            } else {
                reject(error);
            }
        });
    });
}

// ==========================================
// Progress Modal
// ==========================================
function showProgressModal() {
    var overlay = document.getElementById('loadingOverlay');
    var content = document.querySelector('.loading-content');
    
    if (content) {
        content.innerHTML = `
            <div class="progress-modal">
                <div class="progress-header">
                    <div class="spinner"></div>
                    <h3 id="progressTitle">Processing...</h3>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" id="progressBarFill"></div>
                </div>
                <div class="progress-percentage" id="progressPercentage">0%</div>
                <div class="progress-status" id="progressStatus">Preparing...</div>
                <div class="progress-steps" id="progressSteps">
                    <div class="step" data-step="upload"><span class="step-icon">○</span> Upload Images</div>
                    <div class="step" data-step="color"><span class="step-icon">○</span> Color Analysis</div>
                    <div class="step" data-step="pattern"><span class="step-icon">○</span> Pattern Analysis</div>
                    <div class="step" data-step="repetition"><span class="step-icon">○</span> Pattern Repetition</div>
                    <div class="step" data-step="scoring"><span class="step-icon">○</span> Calculate Scores</div>
                    <div class="step" data-step="report"><span class="step-icon">○</span> Generate Report</div>
                </div>
            </div>
        `;
    }
    
    if (overlay) overlay.style.display = 'flex';
}

function hideProgressModal() {
    var overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = 'none';
}

function updateProgress(step, percentage, status) {
    var bar = document.getElementById('progressBarFill');
    var pct = document.getElementById('progressPercentage');
    var stat = document.getElementById('progressStatus');
    var title = document.getElementById('progressTitle');
    
    if (bar) bar.style.width = percentage + '%';
    if (pct) pct.textContent = percentage + '%';
    if (stat) stat.textContent = status;
    if (title) title.textContent = 'Processing... ' + percentage + '%';
    
    // Mark step as active
    var stepEl = document.querySelector('.step[data-step="' + step + '"]');
    if (stepEl) {
        stepEl.classList.add('active');
        var icon = stepEl.querySelector('.step-icon');
        if (icon) icon.textContent = '●';
    }
}

function completeStep(step) {
    var stepEl = document.querySelector('.step[data-step="' + step + '"]');
    if (stepEl) {
        stepEl.classList.remove('active');
        stepEl.classList.add('completed');
        var icon = stepEl.querySelector('.step-icon');
        if (icon) icon.textContent = '✓';
    }
}

function completeAllSteps() {
    var steps = document.querySelectorAll('.progress-steps .step');
    steps.forEach(function(step) {
        step.classList.remove('active');
        step.classList.add('completed');
        var icon = step.querySelector('.step-icon');
        if (icon) icon.textContent = '✓';
    });
    
    var bar = document.getElementById('progressBarFill');
    var pct = document.getElementById('progressPercentage');
    var stat = document.getElementById('progressStatus');
    var title = document.getElementById('progressTitle');
    
    if (bar) bar.style.width = '100%';
    if (pct) pct.textContent = '100%';
    if (stat) stat.textContent = 'Processing complete!';
    if (title) title.textContent = 'Complete!';
}

// ==========================================
// Results Display
// ==========================================
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
        if (data.decision === 'ACCEPT') badge.classList.add('accept');
        else if (data.decision.indexOf('CONDITIONAL') >= 0) badge.classList.add('conditional');
        else badge.classList.add('reject');
    }
    
    // Animate scores
    animateScore('colorScore', 'colorBar', data.color_score || 0);
    animateScore('patternScore', 'patternBar', data.pattern_score || 0);
    animateScore('overallScore', 'overallBar', data.overall_score || 0);
    
    // Enable download
    var btnDownload = document.getElementById('btnDownload');
    if (btnDownload) btnDownload.disabled = false;
}

function animateScore(valueId, barId, score) {
    var valueEl = document.getElementById(valueId);
    var barEl = document.getElementById(barId);
    
    if (valueEl) {
        var current = 0;
        var step = Math.max(score / 30, 1);
        var interval = setInterval(function() {
            current += step;
            if (current >= score) {
                current = score;
                clearInterval(interval);
            }
            valueEl.textContent = current.toFixed(1);
        }, 25);
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

// ==========================================
// Delete Images
// ==========================================
function deleteImages() {
    if (!confirm('Delete all images and start over?')) return;
    
    AppState.sessionId = null;
    AppState.refFile = null;
    AppState.testFile = null;
    AppState.pdfFilename = null;
    
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
    
    var resultsSection = document.getElementById('resultsSection');
    if (resultsSection) resultsSection.style.display = 'none';
    
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

// ==========================================
// Downloads
// ==========================================
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
    
    if (overlay) {
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) closeModal();
        });
    }
    
    var tabs = document.querySelectorAll('.modal-tabs .tab');
    tabs.forEach(function(tab) {
        tab.addEventListener('click', function() {
            switchTab(this.getAttribute('data-tab'));
        });
    });
    
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
    document.querySelectorAll('.modal-tabs .tab').forEach(function(tab) {
        tab.classList.toggle('active', tab.getAttribute('data-tab') === tabName);
    });
    document.querySelectorAll('.tab-content').forEach(function(content) {
        content.classList.toggle('active', content.id === 'tab-' + tabName);
    });
}

// ==========================================
// Settings
// ==========================================
function collectSettings() {
    return {
        delta_e_threshold: getNum('delta_e_threshold', 2.0),
        delta_e_conditional: getNum('delta_e_conditional', 3.5),
        ssim_pass_threshold: getNum('ssim_pass_threshold', 0.95),
        ssim_conditional_threshold: getNum('ssim_conditional_threshold', 0.90),
        color_score_threshold: getNum('color_score_threshold', 70),
        pattern_score_threshold: getNum('pattern_score_threshold', 90),
        overall_score_threshold: getNum('overall_score_threshold', 70),
        use_delta_e_cmc: getCheck('use_delta_e_cmc', true),
        cmc_l_c_ratio: getVal('cmc_l_c_ratio', '2:1'),
        observer_angle: getVal('observer_angle', '2'),
        geometry_mode: getVal('geometry_mode', 'd/8 SCI'),
        lbp_points: getNum('lbp_points', 24),
        lbp_radius: getNum('lbp_radius', 3),
        wavelet_type: getVal('wavelet_type', 'db4'),
        wavelet_levels: getNum('wavelet_levels', 3),
        pattern_min_area: getNum('pattern_min_area', 100),
        pattern_max_area: getNum('pattern_max_area', 5000),
        keypoint_detector: getVal('keypoint_detector', 'ORB'),
        enable_color_unit: getCheck('enable_color_unit', true),
        enable_pattern_unit: getCheck('enable_pattern_unit', true),
        enable_pattern_repetition: getCheck('enable_pattern_repetition', true),
        enable_spectrophotometer: getCheck('enable_spectrophotometer', true),
        enable_analysis_settings: getCheck('enable_analysis_settings', false),
        operator_name: getVal('operator_name', 'Operator')
    };
}

function getNum(id, def) { var el = document.getElementById(id); return el ? (parseFloat(el.value) || def) : def; }
function getCheck(id, def) { var el = document.getElementById(id); return el ? el.checked : def; }
function getVal(id, def) { var el = document.getElementById(id); return el ? el.value : def; }

function loadDefaultSettings() {
    fetch('/api/settings/default')
        .then(function(r) { return r.json(); })
        .then(function(defaults) {
            Object.keys(defaults).forEach(function(key) {
                var el = document.getElementById(key);
                if (el) {
                    if (el.type === 'checkbox') el.checked = defaults[key];
                    else el.value = defaults[key];
                }
            });
            AppState.settings = defaults;
        })
        .catch(function(e) { console.error('Settings error:', e); });
}
