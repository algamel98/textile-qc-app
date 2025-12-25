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
    initLanguageSwitcher();
    initFileInputs();
    initShapeControls();
    initButtons();
    initModal();
    initOverlayTracking();
    loadDefaultSettings();
    initCodeDownload();
    initSampleTests();
    initDevelopmentModal();
    
    // Initialize samples language note
    updateSamplesLanguageNote();
    
    // Listen for language changes
    document.addEventListener('languageChanged', function(e) {
        // Re-translate dynamic content
        updateDynamicTranslations();
    });
});

// ==========================================
// Language Switcher
// ==========================================
function initLanguageSwitcher() {
    var btn = document.getElementById('btnLanguageSwitcher');
    if (!btn) return;
    
    btn.addEventListener('click', function() {
        var currentLang = I18n.getLanguage();
        var newLang = currentLang === 'en' ? 'tr' : 'en';
        I18n.setLanguage(newLang);
    });
    
    // Initial update
    updateLanguageSwitcher();
}

function updateDynamicTranslations() {
    // Update size value display
    var sizeValue = document.getElementById('sizeValue');
    if (sizeValue) {
        var size = AppState.shapeSize || 100;
        sizeValue.innerHTML = size + ' <span data-i18n="px">px</span>';
        // Re-translate px text
        var pxSpan = sizeValue.querySelector('span[data-i18n="px"]');
        if (pxSpan) pxSpan.textContent = I18n.t('px');
    }
    
    // Update operator name placeholder
    var operatorInput = document.getElementById('operator_name');
    if (operatorInput && !operatorInput.value) {
        operatorInput.placeholder = I18n.t('operator');
    }
    
    // Update help dialog if it's open
    if (currentHelpType) {
        var bodyEl = document.getElementById('helpDialogBody');
        var downloadBtn = document.getElementById('helpDialogDownload');
        if (bodyEl) {
            var content = getHelpContent(currentHelpType);
            if (content) {
                bodyEl.innerHTML = content.body;
            }
        }
        if (downloadBtn) {
            var btnSpan = downloadBtn.querySelector('span[data-i18n]');
            if (btnSpan) {
                btnSpan.textContent = I18n.t('download.this.format');
            }
        }
    }
    
    // Re-render sample cards if they exist
    if (SampleTestState.samples && SampleTestState.samples.length > 0) {
        renderSampleCards(SampleTestState.samples);
    }
    
    // Update samples language note
    updateSamplesLanguageNote();
}

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
        alert(I18n.t('error.reading.file'));
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
            if (info) {
                if (img.width && img.height) {
                    info.textContent = img.width + '×' + img.height;
                } else {
                    info.textContent = I18n.t('no.image');
                }
            }
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
            sizeValue.innerHTML = AppState.shapeSize + ' <span data-i18n="px">px</span>';
            // Re-translate px text
            var pxSpan = sizeValue.querySelector('span[data-i18n="px"]');
            if (pxSpan) pxSpan.textContent = I18n.t('px');
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
        alert(I18n.t('please.upload.both'));
        return;
    }
    
    // Show development modal instead of processing
    showDevelopmentModal();
    return;
    
    if (AppState.isProcessing) return;
    AppState.isProcessing = true;
    updateButtonStates();
    
    // Show progress modal
    showProgressModal();
    
    // Start upload
    updateProgress('upload', 0, I18n.t('uploading.images'));
    
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
            updateProgress('color', currentProgress, I18n.t('analyzing.colors'));
            currentProgress += 25;
        }
        
        setTimeout(function() {
            if (settings.enable_pattern_unit) {
                updateProgress('pattern', currentProgress, I18n.t('analyzing.patterns'));
                currentProgress += 25;
            }
        }, 500);
        
        setTimeout(function() {
            if (settings.enable_pattern_repetition) {
                updateProgress('repetition', currentProgress, I18n.t('analyzing.repetition'));
                currentProgress += 20;
            }
        }, 1000);
        
        setTimeout(function() {
            updateProgress('scoring', currentProgress, I18n.t('calculating.scores'));
        }, 1500);
        
        setTimeout(function() {
            updateProgress('report', 90, I18n.t('generating.report'));
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
                <div class="progress-status" id="progressStatus">` + I18n.t('preparing') + `</div>
                <div class="progress-steps" id="progressSteps">
                    <div class="step" data-step="upload"><span class="step-icon">○</span> ` + I18n.t('upload.images') + `</div>
                    <div class="step" data-step="color"><span class="step-icon">○</span> ` + I18n.t('color.analysis.step') + `</div>
                    <div class="step" data-step="pattern"><span class="step-icon">○</span> ` + I18n.t('pattern.analysis.step') + `</div>
                    <div class="step" data-step="repetition"><span class="step-icon">○</span> ` + I18n.t('pattern.repetition.step') + `</div>
                    <div class="step" data-step="scoring"><span class="step-icon">○</span> ` + I18n.t('calculate.scores') + `</div>
                    <div class="step" data-step="report"><span class="step-icon">○</span> ` + I18n.t('generate.report') + `</div>
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
    if (stat) stat.textContent = I18n.t('processing.complete');
    if (title) title.textContent = I18n.t('complete');
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
    if (!confirm(I18n.t('delete.confirm'))) return;
    
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
        if (info) info.textContent = I18n.t('no.image');
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

// ==========================================
// Code Download Feature
// ==========================================
function getHelpContent(type) {
    if (type === 'py') {
        return {
            title: I18n.t('python.script'),
            icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>',
            body: `
                <h4>📄 ` + I18n.t('what.is.python') + `</h4>
                <p>` + I18n.t('python.script.desc') + `</p>
                <ul>
                    <li>` + I18n.t('python.works.with') + `</li>
                    <li>` + I18n.t('python.run.directly') + `</li>
                    <li>` + I18n.t('python.ideal.for') + `</li>
                    <li>` + I18n.t('python.can.import') + `</li>
                </ul>
                <div class="highlight-box">
                    <p>💡 ` + I18n.t('best.for') + ` ` + I18n.t('python.best.for') + `</p>
                </div>
            `
        };
    } else if (type === 'ipynb') {
        return {
            title: I18n.t('jupyter.notebook'),
            icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>',
            body: `
                <h4>📓 ` + I18n.t('what.is.notebook') + `</h4>
                <p>` + I18n.t('notebook.desc') + `</p>
                <ul>
                    <li>` + I18n.t('notebook.runs.colab') + `</li>
                    <li>` + I18n.t('notebook.interactive') + `</li>
                    <li>` + I18n.t('notebook.easy.modify') + `</li>
                    <li>` + I18n.t('notebook.visualizations') + `</li>
                </ul>
                <div class="highlight-box">
                    <p>☁️ ` + I18n.t('best.for') + ` ` + I18n.t('notebook.best.for') + `</p>
                </div>
            `
        };
    }
    return null;
}

var currentHelpType = null;

function initCodeDownload() {
    var btnCodeDownload = document.getElementById('btnCodeDownload');
    var codeDropdown = document.getElementById('codeDropdown');
    var helpOverlay = document.getElementById('helpDialogOverlay');
    var helpClose = document.getElementById('helpDialogClose');
    var helpDownload = document.getElementById('helpDialogDownload');
    
    if (!btnCodeDownload || !codeDropdown) return;
    
    // Toggle dropdown
    btnCodeDownload.addEventListener('click', function(e) {
        e.stopPropagation();
        var isOpen = codeDropdown.classList.contains('show');
        closeAllDropdowns();
        if (!isOpen) {
            codeDropdown.classList.add('show');
            btnCodeDownload.classList.add('active');
        }
    });
    
    // Handle dropdown item clicks
    var dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach(function(item) {
        item.addEventListener('click', function(e) {
            // Don't trigger download if clicking on help button
            if (e.target.closest('.btn-help')) return;
            
            var fileType = item.getAttribute('data-type');
            downloadSourceCode(fileType);
            closeAllDropdowns();
        });
    });
    
    // Handle help button clicks
    var helpButtons = document.querySelectorAll('.btn-help');
    helpButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            var helpType = btn.getAttribute('data-help');
            showHelpDialog(helpType);
        });
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.code-download-container')) {
            closeAllDropdowns();
        }
    });
    
    // Help dialog close
    if (helpClose) {
        helpClose.addEventListener('click', closeHelpDialog);
    }
    
    if (helpOverlay) {
        helpOverlay.addEventListener('click', function(e) {
            if (e.target === helpOverlay) closeHelpDialog();
        });
    }
    
    // Help dialog download button
    if (helpDownload) {
        helpDownload.addEventListener('click', function() {
            if (currentHelpType) {
                downloadSourceCode(currentHelpType);
                closeHelpDialog();
            }
        });
    }
    
    // Escape key closes dialogs
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllDropdowns();
            closeHelpDialog();
        }
    });
}

