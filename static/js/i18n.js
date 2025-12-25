/**
 * Internationalization (i18n) System for Textile QC System
 * Supports English and Turkish
 */

var I18n = {
    currentLang: 'en',
    
    translations: {
        en: {
            // Header
            'app.title': 'Textile QC System',
            'app.subtitle': 'Professional Color & Pattern Analysis',
            'source.code': 'Source Code',
            'download.source': 'Download Source',
            
            // Sample Tests
            'samples': 'Samples',
            'sample.tests': 'Sample Tests',
            'loading.samples': 'Loading samples...',
            'preconfigured.tests': 'Pre-configured tests with generated reports',
            'run': 'Run',
            'ready': 'Ready',
            'ref.label': 'Ref',
            'sample.label': 'Sample',
            'samples.language.note.en': 'If you want the samples in Turkish, change the site language.',
            'samples.language.note.tr': 'If you want the samples in English, change the site language.',
            
            // Main Content
            'page.title': 'Image Quality Control Analysis',
            'page.subtitle': 'Upload reference and sample images to begin quality control analysis',
            'reference.image': 'Reference Image',
            'sample.image': 'Sample Image',
            'no.image': 'No image',
            'click.to.upload': 'Click to upload',
            
            // Shape Controls
            'circle': 'Circle',
            'square': 'Square',
            'process.entire.image': 'Process Entire Image',
            'size.px': 'Size (px):',
            'px': 'px',
            
            // Buttons
            'advanced.settings': 'Advanced Settings',
            'start.processing': 'Start Processing',
            'delete.images': 'Delete Images',
            
            // Results
            'analysis.results': 'Analysis Results',
            'color.score': 'Color Score',
            'pattern.score': 'Pattern Score',
            'overall.score': 'Overall Score',
            'download.report': 'Download Report (PDF)',
            'download.settings': 'Download Settings',
            
            // Loading
            'processing': 'Processing...',
            'please.wait': 'Please wait',
            'uploading.images': 'Uploading images...',
            'analyzing.colors': 'Analyzing colors...',
            'analyzing.patterns': 'Analyzing patterns...',
            'analyzing.repetition': 'Analyzing repetition...',
            'calculating.scores': 'Calculating scores...',
            'generating.report': 'Generating report...',
            'processing.complete': 'Processing complete!',
            'complete': 'Complete!',
            'preparing': 'Preparing...',
            'load.images': 'Load Images',
            'load.report': 'Load Report',
            'loading.sample.test': 'Loading Sample Test...',
            
            // Modal - Tabs
            'thresholds': 'Thresholds',
            'color.analysis': 'Color Analysis',
            'pattern.analysis': 'Pattern Analysis',
            'report.sections': 'Report Sections',
            'advanced.settings.title': 'Advanced Settings',
            'configure.parameters': 'Configure analysis parameters',
            
            // Modal - Thresholds
            'color.thresholds': 'Color Thresholds',
            'de.pass.threshold': 'ΔE Pass Threshold',
            'de.conditional.threshold': 'ΔE Conditional Threshold',
            'pattern.thresholds': 'Pattern Thresholds',
            'ssim.pass.threshold': 'SSIM Pass Threshold',
            'ssim.conditional.threshold': 'SSIM Conditional Threshold',
            'score.thresholds': 'Score Thresholds',
            'color.score.threshold': 'Color Score Threshold',
            'pattern.score.threshold': 'Pattern Score Threshold',
            'overall.score.threshold': 'Overall Score Threshold',
            
            // Modal - Color Analysis
            'color.difference.methods': 'Color Difference Methods',
            'use.cmc': 'Use CMC Color Difference',
            'cmc.ratio': 'CMC l:c Ratio',
            'acceptability': 'Acceptability',
            'perceptibility': 'Perceptibility',
            'spectrophotometer.settings': 'Spectrophotometer Settings',
            'observer.angle': 'Observer Angle',
            'standard.observer': 'Standard Observer',
            'geometry.mode': 'Geometry Mode',
            
            // Modal - Pattern Analysis
            'texture.parameters': 'Texture Parameters',
            'lbp.points': 'LBP Points',
            'lbp.radius': 'LBP Radius',
            'wavelet.type': 'Wavelet Type',
            'wavelet.levels': 'Wavelet Levels',
            'pattern.repetition': 'Pattern Repetition',
            'pattern.min.area': 'Pattern Min Area (px)',
            'pattern.max.area': 'Pattern Max Area (px)',
            'keypoint.detector': 'Keypoint Detector',
            'fast': 'Fast',
            'accurate': 'Accurate',
            
            // Modal - Report Sections
            'color.unit': 'Color Unit',
            'pattern.unit': 'Pattern Unit',
            'pattern.repetition.unit': 'Pattern Repetition',
            'spectrophotometer': 'Spectrophotometer',
            'analysis.settings.page': 'Analysis Settings Page',
            'operator.info': 'Operator Info',
            'operator.name': 'Operator Name',
            'operator': 'Operator',
            
            // Modal - Buttons
            'reset.to.defaults': 'Reset to Defaults',
            'cancel': 'Cancel',
            'apply.settings': 'Apply Settings',
            
            // Help Dialog
            'format.information': 'Format Information',
            'python.script': 'Python Script (.py)',
            'jupyter.notebook': 'Jupyter Notebook (.ipynb)',
            'download.this.format': 'Download this format',
            'learn.more': 'Learn more',
            
            // Errors & Messages
            'error.reading.file': 'Error reading file',
            'please.upload.both': 'Please upload both reference and sample images',
            'delete.confirm': 'Delete all images and start over?',
            'failed.to.load.samples': 'Failed to load samples',
            
            // Development Modal
            'development.title': 'Website Under Development',
            'development.message': 'This website is currently under development.',
            'development.view.samples': 'You can view the results through the ready-made samples from the Samples section on the left side of the screen.',
            'development.test.new': 'Or, to test new samples, download the source code (Python) and test it directly in the Google Colab environment.',
            'development.logos.note': 'To obtain full results, these logos must be added to Google Colab with the same filenames.',
            'development.download.logo': 'Download logo',
            'development.go.colab': 'Go to Google Colab',
            'development.download.code': 'Download the code available on the homepage',
            'development.source.code': 'Source Code',
            'development.close': 'Close',
            
            // Footer
            'copyright': '© 2025 Textile Engineering Solutions | Abdelbary Algamel PAU',
            
            // Progress Steps
            'upload.images': 'Upload Images',
            'color.analysis.step': 'Color Analysis',
            'pattern.analysis.step': 'Pattern Analysis',
            'pattern.repetition.step': 'Pattern Repetition',
            'calculate.scores': 'Calculate Scores',
            'generate.report': 'Generate Report',
            
            // Source Code Help
            'what.is.python': 'What is a Python (.py) file?',
            'what.is.notebook': 'What is a Jupyter Notebook (.ipynb)?',
            'best.for': 'Best for:',
            'local.development': 'Local development, integration into existing projects, or running on servers.',
            'google.colab': 'Google Colab, quick experiments, learning, or when you don\'t want to set up a local environment.',
            'python.script.desc': 'A <strong>.py file</strong> is a standard Python script that can be executed in any Python environment.',
            'python.works.with': 'Works with Python 3.7 or higher',
            'python.run.directly': 'Run directly from command line or any IDE',
            'python.ideal.for': 'Ideal for local development and integration',
            'python.can.import': 'Can be imported as a module in your projects',
            'python.best.for': 'Local development, integration into existing projects, or running on servers.',
            'notebook.desc': 'A <strong>.ipynb file</strong> is an interactive notebook format perfect for step-by-step analysis and visualization.',
            'notebook.runs.colab': 'Runs directly in <strong>Google Colab</strong> — no setup needed!',
            'notebook.interactive': 'Interactive cells with explanations',
            'notebook.easy.modify': 'Easy to modify and experiment with',
            'notebook.visualizations': 'Visualizations are displayed inline',
            'notebook.best.for': 'Google Colab, quick experiments, learning, or when you don\'t want to set up a local environment.'
        },
        
        tr: {
            // Header
            'app.title': 'Tekstil Kalite Kontrol Sistemi',
            'app.subtitle': 'Profesyonel Renk ve Desen Analizi',
            'source.code': 'Kaynak Kod',
            'download.source': 'Kaynak Kod İndir',
            
            // Sample Tests
            'samples': 'Örnekler',
            'sample.tests': 'Örnek Testler',
            'loading.samples': 'Örnekler yükleniyor...',
            'preconfigured.tests': 'Hazır raporlarla önceden yapılandırılmış testler',
            'run': 'Çalıştır',
            'ready': 'Hazır',
            'ref.label': 'Ref',
            'sample.label': 'Örnek',
            'samples.language.note.en': 'Örnekleri Türkçe olarak görmek istiyorsanız, site dilini değiştirin.',
            'samples.language.note.tr': 'Örnekleri İngilizce olarak görmek istiyorsanız, site dilini değiştirin.',
            
            // Main Content
            'page.title': 'Görüntü Kalite Kontrol Analizi',
            'page.subtitle': 'Kalite kontrol analizine başlamak için referans ve örnek görüntüleri yükleyin',
            'reference.image': 'Referans Görüntü',
            'sample.image': 'Örnek Görüntü',
            'no.image': 'Görüntü yok',
            'click.to.upload': 'Yüklemek için tıklayın',
            
            // Shape Controls
            'circle': 'Daire',
            'square': 'Kare',
            'process.entire.image': 'Tüm Görüntüyü İşle',
            'size.px': 'Boyut (px):',
            'px': 'px',
            
            // Buttons
            'advanced.settings': 'Gelişmiş Ayarlar',
            'start.processing': 'İşlemeyi Başlat',
            'delete.images': 'Görüntüleri Sil',
            
            // Results
            'analysis.results': 'Analiz Sonuçları',
            'color.score': 'Renk Skoru',
            'pattern.score': 'Desen Skoru',
            'overall.score': 'Genel Skor',
            'download.report': 'Raporu İndir (PDF)',
            'download.settings': 'Ayarları İndir',
            
            // Loading
            'processing': 'İşleniyor...',
            'please.wait': 'Lütfen bekleyin',
            'uploading.images': 'Görüntüler yükleniyor...',
            'analyzing.colors': 'Renkler analiz ediliyor...',
            'analyzing.patterns': 'Desenler analiz ediliyor...',
            'analyzing.repetition': 'Tekrar analiz ediliyor...',
            'calculating.scores': 'Skorlar hesaplanıyor...',
            'generating.report': 'Rapor oluşturuluyor...',
            'processing.complete': 'İşleme tamamlandı!',
            'complete': 'Tamamlandı!',
            'preparing': 'Hazırlanıyor...',
            'load.images': 'Görüntüleri Yükle',
            'load.report': 'Raporu Yükle',
            'loading.sample.test': 'Örnek Test Yükleniyor...',
            
            // Modal - Tabs
            'thresholds': 'Eşikler',
            'color.analysis': 'Renk Analizi',
            'pattern.analysis': 'Desen Analizi',
            'report.sections': 'Rapor Bölümleri',
            'advanced.settings.title': 'Gelişmiş Ayarlar',
            'configure.parameters': 'Analiz parametrelerini yapılandır',
            
            // Modal - Thresholds
            'color.thresholds': 'Renk Eşikleri',
            'de.pass.threshold': 'ΔE Geçiş Eşiği',
            'de.conditional.threshold': 'ΔE Koşullu Eşik',
            'pattern.thresholds': 'Desen Eşikleri',
            'ssim.pass.threshold': 'SSIM Geçiş Eşiği',
            'ssim.conditional.threshold': 'SSIM Koşullu Eşik',
            'score.thresholds': 'Skor Eşikleri',
            'color.score.threshold': 'Renk Skoru Eşiği',
            'pattern.score.threshold': 'Desen Skoru Eşiği',
            'overall.score.threshold': 'Genel Skor Eşiği',
            
            // Modal - Color Analysis
            'color.difference.methods': 'Renk Farkı Yöntemleri',
            'use.cmc': 'CMC Renk Farkı Kullan',
            'cmc.ratio': 'CMC l:c Oranı',
            'acceptability': 'Kabul Edilebilirlik',
            'perceptibility': 'Algılanabilirlik',
            'spectrophotometer.settings': 'Spektrofotometre Ayarları',
            'observer.angle': 'Gözlemci Açısı',
            'standard.observer': 'Standart Gözlemci',
            'geometry.mode': 'Geometri Modu',
            
            // Modal - Pattern Analysis
            'texture.parameters': 'Doku Parametreleri',
            'lbp.points': 'LBP Noktaları',
            'lbp.radius': 'LBP Yarıçapı',
            'wavelet.type': 'Dalga Tipi',
            'wavelet.levels': 'Dalga Seviyeleri',
            'pattern.repetition': 'Desen Tekrarı',
            'pattern.min.area': 'Desen Min Alan (px)',
            'pattern.max.area': 'Desen Maks Alan (px)',
            'keypoint.detector': 'Anahtar Nokta Dedektörü',
            'fast': 'Hızlı',
            'accurate': 'Doğru',
            
            // Modal - Report Sections
            'color.unit': 'Renk Birimi',
            'pattern.unit': 'Desen Birimi',
            'pattern.repetition.unit': 'Desen Tekrarı',
            'spectrophotometer': 'Spektrofotometre',
            'analysis.settings.page': 'Analiz Ayarları Sayfası',
            'operator.info': 'Operatör Bilgisi',
            'operator.name': 'Operatör Adı',
            'operator': 'Operatör',
            
            // Modal - Buttons
            'reset.to.defaults': 'Varsayılanlara Sıfırla',
            'cancel': 'İptal',
            'apply.settings': 'Ayarları Uygula',
            
            // Help Dialog
            'format.information': 'Biçim Bilgisi',
            'python.script': 'Python Betiği (.py)',
            'jupyter.notebook': 'Jupyter Defteri (.ipynb)',
            'download.this.format': 'Bu biçimi indir',
            'learn.more': 'Daha fazla bilgi',
            
            // Errors & Messages
            'error.reading.file': 'Dosya okuma hatası',
            'please.upload.both': 'Lütfen hem referans hem de örnek görüntüleri yükleyin',
            'delete.confirm': 'Tüm görüntüleri silip yeniden başlamak istiyor musunuz?',
            'failed.to.load.samples': 'Örnekler yüklenemedi',
            
            // Development Modal
            'development.title': 'Web Sitesi Geliştirme Aşamasında',
            'development.message': 'Bu web sitesi şu anda geliştirme aşamasındadır.',
            'development.view.samples': 'Sonuçları ekranın sol tarafındaki Örnekler bölümündeki hazır örnekler aracılığıyla görüntüleyebilirsiniz.',
            'development.test.new': 'Veya yeni örnekleri test etmek için kaynak kodu (Python) indirin ve doğrudan Google Colab ortamında test edin.',
            'development.logos.note': 'Tam sonuçları elde etmek için bu logolar aynı dosya adlarıyla Google Colab\'a eklenmelidir.',
            'development.download.logo': 'Logoyu indir',
            'development.go.colab': 'Google Colab\'a Git',
            'development.download.code': 'Ana sayfadaki kodu indir',
            'development.source.code': 'Kaynak Kod',
            'development.close': 'Kapat',
            
            // Footer
            'copyright': '© 2025 Tekstil Mühendisliği Çözümleri | Abdelbary Algamel PAU',
            
            // Progress Steps
            'upload.images': 'Görüntüleri Yükle',
            'color.analysis.step': 'Renk Analizi',
            'pattern.analysis.step': 'Desen Analizi',
            'pattern.repetition.step': 'Desen Tekrarı',
            'calculate.scores': 'Skorları Hesapla',
            'generate.report': 'Rapor Oluştur',
            
            // Source Code Help
            'what.is.python': 'Python (.py) dosyası nedir?',
            'what.is.notebook': 'Jupyter Notebook (.ipynb) nedir?',
            'best.for': 'En iyi:',
            'local.development': 'Yerel geliştirme, mevcut projelere entegrasyon veya sunucularda çalıştırma.',
            'google.colab': 'Google Colab, hızlı denemeler, öğrenme veya yerel ortam kurmak istemediğinizde.',
            'python.script.desc': '<strong>.py dosyası</strong>, herhangi bir Python ortamında çalıştırılabilen standart bir Python betiğidir.',
            'python.works.with': 'Python 3.7 veya daha yüksek sürümlerle çalışır',
            'python.run.directly': 'Komut satırından veya herhangi bir IDE\'den doğrudan çalıştırın',
            'python.ideal.for': 'Yerel geliştirme ve entegrasyon için idealdir',
            'python.can.import': 'Projelerinizde modül olarak içe aktarılabilir',
            'python.best.for': 'Yerel geliştirme, mevcut projelere entegrasyon veya sunucularda çalıştırma.',
            'notebook.desc': '<strong>.ipynb dosyası</strong>, adım adım analiz ve görselleştirme için mükemmel olan etkileşimli bir defter formatıdır.',
            'notebook.runs.colab': '<strong>Google Colab</strong> içinde doğrudan çalışır — kurulum gerekmez!',
            'notebook.interactive': 'Açıklamalı etkileşimli hücreler',
            'notebook.easy.modify': 'Değiştirmesi ve denemesi kolay',
            'notebook.visualizations': 'Görselleştirmeler satır içi gösterilir',
            'notebook.best.for': 'Google Colab, hızlı denemeler, öğrenme veya yerel ortam kurmak istemediğinizde.'
        }
    },
    
    /**
     * Initialize i18n system
     */
    init: function() {
        // Load saved language preference or default to English
        var savedLang = localStorage.getItem('textile_qc_lang');
        if (savedLang && this.translations[savedLang]) {
            this.currentLang = savedLang;
        }
        
        // Set HTML lang attribute
        document.documentElement.lang = this.currentLang;
        
        // Apply translations
        this.translatePage();
    },
    
    /**
     * Translate a key
     */
    t: function(key) {
        var translation = this.translations[this.currentLang];
        if (!translation) {
            translation = this.translations['en'];
        }
        return translation[key] || key;
    },
    
    /**
     * Translate entire page
     */
    translatePage: function() {
        // Translate elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(function(el) {
            var key = el.getAttribute('data-i18n');
            var translation = I18n.t(key);
            
            // Handle different element types
            if (el.tagName === 'INPUT' && el.type === 'text' || el.tagName === 'INPUT' && el.type === 'number') {
                if (el.placeholder) {
                    el.placeholder = translation;
                } else {
                    el.value = translation;
                }
            } else if (el.tagName === 'INPUT' && el.type === 'button' || el.tagName === 'BUTTON') {
                // Don't translate button text if it contains dynamic content
                if (!el.hasAttribute('data-no-translate')) {
                    el.textContent = translation;
                }
            } else if (el.hasAttribute('data-i18n-html')) {
                el.innerHTML = translation;
            } else {
                el.textContent = translation;
            }
        });
        
        // Translate title
        var titleEl = document.querySelector('title');
        if (titleEl) {
            titleEl.textContent = I18n.t('app.title') + ' - ' + I18n.t('app.subtitle');
        }
        
        // Update language switcher button
        updateLanguageSwitcher();
    },
    
    /**
     * Change language
     */
    setLanguage: function(lang) {
        if (!this.translations[lang]) {
            console.warn('Language not supported:', lang);
            return;
        }
        
        this.currentLang = lang;
        localStorage.setItem('textile_qc_lang', lang);
        document.documentElement.lang = lang;
        this.translatePage();
        
        // Trigger custom event for other scripts
        document.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang: lang } }));
    },
    
    /**
     * Get current language
     */
    getLanguage: function() {
        return this.currentLang;
    }
};

/**
 * Update language switcher button appearance
 */
function updateLanguageSwitcher() {
    var btn = document.getElementById('btnLanguageSwitcher');
    if (!btn) return;
    
    var lang = I18n.getLanguage();
    var langText = lang === 'en' ? 'TR' : 'EN';
    var flag = lang === 'en' ? '🇹🇷' : '🇬🇧';
    
    var span = btn.querySelector('.lang-text');
    if (span) {
        span.textContent = langText;
    }
    
    var flagSpan = btn.querySelector('.lang-flag');
    if (flagSpan) {
        flagSpan.textContent = flag;
    }
    
    // Update title
    btn.title = lang === 'en' ? 'Türkçe\'ye Geç' : 'Switch to English';
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        I18n.init();
    });
} else {
    I18n.init();
}

