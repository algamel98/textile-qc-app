// ==========================================
// Development Modal
// ==========================================
function initDevelopmentModal() {
    var modal = document.getElementById('developmentModal');
    var closeBtn = document.getElementById('btnDevelopmentClose');
    var colabBtn = document.getElementById('btnDevelopmentColab');
    var downloadCodeBtn = document.getElementById('btnDevelopmentDownloadCode');
    var logoButtons = document.querySelectorAll('.btn-logo-download');
    
    if (!modal) return;
    
    // Close button
    if (closeBtn) {
        closeBtn.addEventListener('click', hideDevelopmentModal);
    }
    
    // Close on overlay click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            hideDevelopmentModal();
        }
    });
    
    // Google Colab button
    if (colabBtn) {
        colabBtn.addEventListener('click', function() {
            window.open('https://colab.research.google.com/', '_blank');
        });
    }
    
    // Download code button
    if (downloadCodeBtn) {
        downloadCodeBtn.addEventListener('click', function() {
            downloadSourceCode('ipynb');
            // Also show code in modal
            loadSourceCodeInModal();
        });
    }
    
    // Logo download buttons
    logoButtons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var logoName = btn.getAttribute('data-logo');
            downloadLogo(logoName);
        });
    });
    
    // Escape key closes modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display !== 'none') {
            hideDevelopmentModal();
        }
    });
}

function showDevelopmentModal() {
    var modal = document.getElementById('developmentModal');
    if (!modal) return;
    
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    // Apply translations
    I18n.translatePage();
}

function hideDevelopmentModal() {
    var modal = document.getElementById('developmentModal');
    if (!modal) return;
    
    modal.style.display = 'none';
    document.body.style.overflow = '';
}

function downloadLogo(logoName) {
    var downloadUrl = '/api/download/logo/' + logoName;
    
    var a = document.createElement('a');
    a.href = downloadUrl;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function loadSourceCodeInModal() {
    var codeSection = document.getElementById('developmentCodeSection');
    var codeContent = document.getElementById('developmentCodeContent');
    
    if (!codeSection || !codeContent) return;
    
    // Fetch the source code
    fetch('/api/source/ipynb')
        .then(function(response) {
            if (!response.ok) throw new Error('Failed to load source code');
            return response.blob();
        })
        .then(function(blob) {
            return blob.text();
        })
        .then(function(text) {
            codeContent.textContent = text;
            codeSection.style.display = 'block';
            codeSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        })
        .catch(function(error) {
            console.error('Error loading source code:', error);
            codeContent.textContent = 'Error loading source code. Please use the download button.';
            codeSection.style.display = 'block';
        });
}