function closeAllDropdowns() {
    var dropdown = document.getElementById('codeDropdown');
    var btn = document.getElementById('btnCodeDownload');
    if (dropdown) dropdown.classList.remove('show');
    if (btn) btn.classList.remove('active');
}

function showHelpDialog(type) {
    var overlay = document.getElementById('helpDialogOverlay');
    var iconEl = document.getElementById('helpDialogIcon');
    var titleEl = document.getElementById('helpDialogTitle');
    var bodyEl = document.getElementById('helpDialogBody');
    var downloadBtn = document.getElementById('helpDialogDownload');
    
    if (!overlay) return;
    
    var content = getHelpContent(type);
    if (!content) return;
    
    currentHelpType = type;
    
    iconEl.innerHTML = content.icon;
    // Title is translated via data-i18n, so just update the body
    bodyEl.innerHTML = content.body;
    
    // Update download button text
    if (downloadBtn) {
        var btnSpan = downloadBtn.querySelector('span[data-i18n]');
        if (btnSpan) {
            btnSpan.textContent = I18n.t('download.this.format');
        }
    }
    
    overlay.style.display = 'flex';
    closeAllDropdowns();
}

function closeHelpDialog() {
    var overlay = document.getElementById('helpDialogOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
    currentHelpType = null;
}

function downloadSourceCode(fileType) {
    var downloadUrl = '/api/source/' + fileType;
    
    // Create a temporary link and trigger download
    var a = document.createElement('a');
    a.href = downloadUrl;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// ==========================================
// Sample Tests Feature
// ==========================================
var SampleTestState = {
    isActive: false,
    currentSample: null,
    samples: []
};

function initSampleTests() {
    var toggleBtn = document.getElementById('samplesToggleBtn');
    var sidebar = document.getElementById('samplesSidebar');
    var overlay = document.getElementById('samplesOverlay');
    var closeBtn = document.getElementById('samplesSidebarClose');
    
    if (!toggleBtn || !sidebar) return;
    
    // Toggle sidebar
    toggleBtn.addEventListener('click', function() {
        openSamplesSidebar();
    });
    
    // Close sidebar
    if (closeBtn) {
        closeBtn.addEventListener('click', closeSamplesSidebar);
    }
    
    if (overlay) {
        overlay.addEventListener('click', closeSamplesSidebar);
    }
    
    // Escape key closes sidebar
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) {
            closeSamplesSidebar();
        }
    });
    
    // Load samples on first open
    loadSamples();
}

function openSamplesSidebar() {
    var sidebar = document.getElementById('samplesSidebar');
    var overlay = document.getElementById('samplesOverlay');
    
    if (sidebar) sidebar.classList.add('open');
    if (overlay) overlay.classList.add('show');
    document.body.style.overflow = 'hidden';
    
    // Update language note
    updateSamplesLanguageNote();
}

function closeSamplesSidebar() {
    var sidebar = document.getElementById('samplesSidebar');
    var overlay = document.getElementById('samplesOverlay');
    
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('show');
    document.body.style.overflow = '';
}

function updateSamplesLanguageNote() {
    var noteEl = document.getElementById('samplesLanguageNote');
    if (!noteEl) return;
    
    var currentLang = I18n.getLanguage();
    var noteKey = currentLang === 'en' ? 'samples.language.note.en' : 'samples.language.note.tr';
    noteEl.textContent = I18n.t(noteKey);
}

function loadSamples() {
    fetch('/api/samples/list')
        .then(function(response) { return response.json(); })
        .then(function(samples) {
            SampleTestState.samples = samples;
            renderSampleCards(samples);
        })
        .catch(function(error) {
            console.error('Error loading samples:', error);
            var body = document.getElementById('samplesSidebarBody');
            if (body) {
                body.innerHTML = '<div class="samples-loading"><span>' + I18n.t('failed.to.load.samples') + '</span></div>';
            }
        });
}

function renderSampleCards(samples) {
    var body = document.getElementById('samplesSidebarBody');
    if (!body) return;
    
    var html = '';
    samples.forEach(function(sample) {
        html += `
            <div class="sample-card" data-sample-id="${sample.id}">
                <div class="sample-card-header">
                    <div class="sample-card-number">${sample.id}</div>
                    <div class="sample-card-badge">` + I18n.t('ready') + `</div>
                </div>
                <div class="sample-card-images">
                    <div class="sample-card-image-wrapper">
                        <span class="sample-card-image-label">` + I18n.t('ref.label') + `</span>
                        <img src="/api/samples/image/${sample.reference}" alt="Reference" class="sample-card-image">
                    </div>
                    <div class="sample-card-image-wrapper">
                        <span class="sample-card-image-label">` + I18n.t('sample.label') + `</span>
                        <img src="/api/samples/image/${sample.sample}" alt="Sample" class="sample-card-image">
                    </div>
                </div>
                <button class="sample-card-btn" data-sample-id="${sample.id}" type="button">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    ` + I18n.t('run') + ` ${sample.name}
                </button>
            </div>
        `;
    });
    
    body.innerHTML = html;
    
    // Attach click handlers
    var buttons = body.querySelectorAll('.sample-card-btn');
    buttons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            var sampleId = parseInt(btn.getAttribute('data-sample-id'));
            runSampleTest(sampleId);
        });
    });
}

function runSampleTest(sampleId) {
    var sample = SampleTestState.samples.find(function(s) { return s.id === sampleId; });
    if (!sample) return;
    
    SampleTestState.isActive = true;
    SampleTestState.currentSample = sample;
    
    // Close sidebar
    closeSamplesSidebar();
    
    // Load images into the viewer
    loadSampleImages(sample);
    
    // Start simulated processing after a short delay
    setTimeout(function() {
        runSimulatedProcessing(sample);
    }, 500);
}

function loadSampleImages(sample) {
    var refPreview = document.getElementById('refPreview');
    var testPreview = document.getElementById('testPreview');
    var refPlaceholder = document.getElementById('refPlaceholder');
    var testPlaceholder = document.getElementById('testPlaceholder');
    var refInfo = document.getElementById('refInfo');
    var testInfo = document.getElementById('testInfo');
    
    // Set reference image
    if (refPreview && refPlaceholder) {
        refPreview.src = '/api/samples/image/' + sample.reference;
            refPreview.onload = function() {
                refPreview.style.display = 'block';
                refPlaceholder.style.display = 'none';
                if (refInfo) refInfo.textContent = I18n.t('sample.tests');
            };
    }
    
    // Set sample image
    if (testPreview && testPlaceholder) {
        testPreview.src = '/api/samples/image/' + sample.sample;
            testPreview.onload = function() {
                testPreview.style.display = 'block';
                testPlaceholder.style.display = 'none';
                if (testInfo) testInfo.textContent = I18n.t('sample.tests');
            };
    }
}

function runSimulatedProcessing(sample) {
    // Show progress modal
    showSampleProgressModal();
    
    // Simulated progress steps
    var steps = [
        { step: 'upload', progress: 10, status: I18n.t('uploading.images'), delay: 300 },
        { step: 'color', progress: 35, status: I18n.t('analyzing.colors'), delay: 600 },
        { step: 'pattern', progress: 60, status: I18n.t('analyzing.patterns'), delay: 600 },
        { step: 'repetition', progress: 80, status: I18n.t('analyzing.repetition'), delay: 500 },
        { step: 'scoring', progress: 90, status: I18n.t('calculating.scores'), delay: 400 },
        { step: 'report', progress: 100, status: I18n.t('load.report'), delay: 300 }
    ];
    
    var currentStep = 0;
    
    function processNextStep() {
        if (currentStep >= steps.length) {
            // Complete - show results
            setTimeout(function() {
                hideProgressModal();
                displaySampleResults(sample);
            }, 500);
            return;
        }
        
        var stepData = steps[currentStep];
        updateSampleProgress(stepData.step, stepData.progress, stepData.status);
        
        // Mark previous steps as completed
        for (var i = 0; i < currentStep; i++) {
            completeSampleStep(steps[i].step);
        }
        
        currentStep++;
        setTimeout(processNextStep, stepData.delay);
    }
    
    processNextStep();
}

function showSampleProgressModal() {
    var overlay = document.getElementById('loadingOverlay');
    var content = document.querySelector('.loading-content');
    
    if (content) {
        content.innerHTML = `
            <div class="progress-modal">
                <div class="progress-header">
                    <div class="spinner"></div>
                    <h3 id="progressTitle">` + I18n.t('loading.sample.test') + `</h3>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" id="progressBarFill"></div>
                </div>
                <div class="progress-percentage" id="progressPercentage">0%</div>
                <div class="progress-status" id="progressStatus">` + I18n.t('preparing') + `</div>
                <div class="progress-steps" id="progressSteps">
                    <div class="step" data-step="upload"><span class="step-icon">○</span> ` + I18n.t('load.images') + `</div>
                    <div class="step" data-step="color"><span class="step-icon">○</span> ` + I18n.t('color.analysis.step') + `</div>
                    <div class="step" data-step="pattern"><span class="step-icon">○</span> ` + I18n.t('pattern.analysis.step') + `</div>
                    <div class="step" data-step="repetition"><span class="step-icon">○</span> ` + I18n.t('pattern.repetition.step') + `</div>
                    <div class="step" data-step="scoring"><span class="step-icon">○</span> ` + I18n.t('calculate.scores') + `</div>
                    <div class="step" data-step="report"><span class="step-icon">○</span> ` + I18n.t('load.report') + `</div>
                </div>
            </div>
        `;
    }
    
    if (overlay) overlay.style.display = 'flex';
}

function updateSampleProgress(step, percentage, status) {
    var bar = document.getElementById('progressBarFill');
    var pct = document.getElementById('progressPercentage');
    var stat = document.getElementById('progressStatus');
    var title = document.getElementById('progressTitle');
    
    if (bar) bar.style.width = percentage + '%';
    if (pct) pct.textContent = percentage + '%';
    if (stat) stat.textContent = status;
    if (title) title.textContent = I18n.t('processing') + ' ' + percentage + '%';
    
    // Mark step as active
    var stepEl = document.querySelector('.step[data-step="' + step + '"]');
    if (stepEl) {
        stepEl.classList.add('active');
        var icon = stepEl.querySelector('.step-icon');
        if (icon) icon.textContent = '●';
    }
}

function completeSampleStep(step) {
    var stepEl = document.querySelector('.step[data-step="' + step + '"]');
    if (stepEl) {
        stepEl.classList.remove('active');
        stepEl.classList.add('completed');
        var icon = stepEl.querySelector('.step-icon');
        if (icon) icon.textContent = '✓';
    }
}

function displaySampleResults(sample) {
    var resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Set decision badge based on sample (simulate results)
    var badge = document.getElementById('decisionBadge');
    var decisions = ['ACCEPT', 'CONDITIONAL ACCEPT', 'ACCEPT'];
    var decision = decisions[(sample.id - 1) % decisions.length];
    
    if (badge) {
        badge.textContent = decision;
        badge.className = 'decision-badge';
        if (decision === 'ACCEPT') badge.classList.add('accept');
        else if (decision.indexOf('CONDITIONAL') >= 0) badge.classList.add('conditional');
        else badge.classList.add('reject');
    }
    
    // Simulate scores based on sample
    var scores = [
        { color: 92.5, pattern: 88.3, overall: 90.4 },
        { color: 78.2, pattern: 82.1, overall: 80.2 },
        { color: 95.1, pattern: 91.7, overall: 93.4 }
    ];
    var scoreSet = scores[(sample.id - 1) % scores.length];
    
    animateScore('colorScore', 'colorBar', scoreSet.color);
    animateScore('patternScore', 'patternBar', scoreSet.pattern);
    animateScore('overallScore', 'overallBar', scoreSet.overall);
    
    // Update download button for sample report
    var btnDownload = document.getElementById('btnDownload');
    if (btnDownload) {
        btnDownload.disabled = false;
        // Remove old event listeners and add new one
        var newBtn = btnDownload.cloneNode(true);
        btnDownload.parentNode.replaceChild(newBtn, btnDownload);
        newBtn.addEventListener('click', function() {
            downloadSampleReport(sample.id);
        });
    }
}

function downloadSampleReport(sampleId) {
    // Get current language and append to URL
    var currentLang = I18n.getLanguage();
    var downloadUrl = '/api/samples/report/' + sampleId + '?lang=' + currentLang;
    
    var a = document.createElement('a');
    a.href = downloadUrl;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}
